"""Stage complete upstream Words C++ source as supplemental documentation.

No publication, source execution, header guessing or changes to SDK symbols.
All source lines are retained; large files are split into labelled retrieval parts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
INCLUDES = re.compile(r'^\s*#\s*include\s*[<\"]([^>\"]+)[>\"].*$', re.M)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True, encoding='utf-8').strip()


def contained(root, relative):
    path = Path(relative)
    target = (root / path).resolve()
    if path.is_absolute() or '..' in path.parts or not target.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes configured root: {relative}')
    return target


def split_source(text, limit):
    parts, current, size, start, line = [], [], 0, 1, 1
    for value in text.splitlines(keepends=True):
        if current and size + len(value) > limit:
            parts.append((start, line - 1, ''.join(current)))
            current, size, start = [], 0, line
        current.append(value)
        size += len(value)
        line += 1
    if current:
        parts.append((start, line - 1, ''.join(current)))
    assert ''.join(part[2] for part in parts) == text
    return parts


def source_text(path):
    raw = path.read_bytes()
    encoding = 'utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
    return raw.decode(encoding).replace('\r\n', '\n').replace('\r', '\n')


def render_source(relative, text, *, revision, repository_url, sdk_version, context, limit):
    source_url = repository_url.removesuffix('.git') + '/blob/' + revision + '/' + quote(relative, safe='/')
    parts = split_source(text, limit)
    # Backtick fence lines inside source would be reinterpreted by the existing parser.
    if re.search(r'^\s*```', text, re.M):
        raise ValueError(f'Unsupported embedded Markdown fence in {relative}; refusing lossy extraction')
    title = f'Aspose.Words C++ complete source: {Path(relative).name}'
    front = {'title':title, 'url':source_url, 'type':'docs', 'examples_revision':revision,
             'examples_file':relative, 'examples_sdk_version':sdk_version,
             'examples_source_sha256':hashlib.sha256(text.encode()).hexdigest()}
    out = ['---', *(f'{k}: {json.dumps(v)}' for k,v in front.items()), '---', '', '# '+title, '',
           f'Original source: {source_url}', f'Upstream commit: {revision}. SDK dependency declared by upstream: {sdk_version}.',
           'Full source file, including includes, comments and helper usage. All source lines are retained in order.',
           'These are repository examples, not independently compiled programs. Test fixtures may need companion headers, shared helpers, test frameworks and input files. No main function or headers have been invented.',
           'Header paths are preserved as written for this upstream revision; they are not guaranteed for other SDK versions.', '']
    for n,(start,end,body) in enumerate(parts,1):
        names = list(dict.fromkeys(re.findall(r'\b(?:[A-Za-z_]\w*::)+[A-Za-z_]\w*|\b(?:TEST_F|TEST)\([^\n]+',body)))[:16]
        out += [f'## {Path(relative).stem}: source lines {start}-{end} (part {n}/{len(parts)})',
                'APIs and tests in this part: '+', '.join(names) if names else '',
                f'Source range: {source_url}#L{start}-L{end}',
                'This part is a source fragment; read the other parts and dependency sources before assembling a program.' if len(parts)>1 else 'This part contains the complete source file.',
                '', '```cpp']
        if context:
            out += ['// Dependency context copied from this file and its repository-local headers.',
                    '// Context is repeated for retrieval; original source begins at the line marker below.', *context]
        out += [f'// ORIGINAL SOURCE: {relative}, lines {start}-{end}',body.rstrip('\n'),'```','']
    return '\n'.join(out)


def generate(repo, config, revision):
    files = []
    for scope in config['source_roots']:
        folder = contained(repo, scope)
        if not folder.is_dir():
            raise ValueError(f'Missing examples source root: {folder}')
        files += [p for p in folder.rglob('*') if p.suffix.lower() in {'.cpp','.h','.hpp','.cxx','.cc'} and p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(folder)]
    files = sorted(set(files))
    if not files:
        raise ValueError('No C++ source files found')
    texts = {p:source_text(p) for p in files}
    by_name = {}
    for p in files:
        by_name.setdefault(p.name, []).append(p)
    versions = {}
    for source_root in config['source_roots']:
        project = Path(source_root).parent
        package = repo / project / 'packages.config'
        match = re.search(r'id="Aspose.Words.Cpp"\s+version="([^"]+)"', package.read_text()) if package.exists() else None
        versions[project.as_posix()] = match[1] if match else 'not declared'
    pages, inventory = {}, []
    for path in files:
        relative = path.relative_to(repo).as_posix()
        queue, seen, context = [path], set(), []
        while queue:
            dependency = queue.pop(0)
            if dependency in seen:
                continue
            seen.add(dependency)
            for match in INCLUDES.finditer(texts[dependency]):
                include = match.group(0).strip()
                if include not in context:
                    context.append(include)
                name = match.group(1)
                local = (dependency.parent / name).resolve()
                candidates = by_name.get(Path(name).name, [])
                if local in texts:
                    queue.append(local)
                elif len(candidates) == 1:
                    queue.append(candidates[0])
        version = next((v for folder,v in versions.items() if relative.startswith(folder+'/')), 'not declared')
        # Each source receives a stable collision-resistant generated filename.
        filename = hashlib.sha256(relative.encode()).hexdigest()[:24]+'.md'
        pages[filename] = render_source(relative, texts[path], revision=revision, repository_url=config['url'],
             sdk_version=version, context=context, limit=config['max_part_characters'])
        inventory.append({'file':relative,'page':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                          'lines':len(texts[path].splitlines()),'parts':len(split_source(texts[path],config['max_part_characters'])),
                          'dependencies':[p.relative_to(repo).as_posix() for p in sorted(seen) if p!=path]})
    return pages, inventory


def write_pages(output, pages, inventory, config, revision):
    marker = output / 'manifest.json'
    old = {}
    if output.exists():
        if not marker.exists():
            raise ValueError(f'Refusing unmanaged output directory: {output}')
        old = json.loads(marker.read_text())
        if old.get('generator') != 'words-cpp-complete-examples.v1':
            raise ValueError('Unrecognized generated source manifest')
        for name, checksum in old['page_checksums'].items():
            path = contained(output,name)
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()!=checksum:
                raise ValueError(f'Generated page was edited; preserve changes before regenerating: {path}')
        unmanaged = {p.name for p in output.iterdir()} - set(old['page_checksums']) - {'manifest.json'}
        if unmanaged:
            raise ValueError(f'Unmanaged files in generated directory: {sorted(unmanaged)}')
    output.mkdir(parents=True,exist_ok=True)
    checksums = {}
    for name, text in pages.items():
        content = text.encode('utf-8')
        path = contained(output,name)
        temporary=path.with_suffix('.tmp')
        temporary.write_bytes(content)
        temporary.replace(path)
        checksums[name] = hashlib.sha256(content).hexdigest()
    # Delete only unchanged files owned by the previous generator manifest.
    for name in set(old.get('page_checksums',{}))-set(pages):
        contained(output,name).unlink(missing_ok=True)
    metadata = {'generator':'words-cpp-complete-examples.v1','repository':config['url'],'revision':revision,
                'page_checksums':checksums,'sources':inventory}
    temp=marker.with_suffix('.tmp')
    temp.write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    temp.replace(marker)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--update',action='store_true',help='Fast-forward the example checkout to its configured branch')
    args=parser.parse_args()
    config=json.loads((ROOT/'config/words-cpp-examples.json').read_text())
    plugin=json.loads((ROOT/'plugins/words-cpp/plugin.json').read_text())
    docs=plugin['sources']['docs']
    docs_repo=contained(ROOT/'engine',docs['path'])
    docs_root=contained(docs_repo,docs['prefix'])
    if not docs_root.is_dir():
        raise SystemExit('Clone the Words documentation source first: '+str(docs_root))
    if git(docs_repo,'remote','get-url','origin').rstrip('/') != docs['url'].rstrip('/'):
        raise SystemExit('Documentation checkout origin differs from the Words manifest')
    repo=contained(ROOT,config['checkout'])
    env=dict(os.environ,GIT_LFS_SKIP_SMUDGE='1')
    if not repo.exists():
        repo.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--depth','1','--filter=blob:none','--sparse','--branch',config['branch'],config['url'],str(repo)],env=env,check=True)
        subprocess.run(['git','-C',str(repo),'sparse-checkout','set',*config['sparse_paths']],env=env,check=True)
    if git(repo,'remote','get-url','origin') != config['url']:
        raise SystemExit('Examples checkout origin differs from configuration')
    if git(repo,'status','--porcelain'):
        raise SystemExit('Examples checkout has local changes; refusing to claim a clean source revision')
    if args.update:
        subprocess.run(['git','-C',str(repo),'pull','--ff-only','origin',config['branch']],env=env,check=True)
    revision=git(repo,'rev-parse','HEAD')
    pages, inventory=generate(repo,config,revision)
    output=contained(docs_root,config['output_directory'])
    write_pages(output,pages,inventory,config,revision)
    print(json.dumps({'source_files':len(inventory),'generated_pages':len(pages),'source_parts':sum(i['parts'] for i in inventory),
                      'revision':revision,'output':str(output),'publication':'not_requested'},indent=2))


if __name__=='__main__':
    main()

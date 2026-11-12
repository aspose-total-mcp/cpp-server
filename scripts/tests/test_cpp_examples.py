import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'plugins/words-cpp/src'))
import prepare_cpp_examples as preparation
from adcs_words_cpp import worker

class CompleteExamplesTests(unittest.TestCase):
    def test_split_keeps_every_line_and_final_newline(self):
        for text in ['#include <Document.h>\nint main() { return 0; }\n','abc\ndef','', 'x'*12000+'\nend\n']:
            parts=preparation.split_source(text,20)
            self.assertEqual(''.join(p[2] for p in parts),text)
            if parts: self.assertEqual(parts[0][0],1)

    def test_containment(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): preparation.contained(Path(tmp),'../escape')

    def test_source_dependencies_and_worker_preserve_includes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            source=repo/'Examples/DocsExamples/source'
            source.mkdir(parents=True)
            code='#include "Heading.h"\n// heading and table\nint main() {\n  auto title = u"Café";\n  return 0;\n}\n'
            (source/'Heading.cpp').write_text(code,encoding='utf-8')
            (source/'Heading.h').write_text('#pragma once\n#include <Aspose.Words.Cpp/Document.h>\n#include <Aspose.Words.Cpp/ParagraphFormat.h>\n')
            (source.parent/'packages.config').write_text('<packages><package id="Aspose.Words.Cpp" version="26.9.0" /></packages>')
            vendor=repo/'Examples/gtest'; vendor.mkdir(); (vendor/'ignored.h').write_text('Not a product example')
            cfg={'source_roots':['Examples/DocsExamples/source'],'url':'https://github.com/aspose-words/Aspose.Words-for-C.git','max_part_characters':10000}
            pages, inventory=preparation.generate(repo,cfg,'a'*40)
            self.assertEqual(len(pages),2)
            item=next(i for i in inventory if i['file'].endswith('Heading.cpp'))
            self.assertIn('Examples/DocsExamples/source/Heading.h',item['dependencies'])
            manifest=json.loads((ROOT/'plugins/words-cpp/plugin.json').read_text())
            source_def=manifest['sources']['docs']
            relative=source_def['prefix']+'/complete-cpp-examples/'+item['page']
            result=worker.handle(dict(contract=manifest['contract'],plugin_id=manifest['plugin_id'],product_id='aspose.words',language='cpp',operation='extract',source_kind='docs',repo_id=source_def['repo_id'],product_family='aspose',source_path=source_def['path']+'/'+relative,relative_repo_path=relative,source_prefix=source_def['prefix'],layout_detection=source_def['layout'],canonical_base_url=source_def['canonical_base_url'],source_revision='docs-sha',raw_markdown=pages[item['page']]))
            snippets=[s['code'] for c in result['chunk_records'] for s in c['executable_snippets']]
            self.assertTrue(any(code.strip() in s for s in snippets))
            self.assertTrue(any('#include <Aspose.Words.Cpp/ParagraphFormat.h>' in s for s in snippets))
            self.assertIn('/blob/'+'a'*40+'/',result['normalized_document']['document']['canonical_url'])
            self.assertIn('examples_sdk_version: "26.9.0"', pages[item['page']])

    def test_managed_output_refuses_edits_and_cleans_only_owned_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'output'
            cfg={'url':'https://example.test/examples.git'}
            preparation.write_pages(out,{'old.md':'old'},[],cfg,'a'*40)
            preparation.write_pages(out,{'new.md':'new'},[],cfg,'b'*40)
            self.assertFalse((out/'old.md').exists())
            (out/'new.md').write_text('user edit')
            with self.assertRaises(ValueError): preparation.write_pages(out,{'new.md':'replacement'},[],cfg,'c'*40)
            self.assertEqual((out/'new.md').read_text(),'user edit')

    def test_unmanaged_output_and_fence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): preparation.write_pages(Path(tmp),{},[],{'url':'x'},'a'*40)
        with self.assertRaises(ValueError): preparation.render_source('x.cpp','```cpp\n',revision='a'*40,repository_url='https://example.test/repo.git',sdk_version='unknown',context=[],limit=20)

if __name__=='__main__': unittest.main()

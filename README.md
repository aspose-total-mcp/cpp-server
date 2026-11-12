# Aspose.Total for C++ MCP Server

Serve Aspose.Words and Aspose.TeX for C++ from one shared engine on port **18082**. Each product has its own extraction plugin and indexes; the Total composition queries those product scopes without duplicating ingestion.

## GitHub components

| Folder | Repository | Selected branch |
| --- | --- | --- |
| `engine` | https://github.com/aspose-core-mcp/context-engine | `codex/total-cpp-serving` |
| `plugins/words-cpp` | https://github.com/aspose-words-mcp/cpp-plugin | `main` |
| `plugins/tex-cpp` | https://github.com/aspose-tex-mcp/cpp-plugin | `main` |

The [Total .NET server](https://github.com/aspose-total-mcp/net-server) is a deployment reference, not the engine repository; its `.gitmodules` identifies the same shared context engine.

All remote branch references are fetched for each component. Only one branch can be checked out per component; other branches are available as `origin/<branch>`. Gitlinks still pin exact commits. The C++ serving branch is selected to include the verified Words, TeX and Total routes.

## Setup

Requires Git and Python 3.12+. From a clean server checkout:

```powershell
git submodule sync -- engine plugins/words-cpp plugins/tex-cpp
git submodule update --init engine plugins/words-cpp plugins/tex-cpp
.\scripts\setup.ps1
```

Linux: `sh scripts/setup.sh`. Do not use recursive initialization; historical engine corpus submodules are not needed. Setup creates the engine and both plugin environments and checks registration, but does not provision databases or ingest content. Preserve local component changes before setup.

To refresh all remote branches without changing selected commits:

```powershell
git -C engine fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune
git -C plugins/words-cpp fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune
git -C plugins/tex-cpp fetch origin '+refs/heads/*:refs/remotes/origin/*' --prune
git -C engine branch -r
```

## Configure and run

Configure persistence, retrieval and embedding services using [engine documentation](engine/README.md). Keep ingestion and serving pointed at the same stores. The C++ Compose file exposes PostgreSQL on localhost port 15432; choose configuration matching your deployment.

```powershell
.\scripts\run-engine.ps1 -m uvicorn adcs.api.main:app --host 127.0.0.1 --port 18082
```

Linux: `sh scripts/run-engine.sh -m uvicorn adcs.api.main:app --host 127.0.0.1 --port 18082`. For queued ingestion, run the wrapper with `-m celery -A adcs.worker.celery_app:celery_app worker --loglevel=info` in another terminal.

## Download sources

From the server root, use normal clones only when the destinations do not exist:

```powershell
$env:GIT_LFS_SKIP_SMUDGE = '1'
New-Item -ItemType Directory -Force engine/sources | Out-Null
git clone --branch master https://github.com/aspose-words-mcp/docs.git engine/sources/documentation-current
git clone --branch main https://github.com/aspose-words-mcp/reference.git engine/sources/api-reference
git clone --branch main https://github.com/aspose-tex-mcp/docs.git engine/sources/tex-documentation
git clone --branch master https://github.com/aspose-tex-mcp/reference.git engine/sources/tex-api-reference
```

Stop if any clone fails. On Linux use `export GIT_LFS_SKIP_SMUDGE=1` and `mkdir -p engine/sources` before the same Git commands. Manifests select only `en/cpp` docs and `english/cpp` API references. Existing checkouts must match the manifest repositories; preserve their local work before migration.

## Prepare Gists and ingest

PowerShell, from the server root:

```powershell
$env:PYTHONPATH = Join-Path $PWD 'plugins/words-cpp/src'
& .\plugins\words-cpp\.venv\Scripts\python.exe -m adcs_words_cpp.gist_examples --source-root engine/sources/documentation-current/en/cpp --cache plugins/words-cpp/sources/gist-examples.json --resolve-history
if ($LASTEXITCODE -ne 0) { throw 'Words Gist preparation failed.' }
$env:PYTHONPATH = Join-Path $PWD 'plugins/tex-cpp/src'
& .\plugins\tex-cpp\.venv\Scripts\python.exe -m adcs_tex_cpp.gist_examples --source-root engine/sources/tex-documentation/en/cpp --cache plugins/tex-cpp/sources/gist-examples.json --resolve-history
if ($LASTEXITCODE -ne 0) { throw 'TeX Gist preparation failed.' }

# Validate both products separately:
.\scripts\ingest.ps1 --source-kind both --timeout 300
.\scripts\ingest-tex.ps1 --source-kind both --timeout 300
# Continue only after successful validation:
.\scripts\ingest.ps1 --source-kind docs --publish --timeout 300
.\scripts\ingest.ps1 --source-kind apiref --publish --timeout 300
.\scripts\ingest-tex.ps1 --source-kind docs --publish --timeout 300
.\scripts\ingest-tex.ps1 --source-kind apiref --publish --timeout 300
```

On Linux prepare each Gist cache with `PYTHONPATH=plugins/<plugin>/src plugins/<plugin>/.venv/bin/python -m <module>.gist_examples` and the same source/cache arguments, then use `sh scripts/ingest.sh` for Words and `sh scripts/ingest-tex.sh` for TeX with the same options. Stop on failures and do not run overlapping ingestion. There is no separate Total ingestion.

## Endpoints and product selection

- Words: `http://127.0.0.1:18082/words/cpp/mcp/v1/streamable-http`
- TeX: `http://127.0.0.1:18082/tex/cpp/mcp/v1/streamable-http`
- Total: `http://127.0.0.1:18082/total/cpp/mcp/v1/streamable-http`

Total accepts `product_id: "aspose.words"` or `product_id: "aspose.tex"` to select one member. Omit the product to return grouped results. Language is C++. Localhost URLs require a local engine or tunnel; use a reachable deployment URL for remote clients. Initialization does not prove corpus ingestion.

## Verification and publication

GitHub Actions checks scripts and JSON, performs registration, tests both plugins and example preparation, and runs C++ endpoint regressions. It does not deploy services or ingest data. See [REGISTRATION.md](REGISTRATION.md) for selected revisions and local results.

Publish component changes first, then commit their updated references in this parent repository. Branch tracking in `.gitmodules` does not automatically update a pinned commit. Component licenses remain in their own repositories; select a root deployment license before public release.

## Complete Words C++ source examples

The optional example source is `https://github.com/aspose-words/Aspose.Words-for-C.git` (`master`). Configuration lives in `config/words-cpp-examples.json`. It selects `Examples/DocsExamples/source` and `Examples/ApiExamples/source`, excluding vendored gtest/SQLite sources and binary input documents. The checkout keeps upstream build files and dependency declarations for reference. No examples are compiled or executed.

Preparation preserves full `.cpp`, `.h`, `.hpp`, `.cxx`, and `.cc` source files. Large files become numbered retrieval parts with original line ranges; every part carries copied include context from the file and resolvable local headers. It does not invent headers, translate nested include paths into flat paths, or fabricate main(). Test-harness dependencies remain explicit. Source citations pin the upstream commit, and the inventory records file checksums, dependency paths, SDK versions in generated pages, and part counts.

Generated Markdown lives under `engine/sources/documentation-current/en/cpp/complete-cpp-examples`. It is supplemental local source content, not a change to the upstream documentation repository. Its manifest protects edited/unmanaged files and tracks stale generated pages. Do not manually edit generated pages or commit them to the upstream docs repository. Reprepare after replacing the docs checkout. Existing example checkouts are preserved; `--update` explicitly fast-forwards the examples branch.

First ensure the normal Words documentation checkout and Gist cache are prepared, and the same database/embedding configuration used by serving is available. To prepare only:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_cpp_examples.py
# Optional explicit source update:
# .\.venv\Scripts\python.exe scripts/prepare_cpp_examples.py --update
```

Validate and then publish **Words documentation plus complete source examples together**:

```powershell
.\scripts\ingest-words-examples.ps1 --timeout 300
# Continue only after validation completes successfully:
.\scripts\ingest-words-examples.ps1 --publish --timeout 300
```

Linux:

```sh
sh scripts/ingest-words-examples.sh --timeout 300
sh scripts/ingest-words-examples.sh --publish --timeout 300
```

These commands prepare the examples before invoking the existing Words docs pipeline. They do not publish an examples-only replacement snapshot, re-ingest API references, or touch TeX. Once prepared, ordinary Words `--source-kind docs` or `both` ingestion also includes these pages. The TeX source configuration is unchanged.

After publication, test `query_docs` on the Words C++ endpoint with focused queries such as `DocumentBuilder heading table complete C++ source includes` or `ExDocumentBuilder source includes`. The new source is documentation retrieval content; `get_symbol` still reads the separate structured API-reference store. Retrieval ranking and Copilot header accuracy are not guaranteed by ingestion alone. A complete source file from the upstream test suite may require its project, helpers and data; compile generated programs against the intended SDK separately.

Initial local verification: 375 source files generated 375 Markdown pages / 692 source parts at revision `14d73190ae38a2e45166286271f49ffc10467c5a`. The real Words extractor produced 1,264 chunks and 692 code snippets with C++ scope and pinned GitHub citations. This check did not publish to the databases.

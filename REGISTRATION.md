# Total C++ registration and verification

## GitHub components

| Component | Branch | Commit |
| --- | --- | --- |
| `engine` | `codex/total-cpp-serving` | `e917d8cc1dbff142ba67cc6b45e75c271c8daa16` |
| `plugins/words-cpp` | `main` | `23366c7be8f233b1f2ebd39991f6fa608cdabe65` |
| `plugins/tex-cpp` | `main` | `13e0d67214558c4711338937a3dc8d7b40429889` |

The shared engine URL is `https://github.com/aspose-core-mcp/context-engine.git`. The Total .NET server is a deployment reference, not engine source. All remote branch references are fetched; nested corpus submodules are not initialized. The parent still pins exact component revisions.

## Local verification

- Both plugin registrations, retrieval profiles and isolated workers passed.
- Words, TeX and Total endpoint initialization identities passed with this deployment catalog.
- Words plugin: 12 tests passed.
- TeX plugin: 14 tests passed.
- Complete Words example preparation: 5 tests passed.
- C++ endpoint regressions: 142 tests passed.

Checks used an existing Python environment against this checkout. A fresh environment installation, hosted GitHub Actions, Docker services and full ingestion were not run. A Starlette/httpx deprecation warning was non-failing.

## Publication

The parent Git repository is initialized and its submodule references are staged; no commit or push was performed. Its origin remote is `https://github.com/aspose-total-mcp/cpp-server.git`. The Total .NET repository is only a deployment reference.

Commit and push component edits first, then commit parent references and setup/documentation changes. Preserve engine and plugin licenses; select a root deployment license before public release.

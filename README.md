# Aspose.Total for C++ MCP Server

One context engine serving **Aspose.Words for C++ and Aspose.TeX for C++** through a Total MCP endpoint. This deployment currently covers these two products only; it does not include every Aspose.Total component.

Total is a serving composition, not another extractor or corpus. Ingest each product separately, then query both through `/total/cpp/mcp/v1/streamable-http`. Omitting `product_id` searches the member products independently; selecting `aspose.words` or `aspose.tex` narrows the request. Results remain product-scoped and C++-only.

[Setup](docs/setup.md) · [Ingestion](docs/ingestion.md) · [Clients](docs/clients.md) · [Maintenance](docs/public-release.md)

## Project family

| Repository | Responsibility |
| --- | --- |
| [context-engine](https://github.com/aspose-core-mcp/context-engine) | Shared ingestion, indexing, retrieval, and MCP infrastructure |
| [Words/C++ plugin](https://github.com/aspose-words-mcp/cpp-plugin) | Words extraction and retrieval profile |
| [TeX/C++ plugin](https://github.com/aspose-tex-mcp/cpp-plugin) | TeX extraction and C++ retrieval configuration |
| [Total/C++ server](https://github.com/aspose-total-mcp/cpp-server) **(this repository)** | Pinned engine, both plugins, and Total composition |

## Get started

Requires Git and Python 3.12 or newer:

```sh
git clone https://github.com/aspose-total-mcp/cpp-server.git
cd cpp-server
sh scripts/setup.sh
```

Setup initializes only the immediate engine/plugin submodules, installs engine dependencies, creates separate plugin interpreters, and verifies registration, extraction, and MCP routing. Do not clone recursively: legacy engine source submodules are not needed. Setup does not provision stores, download corpora, or publish indexes.

Configure runtime services, credentials, and embeddings using [setup](docs/setup.md), then launch:

```sh
sh scripts/run-engine.sh -m uvicorn adcs.api.main:app --host 127.0.0.1 --port 18082
# Separate terminal for queued ingestion:
sh scripts/run-engine.sh -m celery -A adcs.worker.celery_app:celery_app worker --loglevel=info
```

## Validate, then publish

After [downloading sources and preparing Gist caches](docs/ingestion.md), validate each C++ product:

```sh
sh scripts/ingest.sh words --source-kind both
sh scripts/ingest.sh tex --source-kind both
```

These commands validate only. After successful validation, follow the [publication commands](docs/ingestion.md#validate-then-publish) to ingest into the configured stores.

Connect a client to your deployment:

```text
https://YOUR_MCP_HOST/total/cpp/mcp/v1/streamable-http
```

Words and TeX endpoints remain available on the same process. Other inherited compatibility routes remain defined; restrict exposed paths at ingress if needed. No hosted endpoint is provided.

## Registration and workspaces

`config/product-platform-plugins.json` registers both public plugins and `config/total-cpp.json` selects exactly those two members. The shared engine's default catalog stays unchanged. The launch wrapper sets both catalog environment variables.

Each plugin retains its published manifest. Both use the engine workspace with four distinct source folders; registration rejects overlapping source paths. Each plugin owns its Gist cache. Both publish to shared stores with separate product/language metadata. Never ingest `aspose.total.cpp` as a third product.

Windows users can use `scripts/setup.ps1`, `scripts/run-engine.ps1` and the ingestion PowerShell wrappers. Use the `words` or `tex` selector with either ingestion wrapper; see [ingestion](docs/ingestion.md). The optional [complete Words C++ example workflow](docs/ingestion.md#complete-words-examples) is retained.

## Validation and maintenance

GitHub CI checks shell syntax, catalogs, both plugin suites, extraction contracts, endpoint identities, Total fan-out, product selection, and rejection of unsupported scopes. These checks use fixtures and mocked retrieval; verify actual indexed citations after deployment.

Gitlinks pin reviewed public component commits. Upstream releases do not update this deployment automatically. See [maintenance](docs/public-release.md).

## License

[MIT](LICENSE), copyright (c) 2001-2026 Aspose Pty Ltd. Preserve the licenses and notices of the pinned engine and plugins when distributing them.

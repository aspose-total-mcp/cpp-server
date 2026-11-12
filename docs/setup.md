# Setup and runtime configuration

Run `sh scripts/setup.sh` from the repository root. Set `PYTHON=/path/to/python3.12` to choose an interpreter. It initializes `engine`, `plugins/words-cpp`, and `plugins/tex-cpp` without nested source submodules. The engine uses `.venv`; each standard-library plugin has its own `.venv`.

## Registration

Both plugins are already registered in the deployment catalog. `total-cpp.json` defines a C++ composition with Words and TeX and `owns_sources: false`. No shared context-engine repository change or extra registration is required.

Both C++ manifests supply retrieval profiles; TeX has no Words-specific ranking rules. `scripts/run-engine.sh` sets `ADCS_PRODUCT_PLUGIN_CATALOG` and `ADCS_RETRIEVAL_PLUGIN_CATALOG` to the deployment catalog and runs commands from `engine/`.

## Runtime stores

Follow the pinned engine's deployment guidance for PostgreSQL, Valkey, RabbitMQ, Qdrant, OpenSearch, authentication, and embeddings. Review `engine/.env.example` and create `engine/.env.local` with your settings. Use matching stores and embedding settings for API and ingestion workers. API symbol publication requires the structured symbol store to be enabled.

The engine's `make infra-up` provides development backing services. Review its environment and ports first. These host-Python helpers do not provision production infrastructure or include a product-specific Compose/Helm composition.

## Ingestion workspace

Both plugins use `engine/` as their workspace. Words uses `sources/documentation-current` and `sources/api-reference`; TeX uses `sources/tex-documentation` and `sources/tex-api-reference`. Registration checks all four resolved paths for overlap and confinement. Unlike the .NET manifests, these C++ paths do not collide, so separate workspaces are not required. Gist caches remain under each plugin's `sources/` directory.

Queued workers must see the same absolute plugin, source, cache, catalog and interpreter paths. Keep revisions stable while jobs are pending. Container deployments must mount those paths explicitly.

On Windows run `scripts/setup.ps1` (optionally `-Python 'C:/path/to/python.exe'`) and use the PowerShell wrappers. The C++ local Compose file maps PostgreSQL to port 15432; align the engine settings with the selected backing services.

## Expose the API

Use TLS, authentication, and suitable ingress configuration for external clients. Preserve MCP headers and streaming behavior. The README launch binds to loopback. Check `/healthz`, authenticated MCP initialization, and real product-specific retrieval after publication; health and fixture checks alone do not prove a corpus is live.

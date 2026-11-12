"""Validate the deployment and exercise the actual registered worker with a fixture."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine/src"))
from adcs.plugins.catalog import PluginCatalog
from adcs.retrieval.profiles import load_profiles

path = ROOT / "config/product-platform-plugins.json"
catalog = PluginCatalog(path)
assert set(catalog.plugins) == {"aspose.words.cpp", "aspose.tex.cpp"}
assert catalog.compositions["aspose.total.cpp"].members == ["aspose.words.cpp", "aspose.tex.cpp"]
source_paths = [source.path for plugin in catalog.plugins.values() for source in plugin.sources.values()]
assert len(source_paths) == len(set(source_paths)), "Product source checkouts must not overlap"
for plugin_id, plugin_dir in [("aspose.words.cpp", "words-cpp"), ("aspose.tex.cpp", "tex-cpp")]:
    manifest = catalog.extractor(plugin_id)
    profiles = load_profiles(str(path))
    assert set(profiles) == {("aspose.words", "cpp"), ("aspose.tex", "cpp")}
    source = manifest.sources["docs"]
    relative = source.prefix + "/_index.md"
    request = {
        "contract": manifest.contract, "plugin_id": manifest.plugin_id,
        "product_id": manifest.product_id, "language": manifest.language,
        "operation": "extract", "source_kind": "docs", "repo_id": source.repo_id,
        "product_family": "aspose", "source_path": source.path + "/" + relative,
        "relative_repo_path": relative, "source_prefix": source.prefix,
        "layout_detection": source.layout, "source_revision": "deployment-fixture",
        "canonical_base_url": source.canonical_base_url,
        "raw_markdown": (ROOT / "plugins" / plugin_dir / "tests/fixtures/docs.md").read_text(encoding="utf-8"),
    }
    plugin_python = ROOT / "plugins" / plugin_dir / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    interpreter = str(plugin_python) if plugin_python.is_file() else sys.executable
    result = subprocess.run(catalog.command(manifest.plugin_id, python=interpreter),
                            input=json.dumps(request), text=True, encoding="utf-8", capture_output=True, check=True)
    payload = json.loads(result.stdout)
    assert payload["plugin_id"] == manifest.plugin_id
    assert payload["result"]["chunk_records"]
    print(f"{plugin_id}: registration, retrieval profile and worker extraction verified")

route_check = """
from fastapi import FastAPI
from fastapi.testclient import TestClient
from adcs.api.mcp_gateway import router
from adcs.mcp.product_scope import TOTAL_CPP_SCOPE
assert [(s.product_id, s.language) for s in TOTAL_CPP_SCOPE.members] == [
    ('aspose.words', 'cpp'), ('aspose.tex', 'cpp')]
app = FastAPI()
app.include_router(router)
from adcs.mcp.tool_gateway import MCPToolGateway
from unittest.mock import Mock
app.state.mcp_tool_gateway = MCPToolGateway(
    public_query_service=Mock(), supported_revisions=("2025-11-25",),
    primary_revision="2025-11-25")
client = TestClient(app)
for product in ('words', 'tex', 'total'):
    response = client.post(f'/{product}/cpp/mcp/v1/streamable-http', json={
        'jsonrpc':'2.0', 'id':1, 'method':'initialize', 'params':{}})
    assert response.status_code == 200, response.text
    assert response.json()['result']['serverInfo']['name'] == f'aspose-{product}-cpp-mcp'
print('Words, TeX and Total C++ MCP identities verified with deployment catalog')
"""
subprocess.run([sys.executable, "-c", route_check], check=True, cwd=ROOT / "engine",
               env={**os.environ, "PYTHONPATH": str(ROOT / "engine/src"),
                    "ADCS_PRODUCT_PLUGIN_CATALOG": str(path),
                    "ADCS_RETRIEVAL_PLUGIN_CATALOG": str(path),
                    "ADCS_ENV": "dev", "ADCS_API_KEY": "replace-me"})

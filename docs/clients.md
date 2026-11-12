# Connect an MCP client

Use your deployed endpoint. For the README's local launch:

| Scope | URL |
| --- | --- |
| Total (Words + TeX) | `http://127.0.0.1:18082/total/cpp/mcp/v1/streamable-http` |
| Words | `http://127.0.0.1:18082/words/cpp/mcp/v1/streamable-http` |
| TeX | `http://127.0.0.1:18082/tex/cpp/mcp/v1/streamable-http` |

All three are served by one engine process. Total initializes as `aspose-total-cpp-mcp`. Its tools allow Words and TeX C++ only. Omit `product_id` to query both members; pass `aspose.words` or `aspose.tex` to select one. `aspose.total` is the endpoint identity, not an ingestible product or a valid member filter. Results are returned by product rather than treating the corpora as one product.

## VS Code Copilot

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "total-cpp": {
      "type": "http",
      "url": "https://YOUR_MCP_HOST/total/cpp/mcp/v1/streamable-http"
    }
  }
}
```

Replace the host and configure authentication using your client's supported credential mechanism. Start the entry via **MCP: List Servers** and enable its tools in Agent mode. No custom Total agent is bundled; adding an MCP server does not create an agent-picker entry.

After ingestion, ask product-specific questions and inspect tool calls and citations. Initialization and tool discovery confirm protocol connectivity, not published corpus quality. Other MCP clients may use a `mcpServers` configuration object; consult their HTTP transport documentation.

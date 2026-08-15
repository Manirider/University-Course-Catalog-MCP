# MCP Protocol Overview

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that enables AI applications to securely connect to external data sources and tools. It provides a standardized way for AI assistants to discover and invoke capabilities.

## Key Concepts

### Tools
Functions that AI can invoke to perform actions or retrieve data.

```typescript
// Example: Search for courses
await mcp.callTool("search_courses", {
  query: "machine learning",
  department_code: "AIML"
});
```

### Resources
Read-only data sources that AI can access.

```typescript
// Example: Read all course descriptions
await mcp.readResource("resource://course_descriptions");
```

### Prompts
Reusable prompt templates for common tasks.

```typescript
// Example: Compare two courses
await mcp.getPrompt("course_comparison_template", {
  course_code_1: "CS101",
  course_code_2: "CS102"
});
```

## Transport

This server uses **Streamable HTTP** transport:

```
GET /mcp
```

Compatible with:
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- Claude Desktop
- Custom MCP clients

## Capability Discovery

### List Tools

```typescript
const tools = await mcp.listTools();
// Returns: search_courses, get_prerequisites, lookup_instructor, get_prerequisite_graph
```

### List Resources

```typescript
const resources = await mcp.listResources();
// Returns: resource://course_descriptions, resource://department_directory
```

### List Prompts

```typescript
const prompts = await mcp.listPrompts();
// Returns: course_comparison_template, course_advisor
```

## Error Handling

All tools return structured responses:

```typescript
// Success
{
  "course_code": "CS301",
  "prerequisites": [
    {"course_code": "CS102", "title": "Data Structures"}
  ]
}

// Error
{
  "error": "Course not found"
}
```

## Schema Validation

All inputs/outputs validated via Pydantic schemas:

- Input validation on tool invocation
- Output serialization
- Automatic error responses for invalid input

## Version Compatibility

| MCP SDK | Protocol Version |
|---------|------------------|
| 1.6+ | 2024-11-05 |

## Client Examples

### Python (Official SDK)

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8080/mcp") as (read, write):
    async with ClientSession(read, write) as session:
        tools = await session.list_tools()
        result = await session.call_tool("search_courses", {"query": "programming"})
```

### JavaScript/TypeScript

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const transport = new StreamableHTTPClientTransport(
  new URL("http://localhost:8080/mcp")
);
const client = new Client({ name: "my-client", version: "1.0.0" });
await client.connect(transport);

const tools = await client.listTools();
const result = await client.callTool({ name: "search_courses", arguments: { query: "programming" }});
```

### cURL (Raw HTTP)

```bash
# Initialize
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# List tools
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
```

## Best Practices

1. **Always discover capabilities first** — Use `listTools`, `listResources`, `listPrompts`
2. **Handle errors gracefully** — Check for `error` field in responses
3. **Use typed schemas** — Validate inputs before sending
4. **Cache capabilities** — Discovery doesn't change at runtime
5. **Respect rate limits** — Implement backoff if needed

## Debugging

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8080/mcp
```

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG python -m uvicorn university_catalog.main:app
```

### Inspect Raw Traffic

Use browser DevTools or `tcpdump` to inspect HTTP traffic to `/mcp`
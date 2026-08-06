"""StreamXpress MCP Server — MCP v2 server with tool registrations."""

import json
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolRequestParams

from .client import StreamXpressClient

# ── Global client singleton ──

_client: StreamXpressClient | None = None


def get_client() -> StreamXpressClient:
    global _client
    if _client is None:
        _client = StreamXpressClient()
    return _client


# ── Tool logic (testable without MCP) ──

def streamxpress_connect(host: str, port: int) -> dict:
    client = get_client()
    try:
        client.disconnect()
    except Exception:
        pass
    client.connect(host, port)
    return {"status": "connected", "host": host, "port": port}


def streamxpress_disconnect() -> dict:
    client = get_client()
    client.disconnect()
    return {"status": "disconnected"}


# ── Tool registry ──

TOOLS = [
    Tool(name="streamxpress_connect", description="Connect to StreamXpress RC session.",
         inputSchema={"type": "object", "properties": {
             "host": {"type": "string"}, "port": {"type": "integer"}},
             "required": ["host", "port"]}),
    Tool(name="streamxpress_disconnect", description="Disconnect from RC session.",
         inputSchema={"type": "object", "properties": {}}),
]

_DISPATCH = {
    "streamxpress_connect": streamxpress_connect,
    "streamxpress_disconnect": streamxpress_disconnect,
}


async def _list_tools_handler(ctx, params):
    return TOOLS


async def _call_tool_handler(ctx, params: CallToolRequestParams):
    handler = _DISPATCH.get(params.name)
    if handler is None:
        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool: {params.name}"}))]
    try:
        args = params.arguments or {}
        result = handler(**args)
        return [TextContent(type="text", text=json.dumps(result))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# ── MCP server instance ──

mcp = Server(
    "streamxpress-mcp",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, NotificationOptions())

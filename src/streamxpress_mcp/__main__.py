"""Entry point: python -m streamxpress_mcp

Starts the StreamXpress MCP server on stdio transport.
Configure in your MCP client as:

{
  "mcpServers": {
    "streamxpress": {"command": "python", "args": ["-m", "streamxpress_mcp"]}
  }
}
"""

import asyncio
from .server import run_server


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

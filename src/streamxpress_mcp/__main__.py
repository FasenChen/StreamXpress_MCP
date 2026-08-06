"""Entry point: python -m streamxpress_mcp

Starts the StreamXpress MCP server on stdio transport.
Configure in your MCP client (e.g. Claude Desktop) as:

{
  "mcpServers": {
    "streamxpress": {
      "command": "python",
      "args": ["-m", "streamxpress_mcp"]
    }
  }
}
"""

from .server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()

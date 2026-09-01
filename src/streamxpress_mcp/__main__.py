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

import argparse
from importlib.metadata import PackageNotFoundError, version

from .server import mcp


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="streamxpress-mcp")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_distribution_version()}",
    )
    parser.parse_args(argv)
    mcp.run()


def _distribution_version() -> str:
    try:
        return version("streamxpress-mcp")
    except PackageNotFoundError:
        return "uninstalled-source"


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()

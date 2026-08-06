# StreamXpress MCP Server

MCP (Model Context Protocol) server for [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/), allowing AI agents to control TS (Transport Stream) playout via the SpRcApi remote-control interface.

## Prerequisites

- **StreamXpress** v3.x with **DTC-302-RC license** (remote control)
- DekTec output adapter with **DTC-300-SP** (playback) or **DTC-300-NICP** (IP via local NIC)
- Python 3.10+

## Quick Start

```powershell
# 1. Clone and install
git clone <repo-url>
cd StreamXpress_MCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 2. Start StreamXpress in remote-control mode
StreamXpress.exe -rc 5000

# 3. Run the MCP server
python -m streamxpress_mcp
```

## MCP Client Configuration

Add to Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "streamxpress": {
      "command": "python",
      "args": ["-m", "streamxpress_mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|---|---|
| `streamxpress_connect` | Connect to StreamXpress RC session |
| `streamxpress_disconnect` | Disconnect from session |
| `streamxpress_scan_ports` | List available output ports |
| `streamxpress_select_port` | Select an output port |
| `streamxpress_open_file` | Load a TS file |
| `streamxpress_start` | Start playout |
| `streamxpress_stop` | Stop playout |
| `streamxpress_get_status` | Get playout progress |
| `streamxpress_set_rate` | Set TS bitrate (bps) |
| `streamxpress_set_tsoip_params` | Configure UDP/RTP TS-over-IP |
| `streamxpress_set_rf_params` | Set RF frequency/level |
| `streamxpress_set_asi_params` | Set ASI remux/packet mode |

## Example

```
User: Push news.ts to multicast 239.1.1.1:1234 at 25 Mbps

AI uses:
  1. streamxpress_connect(host="http://localhost", port=5000)
  2. streamxpress_scan_ports()
  3. streamxpress_select_port(serial=..., port_num=1)
  4. streamxpress_set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234)
  5. streamxpress_set_rate(rate_bps=25_000_000)
  6. streamxpress_open_file(filepath="C:\\Streams\\news.ts")
  7. streamxpress_start()
  8. streamxpress_get_status()
```

## License

This project wraps DekTec SpRcApi. Valid DekTec licenses (DTC-300-SP + DTC-302-RC) required.

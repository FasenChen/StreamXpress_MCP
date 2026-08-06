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
    c = get_client()
    try:
        c.disconnect()
    except Exception:
        pass
    c.connect(host, port)
    return {"status": "connected", "host": host, "port": port}


def streamxpress_disconnect() -> dict:
    get_client().disconnect()
    return {"status": "disconnected"}


# ── Port discovery ──

OUTPUT_TYPE_LABELS = {
    0x00001: "ASI", 0x00002: "ATSC", 0x00004: "CMMB", 0x00008: "DTMB",
    0x00010: "DVB-S", 0x00020: "DVB-S2", 0x00040: "DVB-T", 0x00080: "DVB-T2",
    0x00100: "DVB-T2MI", 0x00200: "IQ", 0x00400: "ISDB-S", 0x00800: "ISDB-T",
    0x01000: "QAM-A", 0x02000: "QAM-B", 0x04000: "QAM-C", 0x08000: "SD-SDI",
    0x10000: "SPI", 0x20000: "TS-over-IP", 0x40000: "ISDB-S3",
    0x80000: "DRM", 0x100000: "ATSC3-STLTP",
}


def _describe_output_type(flags: int) -> list[str]:
    return [name for mask, name in OUTPUT_TYPE_LABELS.items() if flags & mask]


def streamxpress_scan_ports() -> list[dict]:
    ports = get_client().scan_ports()
    return [{"serial": p.Serial, "type_number": p.TypeNumber, "port": p.Port,
             "output_types": _describe_output_type(p.OutputType), "in_use": p.InUse != 0}
            for p in ports]


def streamxpress_select_port(serial: int, port_num: int, modulation: int = 0) -> dict:
    get_client().select_port(serial, port_num, modulation)
    return {"status": "ok", "serial": serial, "port": port_num}


def streamxpress_open_file(filepath: str) -> dict:
    get_client().open_file(filepath)
    return {"status": "ok", "file": filepath}


# ── Playback control ──

def streamxpress_start() -> dict:
    get_client().start()
    return {"status": "playing"}


def streamxpress_stop() -> dict:
    get_client().stop()
    return {"status": "stopped"}


def streamxpress_get_status() -> dict:
    return get_client().get_status()


# ── Parameters ──

def streamxpress_set_rate(rate_bps: int) -> dict:
    get_client().set_rate(rate_bps)
    return {"status": "ok", "rate_bps": rate_bps}


def streamxpress_set_tsoip_params(
    dest_ip: str, dest_port: int, num_tp_per_ip: int = 7,
    protocol: str = "UDP", ttl: int = 64, fec_rows: int = 0, fec_cols: int = 0,
) -> dict:
    get_client().set_tsoip_params(dest_ip=dest_ip, dest_port=dest_port,
                                  num_tp_per_ip=num_tp_per_ip, protocol=protocol,
                                  ttl=ttl, fec_rows=fec_rows, fec_cols=fec_cols)
    return {"status": "ok", "dest_ip": dest_ip, "dest_port": dest_port, "protocol": protocol}


def streamxpress_set_rf_params(frequency_hz: int, level_dbm: float) -> dict:
    get_client().set_rf_params(frequency_hz, level_dbm)
    return {"status": "ok", "frequency_hz": frequency_hz, "level_dbm": level_dbm}


def streamxpress_set_asi_params(remux: bool = True, playout_rate: int = 0, tx_mode: int = 0) -> dict:
    get_client().set_asi_params(remux=remux, playout_rate=playout_rate, tx_mode=tx_mode)
    return {"status": "ok"}


# ── Tool registry ──

TOOLS = [
    Tool(name="streamxpress_connect", description="Connect to StreamXpress RC session.",
         inputSchema={"type": "object", "properties": {"host": {"type": "string"}, "port": {"type": "integer"}}, "required": ["host", "port"]}),
    Tool(name="streamxpress_disconnect", description="Disconnect from RC session.",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="streamxpress_scan_ports", description="Scan for available output ports.",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="streamxpress_select_port", description="Select a physical port for playout.",
         inputSchema={"type": "object", "properties": {"serial": {"type": "integer"}, "port_num": {"type": "integer"}, "modulation": {"type": "integer", "default": 0}}, "required": ["serial", "port_num"]}),
    Tool(name="streamxpress_open_file", description="Open a TS file for playout.",
         inputSchema={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}),
    Tool(name="streamxpress_start", description="Start TS playout.",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="streamxpress_stop", description="Stop TS playout.",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="streamxpress_get_status", description="Get current playout status.",
         inputSchema={"type": "object", "properties": {}}),
    Tool(name="streamxpress_set_rate", description="Set TS playout bitrate (bps).",
         inputSchema={"type": "object", "properties": {"rate_bps": {"type": "integer"}}, "required": ["rate_bps"]}),
    Tool(name="streamxpress_set_tsoip_params", description="Configure TS-over-IP (UDP/RTP) output.",
         inputSchema={"type": "object", "properties": {"dest_ip": {"type": "string"}, "dest_port": {"type": "integer"}, "num_tp_per_ip": {"type": "integer", "default": 7}, "protocol": {"type": "string", "default": "UDP"}, "ttl": {"type": "integer", "default": 64}, "fec_rows": {"type": "integer", "default": 0}, "fec_cols": {"type": "integer", "default": 0}}, "required": ["dest_ip", "dest_port"]}),
    Tool(name="streamxpress_set_rf_params", description="Set RF frequency and level.",
         inputSchema={"type": "object", "properties": {"frequency_hz": {"type": "integer"}, "level_dbm": {"type": "number"}}, "required": ["frequency_hz", "level_dbm"]}),
    Tool(name="streamxpress_set_asi_params", description="Set ASI output parameters.",
         inputSchema={"type": "object", "properties": {"remux": {"type": "boolean", "default": True}, "playout_rate": {"type": "integer", "default": 0}, "tx_mode": {"type": "integer", "default": 0}}}),
]

_DISPATCH = {
    "streamxpress_connect": streamxpress_connect,
    "streamxpress_disconnect": streamxpress_disconnect,
    "streamxpress_scan_ports": streamxpress_scan_ports,
    "streamxpress_select_port": streamxpress_select_port,
    "streamxpress_open_file": streamxpress_open_file,
    "streamxpress_start": streamxpress_start,
    "streamxpress_stop": streamxpress_stop,
    "streamxpress_get_status": streamxpress_get_status,
    "streamxpress_set_rate": streamxpress_set_rate,
    "streamxpress_set_tsoip_params": streamxpress_set_tsoip_params,
    "streamxpress_set_rf_params": streamxpress_set_rf_params,
    "streamxpress_set_asi_params": streamxpress_set_asi_params,
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


mcp = Server("streamxpress-mcp", on_list_tools=_list_tools_handler, on_call_tool=_call_tool_handler)


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, NotificationOptions())

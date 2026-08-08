"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

from fastmcp import FastMCP

from .client import StreamXpressClient
from .config import load_config, resolve_wsdl_path
from .launcher import launch_streamxpress
from .sprc_import import SPRC_client

# ── FastMCP application ──

mcp = FastMCP("streamxpress-mcp")

# ── Global client singleton ──

_client: StreamXpressClient | None = None


def get_client() -> StreamXpressClient:
    """Return the global singleton client, creating it if needed."""
    global _client
    if _client is None:
        cfg = load_config()
        wsdl = resolve_wsdl_path(cfg)
        if wsdl is not None:
            _client = StreamXpressClient(
                sprc_factory=lambda: SPRC_client(wsdl_template=wsdl)
            )
        else:
            _client = StreamXpressClient()
    return _client


# ── Connection tools ──

@mcp.tool()
def connect(host: str, port: int) -> dict:
    """Connect to a StreamXpress instance running in remote-control mode.

    The StreamXpress must be started with: StreamXpress.exe -rc <port>

    Args:
        host: HTTP URL of the StreamXpress host, e.g. "http://localhost"
        port: TCP port the -rc listener is bound to, e.g. 5000
    """
    client = get_client()
    try:
        client.disconnect()
    except Exception:
        pass
    client.connect(host, port)
    return {"status": "connected", "host": host, "port": port}


@mcp.tool()
def disconnect() -> dict:
    """Disconnect from the StreamXpress remote-control session."""
    client = get_client()
    client.disconnect()
    return {"status": "disconnected"}


@mcp.tool()
def get_remote_version() -> dict:
    """Get the SpRcApi version running on the connected StreamXpress server."""
    return get_client().get_remote_version()


@mcp.tool()
def get_remote_dtapi_version() -> dict:
    """Get the DTAPI version StreamXpress was built with (server side)."""
    return get_client().get_remote_dtapi_version()


@mcp.tool()
def get_app_info() -> dict:
    """Get application name and version of the connected StreamXpress."""
    return get_client().get_app_info()


@mcp.tool()
def show_window(show: bool) -> dict:
    """Show or hide the StreamXpress application window on the server.

    Args:
        show: True to show the window, False to hide it.
    """
    client = get_client()
    client.show_window(show)
    return {"status": "ok", "show": show}


@mcp.tool()
def clear_errors() -> dict:
    """Clear the playout error counters (e.g. underflows) on the server."""
    client = get_client()
    client.clear_errors()
    return {"status": "ok"}


# ── Port discovery tools ──

OUTPUT_TYPE_LABELS = {
    0x00001: "ASI", 0x00002: "ATSC", 0x00004: "CMMB",
    0x00008: "DTMB", 0x00010: "DVB-S", 0x00020: "DVB-S2",
    0x00040: "DVB-T", 0x00080: "DVB-T2", 0x00100: "DVB-T2MI",
    0x00200: "IQ", 0x00400: "ISDB-S", 0x00800: "ISDB-T",
    0x01000: "QAM-A", 0x02000: "QAM-B", 0x04000: "QAM-C",
    0x08000: "SD-SDI", 0x10000: "SPI", 0x20000: "TS-over-IP",
    0x40000: "ISDB-S3", 0x80000: "DRM", 0x100000: "ATSC3-STLTP",
}


def _describe_output_type(flags: int) -> list[str]:
    """Convert OutputType bitmask to human-readable labels."""
    labels = []
    for mask, name in OUTPUT_TYPE_LABELS.items():
        if flags & mask:
            labels.append(name)
    return labels


@mcp.tool()
def scan_ports() -> list[dict]:
    """Scan for available output ports on the connected StreamXpress.

    Returns a list of port descriptors with serial, type, and output capabilities.
    """
    client = get_client()
    ports = client.scan_ports()
    return [
        {
            "serial": p.Serial,
            "type_number": p.TypeNumber,
            "port": p.Port,
            "output_types": _describe_output_type(p.OutputType),
            "in_use": p.InUse != 0,
        }
        for p in ports
    ]


@mcp.tool()
def select_port(serial: int, port_num: int, modulation: int = 0) -> dict:
    """Select a physical output port for playout.

    Args:
        serial: Device serial number (from scan_ports)
        port_num: Physical port number on the device
        modulation: Initial modulation standard (0=none, use SPRC.MOD_* constants)
    """
    client = get_client()
    client.select_port(serial, port_num, modulation)
    return {"status": "ok", "serial": serial, "port": port_num}


@mcp.tool()
def open_file(filepath: str) -> dict:
    """Open a TS file for playout.

    Args:
        filepath: Full path to the .ts file or StreamXpress .xml settings file
    """
    client = get_client()
    client.open_file(filepath)
    return {"status": "ok", "file": filepath}


# ── Playback control tools ──

@mcp.tool()
def start() -> dict:
    """Start TS playout on the selected port."""
    client = get_client()
    client.start()
    return {"status": "playing"}


@mcp.tool()
def stop() -> dict:
    """Stop TS playout."""
    client = get_client()
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
def get_status() -> dict:
    """Get current playout status including position, wraps, filename, and bitrate."""
    client = get_client()
    return client.get_status()


# ── Parameter tools ──

@mcp.tool()
def set_rate(rate_bps: int) -> dict:
    """Set the TS playout bitrate in bits per second (188-byte packets).

    Args:
        rate_bps: Target bitrate, e.g. 25_000_000 for 25 Mbps
    """
    client = get_client()
    client.set_rate(rate_bps)
    return {"status": "ok", "rate_bps": rate_bps}


@mcp.tool()
def set_tsoip_params(
    dest_ip: str,
    dest_port: int,
    num_tp_per_ip: int = 7,
    protocol: str = "UDP",
    ttl: int = 64,
    fec_rows: int = 0,
    fec_cols: int = 0,
) -> dict:
    """Configure TS-over-IP output parameters (UDP/RTP).

    Args:
        dest_ip: Destination IP address, e.g. "239.1.1.1" (multicast) or "192.168.1.100" (unicast)
        dest_port: Destination UDP port, e.g. 1234
        num_tp_per_ip: Number of TS packets per IP packet (1-7)
        protocol: "UDP" or "RTP"
        ttl: Time-To-Live for multicast
        fec_rows: FEC matrix rows (D), 0 disables FEC
        fec_cols: FEC matrix columns (L), 0 disables FEC
    """
    client = get_client()
    client.set_tsoip_params(
        dest_ip=dest_ip,
        dest_port=dest_port,
        num_tp_per_ip=num_tp_per_ip,
        protocol=protocol,
        ttl=ttl,
        fec_rows=fec_rows,
        fec_cols=fec_cols,
    )
    return {
        "status": "ok",
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "protocol": protocol,
    }


@mcp.tool()
def set_rf_params(frequency_hz: int, level_dbm: float) -> dict:
    """Set RF output frequency and level (modulator ports only).

    Args:
        frequency_hz: Center frequency in Hz, e.g. 500_000_000 for 500 MHz
        level_dbm: Output level in dBm, e.g. -37.5
    """
    client = get_client()
    client.set_rf_params(frequency_hz, level_dbm)
    return {"status": "ok", "frequency_hz": frequency_hz, "level_dbm": level_dbm}


@mcp.tool()
def set_asi_params(
    remux: bool = True,
    playout_rate: int = 0,
    tx_mode: int = 0,
) -> dict:
    """Set ASI output parameters.

    Args:
        remux: Enable real-time remultiplexing (add null packets to match output rate)
        playout_rate: Output rate in bps (0 = use file native rate)
        tx_mode: 0=188-byte packets, 2=204-byte (Add16), 3=188-from-204 (Min16)
    """
    client = get_client()
    client.set_asi_params(remux=remux, playout_rate=playout_rate, tx_mode=tx_mode)
    return {"status": "ok"}


# ── Launch tool ──

@mcp.tool()
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    at the repository root, starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with connect.
    """
    return launch_streamxpress(load_config())

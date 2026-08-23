"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

import threading

from fastmcp import FastMCP

from .client import StreamXpressClient
from .config import load_config, resolve_wsdl_path
from .launcher import launch_streamxpress
from .sprc_import import SPRC_client

# ── FastMCP application ──

mcp = FastMCP("streamxpress-mcp")

# ── Global client singleton ──

_client: StreamXpressClient | None = None
_client_lock = threading.Lock()


def get_client() -> StreamXpressClient:
    """Return the global singleton client, creating it if needed."""
    global _client
    if _client is None:
        with _client_lock:
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


def _ensure_local_session(client: StreamXpressClient) -> None:
    """Connect to localhost StreamXpress, launching it first if needed."""
    if client.connected:
        return
    cfg = load_config()
    host = "http://localhost"
    try:
        client.connect(host, cfg.rc_port)
        return
    except Exception:
        launch_result = launch_streamxpress(cfg)
        try:
            client.connect(host, cfg.rc_port)
        except Exception as second:
            launch_note = ""
            if not launch_result.get("ok"):
                launch_note = f"; launch: {launch_result.get('error')}"
            raise RuntimeError(
                f"failed to connect to StreamXpress at {host}:{cfg.rc_port}: "
                f"{second}{launch_note}"
            ) from second


@mcp.tool()
def connect(host: str = "http://localhost", port: int | None = None) -> dict:
    """Connect to a StreamXpress instance running in remote-control mode.

    The StreamXpress must be started with: StreamXpress.exe -rc <port>
    Defaults are this machine (`http://localhost`) and `rc_port` from config.json.

    Args:
        host: HTTP URL of the StreamXpress host, e.g. "http://localhost"
        port: TCP port the -rc listener is bound to. None uses config.json rc_port.
    """
    cfg = load_config()
    resolved_port = cfg.rc_port if port is None else int(port)
    client = get_client()
    try:
        client.disconnect()
    except Exception:
        pass
    client.connect(host, resolved_port)
    return {"status": "connected", "host": host, "port": resolved_port}


@mcp.tool()
def disconnect() -> dict:
    """Disconnect from the StreamXpress remote-control session."""
    client = get_client()
    try:
        client.disconnect()
        return {"status": "disconnected"}
    except RuntimeError as e:
        # Session cleanup failed (e.g. network drop) — local state is reset
        # regardless, so report the warning without turning it into a failure.
        return {"status": "disconnected", "warning": str(e)}


@mcp.tool()
def play(settings_xml: str, stream: str, loop: bool = True) -> dict:
    """Play a stream using a StreamXpress settings XML preset.

    Loads the XML first (modulation / RF / loop flags), then the stream file,
    then starts playout. One XML can be reused by a group of streams.
    Auto-connects to localhost StreamXpress and selects the DTU-315 (or the
    unique idle port) before opening files.

    Args:
        settings_xml: Full path to a StreamXpress Save Settings .xml file.
            Root element must be StreamXpressSettings. Keep Filename empty
            in the XML so OpenFile(xml) does not look up a stale TS path.
        stream: Full path to the transport-stream file (.ts / .trp / ...).
        loop: If True (default), play continuously until stop().
    """
    cfg = load_config()
    client = get_client()
    _ensure_local_session(client)
    return client.play(
        settings_xml=settings_xml,
        stream=stream,
        loop=loop,
        preferred_serial=cfg.preferred_serial,
        preferred_type_number=cfg.preferred_type_number,
    )


@mcp.tool()
def stop() -> dict:
    """Stop playout."""
    client = get_client()
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
def get_status() -> dict:
    """Get current playout position, wrap count, and file info."""
    return get_client().get_status()


@mcp.tool()
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    at the repository root, starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with connect.
    """
    return launch_streamxpress(load_config())

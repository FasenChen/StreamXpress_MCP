"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

import logging
import threading

from fastmcp import FastMCP

from .client import StreamXpressClient
from .config import load_config, resolve_wsdl_path
from .launcher import launch_streamxpress
from .sprc_import import SPRC_client

logger = logging.getLogger(__name__)

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
        logger.debug("本地会话已连接，无需重复连接")
        return
    cfg = load_config()
    host = "http://localhost"
    try:
        client.connect(host, cfg.rc_port)
        logger.info("已连接到本机 StreamXpress: %s:%d", host, cfg.rc_port)
        return
    except Exception:
        logger.info("直接连接失败，尝试启动 StreamXpress")
        launch_result = launch_streamxpress(cfg)
        try:
            client.connect(host, cfg.rc_port)
            logger.info("启动后已连接到本机 StreamXpress: %s:%d", host, cfg.rc_port)
        except Exception as second:
            launch_note = ""
            if not launch_result.get("ok"):
                launch_note = f"；启动失败: {launch_result.get('error')}"
            raise RuntimeError(
                f"连接本机 StreamXpress 失败（{host}:{cfg.rc_port}）"
                f"{launch_note}；原始错误: {second}"
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
    try:
        resolved_port = cfg.rc_port if port is None else int(port)
    except (TypeError, ValueError):
        raise ValueError(f"端口必须是整数，收到: {port!r}")
    client = get_client()
    logger.info("正在连接 %s:%d", host, resolved_port)
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
            Root element must be StreamXpressSettings. The <Filename> element,
            if present, is auto-injected with the stream path by the server
            (StreamXpress' OpenFile fails with E_FILE_CANT_FIND on an empty
            Filename), so any saved snapshot works as-is.
        stream: Full path to the transport-stream file (.ts / .trp / ...).
        loop: If True (default), play continuously until stop().
    """
    client = get_client()
    _ensure_local_session(client)
    return client.play(
        settings_xml=settings_xml,
        stream=stream,
        loop=loop,
    )


@mcp.tool()
def stop() -> dict:
    """Stop playout."""
    client = get_client()
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
def pause() -> dict:
    """Pause playout and preserve the current file position.

    Use resume() to continue from this position. Pause is not equivalent to
    stop(): stop exits hold mode, while pause keeps the player in hold mode.
    """
    client = get_client()
    client.pause()
    return {"status": "paused"}


@mcp.tool()
def resume() -> dict:
    """Resume playout from pause without reloading the stream or preset."""
    client = get_client()
    client.resume()
    return {"status": "playing"}


@mcp.tool()
def get_status() -> dict:
    """Get current playout state, progress, counters, and health summary."""
    return get_client().get_status()


@mcp.tool()
def clear_errors() -> dict:
    """Clear the StreamXpress playout error counter."""
    client = get_client()
    client.clear_errors()
    return {"status": "ok"}


@mcp.tool()
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    at the repository root, starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with connect.
    """
    result = launch_streamxpress(load_config())
    if result.get("ok"):
        logger.info("StreamXpress 启动成功: pid=%s, port=%s", result.get("pid"), result.get("port"))
    else:
        logger.error("StreamXpress 启动失败: %s", result.get("error"))
    return result

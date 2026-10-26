"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

import logging
import threading
from dataclasses import replace
from functools import wraps

from fastmcp import FastMCP

from .client import StreamXpressClient, _require_file, validate_settings_xml
from .config import load_config, resolve_rc_port, resolve_wsdl_path
from .launcher import close_streamxpress, launch_streamxpress
from .sprc_import import SPRC_client

logger = logging.getLogger(__name__)

# ── FastMCP application ──

mcp = FastMCP("streamxpress-mcp")

# ── Global client singleton ──

_client: StreamXpressClient | None = None
_client_lock = threading.Lock()
_tool_lock = threading.RLock()


def _serialized(function):
    @wraps(function)
    def call(*args, **kwargs):
        # Keep each port switch and SOAP operation together across worker threads.
        with _tool_lock:
            return function(*args, **kwargs)
    return call


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


def _get_control_client(rc_port: int | None = None) -> StreamXpressClient:
    """Connect to the existing player without launching or changing playout."""
    client = get_client()
    port = resolve_rc_port(load_config(), rc_port)
    if rc_port is not None and client.connected and client.endpoint != ("http://localhost", port):
        client.disconnect()
    if not client.connected:
        client.connect("http://localhost", port)
    return client


def _ensure_local_session(client: StreamXpressClient, rc_port: int | None = None) -> None:
    """Connect to localhost StreamXpress, launching it first if needed."""
    cfg = load_config()
    cfg = replace(cfg, rc_port=resolve_rc_port(cfg, rc_port))
    if rc_port is not None and client.connected and client.endpoint != ("http://localhost", cfg.rc_port):
        client.disconnect()
    if client.connected:
        logger.debug("本地会话已连接，无需重复连接")
        return
    host = "http://localhost"
    try:
        client.connect(host, cfg.rc_port)
        logger.info("已连接到本机 StreamXpress: %s:%d", host, cfg.rc_port)
        return
    except Exception:
        logger.info("直接连接失败，尝试启动 StreamXpress")
        launch_result = launch_streamxpress(cfg)
        if not launch_result.get("ok"):
            raise RuntimeError(f"启动 StreamXpress 失败: {launch_result.get('error')}")
        try:
            client.connect(host, cfg.rc_port)
            logger.info("启动后已连接到本机 StreamXpress: %s:%d", host, cfg.rc_port)
        except Exception as second:
            raise RuntimeError(
                f"连接本机 StreamXpress 失败（{host}:{cfg.rc_port}）"
                f"；原始错误: {second}"
            ) from second


@mcp.tool()
@_serialized
def connect(host: str = "http://localhost", port: int | None = None) -> dict:
    """Connect to a StreamXpress instance running in remote-control mode.

    The StreamXpress must be started with: StreamXpress.exe -rc <port>
    Defaults are this machine (`http://localhost`) and `rc_port` from config.json.

    Args:
        host: HTTP URL of the StreamXpress host, e.g. "http://localhost"
        port: TCP port the -rc listener is bound to. None uses config.json rc_port.
    """
    cfg = load_config()
    resolved_port = resolve_rc_port(cfg, port)
    client = get_client()
    logger.info("正在连接 %s:%d", host, resolved_port)
    try:
        client.disconnect()
    except Exception:
        pass
    client.connect(host, resolved_port)
    return {"status": "connected", "host": host, "port": resolved_port}


@mcp.tool()
@_serialized
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
@_serialized
def close(rc_port: int | None = None) -> dict:
    """Gracefully close local StreamXpress and verify its processes have exited.

    Targets the configured executable and rc_port (default from config.json),
    including across fresh stdio sessions. Multiple processes with the same
    rc_port are ambiguous and will not be closed. Never connects or launches.
    Stop playout on the same rc_port before calling this tool.
    Returns ok, status (closed or not_running), running=false and process IDs
    only after confirming exit. A blocked window or timeout returns ok=false;
    it never force-kills the player. Do not call play/get_status after closing.
    """
    cfg = load_config()
    cfg = replace(cfg, rc_port=resolve_rc_port(cfg, rc_port))
    client = get_client()
    session_result = {}
    if not client.connected or client.endpoint in (
        ("http://localhost", cfg.rc_port), ("http://127.0.0.1", cfg.rc_port),
    ):
        session_result = disconnect()
    result = close_streamxpress(cfg)
    if "warning" in session_result:
        result["warning"] = session_result["warning"]
    return result


@mcp.tool()
@_serialized
def play(
    settings_xml: str, stream: str, loop: bool = True,
    rc_port: int | None = None, serial: int = 0,
) -> dict:
    """Play a stream using a StreamXpress settings XML preset.

    Loads the XML first (modulation / RF / loop flags), then the stream file,
    then starts playout. One XML can be reused by a group of streams.
    Auto-connects to the local rc_port (default from config.json). Use distinct
    rc_port and serial values for simultaneous instances; repeat rc_port on
    every later control/status call. Validates files before connecting/launching.

    Args:
        settings_xml: Full path to a StreamXpress Save Settings .xml file.
            Root element must be StreamXpressSettings. The <Filename> element,
            if present, is auto-injected with the stream path by the server
            (StreamXpress' OpenFile fails with E_FILE_CANT_FIND on an empty
            Filename), so any saved snapshot works as-is.
        stream: Full path to the transport-stream file (.ts / .trp / ...).
        loop: If True (default), play continuously until stop().
        rc_port: Local instance's RC TCP port; None uses the current session
            or config.json in a fresh stdio process.
        serial: Device serial number; 0 auto-selects a free/current DTU-315.
    """
    settings_xml = validate_settings_xml(settings_xml)
    stream = _require_file(stream, "码流文件")
    if serial < 0:
        raise ValueError("serial 必须为非负设备序列号")
    client = get_client()
    _ensure_local_session(client, rc_port)
    return client.play(
        settings_xml=settings_xml,
        stream=stream,
        loop=loop,
        preferred_serial=serial,
    )


@mcp.tool()
@_serialized
def stop(rc_port: int | None = None) -> dict:
    """Stop playout on rc_port (default config.json); never launches or selects a device."""
    client = _get_control_client(rc_port)
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
@_serialized
def pause(rc_port: int | None = None) -> dict:
    """Pause playout and preserve the current file position.

    Use resume() to continue from this position. Pause is not equivalent to
    stop(): stop exits hold mode, while pause keeps the player in hold mode.
    Auto-connects to the local rc_port (default config.json); never launches.
    """
    client = _get_control_client(rc_port)
    client.pause()
    return {"status": "paused"}


@mcp.tool()
@_serialized
def resume(rc_port: int | None = None) -> dict:
    """Resume playout from pause without reloading the stream or preset.

    Auto-connects to the local rc_port (default config.json); never launches.
    """
    client = _get_control_client(rc_port)
    client.resume()
    return {"status": "playing"}


@mcp.tool()
@_serialized
def get_status(rc_port: int | None = None) -> dict:
    """Get current playout state, progress, counters, and health summary.

    Auto-connects to the local rc_port (default config.json); never launches
    or selects a device. E_NO_PORT means this instance has no selected output.
    """
    return _get_control_client(rc_port).get_status()


@mcp.tool()
@_serialized
def clear_errors(rc_port: int | None = None) -> dict:
    """Clear the StreamXpress playout error counter.

    Auto-connects to the local rc_port (default config.json); never launches.
    """
    client = _get_control_client(rc_port)
    client.clear_errors()
    return {"status": "ok"}


@mcp.tool()
@_serialized
def launch(rc_port: int | None = None) -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path from config.json; rc_port overrides its default.
    Rejects an occupied TCP port before starting. Ready is true only when the
    new process owns the RC listener. Use distinct ports for multiple instances
    and repeat rc_port on every play/control/close call.
    """
    cfg = load_config()
    result = launch_streamxpress(replace(cfg, rc_port=resolve_rc_port(cfg, rc_port)))
    if result.get("ok"):
        logger.info("StreamXpress 启动成功: pid=%s, port=%s", result.get("pid"), result.get("port"))
    else:
        logger.error("StreamXpress 启动失败: %s", result.get("error"))
    return result

"""Launch StreamXpress in remote-control mode from configuration."""

import socket
import subprocess
import time
from pathlib import Path

from .config import StreamXpressConfig


def _port_open(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def launch_streamxpress(cfg: StreamXpressConfig) -> dict:
    """Start `streamxpress_path -rc <rc_port>` and probe the port.

    Returns {"ok": True, "pid", "port", "ready"} on success, or
    {"ok": False, "error"} when not configured / executable missing.
    """
    if not cfg.streamxpress_path:
        return {
            "ok": False,
            "error": "config.json 未配置 streamxpress_path，请先复制 config.example.json 为 config.json 并填写",
        }
    exe = cfg.streamxpress_path
    if not Path(exe).is_file():
        return {"ok": False, "error": f"StreamXpress 可执行文件不存在: {exe}"}

    try:
        proc = subprocess.Popen(
            [exe, "-rc", str(cfg.rc_port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError as exc:
        return {"ok": False, "error": f"启动 StreamXpress 失败: {exc}"}
    ready = False
    for _ in range(10):
        time.sleep(0.5)
        if _port_open(cfg.rc_port):
            ready = True
            break
    return {"ok": True, "pid": proc.pid, "port": cfg.rc_port, "ready": ready}

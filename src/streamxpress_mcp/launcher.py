"""Launch StreamXpress in remote-control mode from configuration."""

import logging
import socket
import subprocess
import time
from pathlib import Path

from .config import StreamXpressConfig

logger = logging.getLogger(__name__)


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
        logger.warning("config.json 未配置 streamxpress_path")
        return {
            "ok": False,
            "error": "config.json 未配置 streamxpress_path，请编辑项目根 config.json 填写 StreamXpress 可执行文件路径",
        }
    exe = cfg.streamxpress_path
    if not Path(exe).is_file():
        logger.error("StreamXpress 可执行文件不存在: %s", exe)
        return {"ok": False, "error": f"StreamXpress 可执行文件不存在: {exe}"}

    logger.info("正在启动 StreamXpress: %s -rc %d", exe, cfg.rc_port)
    try:
        proc = subprocess.Popen(
            [exe, "-rc", str(cfg.rc_port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    except OSError as exc:
        logger.error("启动 StreamXpress 失败: %s", exc)
        return {"ok": False, "error": f"启动 StreamXpress 失败: {exc}"}
    ready = False
    for _ in range(10):
        time.sleep(0.5)
        if _port_open(cfg.rc_port):
            ready = True
            break
    if ready:
        logger.info("StreamXpress 已就绪，pid=%d, port=%d", proc.pid, cfg.rc_port)
    else:
        logger.warning("StreamXpress 启动后端口 %d 未就绪", cfg.rc_port)
    return {"ok": True, "pid": proc.pid, "port": cfg.rc_port, "ready": ready}

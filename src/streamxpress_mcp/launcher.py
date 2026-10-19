"""Launch StreamXpress in remote-control mode from configuration."""

import json
import logging
import socket
import subprocess
import time
from pathlib import Path

from .config import StreamXpressConfig

logger = logging.getLogger(__name__)


def _start_detached_process(command: list[str]) -> int:
    # WMI creates the player outside the MCP client's kill-on-close Job Object.
    script = """
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$startup = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ShowWindow = [uint16]0}
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = [Console]::In.ReadToEnd()
    ProcessStartupInformation = $startup
} | Select-Object ReturnValue, ProcessId | ConvertTo-Json -Compress
"""
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script],
        input=subprocess.list2cmdline(command),
        capture_output=True, text=True, encoding="utf-8", timeout=15,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if completed.returncode:
        raise RuntimeError(f"PowerShell 创建进程失败: {completed.stderr.strip()}")
    result = json.loads(completed.stdout)
    if not isinstance(result, dict) or result.get("ReturnValue") != 0:
        raise RuntimeError(f"Win32_Process.Create 失败: {result!r}")
    pid = result.get("ProcessId")
    if type(pid) is not int or pid <= 0:
        raise RuntimeError(f"Win32_Process.Create 未返回有效进程 ID: {result!r}")
    return pid


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
        pid = _start_detached_process([exe, "-rc", str(cfg.rc_port)])
    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        logger.error("启动 StreamXpress 失败: %s", exc)
        return {"ok": False, "error": f"启动 StreamXpress 失败: {exc}"}
    ready = False
    for _ in range(10):
        time.sleep(0.5)
        if _port_open(cfg.rc_port):
            ready = True
            break
    if ready:
        logger.info("StreamXpress 已就绪，pid=%d, port=%d", pid, cfg.rc_port)
    else:
        logger.warning("StreamXpress 启动后端口 %d 未就绪", cfg.rc_port)
    return {"ok": True, "pid": pid, "port": cfg.rc_port, "ready": ready}

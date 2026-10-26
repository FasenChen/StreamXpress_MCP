"""Launch and close the local StreamXpress application from configuration."""

import json
import logging
import socket
import subprocess
import time
from pathlib import Path

from .config import StreamXpressConfig, resolve_rc_port

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


def _listener_pids(port: int) -> list[int]:
    """Read TCP ownership so another process cannot satisfy launch readiness."""
    script = """
$ErrorActionPreference = 'Stop'
$port = [int][Console]::In.ReadToEnd()
$owners = @(Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq $port } |
    Select-Object -ExpandProperty OwningProcess -Unique)
ConvertTo-Json -InputObject $owners -Compress
"""
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script],
        input=str(port), capture_output=True, text=True, encoding="utf-8", timeout=15,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if completed.returncode:
        raise RuntimeError(f"无法确认 RC 监听进程: {completed.stderr.strip()}")
    owners = json.loads(completed.stdout)
    if not isinstance(owners, list) or any(type(pid) is not int or pid <= 0 for pid in owners):
        raise RuntimeError(f"无效的 RC 监听进程: {owners!r}")
    return owners


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
    resolve_rc_port(cfg)

    logger.info("正在启动 StreamXpress: %s -rc %d", exe, cfg.rc_port)
    try:
        if _listener_pids(cfg.rc_port):
            return {"ok": False, "port": cfg.rc_port,
                    "error": f"RC 端口 {cfg.rc_port} 已被占用；请连接已有实例或使用不同 rc_port，未重复启动"}
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
        try:
            owners = _listener_pids(cfg.rc_port)
            if owners != [pid]:
                raise RuntimeError(f"RC 监听进程 {owners} 不是本次启动的进程 {pid}")
        except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
            return {"ok": False, "pid": pid, "port": cfg.rc_port, "ready": False, "error": str(exc)}
        logger.info("StreamXpress 已就绪，pid=%d, port=%d", pid, cfg.rc_port)
    else:
        logger.warning("StreamXpress 启动后端口 %d 未就绪", cfg.rc_port)
        return {"ok": False, "pid": pid, "port": cfg.rc_port, "ready": False,
                "error": "StreamXpress 启动后 RC 端口未就绪，保留进程供诊断"}
    return {"ok": True, "pid": pid, "port": cfg.rc_port, "ready": ready}


def close_streamxpress(cfg: StreamXpressConfig) -> dict:
    """Close one local player matched by executable path and RC port."""
    if not cfg.streamxpress_path:
        return {"ok": False, "error": "config.json 未配置 streamxpress_path，无法定位要关闭的应用"}
    if not Path(cfg.streamxpress_path).is_absolute():
        return {"ok": False, "error": "streamxpress_path 必须是绝对路径，无法安全定位要关闭的应用"}
    resolve_rc_port(cfg)

    script = r"""
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$target = [Console]::In.ReadToEnd() | ConvertFrom-Json
$exe = [IO.Path]::GetFullPath($target.exe)
$name = [IO.Path]::GetFileName($exe)
$candidates = @(Get-CimInstance Win32_Process | Where-Object {
    if ($_.Name -ne $name) { return $false }
    if (-not $_.ExecutablePath -or -not $_.CommandLine) {
        throw "Cannot verify executable path/command line for process $($_.ProcessId)"
    }
    if ($_.ExecutablePath -ne $exe) { return $false }
    $playerArguments = @([regex]::Matches($_.CommandLine, '"[^"]*"|\S+') |
        ForEach-Object { $_.Value.Trim('"') })
    $rcIndex = [Array]::IndexOf($playerArguments, '-rc')
    $rcIndex -ge 1 -and $rcIndex + 1 -lt $playerArguments.Count -and
        $playerArguments[$rcIndex + 1] -eq [string]$target.rc_port
})
if ($candidates.Count -gt 1) {
    throw "Multiple StreamXpress processes use rc_port $($target.rc_port); refusing ambiguous close"
}
$players = @($candidates | ForEach-Object {
    $process = Get-Process -Id $_.ProcessId
    if ($process.Path -ne $exe) { throw 'Process identity changed before close' }
    $process
})
$playerIds = @($players | ForEach-Object { $_.Id })
foreach ($player in $players) {
    if ($player.HasExited) { continue }
    if (-not $player.CloseMainWindow()) {
        throw "Cannot close StreamXpress window for process $($player.Id)"
    }
    if (-not $player.WaitForExit(5000)) {
        throw "StreamXpress process $($player.Id) did not exit within 5 seconds"
    }
}
$status = if ($players.Count) { 'closed' } else { 'not_running' }
@{ok = $true; status = $status; running = $false; pids = $playerIds} | ConvertTo-Json -Compress
"""
    try:
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script],
            input=json.dumps({"exe": cfg.streamxpress_path, "rc_port": cfg.rc_port}),
            capture_output=True, text=True, encoding="utf-8", timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip())
        result = json.loads(completed.stdout)
        if (
            not isinstance(result, dict)
            or result.get("ok") is not True
            or result.get("status") not in ("closed", "not_running")
            or result.get("running") is not False
            or not isinstance(result.get("pids"), list)
        ):
            raise RuntimeError(f"无效的关闭结果: {result!r}")
        return result
    except (OSError, subprocess.SubprocessError, ValueError, RuntimeError) as exc:
        logger.error("关闭 StreamXpress 失败: %s", exc)
        return {"ok": False, "error": f"关闭 StreamXpress 失败，未确认应用退出: {exc}"}

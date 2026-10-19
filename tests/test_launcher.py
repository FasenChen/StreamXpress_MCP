from unittest.mock import patch
import subprocess
import pytest
from streamxpress_mcp.config import StreamXpressConfig
from streamxpress_mcp import launcher


def test_launch_returns_error_when_path_empty():
    result = launcher.launch_streamxpress(StreamXpressConfig())
    assert result["ok"] is False
    assert "streamxpress_path" in result["error"]


def test_launch_returns_error_when_exe_missing(tmp_path):
    cfg = StreamXpressConfig(streamxpress_path=str(tmp_path / "nope.exe"))
    result = launcher.launch_streamxpress(cfg)
    assert result["ok"] is False
    assert "不存在" in result["error"]


@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher._start_detached_process")
def test_launch_starts_with_rc_args_and_probes_port(mock_start, mock_port_open, tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    mock_start.return_value = 12345
    mock_port_open.side_effect = [False, False, True]  # 第 3 次探测成功

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    with patch("streamxpress_mcp.launcher.time.sleep"):
        result = launcher.launch_streamxpress(cfg)

    mock_start.assert_called_once_with([str(exe), "-rc", "5000"])
    assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}


@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher._start_detached_process")
@pytest.mark.parametrize("error", [OSError("dll missing"), RuntimeError("WMI denied"),
                                        subprocess.TimeoutExpired("powershell.exe", 15)])
def test_launch_returns_error_when_start_fails(mock_start, mock_port_open, tmp_path, error):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    mock_start.side_effect = error

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    result = launcher.launch_streamxpress(cfg)

    assert result["ok"] is False
    assert "启动 StreamXpress 失败" in result["error"]
    assert str(error) in result["error"]
    mock_port_open.assert_not_called()


@patch("streamxpress_mcp.launcher.subprocess.run")
def test_start_detached_process_passes_command_as_data(mock_run):
    command = ["C:/测试 files/$(example)&/StreamXpress64.exe", "-rc", "5000"]
    mock_run.return_value = subprocess.CompletedProcess(
        [], 0, stdout='{"ReturnValue":0,"ProcessId":12345}', stderr="",
    )
    assert launcher._start_detached_process(command) == 12345
    args, kwargs = mock_run.call_args
    assert args[0][:6] == ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command"]
    assert command[0] not in args[0][-1]
    assert kwargs["input"] == subprocess.list2cmdline(command)
    assert kwargs["creationflags"] == subprocess.CREATE_NO_WINDOW
    assert kwargs["timeout"] == 15


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("exit_code,stdout,stderr,error", [
    (1, "", "WMI unavailable", "WMI unavailable"),
    (0, '{"ReturnValue":2}', "", "Win32_Process.Create 失败"),
    (0, '{"ReturnValue":0,"ProcessId":0}', "", "有效进程 ID"),
    (0, "[]", "", "Win32_Process.Create 失败"),
    (0, "invalid json", "", "Expecting value"),
])
def test_start_detached_process_rejects_failed_or_invalid_result(
    mock_run, exit_code, stdout, stderr, error,
):
    mock_run.return_value = subprocess.CompletedProcess([], exit_code, stdout=stdout, stderr=stderr)
    with pytest.raises((RuntimeError, ValueError), match=error):
        launcher._start_detached_process(["StreamXpress64.exe", "-rc", "5000"])

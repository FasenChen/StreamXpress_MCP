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


@patch("streamxpress_mcp.launcher._listener_pids", side_effect=[[], [12345]])
@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher._start_detached_process")
def test_launch_starts_with_rc_args_and_probes_port(mock_start, mock_port_open, mock_owners, tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    mock_start.return_value = 12345
    mock_port_open.side_effect = [False, False, True]  # 第 3 次探测成功

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    with patch("streamxpress_mcp.launcher.time.sleep"):
        result = launcher.launch_streamxpress(cfg)

    mock_start.assert_called_once_with([str(exe), "-rc", "5000"])
    assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}
    assert mock_owners.call_count == 2


@patch("streamxpress_mcp.launcher._listener_pids", return_value=[])
@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher._start_detached_process")
@pytest.mark.parametrize("error", [OSError("dll missing"), RuntimeError("WMI denied"),
                                        subprocess.TimeoutExpired("powershell.exe", 15)])
def test_launch_returns_error_when_start_fails(mock_start, mock_port_open, mock_owners, tmp_path, error):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    mock_start.side_effect = error
    mock_port_open.return_value = False

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


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("exe", ["", "StreamXpress64.exe"])
def test_close_rejects_missing_or_relative_path(mock_run, exe):
    result = launcher.close_streamxpress(StreamXpressConfig(streamxpress_path=exe))
    assert result["ok"] is False
    assert "streamxpress_path" in result["error"]
    mock_run.assert_not_called()


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("status,pids", [("closed", [12345]), ("not_running", [])])
def test_close_passes_executable_as_data_and_returns_verified_result(mock_run, status, pids):
    import json

    exe = "C:/测试 files/$(example)&/StreamXpress64.exe"
    expected = {"ok": True, "status": status, "running": False, "pids": pids}
    mock_run.return_value = subprocess.CompletedProcess(
        [], 0, stdout=json.dumps(expected), stderr="",
    )
    assert launcher.close_streamxpress(StreamXpressConfig(streamxpress_path=exe)) == expected
    args, kwargs = mock_run.call_args
    assert exe not in args[0][-1]
    assert json.loads(kwargs["input"]) == {"exe": exe, "rc_port": 5000}
    assert kwargs["timeout"] == 15
    assert kwargs["creationflags"] == subprocess.CREATE_NO_WINDOW


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("exit_code,stdout,stderr", [
    (1, "", "Cannot close StreamXpress window"),
    (1, "", "StreamXpress did not exit within 5 seconds"),
    (1, "", "Access denied"),
    (0, "invalid json", ""),
    (0, "[]", ""),
    (0, '{"ok":true,"status":[],"running":false,"pids":[]}', ""),
    (0, '{"ok":true,"status":"closed","running":true,"pids":[1]}', ""),
    (0, '{"ok":true,"status":"disconnected","running":false,"pids":[]}', ""),
])
def test_close_does_not_claim_exit_on_failed_or_invalid_result(mock_run, exit_code, stdout, stderr):
    mock_run.return_value = subprocess.CompletedProcess([], exit_code, stdout=stdout, stderr=stderr)
    result = launcher.close_streamxpress(
        StreamXpressConfig(streamxpress_path="C:/DekTec/StreamXpress64.exe"),
    )
    assert result["ok"] is False
    assert "未确认应用退出" in result["error"]
    assert "running" not in result


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("error", [OSError("PowerShell unavailable"),
                                        subprocess.TimeoutExpired("powershell.exe", 15)])
def test_close_reports_process_control_errors(mock_run, error):
    mock_run.side_effect = error
    result = launcher.close_streamxpress(
        StreamXpressConfig(streamxpress_path="C:/DekTec/StreamXpress64.exe"),
    )
    assert result["ok"] is False
    assert str(error) in result["error"]


def test_launch_does_not_start_another_process_on_occupied_port(tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.touch()
    with (
        patch.object(launcher, "_listener_pids", return_value=[12345]),
        patch.object(launcher, "_start_detached_process") as start,
    ):
        result = launcher.launch_streamxpress(StreamXpressConfig(str(exe), rc_port=5001))
    assert result["ok"] is False
    assert "已被占用" in result["error"]
    start.assert_not_called()


@pytest.mark.parametrize("owners", [[54321], [12345, 54321], []])
def test_launch_does_not_claim_ready_for_another_listener(tmp_path, owners):
    exe = tmp_path / "StreamXpress64.exe"
    exe.touch()
    with (
        patch.object(launcher, "_port_open", return_value=True),
        patch.object(launcher, "_start_detached_process", return_value=12345),
        patch.object(launcher, "_listener_pids", side_effect=[[], owners]),
        patch.object(launcher.time, "sleep"),
    ):
        result = launcher.launch_streamxpress(StreamXpressConfig(str(exe), rc_port=5001))
    assert result["ok"] is False and result["ready"] is False
    assert result["pid"] == 12345
    assert "不是本次启动" in result["error"]


def test_launch_timeout_is_a_failure_with_diagnostic_pid(tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.touch()
    with (
        patch.object(launcher, "_port_open", return_value=False),
        patch.object(launcher, "_start_detached_process", return_value=12345),
        patch.object(launcher, "_listener_pids", return_value=[]) as owners,
        patch.object(launcher.time, "sleep"),
    ):
        result = launcher.launch_streamxpress(StreamXpressConfig(str(exe), rc_port=5001))
    assert result["ok"] is False and result["ready"] is False
    assert result["pid"] == 12345
    owners.assert_called_once_with(5001)


@patch("streamxpress_mcp.launcher.subprocess.run")
@pytest.mark.parametrize("stdout", ['{}', '[0]', '[true]', '["12345"]'])
def test_listener_lookup_rejects_invalid_owners(mock_run, stdout):
    mock_run.return_value = subprocess.CompletedProcess([], 0, stdout=stdout, stderr="")
    with pytest.raises(RuntimeError, match="无效"):
        launcher._listener_pids(5001)

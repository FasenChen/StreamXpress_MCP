from unittest.mock import patch, MagicMock
import subprocess
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
@patch("streamxpress_mcp.launcher.subprocess.Popen")
def test_launch_starts_with_rc_args_and_probes_port(mock_popen, mock_port_open, tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    proc = MagicMock()
    proc.pid = 12345
    mock_popen.return_value = proc
    mock_port_open.side_effect = [False, False, True]  # 第 3 次探测成功

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    with patch("streamxpress_mcp.launcher.time.sleep"):
        result = launcher.launch_streamxpress(cfg)

    mock_popen.assert_called_once_with(
        [str(exe), "-rc", "5000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}


@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher.subprocess.Popen")
def test_launch_returns_error_when_popen_raises_oserror(mock_popen, mock_port_open, tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    mock_popen.side_effect = OSError("dll missing")

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    result = launcher.launch_streamxpress(cfg)

    assert result["ok"] is False
    assert "启动 StreamXpress 失败" in result["error"]
    assert "dll missing" in result["error"]

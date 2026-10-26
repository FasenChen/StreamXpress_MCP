"""Windows integration boundary: an external player must outlive stdio cleanup."""

import asyncio
import json
import sys
import socket
import subprocess
import time
import os

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows Job Object lifecycle")


@pytest.fixture
def local_players(tmp_path):
    """Disposable GUI/listener processes exercise Windows targeting without RF hardware."""
    import win32api
    import win32con
    import win32event
    from streamxpress_mcp.launcher import _start_detached_process

    exe = tmp_path / "测试 & -rc 5000 player" / "StreamXpress64.exe"
    exe.parent.mkdir()
    source = """
using System;
using System.Net;
using System.Net.Sockets;
using System.Runtime.InteropServices;
using System.Windows.Forms;
public class Player {
    [DllImport("user32.dll")] static extern bool ShowWindow(IntPtr window, int command);
    [STAThread] public static void Main(string[] args) {
        TcpListener listener = null;
        if (args.Length == 2) {
            listener = new TcpListener(IPAddress.Loopback, int.Parse(args[1]));
            listener.Start();
        }
        Form form = new Form { Text = "StreamXpress targeting test" };
        form.Shown += (sender, e) => ShowWindow(form.Handle, 5);
        try { Application.Run(form); }
        finally { if (listener != null) listener.Stop(); }
    }
}
"""
    script = """
$ErrorActionPreference = 'Stop'
$data = [Console]::In.ReadToEnd() | ConvertFrom-Json
Add-Type -TypeDefinition $data.source -ReferencedAssemblies System.Windows.Forms,System.Drawing -OutputAssembly $data.exe -OutputType WindowsApplication
"""
    compiled = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", script],
        input=json.dumps({"exe": str(exe), "source": source}),
        capture_output=True, text=True, encoding="utf-8", timeout=20,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    assert compiled.returncode == 0, compiled.stderr
    handles = []

    def track(pid):
        handle = win32api.OpenProcess(win32con.SYNCHRONIZE | win32con.PROCESS_TERMINATE, False, pid)
        handles.append(handle)
        return handle

    def duplicate(port):
        return track(_start_detached_process([str(exe), "-rc", str(port), "--no-listener"]))

    try:
        yield exe, track, duplicate
    finally:
        for handle in handles:
            try:
                if win32event.WaitForSingleObject(handle, 0) == win32con.WAIT_TIMEOUT:
                    win32api.TerminateProcess(handle, 0)
                    win32event.WaitForSingleObject(handle, 5000)
            finally:
                handle.Close()


def _free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def _call_lifecycle_tool(config_file, tool_name, rc_port):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def call():
        parameters = StdioServerParameters(
            command=sys.executable, args=["-B", "-m", "streamxpress_mcp"],
            env={**os.environ, "STREAMXPRESS_MCP_CONFIG": str(config_file)},
        )
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, {"rc_port": rc_port})
                assert not result.is_error, result
                return json.loads(result.content[0].text)
    return asyncio.run(call())


def test_two_instances_have_distinct_listeners_and_close_independently(local_players):
    import win32con
    import win32event
    from streamxpress_mcp.config import StreamXpressConfig
    from streamxpress_mcp.launcher import launch_streamxpress, close_streamxpress, _listener_pids

    exe, track, _ = local_players
    config_file = exe.parent / "config.json"
    config_file.write_text(json.dumps({"streamxpress_path": str(exe)}), encoding="utf-8")
    cfg_a = StreamXpressConfig(str(exe), rc_port=_free_port())
    first = _call_lifecycle_tool(config_file, "launch", cfg_a.rc_port)
    if first.get("pid"):
        handle_a = track(first["pid"])
    assert first["ok"], first
    cfg_b = StreamXpressConfig(str(exe), rc_port=_free_port())
    second = _call_lifecycle_tool(config_file, "launch", cfg_b.rc_port)
    if second.get("pid"):
        handle_b = track(second["pid"])
    assert second["ok"], second
    assert _listener_pids(cfg_a.rc_port) == [first["pid"]]
    assert _listener_pids(cfg_b.rc_port) == [second["pid"]]
    assert launch_streamxpress(cfg_a)["ok"] is False
    wrong_target = close_streamxpress(StreamXpressConfig(str(exe), rc_port=5000))
    assert wrong_target["status"] == "not_running", wrong_target

    result = _call_lifecycle_tool(config_file, "close", cfg_a.rc_port)
    assert result == {"ok": True, "status": "closed", "running": False, "pids": [first["pid"]]}
    assert win32event.WaitForSingleObject(handle_a, 0) == win32con.WAIT_OBJECT_0
    assert win32event.WaitForSingleObject(handle_b, 0) == win32con.WAIT_TIMEOUT
    assert _listener_pids(cfg_b.rc_port) == [second["pid"]]
    assert close_streamxpress(cfg_a)["status"] == "not_running"
    assert _call_lifecycle_tool(config_file, "close", cfg_b.rc_port)["ok"] is True
    assert win32event.WaitForSingleObject(handle_b, 0) == win32con.WAIT_OBJECT_0


def test_close_refuses_duplicate_rc_port_without_closing_either_player(local_players):
    import win32con
    import win32event
    from streamxpress_mcp.config import StreamXpressConfig
    from streamxpress_mcp.launcher import launch_streamxpress, close_streamxpress

    exe, track, duplicate = local_players
    cfg = StreamXpressConfig(str(exe), rc_port=_free_port())
    first = launch_streamxpress(cfg)
    if first.get("pid"):
        handle_a = track(first["pid"])
    assert first["ok"], first
    handle_b = duplicate(cfg.rc_port)
    time.sleep(0.5)
    result = close_streamxpress(cfg)
    assert result["ok"] is False
    assert "Multiple StreamXpress processes" in result["error"]
    assert win32event.WaitForSingleObject(handle_a, 0) == win32con.WAIT_TIMEOUT
    assert win32event.WaitForSingleObject(handle_b, 0) == win32con.WAIT_TIMEOUT


def test_player_process_survives_mcp_session_shutdown(tmp_path):
    import win32api
    import win32con
    import win32event
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server_file = tmp_path / "launcher_server.py"
    server_file.write_text("""
import sys
from fastmcp import FastMCP
from streamxpress_mcp.launcher import _start_detached_process

mcp = FastMCP("launcher-lifecycle")

@mcp.tool()
def launch_child() -> dict:
    return {"pid": _start_detached_process([sys.executable, "-c", "import time; time.sleep(60)"])}

if __name__ == "__main__":
    mcp.run()
""", encoding="utf-8")

    child_handle = None

    async def exercise():
        nonlocal child_handle
        parameters = StdioServerParameters(command=sys.executable, args=[str(server_file)])
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                result = await session.call_tool("launch_child", {})
                assert not result.is_error, result
                child_pid = json.loads(result.content[0].text)["pid"]
                child_handle = win32api.OpenProcess(
                    win32con.SYNCHRONIZE | win32con.PROCESS_TERMINATE, False, child_pid,
                )

    try:
        asyncio.run(exercise())
        assert win32event.WaitForSingleObject(child_handle, 0) == win32con.WAIT_TIMEOUT
    finally:
        if child_handle is not None:
            try:
                if win32event.WaitForSingleObject(child_handle, 0) == win32con.WAIT_TIMEOUT:
                    win32api.TerminateProcess(child_handle, 0)
                    win32event.WaitForSingleObject(child_handle, 5000)
            finally:
                child_handle.Close()

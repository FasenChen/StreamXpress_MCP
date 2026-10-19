"""Windows integration boundary: an external player must outlive stdio cleanup."""

import asyncio
import json
import sys

import pytest

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows Job Object lifecycle")


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

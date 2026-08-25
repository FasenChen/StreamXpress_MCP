import pytest
from unittest.mock import MagicMock, patch

class TestServerConnectTool:
    @patch("streamxpress_mcp.server.get_client")
    def test_connect_tool_succeeds(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import connect

        result = connect(host="http://localhost", port=5000)
        assert result["status"] == "connected"
        mock_client.connect.assert_called_once_with("http://localhost", 5000)

    @patch("streamxpress_mcp.server.get_client")
    def test_disconnect_tool_succeeds(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import disconnect

        result = disconnect()
        assert result["status"] == "disconnected"
        mock_client.disconnect.assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_disconnect_tool_surfaces_warning(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.disconnect.side_effect = RuntimeError(
            "failed to close StreamXpress session: boom")
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import disconnect
        result = disconnect()
        assert result["status"] == "disconnected"
        assert "failed to close" in result["warning"]


class TestServerPlayoutTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_stop(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import stop
        result = stop()
        assert result["status"] == "stopped"

    @patch("streamxpress_mcp.server.get_client")
    def test_get_status(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_status.return_value = {
            "position_percent": 75.5, "num_wraps": 2,
            "playout_state": 1, "file_name": "test.ts", "ts_rate_bps": 25_000_000}
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import get_status
        result = get_status()
        assert result["position_percent"] == 75.5


EXPECTED_TOOL_NAMES = {
    "launch", "connect", "play", "stop", "get_status", "disconnect",
}

class TestToolNaming:
    """工具注册名不得再带 streamxpress_ 前缀（客户端会自行加 server 名前缀）。"""

    def test_registered_tool_names_have_no_streamxpress_prefix(self):
        import asyncio

        from streamxpress_mcp.server import mcp

        tools = asyncio.run(mcp.list_tools())
        names = {t.name for t in tools}
        assert names == EXPECTED_TOOL_NAMES, (
            f"工具名不匹配: 期望 {sorted(EXPECTED_TOOL_NAMES)}, 实际 {sorted(names)}"
        )
        assert not any(n.startswith("streamxpress_") for n in names), (
            f"工具名仍带前缀: {sorted(n for n in names if n.startswith('streamxpress_'))}"
        )


class TestLaunchTool:
    @patch("streamxpress_mcp.server.launch_streamxpress")
    def test_launch_tool_returns_launcher_result(self, mock_launch):
        mock_launch.return_value = {"ok": True, "pid": 12345, "port": 5000, "ready": True}

        from streamxpress_mcp.server import launch

        result = launch()
        assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}
        assert mock_launch.call_count == 1


class TestGetClientWsdl:
    @pytest.fixture(autouse=True)
    def reset_client_singleton(self):
        import streamxpress_mcp.server as server_mod

        server_mod._client = None
        yield
        server_mod._client = None

    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.resolve_wsdl_path")
    def test_custom_wsdl_used_when_configured(self, mock_resolve, mock_load):
        from streamxpress_mcp.config import StreamXpressConfig
        from streamxpress_mcp.server import get_client

        mock_load.return_value = StreamXpressConfig(sprc_api_path="D:/SpRcApi")
        mock_resolve.return_value = "D:/SpRcApi/WSDL/SpRc.wsdl"

        client = get_client()
        sprc = client._sprc_factory()
        assert sprc._wsdl_template == "D:/SpRcApi/WSDL/SpRc.wsdl"

    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.resolve_wsdl_path")
    def test_default_factory_when_no_custom_wsdl(self, mock_resolve, mock_load):
        from streamxpress_mcp.config import StreamXpressConfig
        from streamxpress_mcp.server import get_client

        mock_load.return_value = StreamXpressConfig()
        mock_resolve.return_value = None

        client = get_client()
        sprc = client._sprc_factory()
        assert sprc._wsdl_template is None


class TestServerPlayTool:
    @patch("streamxpress_mcp.server.launch_streamxpress")
    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.get_client")
    def test_play_tool_forwards_to_client(self, mock_get_client, mock_load, mock_launch):
        from streamxpress_mcp.config import StreamXpressConfig
        mock_load.return_value = StreamXpressConfig()
        mock_client = MagicMock()
        mock_client.connected = True
        mock_client.play.return_value = {
            "status": "playing", "settings_xml": "a.xml", "stream": "a.ts",
            "serial": 315002019, "port": 1,
        }
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import play
        result = play("a.xml", "a.ts", loop=True)
        mock_launch.assert_not_called()
        mock_client.play.assert_called_once_with(
            settings_xml="a.xml", stream="a.ts", loop=True,
        )
        assert result["status"] == "playing"

    @patch("streamxpress_mcp.server.launch_streamxpress")
    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.get_client")
    def test_play_auto_connects_without_launch_if_already_listening(
        self, mock_get_client, mock_load, mock_launch
    ):
        from streamxpress_mcp.config import StreamXpressConfig
        mock_load.return_value = StreamXpressConfig(rc_port=5000)
        mock_client = MagicMock()
        mock_client.connected = False
        mock_client.play.return_value = {
            "status": "playing", "settings_xml": "a.xml", "stream": "a.ts",
            "serial": 1, "port": 1,
        }
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import play
        play("a.xml", "a.ts")
        mock_client.connect.assert_called_once_with("http://localhost", 5000)
        mock_launch.assert_not_called()

    @patch("streamxpress_mcp.server.launch_streamxpress")
    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.get_client")
    def test_play_launches_when_connect_fails(self, mock_get_client, mock_load, mock_launch):
        from streamxpress_mcp.config import StreamXpressConfig
        mock_load.return_value = StreamXpressConfig(rc_port=5000)
        mock_launch.return_value = {"ok": True, "pid": 1, "port": 5000, "ready": True}
        mock_client = MagicMock()
        mock_client.connected = False
        mock_client.connect.side_effect = [RuntimeError("refused"), None]
        mock_client.play.return_value = {
            "status": "playing", "settings_xml": "a.xml", "stream": "a.ts",
            "serial": 1, "port": 1,
        }
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import play
        play("a.xml", "a.ts")
        mock_launch.assert_called_once()
        assert mock_client.connect.call_count == 2


class TestServerConnectDefaults:
    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.get_client")
    def test_connect_defaults_to_localhost_and_config_port(self, mock_get_client, mock_load):
        from streamxpress_mcp.config import StreamXpressConfig
        mock_load.return_value = StreamXpressConfig(rc_port=6000)
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import connect
        result = connect()
        mock_client.connect.assert_called_once_with("http://localhost", 6000)
        assert result == {"status": "connected", "host": "http://localhost", "port": 6000}


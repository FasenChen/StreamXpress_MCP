import pytest
from unittest.mock import MagicMock, patch


class TestStreamXpressConnect:
    def test_connect_creates_session(self, client, mock_sprc):
        client.connect("http://192.168.1.1", 5000)
        mock_sprc.open_session.assert_called_once_with(
            ip_host="http://192.168.1.1", ip_port=5000
        )

    def test_connect_fails_if_already_connected(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="already connected"):
            client.connect("http://localhost", 5000)

    def test_disconnect_closes_session(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.disconnect()
        mock_sprc.cleanup.assert_called_once()

    def test_disconnect_when_not_connected_noops(self, client):
        # Should not raise
        client.disconnect()


class TestStreamXpressPortOps:
    def test_scan_ports_returns_list(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcPortDesc

        mock_port = SpRcPortDesc(
            Serial=217400001,
            TypeNumber=2174,
            Ip=bytes([0, 0, 0, 0]),
            Mac=bytes([0, 0, 0, 0, 0, 0]),
            FirmwareVersion=100,
            FirmwareVariant=0,
            Port=1,
            OutputType=0x00001,  # OTYPE_ASI
            Capabilities=0,
            InUse=0,
        )
        mock_sprc.scan_ports.return_value = [mock_port]

        client.connect("http://localhost", 5000)
        ports = client.scan_ports()

        assert len(ports) == 1
        assert ports[0].Serial == 217400001

    def test_select_port(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.select_port(217400001, 1, 0)
        mock_sprc.select_port.assert_called_once_with(217400001, 1, 0)

    def test_scan_ports_requires_connection(self, client):
        with pytest.raises(RuntimeError, match="not connected"):
            client.scan_ports()


class TestStreamXpressPlayout:
    def test_open_file(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.open_file("C:\\Streams\\test.ts")
        mock_sprc.open_file.assert_called_once_with("C:\\Streams\\test.ts")

    def test_start_stop(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        client.connect("http://localhost", 5000)
        client.start()
        mock_sprc.set_playout_state.assert_called_with(SPRC.STATE_PLAY)
        client.stop()
        mock_sprc.set_playout_state.assert_called_with(SPRC.STATE_STOP)

    def test_get_status(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcPlayoutStatus, SpRcPlayoutInfo

        mock_sprc.get_playout_status.return_value = SpRcPlayoutStatus(
            PosRel=0.5, NumWraps=0, FifoLoad=0, NumErrors=0, TotalMemLoad=0
        )
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, Filename="test.ts", TsRate=25_000_000,
            BurstMode=False, ExtClock=False, FileCanBeRead=True,
            FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=0, FileSize=0, FileType=0,
            LoopBeginRel=0.0, LoopEndRel=0.0, LoopFlags=0,
            PlayoutRate=0, Remux=False, SymRate=0,
            TimeLoopBegin=0, TimeLoopEnd=0, TimeOffset=0,
            TpSize=188, TxPolarity=0,
        )

        client.connect("http://localhost", 5000)
        status = client.get_status()

        assert status["position_percent"] == 50.0
        assert status["file_name"] == "test.ts"
        assert status["ts_rate_bps"] == 25_000_000


class TestStreamXpressParams:
    def test_set_rate(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.set_rate(25_000_000)
        mock_sprc.set_ts_rate.assert_called_once_with(25_000_000)

    def test_set_tsoip_params_udp(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        client.set_tsoip_params(
            dest_ip="239.1.1.1", dest_port=1234, num_tp_per_ip=7, protocol="UDP", ttl=64
        )
        call_args = mock_sprc.set_tsiop_pars.call_args[0][0]
        assert call_args.Ip == bytes([239, 1, 1, 1])
        assert call_args.Port == 1234
        assert call_args.Protocol == DTAPI.PROTO_UDP

    def test_set_rf_params(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.set_rf_params(500_000_000, -37.5)
        call_args = mock_sprc.set_rf_pars.call_args[0][0]
        assert call_args.Frequency == 500_000_000
        assert call_args.Level == -37.5

    def test_set_asi_params(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        client.set_asi_params(remux=True, playout_rate=20_000_000, tx_mode=DTAPI.TXMODE_188)
        call_args = mock_sprc.set_asi_pars.call_args[0][0]
        assert call_args.Remux is True
        assert call_args.PlayoutRate == 20_000_000


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


class TestServerPortTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_scan_ports(self, mock_get_client):
        from streamxpress_mcp.sprc_import import SpRcPortDesc
        mock_client = MagicMock()
        mock_client.scan_ports.return_value = [
            SpRcPortDesc(Serial=217400001, TypeNumber=2174, Ip=bytes(4), Mac=bytes(6),
                         FirmwareVersion=100, FirmwareVariant=0, Port=1,
                         OutputType=0x00001, Capabilities=0, InUse=0)]
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import scan_ports
        result = scan_ports()
        assert len(result) == 1
        assert result[0]["serial"] == 217400001
        assert "ASI" in result[0]["output_types"]

    @patch("streamxpress_mcp.server.get_client")
    def test_select_port(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import select_port
        result = select_port(serial=217400001, port_num=1)
        assert result["status"] == "ok"
        mock_client.select_port.assert_called_once_with(217400001, 1, 0)

    @patch("streamxpress_mcp.server.get_client")
    def test_open_file(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import open_file
        result = open_file("C:\\Streams\\test.ts")
        assert result["status"] == "ok"


class TestServerPlayoutTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_start(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import start
        result = start()
        assert result["status"] == "playing"

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


class TestServerParamTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_set_rate(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_rate
        result = set_rate(25_000_000)
        assert result["status"] == "ok"

    @patch("streamxpress_mcp.server.get_client")
    def test_set_tsoip(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_tsoip_params
        result = set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234)
        assert result["status"] == "ok"

    @patch("streamxpress_mcp.server.get_client")
    def test_set_rf(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_rf_params
        result = set_rf_params(frequency_hz=500_000_000, level_dbm=-37.5)
        assert result["status"] == "ok"

    @patch("streamxpress_mcp.server.get_client")
    def test_set_asi(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_asi_params
        result = set_asi_params(remux=True, playout_rate=20_000_000)
        assert result["status"] == "ok"


EXPECTED_TOOL_NAMES = {
    "connect", "disconnect", "scan_ports", "select_port", "open_file",
    "start", "stop", "get_status", "set_rate", "set_tsoip_params",
    "set_rf_params", "set_asi_params", "launch",
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

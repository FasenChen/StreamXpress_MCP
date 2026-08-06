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

        from streamxpress_mcp.server import streamxpress_connect

        result = streamxpress_connect(host="http://localhost", port=5000)
        assert result["status"] == "connected"
        mock_client.connect.assert_called_once_with("http://localhost", 5000)

    @patch("streamxpress_mcp.server.get_client")
    def test_disconnect_tool_succeeds(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_disconnect

        result = streamxpress_disconnect()
        assert result["status"] == "disconnected"
        mock_client.disconnect.assert_called_once()

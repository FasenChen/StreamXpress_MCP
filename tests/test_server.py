import pytest
from unittest.mock import MagicMock, patch

from streamxpress_mcp.sprc_import import DTAPI


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

    def test_scan_ports_tool_exposes_capabilities(self, client, mock_sprc):
        """3a: Capabilities 位掩码被展开为标签（多 bit 覆盖）。"""
        from streamxpress_mcp.sprc_import import SpRcPortDesc
        from streamxpress_mcp import server as server_mod

        mock_port = SpRcPortDesc(
            Serial=217400001, TypeNumber=2174,
            Ip=bytes([0, 0, 0, 0]), Mac=bytes(6),
            FirmwareVersion=100, FirmwareVariant=0,
            Port=1, OutputType=0x20000,  # TS-over-IP
            Capabilities=1 | 2 | 128,   # ADJLVL | CM | SFN
            InUse=0,
        )
        mock_sprc.scan_ports.return_value = [mock_port]
        client.connect("http://localhost", 5000)

        with patch("streamxpress_mcp.server.get_client", return_value=client):
            result = server_mod.scan_ports()

        assert result[0]["capabilities"] == ["ADJLVL", "CM", "SFN"]
        assert result[0]["capabilities_raw"] == 1 | 2 | 128

    def test_describe_capabilities_multibit(self):
        from streamxpress_mcp.server import _describe_capabilities

        assert _describe_capabilities(1 | 2 | 128) == ["ADJLVL", "CM", "SFN"]
        assert _describe_capabilities(0) == []
        assert _describe_capabilities(1 << 20) == []      # 未知位

    def test_select_port(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.select_port(217400001, 1, 1)
        mock_sprc.select_port.assert_called_once_with(217400001, 1, 1)

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

    def test_pause(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        client.connect("http://localhost", 5000)
        client.pause()
        mock_sprc.set_playout_state.assert_called_once_with(SPRC.STATE_PAUSE)

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

    def test_get_status_all_fields(self, client, mock_sprc):
        """3b: get_status 补齐 8 个新字段，并钉住此前无断言的 5 个字段。"""
        from streamxpress_mcp.sprc_import import SpRcPlayoutStatus, SpRcPlayoutInfo

        mock_sprc.get_playout_status.return_value = SpRcPlayoutStatus(
            PosRel=0.5, NumWraps=3, FifoLoad=42, NumErrors=1, TotalMemLoad=1024)
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, Filename="test.ts", TsRate=25_000_000, PlayoutRate=25_000_000,
            BurstMode=True, ExtClock=True, FileCanBeRead=True,
            FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=25_100_000, FileSize=1024, FileType=1,
            LoopBeginRel=0.25, LoopEndRel=0.75, LoopFlags=3,
            Remux=True, SymRate=27_500_000,
            TimeLoopBegin=0, TimeLoopEnd=0, TimeOffset=10,
            TpSize=188, TxPolarity=1)

        client.connect("http://localhost", 5000)
        status = client.get_status()
        assert status["position_percent"] == 50.0
        assert status["num_wraps"] == 3
        assert status["total_mem_load"] == 1024
        assert status["time_offset"] == 10
        assert status["remux"] is True
        assert status["playout_state"] == 1
        assert status["file_can_be_read"] is True
        assert status["file_rate_est"] == 25_100_000
        assert status["file_type"] == 1
        assert status["loop_begin_rel"] == 0.25
        assert status["loop_end_rel"] == 0.75
        assert status["tx_polarity"] == 1
        assert status["burst_mode"] is True
        assert status["ext_clock"] is True

    def test_get_playout_info_full_pass_through(self, client, mock_sprc):
        """3b: get_playout_info 全量透传（CamelCase 键，杜绝字段漂移）。"""
        from streamxpress_mcp.sprc_import import SpRcPlayoutInfo

        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, Filename="test.ts", TsRate=25_000_000, PlayoutRate=25_000_000,
            BurstMode=False, ExtClock=False, FileCanBeRead=True,
            FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=0, FileSize=1024, FileType=0,
            LoopBeginRel=0.0, LoopEndRel=0.0, LoopFlags=3,
            Remux=False, SymRate=0,
            TimeLoopBegin=0, TimeLoopEnd=0, TimeOffset=0,
            TpSize=188, TxPolarity=0)

        client.connect("http://localhost", 5000)
        info = client.get_playout_info()
        assert info["FileCanBeRead"] is True
        assert info["FileSize"] == 1024
        assert info["LoopFlags"] == 3
        assert info["TpSize"] == 188

    @patch("streamxpress_mcp.server.get_client")
    def test_get_playout_info_tool(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_playout_info.return_value = {"FileCanBeRead": True}
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import get_playout_info
        assert get_playout_info() == {"FileCanBeRead": True}


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

    def test_set_rf_params_preserves_flags(self, client, mock_sprc):
        """1: 未显式指定的标志必须保持服务器现值，不得被清零。"""
        from streamxpress_mcp.sprc_import import SpRcRfPars

        mock_sprc.get_rf_pars.return_value = SpRcRfPars(
            Frequency=100, Level=-10.0, SpecInv=True, CW=True, RfEnabledOnStop=True)
        client.connect("http://localhost", 5000)
        client.set_rf_params(500_000_000, -30.0)
        pars = mock_sprc.set_rf_pars.call_args[0][0]
        assert pars.Frequency == 500_000_000 and pars.Level == -30.0
        assert pars.SpecInv is True and pars.CW is True and pars.RfEnabledOnStop is True

    def test_set_rf_params_explicit_flags_override(self, client, mock_sprc):
        """1: 显式传入的标志必须生效，且不额外读取。"""
        client.connect("http://localhost", 5000)
        client.set_rf_params(500_000_000, -30.0,
                             spec_inv=True, cw=False, rf_enabled_on_stop=True)
        pars = mock_sprc.set_rf_pars.call_args[0][0]
        assert pars.SpecInv is True and pars.CW is False and pars.RfEnabledOnStop is True
        mock_sprc.get_rf_pars.assert_not_called()   # 全部显式 => 不做 RMW 读

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
    "start", "stop", "pause", "get_status", "set_rate", "set_tsoip_params",
    "set_rf_params", "set_asi_params", "launch",
    "get_remote_version", "get_remote_dtapi_version", "get_app_info",
    "show_window", "clear_errors",
    "get_playout_info",
    "get_asi_pars", "get_cmmb_pars", "get_mod_pars", "get_rf_pars",
    "get_tsoip_pars", "get_spi_pars", "get_hw_noise_pars", "get_iq_gain",
    "get_signal_source", "get_use_nit",
    "get_channel_modelling_pars", "get_dvb_t2_group", "get_dvb_t2_pars",
    "get_isdb_t_pars", "get_tdt_adapt_pars", "get_tsg_pars", "get_sfn_status",
    "open_channel_modelling_file", "save_channel_modelling_settings",
    "save_settings", "normalise",
    "set_loop_flags", "set_iq_gain", "set_remux", "set_signal_source",
    "set_use_nit", "set_sfn_mode", "set_sub_loop_pars", "select_dta_plus",
    "set_cmmb_pars", "set_hw_noise_pars", "set_spi_pars", "set_tsg_pars",
    "set_dvb_t2_group",
    "set_mod_pars", "set_channel_modelling_pars", "set_dvb_t2_pars",
    "set_isdb_t_pars", "set_tdt_adapt_pars", "set_playout_state_sfn",
    "wait_for_condition",
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


class TestSerializationHelpers:
    def test_jsonable_converts_bytes_to_list(self):
        from streamxpress_mcp.client import _jsonable

        assert _jsonable(b"\x01\x02") == [1, 2]

    def test_jsonable_recurses_into_lists_and_dicts(self):
        from streamxpress_mcp.client import _jsonable

        assert _jsonable({"a": [b"\x00", {"b": b"\xff"}]}) == {"a": [[0], {"b": [255]}]}

    def test_to_dict_flattens_nested_dataclass(self):
        from streamxpress_mcp.client import _to_dict
        from streamxpress_mcp.sprc_import import SpRcTsoipPars, DTAPI

        pars = SpRcTsoipPars(
            TxMode=DTAPI.TXMODE_188, Ip=b"\xef\x01\x02\x03", Port=1234,
            EnaFailover=False, Ip2=bytes(4), Port2=0, TimeToLive=64,
            NumTpPerIp=7, Protocol=DTAPI.PROTO_UDP, DiffServ=0,
            FecMode=DTAPI.FEC_DISABLE, FecNumRows=0, FecNumCols=0,
        )
        assert _to_dict(pars)["Ip"] == [239, 1, 2, 3]

    def test_sprc_import_exports_new_types(self):
        from streamxpress_mcp.sprc_import import (
            SpRcVersion, SpRcCmmbPars, SpRcCmPars, SpRcCmPath, SpRcDvbT2Group,
            SpRcDvbT2Pars, SpRcHwNoisePars, SpRcIsdbtPars, SpRcIsdbtLayerPars,
            SpRcPlayoutSfnPars, SpRcSpiPars, SpRcSubLoopPars, SpRcDateTime,
            SpRcTdtAdaptPars, SpRcTsgPars, SpRcSfnStatus,
        )

        assert SpRcVersion(MajorVersion=1, MinorVersion=2, BugFixVersion=3, BuildNumber=4).MajorVersion == 1
        assert SpRcCmmbPars(Bandwidth=0, AreaId=1, TxId=2).AreaId == 1

    def test_parse_ip_valid(self):
        from streamxpress_mcp.client import _parse_ip

        assert _parse_ip("239.1.1.1") == bytes([239, 1, 1, 1])

    def test_parse_ip_rejects_wrong_segment_count(self):
        import pytest

        from streamxpress_mcp.client import _parse_ip

        with pytest.raises(ValueError, match="invalid IPv4"):
            _parse_ip("1.2.3")

    def test_parse_ip_rejects_non_numeric_octet(self):
        import pytest

        from streamxpress_mcp.client import _parse_ip

        with pytest.raises(ValueError, match="invalid IPv4"):
            _parse_ip("1.2.x.4")


class TestClientSessionVersion:
    def test_get_remote_version(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcVersion

        mock_sprc.get_remote_version.return_value = SpRcVersion(
            MajorVersion=1, MinorVersion=12, BugFixVersion=0, BuildNumber=21)
        client.connect("http://localhost", 5000)
        assert client.get_remote_version() == {
            "MajorVersion": 1, "MinorVersion": 12, "BugFixVersion": 0, "BuildNumber": 21}

    def test_get_remote_dtapi_version(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcVersion

        mock_sprc.get_remote_dtapi_version.return_value = SpRcVersion(
            MajorVersion=6, MinorVersion=3, BugFixVersion=2, BuildNumber=224)
        client.connect("http://localhost", 5000)
        assert client.get_remote_dtapi_version()["MinorVersion"] == 3

    def test_get_app_info(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcVersion

        mock_sprc.get_app_info.return_value = (
            "StreamXpress",
            SpRcVersion(MajorVersion=3, MinorVersion=31, BugFixVersion=0, BuildNumber=772),
        )
        client.connect("http://localhost", 5000)
        assert client.get_app_info() == {
            "app_name": "StreamXpress",
            "version": {"MajorVersion": 3, "MinorVersion": 31, "BugFixVersion": 0, "BuildNumber": 772},
        }

    def test_show_window(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.show_window(True)
        mock_sprc.show_window.assert_called_once_with(True)

    def test_clear_errors(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.clear_errors()
        mock_sprc.clear_errors.assert_called_once()


class TestServerSessionVersionTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_get_remote_version_tool(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_remote_version.return_value = {"MajorVersion": 1}
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import get_remote_version
        assert get_remote_version() == {"MajorVersion": 1}

    @patch("streamxpress_mcp.server.get_client")
    def test_show_window_tool(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import show_window
        assert show_window(False) == {"status": "ok", "show": False}
        mock_client.show_window.assert_called_once_with(False)


class TestClientParameterGetters:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_get_asi_pars(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcAsiPars, DTAPI

        mock_sprc.get_asi_pars.return_value = SpRcAsiPars(
            Remux=True, PlayoutRate=20_000_000, BurstMode=False,
            TxMode=DTAPI.TXMODE_188, Polarity=DTAPI.TXPOL_NORMAL)
        self._connect(client)
        result = client.get_asi_pars()
        assert result["Remux"] is True
        assert result["PlayoutRate"] == 20_000_000

    def test_get_tsoip_pars_converts_bytes(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcTsoipPars, DTAPI

        mock_sprc.get_tsoip_pars.return_value = SpRcTsoipPars(
            TxMode=DTAPI.TXMODE_188, Ip=b"\xef\x01\x02\x03", Port=1234,
            EnaFailover=False, Ip2=bytes(4), Port2=0, TimeToLive=64,
            NumTpPerIp=7, Protocol=DTAPI.PROTO_UDP, DiffServ=0,
            FecMode=DTAPI.FEC_DISABLE, FecNumRows=0, FecNumCols=0)
        self._connect(client)
        assert client.get_tsoip_pars()["Ip"] == [239, 1, 2, 3]

    def test_get_iq_gain_returns_int(self, client, mock_sprc):
        mock_sprc.get_iq_gain.return_value = 150
        self._connect(client)
        assert client.get_iq_gain() == 150

    def test_get_use_nit_returns_bool(self, client, mock_sprc):
        mock_sprc.get_use_nit.return_value = True
        self._connect(client)
        assert client.get_use_nit() is True


class TestServerParameterGetterTools:
    @pytest.mark.parametrize("tool_name,method", [
        ("get_asi_pars", "get_asi_pars"),
        ("get_cmmb_pars", "get_cmmb_pars"),
        ("get_mod_pars", "get_mod_pars"),
        ("get_rf_pars", "get_rf_pars"),
        ("get_tsoip_pars", "get_tsoip_pars"),
        ("get_spi_pars", "get_spi_pars"),
        ("get_hw_noise_pars", "get_hw_noise_pars"),
        ("get_iq_gain", "get_iq_gain"),
        ("get_signal_source", "get_signal_source"),
        ("get_use_nit", "get_use_nit"),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_getter_tool_returns_client_result(self, mock_get_client, tool_name, method):
        mock_client = MagicMock()
        mock_client.get_use_nit.return_value = True
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        assert tool() == getattr(mock_client, method).return_value


class TestClientComplexGetters:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_get_channel_modelling_pars_nested_paths(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcCmPars, SpRcCmPath

        mock_sprc.get_channel_modelling_pars.return_value = SpRcCmPars(
            CmEnable=True, AwgnEnable=True, Snr=20.0, PathsEnable=True,
            Paths=[SpRcCmPath(Type=0, Attenuation=-10.0, Delay=1.5, Phase=90.0, Doppler=0.0)])
        self._connect(client)
        result = client.get_channel_modelling_pars()
        assert result["CmEnable"] is True
        assert result["Paths"][0]["Delay"] == 1.5

    def test_get_isdb_t_pars_pid2layer(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import (
            SpRcIsdbtPars, SpRcIsdbtLayerPars, DTAPI)

        mock_sprc.get_isdb_t_pars.return_value = SpRcIsdbtPars(
            DoMux=True, BType=0, Mode=3, Guard=2, PartialRx=0, Emergency=0,
            IipPid=0,
            LayerPars=[SpRcIsdbtLayerPars(NumSegments=13, Modulation=DTAPI.ISDBT_MOD_QAM64,
                                          CodeRate=0, TimeInterleave=0)],
            Pid2Layer={100: 1}, LayerOther=0, ParXtra0=0)
        self._connect(client)
        result = client.get_isdb_t_pars()
        assert result["Pid2Layer"] == {100: 1}
        assert result["LayerPars"][0]["NumSegments"] == 13

    def test_get_tdt_adapt_pars_nested_datetime(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcTdtAdaptPars, SpRcDateTime, SPRC

        mock_sprc.get_tdt_adapt_pars.return_value = SpRcTdtAdaptPars(
            TdtAdaptMode=SPRC.TDT_ADAPT_USE_SPECIFIED,
            TdtDateTime=SpRcDateTime(Year=2026, Month=8, Day=8, Hour=12, Minute=0, Second=0))
        self._connect(client)
        result = client.get_tdt_adapt_pars()
        assert result["TdtDateTime"]["Year"] == 2026
        assert result["TdtAdaptMode"] == SPRC.TDT_ADAPT_USE_SPECIFIED

    def test_get_sfn_status(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcSfnStatus, SPRC

        mock_sprc.get_sfn_status.return_value = SpRcSfnStatus(
            GpsStatus=SPRC.GPS_STATUS_10MHZ_1PPS_SYNC, GpsTime=500_000_000,
            SfnMode=SPRC.SFN_MODE_1_PPS, SfnStatus=SPRC.SFN_STATUS_IN_SYNC)
        self._connect(client)
        assert client.get_sfn_status()["SfnStatus"] == SPRC.SFN_STATUS_IN_SYNC


class TestServerComplexGetterTools:
    @pytest.mark.parametrize("tool_name,method", [
        ("get_channel_modelling_pars", "get_channel_modelling_pars"),
        ("get_dvb_t2_group", "get_dvb_t2_group"),
        ("get_dvb_t2_pars", "get_dvb_t2_pars"),
        ("get_isdb_t_pars", "get_isdb_t_pars"),
        ("get_tdt_adapt_pars", "get_tdt_adapt_pars"),
        ("get_tsg_pars", "get_tsg_pars"),
        ("get_sfn_status", "get_sfn_status"),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_complex_getter_tool_returns_client_result(self, mock_get_client, tool_name, method):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        assert tool() == getattr(mock_client, method).return_value


class TestClientFileSettings:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_open_channel_modelling_file(self, client, mock_sprc):
        self._connect(client)
        client.open_channel_modelling_file("C:\\cm\\model.chmx")
        mock_sprc.open_channel_modelling_file.assert_called_once_with("C:\\cm\\model.chmx")

    def test_save_settings(self, client, mock_sprc):
        self._connect(client)
        client.save_settings("C:\\cfg\\settings.xml")
        mock_sprc.save_settings.assert_called_once_with("C:\\cfg\\settings.xml")

    def test_normalise(self, client, mock_sprc):
        self._connect(client)
        client.normalise()
        mock_sprc.normalise.assert_called_once()


class TestServerFileSettingsTools:
    @pytest.mark.parametrize("tool_name,method,extra_kwargs", [
        ("open_channel_modelling_file", "open_channel_modelling_file", {"filepath": "C:\\cm\\model.chmx"}),
        ("save_channel_modelling_settings", "save_channel_modelling_settings", {"filepath": "C:\\cm\\model.chmx"}),
        ("save_settings", "save_settings", {"filepath": "C:\\cfg\\settings.xml"}),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_file_tool_returns_ok(self, mock_get_client, tool_name, method, extra_kwargs):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        result = tool(**extra_kwargs)
        assert result["status"] == "ok"
        getattr(mock_client, method).assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_normalise_tool(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import normalise
        assert normalise() == {"status": "ok"}
        mock_client.normalise.assert_called_once()


class TestClientScalarSetters:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_set_loop_flags(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_loop_flags(SPRC.LOOP_CC | SPRC.LOOP_PCR | SPRC.LOOP_WRAP)
        mock_sprc.set_loop_flags.assert_called_once_with(SPRC.LOOP_CC | SPRC.LOOP_PCR | SPRC.LOOP_WRAP)

    def test_set_remux(self, client, mock_sprc):
        self._connect(client)
        client.set_remux(True)
        mock_sprc.set_remux.assert_called_once_with(True)

    def test_set_sfn_mode(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_sfn_mode(SPRC.SFN_MODE_1_PPS)
        mock_sprc.set_sfn_mode.assert_called_once_with(SPRC.SFN_MODE_1_PPS)

    def test_set_sub_loop_pars(self, client, mock_sprc):
        self._connect(client)
        client.set_sub_loop_pars(use_subloop=True, loop_begin_rel=0.25, loop_end_rel=0.75)
        call_args = mock_sprc.set_sub_loop_pars.call_args[0][0]
        assert call_args.UseSubLoop is True
        assert call_args.LoopBeginRel == 0.25
        assert call_args.LoopEndRel == 0.75

    def test_select_dta_plus(self, client, mock_sprc):
        self._connect(client)
        client.select_dta_plus(True, 217400002)
        mock_sprc.select_dta_plus.assert_called_once_with(True, 217400002)


class TestServerScalarSetterTools:
    @pytest.mark.parametrize("tool_name,kwargs,expected_args", [
        ("set_loop_flags", {"flags": 3}, (3,)),
        ("set_iq_gain", {"gain": 150}, (150,)),
        ("set_remux", {"enabled": True}, (True,)),
        ("set_signal_source", {"source": 1}, (1,)),
        ("set_use_nit", {"use_nit": True}, (True,)),
        ("set_sfn_mode", {"sfn_mode": 1}, (1,)),
        ("set_sub_loop_pars", {"use_subloop": True, "loop_begin_rel": 0.25, "loop_end_rel": 0.75},
         (True, 0.25, 0.75)),
        ("select_dta_plus", {"use_dta_plus": True, "serial": 217400002}, (True, 217400002)),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_setter_tool_returns_ok(self, mock_get_client, tool_name, kwargs, expected_args):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        result = tool(**kwargs)
        assert result["status"] == "ok"
        # T1: 参数必须完整透传给 client，防止载荷静默丢失/互换
        getattr(mock_client, tool_name).assert_called_once_with(*expected_args)


class TestClientStructSetters:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_set_cmmb_pars(self, client, mock_sprc):
        self._connect(client)
        client.set_cmmb_pars({"Bandwidth": 0, "AreaId": 3, "TxId": 200})
        call_args = mock_sprc.set_cmmb_pars.call_args[0][0]
        assert call_args.Bandwidth == 0
        assert call_args.AreaId == 3
        assert call_args.TxId == 200

    def test_set_hw_noise_pars(self, client, mock_sprc):
        self._connect(client)
        client.set_hw_noise_pars({"SnrOn": True, "Snr": 25.0})
        call_args = mock_sprc.set_hw_noise_pars.call_args[0][0]
        assert call_args.SnrOn is True
        assert call_args.Snr == 25.0

    def test_set_tsg_pars(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_tsg_pars({"Type": SPRC.TSG_TYPE_PRBS15, "Pid": 100, "VidStd": 0})
        call_args = mock_sprc.set_tsg_pars.call_args[0][0]
        assert call_args.Type == SPRC.TSG_TYPE_PRBS15
        assert call_args.Pid == 100

    def test_set_dvb_t2_group(self, client, mock_sprc):
        self._connect(client)
        client.set_dvb_t2_group({"GroupName": "VV1xx", "GroupRefName": "VV100"})
        call_args = mock_sprc.set_dvb_t2_group.call_args[0][0]
        assert call_args.GroupName == "VV1xx"
        assert call_args.GroupRefName == "VV100"


class TestServerStructSetterTools:
    @pytest.mark.parametrize("tool_name,kwargs,expected_pars", [
        ("set_cmmb_pars", {"bandwidth": 0, "area_id": 3, "tx_id": 200},
         {"Bandwidth": 0, "AreaId": 3, "TxId": 200}),
        ("set_hw_noise_pars", {"snr_on": True, "snr": 25.0},
         {"SnrOn": True, "Snr": 25.0}),
        ("set_spi_pars", {"remux": False, "playout_rate": 0},
         {"Remux": False, "PlayoutRate": 0, "TxMode": DTAPI.TXMODE_188, "Power": False}),
        ("set_tsg_pars", {"type": 1, "pid": 100, "vid_std": 0},
         {"Type": 1, "Pid": 100, "VidStd": 0, "Flags": 0}),
        ("set_dvb_t2_group", {"group_name": "VV1xx", "group_ref_name": "VV100"},
         {"GroupName": "VV1xx", "GroupRefName": "VV100"}),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_struct_setter_tool_returns_ok(self, mock_get_client, tool_name, kwargs, expected_pars):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        assert tool(**kwargs) == {"status": "ok"}
        # 扁平参数被正确组装成 client 期望的 CamelCase dict
        method = getattr(mock_client, tool_name)
        method.assert_called_once_with(expected_pars)


class TestClientComplexSetters:
    def _connect(self, client):
        client.connect("http://localhost", 5000)

    def test_set_mod_pars(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import DTAPI

        self._connect(client)
        client.set_mod_pars({"ModType": DTAPI.MOD_DVBS2, "ParXtra0": 0, "ParXtra1": 0, "ParXtra2": 0, "SymRate": 27_500_000})
        call_args = mock_sprc.set_mod_pars.call_args[0][0]
        assert call_args.ModType == DTAPI.MOD_DVBS2
        assert call_args.SymRate == 27_500_000

    def test_set_channel_modelling_pars_with_paths(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_channel_modelling_pars({
            "CmEnable": True, "AwgnEnable": True, "Snr": 20.0, "PathsEnable": True,
            "Paths": [{"Type": SPRC.CONSTANT_DELAY, "Attenuation": -10.0,
                       "Delay": 1.5, "Phase": 90.0, "Doppler": 0.0}],
        })
        call_args = mock_sprc.set_channel_modelling_pars.call_args[0][0]
        assert call_args.CmEnable is True
        assert call_args.Paths[0].Delay == 1.5

    def test_set_tdt_adapt_pars_nested_datetime(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_tdt_adapt_pars({
            "TdtAdaptMode": SPRC.TDT_ADAPT_USE_SPECIFIED,
            "TdtDateTime": {"Year": 2026, "Month": 8, "Day": 8, "Hour": 12, "Minute": 0, "Second": 0},
        })
        call_args = mock_sprc.set_tdt_adapt_pars.call_args[0][0]
        assert call_args.TdtAdaptMode == SPRC.TDT_ADAPT_USE_SPECIFIED
        assert call_args.TdtDateTime.Year == 2026

    def test_set_playout_state_sfn(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        self._connect(client)
        client.set_playout_state_sfn(SPRC.STATE_PLAY, 500_000_000)
        call_args = mock_sprc.set_playout_state_sfn.call_args[0][0]
        assert call_args.PlayoutState == SPRC.STATE_PLAY
        assert call_args.SfnStartTime == 500_000_000

    def test_set_isdb_t_pars(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import DTAPI

        self._connect(client)
        client.set_isdb_t_pars({
            "DoMux": True, "BType": 0, "Mode": 3, "Guard": 2, "PartialRx": 0,
            "Emergency": 0, "IipPid": 0,
            "LayerPars": [{"NumSegments": 13, "Modulation": DTAPI.ISDBT_MOD_QAM64,
                           "CodeRate": 0, "TimeInterleave": 0}],
            "Pid2Layer": {100: 1}, "LayerOther": 0, "ParXtra0": 0,
        })
        call_args = mock_sprc.set_isdb_t_pars.call_args[0][0]
        assert call_args.Pid2Layer == {100: 1}
        assert call_args.LayerPars[0].NumSegments == 13

    def test_set_isdb_t_pars_string_pid_keys(self, client, mock_sprc):
        """MCP JSON 透传后 Pid2Layer 键是 str，必须转回 int 才能进 xsd:int 字段。"""
        self._connect(client)
        client.set_isdb_t_pars({
            "DoMux": True, "BType": 0, "Mode": 3, "Guard": 2, "PartialRx": 0,
            "Emergency": 0, "IipPid": 0,
            "LayerPars": [], "Pid2Layer": {"100": 1}, "LayerOther": 0, "ParXtra0": 0,
        })
        call_args = mock_sprc.set_isdb_t_pars.call_args[0][0]
        assert call_args.Pid2Layer == {100: 1}

    def test_set_isdb_t_pars_missing_pid2layer(self, client, mock_sprc):
        """Pid2Layer 缺失或为 None 时应回退为空 dict，而不是崩溃。"""
        self._connect(client)
        client.set_isdb_t_pars({
            "DoMux": True, "BType": 0, "Mode": 3, "Guard": 2, "PartialRx": 0,
            "Emergency": 0, "IipPid": 0,
            "LayerPars": [], "Pid2Layer": None, "LayerOther": 0, "ParXtra0": 0,
        })
        call_args = mock_sprc.set_isdb_t_pars.call_args[0][0]
        assert call_args.Pid2Layer == {}

    def test_set_dvb_t2_pars(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC, DTAPI

        self._connect(client)
        client.set_dvb_t2_pars({
            "T2Version": 1, "Bandwidth": DTAPI.DVBT2_8MHZ, "FftMode": DTAPI.DVBT2_FFT_8K,
            "Miso": DTAPI.DVBT2_MISO_OFF, "GuardInterval": DTAPI.DVBT2_GI_1_32,
            "Papr": DTAPI.DVBT2_PAPR_NONE, "BwtExt": 0, "PilotPattern": 4,
            "NumT2Frames": 2, "NumDataSyms": 60, "L1Modulation": 1,
            "FefEnable": False, "FefType": 0, "FefLength": 0, "FefS1": 2, "FefS2": 1,
            "FefInterval": 1, "FefSignal": 0, "CellId": 0, "NetworkId": 0,
            "T2SystemId": 0, "Frequency": 500_000_000,
            "Hem": False, "Npd": False, "IssyEnabled": False, "Id": 0, "GroupId": 0,
            "Type": 0, "CodeRate": DTAPI.DVBT2_COD_3_4, "Modulation": 2,
            "Rotation": False, "FecType": 0, "TimeIlLength": 0, "TimeIlType": 0,
            "InBandFlag": False, "NumBlocks": 0,
            "FollowMode": SPRC.T2_FOLLOW_OFF,
        })
        call_args = mock_sprc.set_dvb_t2_pars.call_args[0][0]
        assert call_args.Bandwidth == DTAPI.DVBT2_8MHZ
        assert call_args.Frequency == 500_000_000


class TestServerComplexSetterTools:
    @pytest.mark.parametrize("tool_name,arg_name,arg_value", [
        ("set_mod_pars", "mod_pars", {"ModType": 6, "ParXtra0": 0, "ParXtra1": 0, "ParXtra2": 0, "SymRate": 27_500_000}),
        ("set_channel_modelling_pars", "cm_pars", {"CmEnable": True, "AwgnEnable": True, "Snr": 20.0, "PathsEnable": False, "Paths": []}),
        ("set_dvb_t2_pars", "dvb_t2_pars", {"Bandwidth": 4, "FftMode": 3, "GuardInterval": 1, "NumT2Frames": 2, "NumDataSyms": 60, "L1Modulation": 1, "Frequency": 500_000_000, "FollowMode": 0}),
        ("set_isdb_t_pars", "isdb_t_pars", {"DoMux": True, "BType": 0, "Mode": 3, "Guard": 2, "PartialRx": 0, "Emergency": 0, "IipPid": 0, "LayerPars": [], "Pid2Layer": {}, "LayerOther": 0, "ParXtra0": 0}),
        ("set_tdt_adapt_pars", "tdt_adapt_pars", {"TdtAdaptMode": 2, "TdtDateTime": {"Year": 2026, "Month": 8, "Day": 8, "Hour": 12, "Minute": 0, "Second": 0}}),
    ])
    @patch("streamxpress_mcp.server.get_client")
    def test_complex_setter_tool_returns_ok(self, mock_get_client, tool_name, arg_name, arg_value):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp import server as server_mod
        tool = getattr(server_mod, tool_name)
        assert tool(**{arg_name: arg_value}) == {"status": "ok"}
        # T1: 载荷必须完整转发给 client，防止静默丢弃
        getattr(mock_client, tool_name).assert_called_once_with(arg_value)

    @patch("streamxpress_mcp.server.get_client")
    def test_set_playout_state_sfn_tool(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_playout_state_sfn
        assert set_playout_state_sfn(playout_state=1, sfn_start_time=500_000_000) == {
            "status": "ok", "playout_state": 1, "sfn_start_time": 500_000_000}
        mock_client.set_playout_state_sfn.assert_called_once_with(1, 500_000_000)


class TestWaitForCondition:
    def test_client_wait_for_condition(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        client.connect("http://localhost", 5000)
        client.wait_for_condition(SPRC.COND_STOPPED, 10_000)
        mock_sprc.wait_for_condition.assert_called_once_with(SPRC.COND_STOPPED, 10_000)

    @patch("streamxpress_mcp.server.get_client")
    def test_tool_wait_for_condition(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import wait_for_condition
        result = wait_for_condition(condition=1, timeout_ms=-1)
        assert result == {"status": "ok", "condition": 1}
        mock_client.wait_for_condition.assert_called_once_with(1, -1)


class TestEnhancedParams:
    def test_set_tsoip_params_failover(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        client.set_tsoip_params(
            dest_ip="239.1.1.1", dest_port=1234, failover=True,
            dest_ip2="239.1.1.2", dest_port2=1235, diff_serv=46)
        call_args = mock_sprc.set_tsiop_pars.call_args[0][0]
        assert call_args.EnaFailover is True
        assert call_args.Ip2 == bytes([239, 1, 1, 2])
        assert call_args.Port2 == 1235
        assert call_args.DiffServ == 46

    def test_set_asi_params_burst_polarity(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        client.set_asi_params(
            burst_mode=True, polarity=DTAPI.TXPOL_INVERTED, tx_mode=DTAPI.TXMODE_204)
        call_args = mock_sprc.set_asi_pars.call_args[0][0]
        assert call_args.BurstMode is True
        assert call_args.Polarity == DTAPI.TXPOL_INVERTED
        assert call_args.TxMode == DTAPI.TXMODE_204  # R3: 构造出的结构体上钉住 TxMode

    def test_get_status_extra_fields(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcPlayoutStatus, SpRcPlayoutInfo

        mock_sprc.get_playout_status.return_value = SpRcPlayoutStatus(
            PosRel=0.5, NumWraps=0, FifoLoad=42, NumErrors=1, TotalMemLoad=1024)
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, Filename="test.ts", TsRate=25_000_000, PlayoutRate=25_000_000,
            BurstMode=False, ExtClock=False, FileCanBeRead=True,
            FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=0, FileSize=1024, FileType=0,
            LoopBeginRel=0.0, LoopEndRel=0.0, LoopFlags=3,
            Remux=False, SymRate=27_500_000,
            TimeLoopBegin=0, TimeLoopEnd=0, TimeOffset=0,
            TpSize=188, TxPolarity=0)

        client.connect("http://localhost", 5000)
        status = client.get_status()
        assert status["fifo_load"] == 42
        assert status["num_errors"] == 1
        assert status["playout_rate"] == 25_000_000
        assert status["sym_rate"] == 27_500_000
        assert status["loop_flags"] == 3
        assert status["file_size"] == 1024
        assert status["tp_size"] == 188

    def test_set_tsoip_params_rejects_invalid_protocol(self, client, mock_sprc):
        client.connect("http://localhost", 5000)
        with pytest.raises(ValueError, match="invalid protocol"):
            client.set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="UPD")

    def test_set_tsoip_params_lowercase_protocol(self, client, mock_sprc):
        """R5.1: protocol 大小写不敏感（.upper() 归一化）。"""
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        client.set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="udp")
        call_args = mock_sprc.set_tsiop_pars.call_args[0][0]
        assert call_args.Protocol == DTAPI.PROTO_UDP

    def test_set_tsoip_params_fec_and_rtp_and_txmode(self, client, mock_sprc):
        """T2: RTP 分支、FEC 推导、TxMode 传递。"""
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        client.set_tsoip_params(
            dest_ip="239.1.1.1", dest_port=1234, protocol="RTP",
            fec_rows=5, fec_cols=4, tx_mode=DTAPI.TXMODE_204)
        call_args = mock_sprc.set_tsiop_pars.call_args[0][0]
        assert call_args.Protocol == DTAPI.PROTO_RTP
        assert call_args.FecMode == DTAPI.FEC_2D
        assert call_args.FecNumRows == 5
        assert call_args.FecNumCols == 4
        assert call_args.TxMode == DTAPI.TXMODE_204

    def test_set_tsoip_params_partial_fec_disables(self, client, mock_sprc):
        """R2: rows 或 cols 任一为 0 必须禁用 FEC（守卫是 or 不是 and）。"""
        from streamxpress_mcp.sprc_import import DTAPI

        client.connect("http://localhost", 5000)
        for rows, cols in [(4, 0), (0, 4), (0, 0)]:
            mock_sprc.set_tsiop_pars.reset_mock()
            client.set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234,
                                    fec_rows=rows, fec_cols=cols)
            pars = mock_sprc.set_tsiop_pars.call_args[0][0]
            assert pars.FecMode == DTAPI.FEC_DISABLE, f"rows={rows} cols={cols}"

    def test_set_tsoip_params_ttl_and_num_tp(self, client, mock_sprc):
        """R2: ttl / num_tp_per_ip 必须落在正确的结构体字段（防字段互换）。"""
        client.connect("http://localhost", 5000)
        # 用非默认值 7/3，避免与默认 64/7 重合成为等价变异体
        client.set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234,
                                ttl=7, num_tp_per_ip=3)
        pars = mock_sprc.set_tsiop_pars.call_args[0][0]
        assert pars.TimeToLive == 7
        assert pars.NumTpPerIp == 3

    @patch("streamxpress_mcp.server.get_client")
    def test_set_tsoip_params_tool_passes_optional_fields(self, mock_get_client):
        """T3: 工具层不得静默丢弃 protocol/dest_ip2/diff_serv/tx_mode/fec。"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_tsoip_params
        set_tsoip_params(
            dest_ip="239.1.1.1", dest_port=1234, protocol="RTP",
            num_tp_per_ip=3, ttl=7,
            failover=True, dest_ip2="239.1.1.2", dest_port2=1235, diff_serv=46,
            tx_mode=DTAPI.TXMODE_204, fec_rows=5, fec_cols=4)
        mock_client.set_tsoip_params.assert_called_once_with(
            dest_ip="239.1.1.1", dest_port=1234, num_tp_per_ip=3, protocol="RTP",
            ttl=7, fec_rows=5, fec_cols=4, tx_mode=DTAPI.TXMODE_204,
            failover=True, dest_ip2="239.1.1.2", dest_port2=1235, diff_serv=46)

    @patch("streamxpress_mcp.server.get_client")
    def test_set_asi_params_tool_passes_optional_fields(self, mock_get_client):
        """T3: 工具层不得静默丢弃 burst_mode/polarity。"""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        from streamxpress_mcp.server import set_asi_params
        set_asi_params(remux=True, playout_rate=20_000_000, tx_mode=DTAPI.TXMODE_204,
                       burst_mode=True, polarity=DTAPI.TXPOL_INVERTED)
        mock_client.set_asi_params.assert_called_once_with(
            remux=True, playout_rate=20_000_000, tx_mode=DTAPI.TXMODE_204,
            burst_mode=True, polarity=DTAPI.TXPOL_INVERTED)

    def test_set_channel_modelling_pars_paths_none(self, client, mock_sprc):
        """JSON null 表达"无路径"时应回退为空列表而非崩溃。"""
        client.connect("http://localhost", 5000)
        client.set_channel_modelling_pars({
            "CmEnable": True, "AwgnEnable": True, "Snr": 20.0, "PathsEnable": False,
            "Paths": None,
        })
        call_args = mock_sprc.set_channel_modelling_pars.call_args[0][0]
        assert call_args.Paths == []

    def test_set_isdb_t_pars_duplicate_pid_keys(self, client, mock_sprc):
        """Pid2Layer 中同一 PID 重复出现应报错而非静默覆盖。"""
        client.connect("http://localhost", 5000)
        with pytest.raises(ValueError, match="duplicate PID"):
            client.set_isdb_t_pars({
                "DoMux": True, "BType": 0, "Mode": 3, "Guard": 2, "PartialRx": 0,
                "Emergency": 0, "IipPid": 0,
                "LayerPars": [], "Pid2Layer": {"100": 1, 100: 2},
                "LayerOther": 0, "ParXtra0": 0,
            })


class TestErrorBoundary:
    """Wrapper 错误转换边界：SpRcException 可诊断化、传输故障断连、disconnect 暴露失败。"""

    def test_sprc_exception_becomes_diagnosable_runtime_error(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcException, SPRC_RESULT

        mock_sprc.scan_ports.side_effect = SpRcException(SPRC_RESULT.E_NO_LICK)
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="E_NO_LICK") as exc_info:
            client.scan_ports()
        # F2: str(e) 为空时兜底 "no detail"，尾部不留空白
        assert str(exc_info.value).endswith("no detail")
        # R5.2: 错误码数值也被钉住（E_NO_LICK = 0x2000 + 11 = 8203）
        assert "(8203)" in str(exc_info.value)

    def test_long_call_does_not_block_other_calls(self, client, mock_sprc):
        """长阻塞调用不得串行化其他工具调用（锁不能覆盖在途 SOAP 调用）。"""
        import threading
        import time

        started = threading.Event()

        def slow(cond, timeout):
            started.set()
            time.sleep(1.5)  # R5.3: 放宽慢调用时长，避免 CI 负载下 flake

        mock_sprc.wait_for_condition.side_effect = slow
        client.connect("http://localhost", 5000)

        t = threading.Thread(target=lambda: client.wait_for_condition(1, -1), daemon=True)
        t.start()
        assert started.wait(timeout=1.0)

        done = threading.Event()
        threading.Thread(
            target=lambda: (client.scan_ports(), done.set()), daemon=True
        ).start()
        # 在慢调用仍在进行时就应完成
        assert done.wait(timeout=0.3), "scan_ports 被 wait_for_condition 阻塞了"
        t.join()

    def test_stale_failure_does_not_kill_new_session(self):
        """R1: 迟到的传输失败不得把重连后的新会话误标为断开。"""
        from streamxpress_mcp.client import StreamXpressClient

        old, new = MagicMock(), MagicMock()
        factory = MagicMock(side_effect=[old, new])
        client = StreamXpressClient(sprc_factory=factory)

        client.connect("http://localhost", 5000)
        sprc_old = client._sprc
        client.disconnect()
        client.connect("http://localhost", 5000)
        assert client._sprc is new and client._connected is True

        # 迟到的失败（针对已被替换的 old 会话）不得误杀新会话
        client._mark_stale(sprc_old)
        assert client._connected is True, "健康的新会话被迟到的失败误杀了"

        # 对照：当前会话本身失败时仍要标记失效
        client._mark_stale(new)
        assert client._connected is False

    def test_transport_error_marks_session_stale(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcException, SPRC_RESULT

        mock_sprc.get_playout_status.side_effect = SpRcException(SPRC_RESULT.E_COMMUNICATION)
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="E_COMMUNICATION"):
            client.get_status()
        assert client._connected is False
        with pytest.raises(RuntimeError, match="not connected"):
            client.scan_ports()

    def test_oserror_marks_session_stale(self, client, mock_sprc):
        mock_sprc.get_playout_status.side_effect = OSError("network unreachable")
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="network unreachable"):
            client.get_status()
        assert client._connected is False

    def test_disconnect_reports_cleanup_failure(self, client, mock_sprc):
        mock_sprc.cleanup.side_effect = OSError("connection reset")
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="failed to close"):
            client.disconnect()
        # 本地状态仍被无条件重置
        assert client._connected is False
        assert client._sprc is None

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


class TestJsonBoundary:
    """Getter 输出必须能通过严格 JSON 序列化（allow_nan=False）。"""

    def test_jsonable_rejects_nan(self):
        from streamxpress_mcp.client import _jsonable

        with pytest.raises(ValueError, match="non-finite"):
            _jsonable(float("nan"))

    def test_jsonable_rejects_inf(self):
        from streamxpress_mcp.client import _jsonable

        with pytest.raises(ValueError, match="non-finite"):
            _jsonable(float("inf"))

    def test_getter_outputs_pass_strict_json(self, client, mock_sprc):
        import json

        from streamxpress_mcp.sprc_import import SpRcRfPars, SpRcSfnStatus, SpRcCmPars

        mock_sprc.get_rf_pars.return_value = SpRcRfPars(Frequency=500_000_000, Level=-37.5)
        mock_sprc.get_sfn_status.return_value = SpRcSfnStatus(
            GpsStatus=0, GpsTime=500_000_000, SfnMode=0, SfnStatus=1)
        mock_sprc.get_channel_modelling_pars.return_value = SpRcCmPars(
            CmEnable=True, AwgnEnable=True, Snr=20.0, PathsEnable=False, Paths=[])
        client.connect("http://localhost", 5000)
        for result in (client.get_rf_pars(), client.get_sfn_status(),
                       client.get_channel_modelling_pars()):
            json.dumps(result, allow_nan=False)  # 不应抛 ValueError

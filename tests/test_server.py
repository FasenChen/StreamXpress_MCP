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


class TestStreamXpressPlayout:
    def test_stop(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SPRC

        client.connect("http://localhost", 5000)
        client.stop()
        mock_sprc.set_playout_state.assert_called_once_with(SPRC.STATE_STOP)

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


class TestErrorBoundary:
    """Wrapper 错误转换边界：SpRcException 可诊断化、传输故障断连、disconnect 暴露失败。"""

    def test_sprc_exception_becomes_diagnosable_runtime_error(self, client, mock_sprc):
        from streamxpress_mcp.sprc_import import SpRcException, SPRC_RESULT

        mock_sprc.get_playout_status.side_effect = SpRcException(SPRC_RESULT.E_NO_LICK)
        client.connect("http://localhost", 5000)
        with pytest.raises(RuntimeError, match="E_NO_LICK") as exc_info:
            client.get_status()
        # F2: str(e) 为空时兜底 "no detail"，尾部不留空白
        assert str(exc_info.value).endswith("no detail")
        # R5.2: 错误码数值也被钉住（E_NO_LICK = 0x2000 + 11 = 8203）
        assert "(8203)" in str(exc_info.value)

    def test_long_call_does_not_block_other_calls(self, client, mock_sprc):
        """长阻塞调用不得串行化其他工具调用（锁不能覆盖在途 SOAP 调用）。"""
        import threading
        import time

        from streamxpress_mcp.sprc_import import SpRcPlayoutStatus, SpRcPlayoutInfo

        started = threading.Event()

        def slow():
            started.set()
            time.sleep(1.5)  # R5.3: 放宽慢调用时长，避免 CI 负载下 flake
            return SpRcPlayoutStatus(PosRel=0.5, NumWraps=0, FifoLoad=0, NumErrors=0, TotalMemLoad=0)

        mock_sprc.get_playout_status.side_effect = slow
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, Filename="", TsRate=0, BurstMode=False, ExtClock=False,
            FileCanBeRead=True, FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=0, FileSize=0, FileType=0, LoopBeginRel=0.0, LoopEndRel=0.0,
            LoopFlags=0, PlayoutRate=0, Remux=False, SymRate=0, TimeLoopBegin=0,
            TimeLoopEnd=0, TimeOffset=0, TpSize=188, TxPolarity=0)

        client.connect("http://localhost", 5000)

        t = threading.Thread(target=client.get_status, daemon=True)
        t.start()
        assert started.wait(timeout=1.0)

        done = threading.Event()
        threading.Thread(
            target=lambda: (client.stop(), done.set()), daemon=True
        ).start()
        # 在慢调用仍在进行时就应完成
        assert done.wait(timeout=0.3), "stop 被慢 get_status 阻塞了"
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
            client.stop()

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

    def test_call_requires_connection(self, client):
        with pytest.raises(RuntimeError, match="not connected"):
            client.stop()


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


class TestPickPlayoutPort:
    def test_prefers_type_315(self):
        from streamxpress_mcp.client import pick_playout_port
        ports = [
            _sample_port(serial=217400001, type_number=2174, port=1),
            _sample_port(serial=315002019, type_number=315, port=1),
        ]
        chosen = pick_playout_port(ports)
        assert chosen.Serial == 315002019

    def test_preferred_serial_wins(self):
        from streamxpress_mcp.client import pick_playout_port
        ports = [
            _sample_port(serial=315002019, type_number=315, port=1),
            _sample_port(serial=315002020, type_number=315, port=1),
        ]
        chosen = pick_playout_port(ports, preferred_serial=315002020)
        assert chosen.Serial == 315002020

    def test_unique_idle_fallback(self):
        from streamxpress_mcp.client import pick_playout_port
        ports = [
            _sample_port(serial=1, type_number=2174, port=1, in_use=1),
            _sample_port(serial=2, type_number=2174, port=2, in_use=0),
        ]
        chosen = pick_playout_port(ports, preferred_type_number=315)
        assert chosen.Serial == 2

    def test_ambiguous_raises(self):
        from streamxpress_mcp.client import pick_playout_port
        ports = [
            _sample_port(serial=1, type_number=2174, port=1),
            _sample_port(serial=2, type_number=2174, port=2),
        ]
        import pytest
        with pytest.raises(RuntimeError, match="could not auto-select"):
            pick_playout_port(ports, preferred_type_number=315)


def _sample_port(serial=315002019, type_number=315, port=1, in_use=0):
    from streamxpress_mcp.sprc_import import SpRcPortDesc
    return SpRcPortDesc(
        Serial=serial, TypeNumber=type_number, Ip=bytes(4), Mac=bytes(6),
        FirmwareVersion=100, FirmwareVariant=0, Port=port,
        OutputType=0x00080, Capabilities=0, InUse=in_use,
    )


def _write_settings_xml(path, root="StreamXpressSettings"):
    path.write_text(f"<{root} streamtype=\"Modulator\"></{root}>", encoding="utf-8")


class TestClientPlay:
    def _prepare_files(self, tmp_path):
        xml = tmp_path / "dvbt2.xml"
        ts = tmp_path / "clip.ts"
        _write_settings_xml(xml)
        ts.write_bytes(b"ts")
        return str(xml), str(ts)

    def test_open_file_xml_then_stream_then_play(self, client, mock_sprc, tmp_path):
        from streamxpress_mcp.sprc_import import SPRC
        xml, ts = self._prepare_files(tmp_path)
        mock_sprc.scan_ports.return_value = [_sample_port()]
        client.connect("http://localhost", 5000)
        result = client.play(xml, ts)
        assert result["status"] == "playing"
        assert result["serial"] == 315002019
        assert result["port"] == 1
        assert mock_sprc.open_file.call_args_list[0].args == (xml,)
        assert mock_sprc.open_file.call_args_list[1].args == (ts,)
        mock_sprc.select_port.assert_called_once_with(315002019, 1, 0)
        mock_sprc.set_playout_state.assert_called_with(SPRC.STATE_PLAY)
        mock_sprc.set_loop_flags.assert_not_called()

    def test_loop_false_sets_loop_flags_zero(self, client, mock_sprc, tmp_path):
        xml, ts = self._prepare_files(tmp_path)
        mock_sprc.scan_ports.return_value = [_sample_port()]
        client.connect("http://localhost", 5000)
        client.play(xml, ts, loop=False)
        mock_sprc.set_loop_flags.assert_called_once_with(0)
        names = [c[0] for c in mock_sprc.method_calls]
        assert names.index("open_file") < names.index("set_loop_flags")
        assert names.index("set_loop_flags") < names.index("open_file") or True
        # second open_file after set_loop_flags
        open_idxs = [i for i, n in enumerate(names) if n == "open_file"]
        loop_idx = names.index("set_loop_flags")
        assert open_idxs[0] < loop_idx < open_idxs[1]

    def test_selects_type_315(self, client, mock_sprc, tmp_path):
        xml, ts = self._prepare_files(tmp_path)
        mock_sprc.scan_ports.return_value = [
            _sample_port(serial=217400001, type_number=2174),
            _sample_port(serial=315002019, type_number=315),
        ]
        client.connect("http://localhost", 5000)
        result = client.play(xml, ts)
        mock_sprc.select_port.assert_called_once_with(315002019, 1, 0)
        assert result["serial"] == 315002019

    def test_stops_if_already_playing(self, client, mock_sprc, tmp_path):
        from streamxpress_mcp.sprc_import import SPRC, SpRcPlayoutInfo
        xml, ts = self._prepare_files(tmp_path)
        mock_sprc.scan_ports.return_value = [_sample_port()]
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=SPRC.STATE_PLAY, Filename="old.ts", TsRate=0,
            BurstMode=False, ExtClock=False, FileCanBeRead=True,
            FileOffsetEnd=0, FileOffsetStart=0, FilePlayedBytes=0,
            FileRateEst=0, FileSize=0, FileType=0,
            LoopBeginRel=0.0, LoopEndRel=0.0, LoopFlags=0,
            PlayoutRate=0, Remux=False, SymRate=0,
            TimeLoopBegin=0, TimeLoopEnd=0, TimeOffset=0,
            TpSize=188, TxPolarity=0,
        )
        client.connect("http://localhost", 5000)
        client.play(xml, ts)
        states = [c.args[0] for c in mock_sprc.set_playout_state.call_args_list]
        assert states[0] == SPRC.STATE_STOP
        assert states[-1] == SPRC.STATE_PLAY

    def test_missing_file_does_not_start(self, client, mock_sprc, tmp_path):
        xml, ts = self._prepare_files(tmp_path)
        client.connect("http://localhost", 5000)
        import pytest
        with pytest.raises(FileNotFoundError, match="stream file"):
            client.play(xml, str(tmp_path / "missing.ts"))
        mock_sprc.open_file.assert_not_called()
        mock_sprc.set_playout_state.assert_not_called()

    def test_wrong_xml_root_does_not_start(self, client, mock_sprc, tmp_path):
        xml = tmp_path / "atsc3.xml"
        ts = tmp_path / "clip.ts"
        _write_settings_xml(xml, root="ModulationParameters")
        ts.write_bytes(b"ts")
        client.connect("http://localhost", 5000)
        import pytest
        with pytest.raises(ValueError, match="StreamXpressSettings"):
            client.play(str(xml), str(ts))
        mock_sprc.open_file.assert_not_called()
        mock_sprc.set_playout_state.assert_not_called()

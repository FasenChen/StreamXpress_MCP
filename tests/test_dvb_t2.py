"""Tests for the everyday DVB-T2 configure preset."""

import pytest
from unittest.mock import MagicMock, patch

from streamxpress_mcp.dvb_t2 import (
    parse_cell_id,
    parse_dvbt2_bandwidth,
    parse_dvbt2_constellation,
    parse_dvbt2_fft_mode,
    parse_dvbt2_guard_interval,
    parse_frequency_hz,
)
from streamxpress_mcp.sprc_import import DTAPI, SPRC, SpRcDvbT2Pars, SpRcRfPars


def _sample_t2(**overrides) -> SpRcDvbT2Pars:
    kwargs = dict(
        T2Version=0,
        Bandwidth=DTAPI.DVBT2_6MHZ,
        FftMode=DTAPI.DVBT2_FFT_8K,
        Miso=DTAPI.DVBT2_MISO_OFF,
        GuardInterval=DTAPI.DVBT2_GI_1_32,
        Papr=DTAPI.DVBT2_PAPR_NONE,
        BwtExt=0,
        PilotPattern=4,
        NumT2Frames=2,
        NumDataSyms=59,
        L1Modulation=3,
        FefEnable=False,
        FefType=0,
        FefLength=0,
        FefS1=2,
        FefS2=1,
        FefInterval=1,
        FefSignal=0,
        CellId=99,
        NetworkId=12421,
        T2SystemId=32769,
        Frequency=100_000_000,
        Hem=False,
        Npd=False,
        IssyEnabled=False,
        Id=7,
        GroupId=3,
        Type=0,
        CodeRate=DTAPI.DVBT2_COD_3_5,
        Modulation=DTAPI.DVBT2_QAM16,
        Rotation=True,
        FecType=1,
        TimeIlLength=3,
        TimeIlType=0,
        InBandFlag=False,
        NumBlocks=11,
        FollowMode=SPRC.T2_FOLLOW_OPT1,
    )
    kwargs.update(overrides)
    return SpRcDvbT2Pars(**kwargs)


def _sample_rf(**overrides) -> SpRcRfPars:
    kwargs = dict(
        Frequency=100_000_000,
        Level=-20.0,
        SpecInv=True,
        CW=False,
        RfEnabledOnStop=True,
    )
    kwargs.update(overrides)
    return SpRcRfPars(**kwargs)


class TestParsers:
    @pytest.mark.parametrize("value,expected", [
        ("8MHz", DTAPI.DVBT2_8MHZ),
        ("8 MHz", DTAPI.DVBT2_8MHZ),
        ("8mhz", DTAPI.DVBT2_8MHZ),
        ("8", DTAPI.DVBT2_8MHZ),
        ("DVBT2_8MHZ", DTAPI.DVBT2_8MHZ),
        (DTAPI.DVBT2_8MHZ, DTAPI.DVBT2_8MHZ),
        ("7MHz", DTAPI.DVBT2_7MHZ),
        ("1.7MHz", DTAPI.DVBT2_1_7MHZ),
        ("10MHz", DTAPI.DVBT2_10MHZ),
    ])
    def test_bandwidth_aliases(self, value, expected):
        assert parse_dvbt2_bandwidth(value) == expected

    @pytest.mark.parametrize("value,expected", [
        ("32K", DTAPI.DVBT2_FFT_32K),
        ("32k", DTAPI.DVBT2_FFT_32K),
        ("32", DTAPI.DVBT2_FFT_32K),
        ("8K", DTAPI.DVBT2_FFT_8K),
        (DTAPI.DVBT2_FFT_16K, DTAPI.DVBT2_FFT_16K),
    ])
    def test_fft_aliases(self, value, expected):
        assert parse_dvbt2_fft_mode(value) == expected

    @pytest.mark.parametrize("value,expected", [
        ("1/128", DTAPI.DVBT2_GI_1_128),
        ("1_128", DTAPI.DVBT2_GI_1_128),
        ("1:128", DTAPI.DVBT2_GI_1_128),
        ("1/32", DTAPI.DVBT2_GI_1_32),
        ("19/256", DTAPI.DVBT2_GI_19_256),
        (DTAPI.DVBT2_GI_1_4, DTAPI.DVBT2_GI_1_4),
    ])
    def test_gi_aliases(self, value, expected):
        assert parse_dvbt2_guard_interval(value) == expected

    @pytest.mark.parametrize("value,expected", [
        ("256QAM", DTAPI.DVBT2_QAM256),
        ("256 QAM", DTAPI.DVBT2_QAM256),
        ("QAM256", DTAPI.DVBT2_QAM256),
        ("256-QAM", DTAPI.DVBT2_QAM256),
        ("16QAM", DTAPI.DVBT2_QAM16),
        ("QPSK", DTAPI.DVBT2_QPSK),
        (DTAPI.DVBT2_QAM64, DTAPI.DVBT2_QAM64),
    ])
    def test_constellation_aliases(self, value, expected):
        assert parse_dvbt2_constellation(value) == expected

    def test_frequency_and_cell_id(self):
        assert parse_frequency_hz(474_000_000) == 474_000_000
        assert parse_frequency_hz(474000000.0) == 474_000_000
        assert parse_cell_id(0) == 0
        assert parse_cell_id(65535) == 65535

    @pytest.mark.parametrize("fn,value", [
        (parse_dvbt2_bandwidth, "99MHz"),
        (parse_dvbt2_bandwidth, 8),  # 8 is MHz as string, not a DTAPI constant
        (parse_dvbt2_fft_mode, "64K"),
        (parse_dvbt2_fft_mode, 32),
        (parse_dvbt2_guard_interval, "1/64"),
        (parse_dvbt2_constellation, "1024QAM"),
        (parse_frequency_hz, 0),
        (parse_frequency_hz, -1),
        (parse_frequency_hz, True),
        (parse_cell_id, -1),
        (parse_cell_id, 65536),
        (parse_cell_id, True),
    ])
    def test_invalid_values(self, fn, value):
        with pytest.raises(ValueError):
            fn(value)


class TestConfigureDvbT2Client:
    def _prepare(self, client, mock_sprc, *, use_nit=False):
        mock_sprc.get_dvb_t2_pars.return_value = _sample_t2()
        mock_sprc.get_rf_pars.return_value = _sample_rf()
        mock_sprc.get_use_nit.return_value = use_nit
        client.connect("http://localhost", 5000)

    def test_defaults_overlay_and_preserve(self, client, mock_sprc):
        self._prepare(client, mock_sprc)
        result = client.configure_dvb_t2(frequency_hz=474_000_000)

        pars = mock_sprc.set_dvb_t2_pars.call_args[0][0]
        assert pars.Bandwidth == DTAPI.DVBT2_8MHZ
        assert pars.FftMode == DTAPI.DVBT2_FFT_32K
        assert pars.GuardInterval == DTAPI.DVBT2_GI_1_128
        assert pars.Modulation == DTAPI.DVBT2_QAM256
        assert pars.CellId == 0
        assert pars.Frequency == 474_000_000
        # preserved (distinctive non-default values)
        assert pars.CodeRate == DTAPI.DVBT2_COD_3_5
        assert pars.PilotPattern == 4
        assert pars.FollowMode == SPRC.T2_FOLLOW_OPT1
        assert pars.NetworkId == 12421
        assert pars.NumBlocks == 11
        assert pars.Rotation is True
        assert pars.Id == 7

        rf = mock_sprc.set_rf_pars.call_args[0][0]
        assert rf.Frequency == 474_000_000
        assert rf.Level == -20.0
        assert rf.SpecInv is True and rf.CW is False and rf.RfEnabledOnStop is True

        mock_sprc.select_port.assert_not_called()
        mock_sprc.set_use_nit.assert_not_called()
        assert result["port_selected"] is False
        assert result["nit_disabled"] is False
        assert result["level_dbm"] == -20.0
        assert result["bandwidth"] == DTAPI.DVBT2_8MHZ

    def test_explicit_level_and_serial(self, client, mock_sprc):
        self._prepare(client, mock_sprc, use_nit=True)
        result = client.configure_dvb_t2(
            frequency_hz=490_000_000,
            bandwidth="7MHz",
            fft_mode="8K",
            guard_interval="1/32",
            constellation="64QAM",
            cell_id=42,
            level_dbm=-28.5,
            serial=315002019,
            port_num=1,
        )
        mock_sprc.select_port.assert_called_once_with(
            315002019, 1, SPRC.MOD_DVBT2)
        mock_sprc.set_use_nit.assert_called_once_with(False)
        pars = mock_sprc.set_dvb_t2_pars.call_args[0][0]
        assert pars.Bandwidth == DTAPI.DVBT2_7MHZ
        assert pars.FftMode == DTAPI.DVBT2_FFT_8K
        assert pars.GuardInterval == DTAPI.DVBT2_GI_1_32
        assert pars.Modulation == DTAPI.DVBT2_QAM64
        assert pars.CellId == 42
        rf = mock_sprc.set_rf_pars.call_args[0][0]
        assert rf.Level == -28.5
        assert rf.Frequency == 490_000_000
        assert result["port_selected"] is True
        assert result["nit_disabled"] is True
        # select_port must happen before get_dvb_t2_pars
        names = [name for name, *_ in mock_sprc.method_calls]
        assert names.index("select_port") < names.index("get_dvb_t2_pars")

    def test_invalid_bandwidth_does_not_touch_soap(self, client, mock_sprc):
        self._prepare(client, mock_sprc)
        with pytest.raises(ValueError, match="bandwidth"):
            client.configure_dvb_t2(frequency_hz=474_000_000, bandwidth="99MHz")
        mock_sprc.get_dvb_t2_pars.assert_not_called()
        mock_sprc.set_rf_pars.assert_not_called()

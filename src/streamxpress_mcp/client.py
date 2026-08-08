"""StreamXpressClient: singleton wrapper around SPRC_client for MCP server use."""

from dataclasses import asdict

from .sprc_import import SPRC_client, SpRcPortDesc, SpRcException, SPRC_RESULT
from .sprc_import import (
    SpRcAsiPars, SpRcTsoipPars, SpRcRfPars, SpRcModPars, SpRcSubLoopPars,
    SpRcCmmbPars, SpRcHwNoisePars, SpRcSpiPars, SpRcTsgPars, SpRcDvbT2Group,
    SpRcCmPars, SpRcCmPath, SpRcDvbT2Pars, SpRcIsdbtPars, SpRcIsdbtLayerPars,
    SpRcDateTime, SpRcTdtAdaptPars, SpRcPlayoutSfnPars,
)
from .sprc_import import SPRC, DTAPI


def _jsonable(value):
    """Recursively convert asdict() output to JSON-safe types (bytes → list[int])."""
    if isinstance(value, bytes):
        return list(value)
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return value


def _to_dict(obj) -> dict:
    """Convert a dataclass instance (possibly nested) to a JSON-safe dict."""
    return _jsonable(asdict(obj))


def _parse_ip(ip: str) -> bytes:
    """Parse a dotted IPv4 string into exactly 4 bytes, validating octets."""
    octets = ip.split(".")
    if len(octets) != 4:
        raise ValueError(f"invalid IPv4 address: {ip!r}")
    try:
        return bytes(int(o) for o in octets)
    except ValueError:
        raise ValueError(f"invalid IPv4 address: {ip!r}") from None


class StreamXpressClient:
    """Thin wrapper managing a single SPRC_client SOAP session.

    Args:
        sprc_factory: Optional callable → SPRC_client instance (for DI in tests).
                      Defaults to SPRC_client.
    """

    def __init__(self, sprc_factory=None):
        self._sprc_factory = sprc_factory or SPRC_client
        self._sprc: SPRC_client | None = None
        self._connected = False

    def connect(self, host: str, port: int) -> None:
        """Open a remote-control session to StreamXpress.

        Args:
            host: HTTP URL, e.g. "http://localhost" or "http://192.168.1.1"
            port: TCP port the StreamXpress -rc listener is on, e.g. 5000
        """
        if self._connected:
            raise RuntimeError("already connected — disconnect first")
        self._sprc = self._sprc_factory()
        self._sprc.open_session(ip_host=host, ip_port=port)
        self._connected = True

    def disconnect(self) -> None:
        """Close the session and clean up."""
        if self._sprc is not None:
            try:
                self._sprc.cleanup()
            except Exception:
                pass
            self._sprc = None
        self._connected = False

    def _ensure_connected(self) -> SPRC_client:
        if not self._connected or self._sprc is None:
            raise RuntimeError("not connected — call connect() first")
        return self._sprc

    # ── Port discovery ──

    def scan_ports(self) -> list[SpRcPortDesc]:
        sprc = self._ensure_connected()
        return sprc.scan_ports()

    def select_port(self, serial: int, port_num: int, modulation: int = 0) -> None:
        sprc = self._ensure_connected()
        sprc.select_port(serial, port_num, modulation)

    # ── File & playout ──

    def open_file(self, filepath: str) -> None:
        sprc = self._ensure_connected()
        sprc.open_file(filepath)

    def open_channel_modelling_file(self, filepath: str) -> None:
        sprc = self._ensure_connected()
        sprc.open_channel_modelling_file(filepath)

    def save_channel_modelling_settings(self, filepath: str) -> None:
        sprc = self._ensure_connected()
        sprc.save_channel_modelling_settings(filepath)

    def save_settings(self, filepath: str) -> None:
        sprc = self._ensure_connected()
        sprc.save_settings(filepath)

    def normalise(self) -> None:
        sprc = self._ensure_connected()
        sprc.normalise()

    def start(self) -> None:
        sprc = self._ensure_connected()
        sprc.set_playout_state(SPRC.STATE_PLAY)

    def stop(self) -> None:
        sprc = self._ensure_connected()
        sprc.set_playout_state(SPRC.STATE_STOP)

    # ── Session & version ──

    def get_remote_version(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_remote_version())

    def get_remote_dtapi_version(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_remote_dtapi_version())

    def get_app_info(self) -> dict:
        sprc = self._ensure_connected()
        name, version = sprc.get_app_info()
        return {"app_name": name, "version": _to_dict(version)}

    def show_window(self, show: bool) -> None:
        sprc = self._ensure_connected()
        sprc.show_window(show)

    def clear_errors(self) -> None:
        sprc = self._ensure_connected()
        sprc.clear_errors()

    # ── Status ──

    def get_status(self) -> dict:
        sprc = self._ensure_connected()
        status = sprc.get_playout_status()
        info = sprc.get_playout_info()
        return {
            "position_percent": round(status.PosRel * 100, 1),
            "num_wraps": status.NumWraps,
            "num_errors": status.NumErrors,
            "fifo_load": status.FifoLoad,
            "total_mem_load": status.TotalMemLoad,
            "playout_state": info.PlayoutState,
            "file_name": info.Filename,
            "file_size": info.FileSize,
            "ts_rate_bps": info.TsRate,
            "playout_rate": info.PlayoutRate,
            "sym_rate": info.SymRate,
            "time_offset": info.TimeOffset,
            "loop_flags": info.LoopFlags,
            "remux": info.Remux,
            "tp_size": info.TpSize,
        }

    # ── Parameter getters ──

    def get_asi_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_asi_pars())

    def get_cmmb_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_cmmb_pars())

    def get_mod_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_mod_pars())

    def get_rf_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_rf_pars())

    def get_tsoip_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_tsoip_pars())

    def get_spi_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_spi_pars())

    def get_hw_noise_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_hw_noise_pars())

    def get_iq_gain(self) -> int:
        sprc = self._ensure_connected()
        return sprc.get_iq_gain()

    def get_signal_source(self) -> int:
        sprc = self._ensure_connected()
        return sprc.get_signal_source()

    def get_use_nit(self) -> bool:
        sprc = self._ensure_connected()
        return sprc.get_use_nit()

    def get_channel_modelling_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_channel_modelling_pars())

    def get_dvb_t2_group(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_dvb_t2_group())

    def get_dvb_t2_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_dvb_t2_pars())

    def get_isdb_t_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_isdb_t_pars())

    def get_tdt_adapt_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_tdt_adapt_pars())

    def get_tsg_pars(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_tsg_pars())

    def get_sfn_status(self) -> dict:
        sprc = self._ensure_connected()
        return _to_dict(sprc.get_sfn_status())

    # ── Parameters ──

    def set_rate(self, bps: int) -> None:
        sprc = self._ensure_connected()
        sprc.set_ts_rate(bps)

    def set_tsoip_params(
        self,
        dest_ip: str,
        dest_port: int,
        num_tp_per_ip: int = 7,
        protocol: str = "UDP",
        ttl: int = 64,
        fec_rows: int = 0,
        fec_cols: int = 0,
        tx_mode: int = DTAPI.TXMODE_188,
        failover: bool = False,
        dest_ip2: str | None = None,
        dest_port2: int = 0,
        diff_serv: int = 0,
    ) -> None:
        sprc = self._ensure_connected()
        ip_bytes = _parse_ip(dest_ip)
        ip2_bytes = _parse_ip(dest_ip2) if dest_ip2 else bytes([0, 0, 0, 0])
        proto_const = DTAPI.PROTO_UDP if protocol.upper() == "UDP" else DTAPI.PROTO_RTP
        fec_mode = DTAPI.FEC_DISABLE if (fec_rows == 0 or fec_cols == 0) else DTAPI.FEC_2D

        pars = SpRcTsoipPars(
            TxMode=tx_mode,
            Ip=ip_bytes,
            Port=dest_port,
            EnaFailover=failover,
            Ip2=ip2_bytes,
            Port2=dest_port2,
            TimeToLive=ttl,
            NumTpPerIp=num_tp_per_ip,
            Protocol=proto_const,
            DiffServ=diff_serv,
            FecMode=fec_mode,
            FecNumRows=fec_rows,
            FecNumCols=fec_cols,
        )
        sprc.set_tsiop_pars(pars)

    def set_rf_params(self, frequency_hz: int, level_dbm: float) -> None:
        sprc = self._ensure_connected()
        pars = SpRcRfPars(Frequency=frequency_hz, Level=level_dbm)
        sprc.set_rf_pars(pars)

    def set_asi_params(
        self,
        remux: bool = True,
        playout_rate: int = 0,
        tx_mode: int = DTAPI.TXMODE_188,
        burst_mode: bool = False,
        polarity: int = DTAPI.TXPOL_NORMAL,
    ) -> None:
        sprc = self._ensure_connected()
        pars = SpRcAsiPars(
            Remux=remux,
            PlayoutRate=playout_rate,
            BurstMode=burst_mode,
            TxMode=tx_mode,
            Polarity=polarity,
        )
        sprc.set_asi_pars(pars)

    def set_loop_flags(self, flags: int) -> None:
        sprc = self._ensure_connected()
        sprc.set_loop_flags(flags)

    def set_iq_gain(self, gain: int) -> None:
        sprc = self._ensure_connected()
        sprc.set_iq_gain(gain)

    def set_remux(self, enabled: bool) -> None:
        sprc = self._ensure_connected()
        sprc.set_remux(enabled)

    def set_signal_source(self, source: int) -> None:
        sprc = self._ensure_connected()
        sprc.set_signal_source(source)

    def set_use_nit(self, use_nit: bool) -> None:
        sprc = self._ensure_connected()
        sprc.set_use_nit(use_nit)

    def set_sfn_mode(self, sfn_mode: int) -> None:
        sprc = self._ensure_connected()
        sprc.set_sfn_mode(sfn_mode)

    def set_sub_loop_pars(
        self, use_subloop: bool, loop_begin_rel: float = 0.0, loop_end_rel: float = 1.0
    ) -> None:
        sprc = self._ensure_connected()
        sprc.set_sub_loop_pars(
            SpRcSubLoopPars(
                UseSubLoop=use_subloop,
                LoopBeginRel=loop_begin_rel,
                LoopEndRel=loop_end_rel,
            )
        )

    def select_dta_plus(self, use_dta_plus: bool, serial: int) -> None:
        sprc = self._ensure_connected()
        sprc.select_dta_plus(use_dta_plus, serial)

    def set_cmmb_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_cmmb_pars(SpRcCmmbPars(**pars))

    def set_hw_noise_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_hw_noise_pars(SpRcHwNoisePars(**pars))

    def set_spi_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_spi_pars(SpRcSpiPars(**pars))

    def set_tsg_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_tsg_pars(SpRcTsgPars(**pars))

    def set_dvb_t2_group(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_dvb_t2_group(SpRcDvbT2Group(**pars))

    def set_mod_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_mod_pars(SpRcModPars(**pars))

    def set_channel_modelling_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        paths = [SpRcCmPath(**p) for p in pars.get("Paths", [])]
        cm_pars = SpRcCmPars(**{k: v for k, v in pars.items() if k != "Paths"}, Paths=paths)
        sprc.set_channel_modelling_pars(cm_pars)

    def set_dvb_t2_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        sprc.set_dvb_t2_pars(SpRcDvbT2Pars(**pars))

    def set_isdb_t_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        layer_pars = [SpRcIsdbtLayerPars(**lp) for lp in pars.get("LayerPars", [])]
        isdbt_pars = SpRcIsdbtPars(
            **{k: v for k, v in pars.items() if k not in ("LayerPars", "Pid2Layer")},
            LayerPars=layer_pars,
            Pid2Layer={int(k): v for k, v in (pars.get("Pid2Layer") or {}).items()},
        )
        sprc.set_isdb_t_pars(isdbt_pars)

    def set_tdt_adapt_pars(self, pars: dict) -> None:
        sprc = self._ensure_connected()
        dt = SpRcDateTime(**(pars.get("TdtDateTime") or {}))
        sprc.set_tdt_adapt_pars(
            SpRcTdtAdaptPars(TdtAdaptMode=pars["TdtAdaptMode"], TdtDateTime=dt)
        )

    def set_playout_state_sfn(self, playout_state: int, sfn_start_time: int = 0) -> None:
        sprc = self._ensure_connected()
        sprc.set_playout_state_sfn(
            SpRcPlayoutSfnPars(PlayoutState=playout_state, SfnStartTime=sfn_start_time)
        )

    def wait_for_condition(self, condition: int, timeout_ms: int = -1) -> None:
        sprc = self._ensure_connected()
        sprc.wait_for_condition(condition, timeout_ms)

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


# SOAP 层返回的错误码里，这些表示会话/传输已不可用，应把本地连接状态标记为失效。
_TRANSPORT_ERROR_CODES = {SPRC_RESULT.E_COMMUNICATION, SPRC_RESULT.E_SESSION_NOT_OPEN}


def _raise_sprc_error(e: SpRcException) -> None:
    """把 SpRcException 转成带错误码名/值的可诊断 RuntimeError。"""
    raise RuntimeError(
        f"StreamXpress error {e.ErrorCode.name} ({e.ErrorCode.value}): {e or 'no detail'}"
    ) from e


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
        sprc = self._sprc_factory()
        try:
            sprc.open_session(ip_host=host, ip_port=port)
        except SpRcException as e:
            _raise_sprc_error(e)
        self._sprc = sprc
        self._connected = True

    def disconnect(self) -> None:
        """Close the session and clean up.

        Local state is always reset; a failing cleanup (e.g. network drop while
        closing) is reported as a RuntimeError instead of being swallowed, so
        the caller can surface it while still being able to reconnect.
        """
        error = None
        if self._sprc is not None:
            try:
                self._sprc.cleanup()
            except Exception as e:  # noqa: BLE001 — must still reset local state
                error = e
            self._sprc = None
        self._connected = False
        if error is not None:
            raise RuntimeError(f"failed to close StreamXpress session: {error}") from error

    def _ensure_connected(self) -> SPRC_client:
        if not self._connected or self._sprc is None:
            raise RuntimeError("not connected — call connect() first")
        return self._sprc

    def _sprc_call(self, fn):
        """Run a lower-layer call on the connected session with unified error handling.

        - SpRcException → RuntimeError carrying the error-code name/value;
        - transport failures (E_COMMUNICATION / E_SESSION_NOT_OPEN / OSError)
          mark the local session stale so the next call reports a clear
          "not connected" instead of a blank SOAP failure.
        """
        sprc = self._ensure_connected()
        try:
            return fn(sprc)
        except SpRcException as e:
            if e.ErrorCode in _TRANSPORT_ERROR_CODES:
                self._connected = False
            _raise_sprc_error(e)
        except OSError as e:
            self._connected = False
            raise RuntimeError(f"StreamXpress communication error: {e}") from e

    # ── Port discovery ──

    def scan_ports(self) -> list[SpRcPortDesc]:
        return self._sprc_call(lambda s: s.scan_ports())

    def select_port(self, serial: int, port_num: int, modulation: int = 0) -> None:
        self._sprc_call(lambda s: s.select_port(serial, port_num, modulation))

    # ── File & playout ──

    def open_file(self, filepath: str) -> None:
        self._sprc_call(lambda s: s.open_file(filepath))

    def open_channel_modelling_file(self, filepath: str) -> None:
        self._sprc_call(lambda s: s.open_channel_modelling_file(filepath))

    def save_channel_modelling_settings(self, filepath: str) -> None:
        self._sprc_call(lambda s: s.save_channel_modelling_settings(filepath))

    def save_settings(self, filepath: str) -> None:
        self._sprc_call(lambda s: s.save_settings(filepath))

    def normalise(self) -> None:
        self._sprc_call(lambda s: s.normalise())

    def start(self) -> None:
        self._sprc_call(lambda s: s.set_playout_state(SPRC.STATE_PLAY))

    def stop(self) -> None:
        self._sprc_call(lambda s: s.set_playout_state(SPRC.STATE_STOP))

    # ── Session & version ──

    def get_remote_version(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_remote_version()))

    def get_remote_dtapi_version(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_remote_dtapi_version()))

    def get_app_info(self) -> dict:
        def _call(s):
            name, version = s.get_app_info()
            return {"app_name": name, "version": _to_dict(version)}

        return self._sprc_call(_call)

    def show_window(self, show: bool) -> None:
        self._sprc_call(lambda s: s.show_window(show))

    def clear_errors(self) -> None:
        self._sprc_call(lambda s: s.clear_errors())

    # ── Status ──

    def get_status(self) -> dict:
        def _call(s):
            status = s.get_playout_status()
            info = s.get_playout_info()
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

        return self._sprc_call(_call)

    # ── Parameter getters ──

    def get_asi_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_asi_pars()))

    def get_cmmb_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_cmmb_pars()))

    def get_mod_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_mod_pars()))

    def get_rf_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_rf_pars()))

    def get_tsoip_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_tsoip_pars()))

    def get_spi_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_spi_pars()))

    def get_hw_noise_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_hw_noise_pars()))

    def get_iq_gain(self) -> int:
        return self._sprc_call(lambda s: s.get_iq_gain())

    def get_signal_source(self) -> int:
        return self._sprc_call(lambda s: s.get_signal_source())

    def get_use_nit(self) -> bool:
        return self._sprc_call(lambda s: s.get_use_nit())

    def get_channel_modelling_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_channel_modelling_pars()))

    def get_dvb_t2_group(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_dvb_t2_group()))

    def get_dvb_t2_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_dvb_t2_pars()))

    def get_isdb_t_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_isdb_t_pars()))

    def get_tdt_adapt_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_tdt_adapt_pars()))

    def get_tsg_pars(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_tsg_pars()))

    def get_sfn_status(self) -> dict:
        return self._sprc_call(lambda s: _to_dict(s.get_sfn_status()))

    # ── Parameters ──

    def set_rate(self, bps: int) -> None:
        self._sprc_call(lambda s: s.set_ts_rate(bps))

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
        ip_bytes = _parse_ip(dest_ip)
        ip2_bytes = _parse_ip(dest_ip2) if dest_ip2 else bytes([0, 0, 0, 0])
        protocol_upper = protocol.upper()
        if protocol_upper not in ("UDP", "RTP"):
            raise ValueError(f"invalid protocol: {protocol!r} — must be 'UDP' or 'RTP'")
        proto_const = DTAPI.PROTO_UDP if protocol_upper == "UDP" else DTAPI.PROTO_RTP
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
        self._sprc_call(lambda s: s.set_tsiop_pars(pars))

    def set_rf_params(self, frequency_hz: int, level_dbm: float) -> None:
        pars = SpRcRfPars(Frequency=frequency_hz, Level=level_dbm)
        self._sprc_call(lambda s: s.set_rf_pars(pars))

    def set_asi_params(
        self,
        remux: bool = True,
        playout_rate: int = 0,
        tx_mode: int = DTAPI.TXMODE_188,
        burst_mode: bool = False,
        polarity: int = DTAPI.TXPOL_NORMAL,
    ) -> None:
        pars = SpRcAsiPars(
            Remux=remux,
            PlayoutRate=playout_rate,
            BurstMode=burst_mode,
            TxMode=tx_mode,
            Polarity=polarity,
        )
        self._sprc_call(lambda s: s.set_asi_pars(pars))

    def set_loop_flags(self, flags: int) -> None:
        self._sprc_call(lambda s: s.set_loop_flags(flags))

    def set_iq_gain(self, gain: int) -> None:
        self._sprc_call(lambda s: s.set_iq_gain(gain))

    def set_remux(self, enabled: bool) -> None:
        self._sprc_call(lambda s: s.set_remux(enabled))

    def set_signal_source(self, source: int) -> None:
        self._sprc_call(lambda s: s.set_signal_source(source))

    def set_use_nit(self, use_nit: bool) -> None:
        self._sprc_call(lambda s: s.set_use_nit(use_nit))

    def set_sfn_mode(self, sfn_mode: int) -> None:
        self._sprc_call(lambda s: s.set_sfn_mode(sfn_mode))

    def set_sub_loop_pars(
        self, use_subloop: bool, loop_begin_rel: float = 0.0, loop_end_rel: float = 1.0
    ) -> None:
        self._sprc_call(
            lambda s: s.set_sub_loop_pars(
                SpRcSubLoopPars(
                    UseSubLoop=use_subloop,
                    LoopBeginRel=loop_begin_rel,
                    LoopEndRel=loop_end_rel,
                )
            )
        )

    def select_dta_plus(self, use_dta_plus: bool, serial: int) -> None:
        self._sprc_call(lambda s: s.select_dta_plus(use_dta_plus, serial))

    def set_cmmb_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_cmmb_pars(SpRcCmmbPars(**pars)))

    def set_hw_noise_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_hw_noise_pars(SpRcHwNoisePars(**pars)))

    def set_spi_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_spi_pars(SpRcSpiPars(**pars)))

    def set_tsg_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_tsg_pars(SpRcTsgPars(**pars)))

    def set_dvb_t2_group(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_dvb_t2_group(SpRcDvbT2Group(**pars)))

    def set_mod_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_mod_pars(SpRcModPars(**pars)))

    def set_channel_modelling_pars(self, pars: dict) -> None:
        paths = [SpRcCmPath(**p) for p in (pars.get("Paths") or [])]
        cm_pars = SpRcCmPars(**{k: v for k, v in pars.items() if k != "Paths"}, Paths=paths)
        self._sprc_call(lambda s: s.set_channel_modelling_pars(cm_pars))

    def set_dvb_t2_pars(self, pars: dict) -> None:
        self._sprc_call(lambda s: s.set_dvb_t2_pars(SpRcDvbT2Pars(**pars)))

    def set_isdb_t_pars(self, pars: dict) -> None:
        layer_pars = [SpRcIsdbtLayerPars(**lp) for lp in (pars.get("LayerPars") or [])]
        pid_layer = {}
        for k, v in (pars.get("Pid2Layer") or {}).items():
            pk = int(k)
            if pk in pid_layer:
                raise ValueError(f"duplicate PID in Pid2Layer: {pk!r}")
            pid_layer[pk] = v
        isdbt_pars = SpRcIsdbtPars(
            **{k: v for k, v in pars.items() if k not in ("LayerPars", "Pid2Layer")},
            LayerPars=layer_pars,
            Pid2Layer=pid_layer,
        )
        self._sprc_call(lambda s: s.set_isdb_t_pars(isdbt_pars))

    def set_tdt_adapt_pars(self, pars: dict) -> None:
        dt = SpRcDateTime(**(pars.get("TdtDateTime") or {}))
        self._sprc_call(
            lambda s: s.set_tdt_adapt_pars(
                SpRcTdtAdaptPars(TdtAdaptMode=pars["TdtAdaptMode"], TdtDateTime=dt)
            )
        )

    def set_playout_state_sfn(self, playout_state: int, sfn_start_time: int = 0) -> None:
        self._sprc_call(
            lambda s: s.set_playout_state_sfn(
                SpRcPlayoutSfnPars(PlayoutState=playout_state, SfnStartTime=sfn_start_time)
            )
        )

    def wait_for_condition(self, condition: int, timeout_ms: int = -1) -> None:
        self._sprc_call(lambda s: s.wait_for_condition(condition, timeout_ms))

"""StreamXpressClient: singleton wrapper around SPRC_client for MCP server use."""

from dataclasses import asdict

from .sprc_import import SPRC_client, SpRcPortDesc, SpRcException, SPRC_RESULT
from .sprc_import import SpRcAsiPars, SpRcTsoipPars, SpRcRfPars, SpRcModPars
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

    def start(self) -> None:
        sprc = self._ensure_connected()
        sprc.set_playout_state(SPRC.STATE_PLAY)

    def stop(self) -> None:
        sprc = self._ensure_connected()
        sprc.set_playout_state(SPRC.STATE_STOP)

    # ── Status ──

    def get_status(self) -> dict:
        sprc = self._ensure_connected()
        status = sprc.get_playout_status()
        info = sprc.get_playout_info()
        return {
            "position_percent": round(status.PosRel * 100, 1),
            "num_wraps": status.NumWraps,
            "playout_state": info.PlayoutState,
            "file_name": info.Filename,
            "ts_rate_bps": info.TsRate,
        }

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
    ) -> None:
        sprc = self._ensure_connected()
        ip_bytes = bytes(int(octet) for octet in dest_ip.split("."))
        proto_const = DTAPI.PROTO_UDP if protocol.upper() == "UDP" else DTAPI.PROTO_RTP
        fec_mode = DTAPI.FEC_DISABLE if (fec_rows == 0 or fec_cols == 0) else DTAPI.FEC_2D

        pars = SpRcTsoipPars(
            TxMode=DTAPI.TXMODE_188,
            Ip=ip_bytes,
            Port=dest_port,
            EnaFailover=False,
            Ip2=bytes([0, 0, 0, 0]),
            Port2=0,
            TimeToLive=ttl,
            NumTpPerIp=num_tp_per_ip,
            Protocol=proto_const,
            DiffServ=0,
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
        self, remux: bool = True, playout_rate: int = 0, tx_mode: int = DTAPI.TXMODE_188
    ) -> None:
        sprc = self._ensure_connected()
        pars = SpRcAsiPars(
            Remux=remux,
            PlayoutRate=playout_rate,
            BurstMode=False,
            TxMode=tx_mode,
            Polarity=DTAPI.TXPOL_NORMAL,
        )
        sprc.set_asi_pars(pars)

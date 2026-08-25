"""StreamXpressClient: singleton wrapper around SPRC_client for MCP server use."""

import threading
import xml.etree.ElementTree as ET
from pathlib import Path

from .sprc_import import SPRC_client, SpRcPortDesc, SpRcException, SPRC_RESULT
from .sprc_import import SPRC


# SOAP 层返回的错误码里，这些表示会话/传输已不可用，应把本地连接状态标记为失效。
_TRANSPORT_ERROR_CODES = {SPRC_RESULT.E_COMMUNICATION, SPRC_RESULT.E_SESSION_NOT_OPEN}


def _raise_sprc_error(e: SpRcException) -> None:
    """把 SpRcException 转成带错误码名/值的可诊断 RuntimeError。"""
    raise RuntimeError(
        f"StreamXpress error {e.ErrorCode.name} ({e.ErrorCode.value}): {str(e) or 'no detail'}"
    ) from e



def _xml_local_name(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _require_file(path: str, kind: str) -> str:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"{kind} not found: {path}")
    return str(p)


def validate_settings_xml(path: str) -> str:
    """Ensure *path* is a StreamXpress settings snapshot (not Atsc3Xpress)."""
    resolved = _require_file(path, "settings XML")
    try:
        root = ET.parse(resolved).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"settings XML is not valid XML: {path}: {exc}") from exc
    if _xml_local_name(root.tag) != "StreamXpressSettings":
        raise ValueError(
            "settings XML root must be StreamXpressSettings "
            f"(got {root.tag!r}); Atsc3Xpress / other XML is not supported"
        )
    return resolved


def pick_playout_port(
    ports: list[SpRcPortDesc],
    preferred_serial: int = 0,
    preferred_type_number: int = 315,
) -> SpRcPortDesc:
    """Choose a local output port for play().

    Priority: preferred_serial (if non-zero) -> preferred_type_number
    (default 315) -> the unique idle port -> the unique port.
    """
    ports = list(ports)
    if not ports:
        raise RuntimeError("no StreamXpress output ports found")

    def _fmt(ps: list[SpRcPortDesc]) -> str:
        return ", ".join(
            f"S/N {p.Serial} type {p.TypeNumber} port {p.Port}" for p in ps
        )

    if preferred_serial:
        matched = [p for p in ports if p.Serial == preferred_serial]
        if not matched:
            raise RuntimeError(
                f"preferred serial {preferred_serial} not found; available: {_fmt(ports)}"
            )
        return sorted(matched, key=lambda p: p.Port)[0]

    if preferred_type_number:
        matched = [p for p in ports if p.TypeNumber == preferred_type_number]
        if matched:
            return sorted(matched, key=lambda p: (p.Serial, p.Port))[0]

    idle = [p for p in ports if p.InUse == 0]
    if len(idle) == 1:
        return idle[0]
    if len(ports) == 1:
        return ports[0]
    raise RuntimeError(
        f"could not auto-select a port (wanted type {preferred_type_number}); "
        f"available: {_fmt(ports)}"
    )


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
        # FastMCP runs sync tools on worker threads, so two tool calls can
        # genuinely overlap; the RLock serializes session mutations.
        self._lock = threading.RLock()

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
        with self._lock:
            self._sprc = sprc
            self._connected = True

    def disconnect(self) -> None:
        """Close the session and clean up.

        Local state is always reset; a failing cleanup (e.g. network drop while
        closing) is reported as a RuntimeError instead of being swallowed, so
        the caller can surface it while still being able to reconnect.
        """
        with self._lock:
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


    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected and self._sprc is not None

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

        The lock is held only while resolving the session reference and while
        updating the stale flag — never across the SOAP call itself, so a
        long-running call (e.g. an unbounded wait_for_condition) cannot block
        every other tool.
        """
        with self._lock:
            sprc = self._ensure_connected()
        try:
            return fn(sprc)
        except SpRcException as e:
            if e.ErrorCode in _TRANSPORT_ERROR_CODES:
                self._mark_stale(sprc)
            _raise_sprc_error(e)
        except OSError as e:
            self._mark_stale(sprc)
            raise RuntimeError(f"StreamXpress communication error: {e}") from e

    def _mark_stale(self, sprc) -> None:
        """Mark the session stale, but only if it is still the current session.

        An in-flight call may fail late: meanwhile the user may have done a
        disconnect+connect, establishing a fresh healthy session. Without an
        identity check, that late failure would falsely mark the new session as
        disconnected, leaving every subsequent call with "not connected" until
        a manual reconnect.
        """
        with self._lock:
            if self._sprc is sprc:
                self._connected = False

    def stop(self) -> None:
        self._sprc_call(lambda s: s.set_playout_state(SPRC.STATE_STOP))

    def play(
        self,
        settings_xml: str,
        stream: str,
        loop: bool = True,
        preferred_serial: int = 0,
        preferred_type_number: int = 315,
    ) -> dict:
        """Load a settings XML, then a stream, then start playout.

        File/XML checks run before any SOAP call. Port selection and the
        OpenFile(xml) -> OpenFile(stream) -> PLAY sequence run in one
        `_sprc_call` so a transport failure marks the session stale once.
        """
        settings_xml = validate_settings_xml(settings_xml)
        stream = _require_file(stream, "stream file")

        def _call(s):
            try:
                info = s.get_playout_info()
                if getattr(info, "PlayoutState", None) == SPRC.STATE_PLAY:
                    s.set_playout_state(SPRC.STATE_STOP)
            except SpRcException:
                pass

            chosen = pick_playout_port(
                s.scan_ports(),
                preferred_serial=preferred_serial,
                preferred_type_number=preferred_type_number,
            )
            s.select_port(chosen.Serial, chosen.Port, 0)
            s.open_file(settings_xml)
            if not loop:
                s.set_loop_flags(0)
            s.open_file(stream)
            s.set_playout_state(SPRC.STATE_PLAY)
            return {
                "status": "playing",
                "settings_xml": settings_xml,
                "stream": stream,
                "serial": chosen.Serial,
                "port": chosen.Port,
            }

        return self._sprc_call(_call)


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
            "file_can_be_read": info.FileCanBeRead,
            "file_rate_est": info.FileRateEst,
            "file_type": info.FileType,
            "loop_begin_rel": info.LoopBeginRel,
            "loop_end_rel": info.LoopEndRel,
            "tx_polarity": info.TxPolarity,
            "burst_mode": info.BurstMode,
            "ext_clock": info.ExtClock,
            }

        return self._sprc_call(_call)

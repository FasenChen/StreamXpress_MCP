"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

import threading

from fastmcp import FastMCP

from .client import StreamXpressClient
from .config import load_config, resolve_wsdl_path
from .launcher import launch_streamxpress
from .sprc_import import SPRC_client, DTAPI

# ── FastMCP application ──

mcp = FastMCP("streamxpress-mcp")

# ── Global client singleton ──

_client: StreamXpressClient | None = None
_client_lock = threading.Lock()


def get_client() -> StreamXpressClient:
    """Return the global singleton client, creating it if needed."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                cfg = load_config()
                wsdl = resolve_wsdl_path(cfg)
                if wsdl is not None:
                    _client = StreamXpressClient(
                        sprc_factory=lambda: SPRC_client(wsdl_template=wsdl)
                    )
                else:
                    _client = StreamXpressClient()
    return _client


# ── Connection tools ──

@mcp.tool()
def connect(host: str, port: int) -> dict:
    """Connect to a StreamXpress instance running in remote-control mode.

    The StreamXpress must be started with: StreamXpress.exe -rc <port>

    Args:
        host: HTTP URL of the StreamXpress host, e.g. "http://localhost"
        port: TCP port the -rc listener is bound to, e.g. 5000
    """
    client = get_client()
    try:
        client.disconnect()
    except Exception:
        pass
    client.connect(host, port)
    return {"status": "connected", "host": host, "port": port}


@mcp.tool()
def disconnect() -> dict:
    """Disconnect from the StreamXpress remote-control session."""
    client = get_client()
    try:
        client.disconnect()
        return {"status": "disconnected"}
    except RuntimeError as e:
        # Session cleanup failed (e.g. network drop) — local state is reset
        # regardless, so report the warning without turning it into a failure.
        return {"status": "disconnected", "warning": str(e)}


@mcp.tool()
def get_remote_version() -> dict:
    """Get the SpRcApi version running on the connected StreamXpress server."""
    return get_client().get_remote_version()


@mcp.tool()
def get_remote_dtapi_version() -> dict:
    """Get the DTAPI version StreamXpress was built with (server side)."""
    return get_client().get_remote_dtapi_version()


@mcp.tool()
def get_app_info() -> dict:
    """Get application name and version of the connected StreamXpress."""
    return get_client().get_app_info()


@mcp.tool()
def show_window(show: bool) -> dict:
    """Show or hide the StreamXpress application window on the server.

    Args:
        show: True to show the window, False to hide it.
    """
    client = get_client()
    client.show_window(show)
    return {"status": "ok", "show": show}


@mcp.tool()
def clear_errors() -> dict:
    """Clear the playout error counters (e.g. underflows) on the server."""
    client = get_client()
    client.clear_errors()
    return {"status": "ok"}


# ── Port discovery tools ──

OUTPUT_TYPE_LABELS = {
    0x00001: "ASI", 0x00002: "ATSC", 0x00004: "CMMB",
    0x00008: "DTMB", 0x00010: "DVB-S", 0x00020: "DVB-S2",
    0x00040: "DVB-T", 0x00080: "DVB-T2", 0x00100: "DVB-T2MI",
    0x00200: "IQ", 0x00400: "ISDB-S", 0x00800: "ISDB-T",
    0x01000: "QAM-A", 0x02000: "QAM-B", 0x04000: "QAM-C",
    0x08000: "SD-SDI", 0x10000: "SPI", 0x20000: "TS-over-IP",
    0x40000: "ISDB-S3", 0x80000: "DRM", 0x100000: "ATSC3-STLTP",
}

CAPABILITY_LABELS = {
    1: "ADJLVL",    # 输出电平可调
    2: "CM",        # 支持信道建模
    4: "DIGIQ",     # 数字 IQ 输出
    8: "IF",        # IF 输出
    16: "LBAND",    # 可上变频至 L 波段 950–2150 MHz
    32: "UHF",      # 400–862 MHz
    64: "VHF",      # 47–470 MHz
    128: "SFN",     # 支持单频网
}


def _describe_output_type(flags: int) -> list[str]:
    """Convert OutputType bitmask to human-readable labels."""
    labels = []
    for mask, name in OUTPUT_TYPE_LABELS.items():
        if flags & mask:
            labels.append(name)
    return labels


def _describe_capabilities(flags: int) -> list[str]:
    """Convert Capabilities bitmask to human-readable labels."""
    return [name for mask, name in CAPABILITY_LABELS.items() if flags & mask]


@mcp.tool()
def scan_ports() -> list[dict]:
    """Scan for available output ports on the connected StreamXpress.

    Returns a list of port descriptors with serial, type, output types and
    capabilities (adjustable level, channel modelling, SFN, upconverter band...).
    """
    client = get_client()
    ports = client.scan_ports()
    return [
        {
            "serial": p.Serial,
            "type_number": p.TypeNumber,
            "port": p.Port,
            "output_types": _describe_output_type(p.OutputType),
            "capabilities": _describe_capabilities(p.Capabilities),
            "capabilities_raw": p.Capabilities,
            "ip": list(p.Ip) if p.Ip else None,
            "mac": list(p.Mac) if p.Mac else None,
            "in_use": p.InUse != 0,
        }
        for p in ports
    ]


@mcp.tool()
def select_port(serial: int, port_num: int, modulation: int = 0) -> dict:
    """Select a physical output port for playout.

    Args:
        serial: Device serial number (from scan_ports)
        port_num: Physical port number on the device
        modulation: Initial modulation standard for modulator ports — use
                    SPRC.MOD_* constants (NOT DTAPI.MOD_*; the two namespaces
                    have different values). Set to 0 for non-modulator ports.
                    Common values: MOD_DVBT=7, MOD_DVBT2=8, MOD_DVBS=5,
                    MOD_DVBS2=6, MOD_J83A=13 (DVB-C QAM), MOD_ATSC=1,
                    MOD_ISDBT=12, MOD_CMMB=2.
    """
    client = get_client()
    client.select_port(serial, port_num, modulation)
    return {"status": "ok", "serial": serial, "port": port_num}


@mcp.tool()
def open_file(filepath: str) -> dict:
    """Open a TS file for playout.

    Args:
        filepath: Full path to the .ts file or StreamXpress .xml settings file
    """
    client = get_client()
    client.open_file(filepath)
    return {"status": "ok", "file": filepath}


@mcp.tool()
def open_channel_modelling_file(filepath: str) -> dict:
    """Open a channel modelling settings file (.chmx) on the server.

    Args:
        filepath: Full path on the StreamXpress host machine.
    """
    client = get_client()
    client.open_channel_modelling_file(filepath)
    return {"status": "ok", "file": filepath}


@mcp.tool()
def save_channel_modelling_settings(filepath: str) -> dict:
    """Save the current channel modelling settings to a .chmx file on the server."""
    client = get_client()
    client.save_channel_modelling_settings(filepath)
    return {"status": "ok", "file": filepath}


@mcp.tool()
def save_settings(filepath: str) -> dict:
    """Save all current StreamXpress settings to an .xml settings file on the server."""
    client = get_client()
    client.save_settings(filepath)
    return {"status": "ok", "file": filepath}


@mcp.tool()
def normalise() -> dict:
    """Normalise multi-path channel modelling (accumulated path gain to 0 dB)."""
    client = get_client()
    client.normalise()
    return {"status": "ok"}


# ── Playback control tools ──

@mcp.tool()
def start() -> dict:
    """Start TS playout on the selected port."""
    client = get_client()
    client.start()
    return {"status": "playing"}


@mcp.tool()
def stop() -> dict:
    """Stop TS playout."""
    client = get_client()
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
def pause() -> dict:
    """Pause TS playout, preserving the current file position.

    Unlike stop, pause keeps the playout position, so a following start resumes
    from where it left off. Note the playout server does NOT report a paused
    player as stopped, so wait_for_condition(SPRC.COND_STOPPED) will not be
    satisfied while paused.
    """
    client = get_client()
    client.pause()
    return {"status": "paused"}


@mcp.tool()
def get_status() -> dict:
    """Get current playout status including position, wraps, filename, and bitrate.

    Note: total_mem_load's unit is ambiguous between sources — SpRcApi.h says
    "#words", the spec says "#bytes". It is passed through as-is.
    """
    client = get_client()
    return client.get_status()


@mcp.tool()
def get_playout_info() -> dict:
    """Get the full static playout info struct (all SpRcPlayoutInfo fields).

    get_status returns a curated summary merged with dynamic status; this tool
    returns every field verbatim, so newly added vendor fields never go missing.
    """
    return get_client().get_playout_info()


# ── Parameter tools ──

@mcp.tool()
def get_asi_pars() -> dict:
    """Get current DVB-ASI transmission parameters."""
    return get_client().get_asi_pars()


@mcp.tool()
def get_cmmb_pars() -> dict:
    """Get current CMMB modulation parameters."""
    return get_client().get_cmmb_pars()


@mcp.tool()
def get_mod_pars() -> dict:
    """Get current modulation parameters (ModType/ParXtra0-2/SymRate)."""
    return get_client().get_mod_pars()


@mcp.tool()
def get_rf_pars() -> dict:
    """Get current RF parameters (frequency Hz, level dBm, SpecInv, CW, RfEnabledOnStop)."""
    return get_client().get_rf_pars()


@mcp.tool()
def get_tsoip_pars() -> dict:
    """Get current TS-over-IP transmission parameters (Ip is a list of 4 ints)."""
    return get_client().get_tsoip_pars()


@mcp.tool()
def get_spi_pars() -> dict:
    """Get current DVB-SPI transmission parameters."""
    return get_client().get_spi_pars()


@mcp.tool()
def get_hw_noise_pars() -> dict:
    """Get hardware noise generator parameters (DTA-107/DTA-2107)."""
    return get_client().get_hw_noise_pars()


@mcp.tool()
def get_iq_gain() -> int:
    """Get the IQ gain in units of 0.1 dB."""
    return get_client().get_iq_gain()


@mcp.tool()
def get_signal_source() -> int:
    """Get the current signal source: 0=file, 1=test signal generator (SPRC.FROM_FILE / SPRC.TEST_GENERATOR)."""
    return get_client().get_signal_source()


@mcp.tool()
def get_use_nit() -> bool:
    """Get whether the NIT is being used to derive modulation parameters."""
    return get_client().get_use_nit()


@mcp.tool()
def get_channel_modelling_pars() -> dict:
    """Get current channel modelling parameters (noise + multi-path)."""
    return get_client().get_channel_modelling_pars()


@mcp.tool()
def get_dvb_t2_group() -> dict:
    """Get the currently selected DVB-T2 group and set names."""
    return get_client().get_dvb_t2_group()


@mcp.tool()
def get_dvb_t2_pars() -> dict:
    """Get current DVB-T2 modulation parameters (follows SpRcDvbT2Pars fields)."""
    return get_client().get_dvb_t2_pars()


@mcp.tool()
def get_isdb_t_pars() -> dict:
    """Get current ISDB-T modulation parameters (layers + PID-to-layer map)."""
    return get_client().get_isdb_t_pars()


@mcp.tool()
def get_tdt_adapt_pars() -> dict:
    """Get current TDT/TOT adaptation parameters."""
    return get_client().get_tdt_adapt_pars()


@mcp.tool()
def get_tsg_pars() -> dict:
    """Get current test signal generator parameters."""
    return get_client().get_tsg_pars()


@mcp.tool()
def get_sfn_status() -> dict:
    """Get current GPS and SFN playout status."""
    return get_client().get_sfn_status()


@mcp.tool()
def set_rate(rate_bps: int) -> dict:
    """Set the TS playout bitrate in bits per second (188-byte packets).

    Args:
        rate_bps: Target bitrate, e.g. 25_000_000 for 25 Mbps
    """
    client = get_client()
    client.set_rate(rate_bps)
    return {"status": "ok", "rate_bps": rate_bps}


@mcp.tool()
def set_tsoip_params(
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
) -> dict:
    """Configure TS-over-IP output parameters (UDP/RTP).

    Args:
        dest_ip: Destination IP address, e.g. "239.1.1.1" (multicast) or "192.168.1.100" (unicast)
        dest_port: Destination UDP port, e.g. 1234
        num_tp_per_ip: Number of TS packets per IP packet (1-7)
        protocol: "UDP" or "RTP"
        ttl: Time-To-Live for multicast
        fec_rows: FEC matrix rows (D), 0 disables FEC
        fec_cols: FEC matrix columns (L), 0 disables FEC
        tx_mode: DTAPI.TXMODE_188/204/ADD16/MIN16
        failover: Enable redundant second IP port (DTA-2162)
        dest_ip2: Second destination IP for failover
        dest_port2: Second destination port for failover
        diff_serv: Differentiated-services (ToS) value in IP header
    """
    client = get_client()
    client.set_tsoip_params(
        dest_ip=dest_ip,
        dest_port=dest_port,
        num_tp_per_ip=num_tp_per_ip,
        protocol=protocol,
        ttl=ttl,
        fec_rows=fec_rows,
        fec_cols=fec_cols,
        tx_mode=tx_mode,
        failover=failover,
        dest_ip2=dest_ip2,
        dest_port2=dest_port2,
        diff_serv=diff_serv,
    )
    return {
        "status": "ok",
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "protocol": protocol,
    }


@mcp.tool()
def set_rf_params(
    frequency_hz: int,
    level_dbm: float,
    spec_inv: bool | None = None,
    cw: bool | None = None,
    rf_enabled_on_stop: bool | None = None,
) -> dict:
    """Set RF output frequency and level (modulator ports only).

    Args:
        frequency_hz: Center frequency in Hz, e.g. 500_000_000 for 500 MHz.
        level_dbm: Output level in dBm, e.g. -37.5.
        spec_inv: Spectrum inversion. None (default) keeps the current setting.
        cw: CW (continuous-wave) mode. None keeps the current setting.
        rf_enabled_on_stop: Keep RF output up while playout is stopped.
                            None keeps the current setting.

    The three flags default to None rather than False because SetRfPars writes
    the whole struct — passing False would silently clear an operator's setting
    on every frequency change.
    """
    client = get_client()
    client.set_rf_params(
        frequency_hz=frequency_hz,
        level_dbm=level_dbm,
        spec_inv=spec_inv,
        cw=cw,
        rf_enabled_on_stop=rf_enabled_on_stop,
    )
    return {"status": "ok", "frequency_hz": frequency_hz, "level_dbm": level_dbm}


@mcp.tool()
def set_asi_params(
    remux: bool = True,
    playout_rate: int = 0,
    tx_mode: int = DTAPI.TXMODE_188,
    burst_mode: bool = False,
    polarity: int = DTAPI.TXPOL_NORMAL,
) -> dict:
    """Set ASI output parameters.

    Args:
        remux: Enable real-time remultiplexing (add null packets to match output rate)
        playout_rate: Output rate in bps (0 = use file native rate)
        tx_mode: DTAPI.TXMODE_188 (default), 204, ADD16, MIN16
        burst_mode: Enable DVB-ASI burst mode
        polarity: DTAPI.TXPOL_NORMAL=0 or DTAPI.TXPOL_INVERTED=1
    """
    client = get_client()
    client.set_asi_params(
        remux=remux, playout_rate=playout_rate, tx_mode=tx_mode,
        burst_mode=burst_mode, polarity=polarity,
    )
    return {"status": "ok"}


@mcp.tool()
def set_loop_flags(flags: int) -> dict:
    """Set loop-adaptation flags (OR of SPRC.LOOP_CC=1, LOOP_PCR=2, LOOP_TDT=4, LOOP_WRAP=8).

    Args:
        flags: Bitmask, e.g. 3 = adapt CC + PCR.
    """
    client = get_client()
    client.set_loop_flags(flags)
    return {"status": "ok", "flags": flags}


@mcp.tool()
def set_iq_gain(gain: int) -> dict:
    """Set the IQ gain in units of 0.1 dB."""
    client = get_client()
    client.set_iq_gain(gain)
    return {"status": "ok", "gain": gain}


@mcp.tool()
def set_remux(enabled: bool) -> dict:
    """Enable/disable real-time remultiplexing on modulator ports only.

    Note: SetRemux applies to modulator ports; ASI/SPI ports return an error.
    """
    client = get_client()
    client.set_remux(enabled)
    return {"status": "ok", "enabled": enabled}


@mcp.tool()
def set_signal_source(source: int) -> dict:
    """Set the signal source: 0=file (SPRC.FROM_FILE), 1=test generator (SPRC.TEST_GENERATOR)."""
    client = get_client()
    client.set_signal_source(source)
    return {"status": "ok", "source": source}


@mcp.tool()
def set_use_nit(use_nit: bool) -> dict:
    """Enable/disable using the NIT to derive modulation parameters."""
    client = get_client()
    client.set_use_nit(use_nit)
    return {"status": "ok", "use_nit": use_nit}


@mcp.tool()
def set_sfn_mode(sfn_mode: int) -> dict:
    """Set SFN mode: 0=disabled (SPRC.SFN_MODE_DISABLE), 1=1PPS (SPRC.SFN_MODE_1_PPS)."""
    client = get_client()
    client.set_sfn_mode(sfn_mode)
    return {"status": "ok", "sfn_mode": sfn_mode}


@mcp.tool()
def set_sub_loop_pars(use_subloop: bool, loop_begin_rel: float = 0.0, loop_end_rel: float = 1.0) -> dict:
    """Set file sub-loop playout positions (relative 0..1).

    Args:
        use_subloop: Enable the sub-loop.
        loop_begin_rel: Relative start position in the file (0..1).
        loop_end_rel: Relative end position in the file (0..1).
    """
    client = get_client()
    client.set_sub_loop_pars(use_subloop, loop_begin_rel, loop_end_rel)
    return {"status": "ok", "use_subloop": use_subloop}


@mcp.tool()
def select_dta_plus(use_dta_plus: bool, serial: int) -> dict:
    """Select a DtaPlus device to use as an attenuator.

    Args:
        use_dta_plus: True to start using the DtaPlus device.
        serial: Serial number of the DtaPlus device (from scan_ports).
    """
    client = get_client()
    client.select_dta_plus(use_dta_plus, serial)
    return {"status": "ok", "serial": serial}


@mcp.tool()
def set_cmmb_pars(bandwidth: int, area_id: int, tx_id: int) -> dict:
    """Set CMMB modulation parameters.

    Args:
        bandwidth: DTAPI.CMMB_BW_2MHZ=0 / CMMB_BW_8MHZ=1.
        area_id: Area ID (0..127).
        tx_id: Transmitter ID (128..255).
    """
    client = get_client()
    client.set_cmmb_pars({"Bandwidth": bandwidth, "AreaId": area_id, "TxId": tx_id})
    return {"status": "ok"}


@mcp.tool()
def set_hw_noise_pars(snr_on: bool, snr: float) -> dict:
    """Set hardware noise generator parameters (DTA-107/DTA-2107).

    Args:
        snr_on: Enable the noise generator.
        snr: Signal-to-noise ratio in dB.
    """
    client = get_client()
    client.set_hw_noise_pars({"SnrOn": snr_on, "Snr": snr})
    return {"status": "ok"}


@mcp.tool()
def set_spi_pars(
    remux: bool,
    playout_rate: int,
    tx_mode: int = DTAPI.TXMODE_188,
    power: bool = False,
) -> dict:
    """Set DVB-SPI transmission parameters.

    Args:
        remux: Enable remultiplexing (add null packets to match playout_rate).
        playout_rate: Output rate in bps (only used when remux is on).
        tx_mode: DTAPI.TXMODE_188/192/204/ADD16/MIN16/RAW — 192 is DTA-102 only.
        power: Power for the external adapter.
    """
    client = get_client()
    client.set_spi_pars({
        "Remux": remux,
        "PlayoutRate": playout_rate,
        "TxMode": tx_mode,
        "Power": power,
    })
    return {"status": "ok"}


@mcp.tool()
def set_tsg_pars(
    type: int,
    pid: int,
    vid_std: int = 0,
    flags: int = 0,
) -> dict:
    """Set test signal generator parameters.

    Args:
        type: SPRC.TSG_TYPE_* — PRBS7=0 / PRBS15=1 / PRBS23=2 / PRBS31=3 /
              SDI_STATIC_NO_AUDIO=5 (SMPTE RP-198, no audio) /
              SDI_DYNAMIC_NO_AUDIO=6 / SDI_STATIC=7 (SMPTE RP-198) /
              SDI_DYNAMIC=8 (DekTec bouncing blocks).
              TS_CNT=4 is DekTec-internal. RP-219-1 requires SpRcApi v1.12
              (the vendored layer is v1.11), so it is not available.
        pid: PID carrying the generated stream (ignored in SDI mode).
        vid_std: SPRC.VIDSTD_* (only for SDI generators). Common values:
                 525I59_94=0x01, 625I50=0x02, 720P50=0x08, 1080I50=0x0B,
                 1080P50=0x13, 2160P50=0x24. 40 standards are defined — see
                 sprc_import/SPRC_constants.py. Note 0 is NOT a valid standard.
        flags: Reserved, set to 0.
    """
    client = get_client()
    client.set_tsg_pars({"Type": type, "Pid": pid, "VidStd": vid_std, "Flags": flags})
    return {"status": "ok"}


@mcp.tool()
def set_dvb_t2_group(group_name: str, group_ref_name: str) -> dict:
    """Select a DVB-T2 parameter group.

    Args:
        group_name: Group name, e.g. "VV1xx".
        group_ref_name: Specific set in the group, e.g. "VV100".
    """
    client = get_client()
    client.set_dvb_t2_group({"GroupName": group_name, "GroupRefName": group_ref_name})
    return {"status": "ok"}


@mcp.tool()
def set_mod_pars(mod_pars: dict) -> dict:
    """Set modulation parameters for the selected modulator port.

    Args:
        mod_pars: dict with keys ModType (DTAPI.MOD_* — NOT SPRC.MOD_*, the two
                  namespaces have different values; SPRC.MOD_* is only for
                  select_port's modulation argument), ParXtra0/1/2 (int),
                  SymRate (int baud, -1 if unused).
    """
    client = get_client()
    client.set_mod_pars(mod_pars)
    return {"status": "ok"}


@mcp.tool()
def set_channel_modelling_pars(cm_pars: dict) -> dict:
    """Set channel modelling parameters (noise injection + multi-path).

    Note: the vendored SpRcApi is v1.11, so the v1.12 UseManualSeed/ManualSeed fields are NOT supported.

    Args:
        cm_pars: dict with keys CmEnable (bool), AwgnEnable (bool), Snr (float dB),
                 PathsEnable (bool), Paths (list of up to 32
                 {Type, Attenuation, Delay, Phase, Doppler}).
                 Path Type: SPRC.CONSTANT_DELAY=0 (constant delay/phase),
                 CONSTANT_DOPPLER=1, RAYLEIGH_JAKES=2 (mobile-path model),
                 RAYLEIGH_GAUSSIAN=3 (ionospheric model).
                 Constraints: total attenuation across all paths must not exceed
                 0 dB or the channel simulator overflows (call normalise to
                 enforce); max delay is 896 us for an 8 MHz channel. Phase is
                 ignored for both Rayleigh types; Doppler is ignored for
                 CONSTANT_DELAY.
    """
    client = get_client()
    client.set_channel_modelling_pars(cm_pars)
    return {"status": "ok"}


@mcp.tool()
def set_dvb_t2_pars(dvb_t2_pars: dict) -> dict:
    """Set DVB-T2 modulation parameters (follows SpRcDvbT2Pars field names).

    All 36 fields are required. Easiest path: call get_dvb_t2_pars() first and
    edit the returned dict, keeping the exact SpRcDvbT2Pars field names
    (Bandwidth=DTAPI.DVBT2_8MHZ, FftMode=DTAPI.DVBT2_FFT_8K, ...). Optional
    FollowMode defaults to SPRC.T2_FOLLOW_OFF.
    """
    client = get_client()
    client.set_dvb_t2_pars(dvb_t2_pars)
    return {"status": "ok"}


@mcp.tool()
def set_isdb_t_pars(isdb_t_pars: dict) -> dict:
    """Set ISDB-T modulation parameters.

    Args:
        isdb_t_pars: dict with keys DoMux, BType, Mode, Guard, PartialRx, Emergency, IipPid,
                     LayerPars (list of {NumSegments, Modulation, CodeRate, TimeInterleave}),
                     Pid2Layer (dict PID->layer flags), LayerOther, ParXtra0, Virtual13Segm.
    """
    client = get_client()
    client.set_isdb_t_pars(isdb_t_pars)
    return {"status": "ok"}


@mcp.tool()
def set_tdt_adapt_pars(tdt_adapt_pars: dict) -> dict:
    """Set TDT/TOT adaptation parameters.

    Args:
        tdt_adapt_pars: dict with key TdtAdaptMode (SPRC.TDT_ADAPT_*), and when mode is
                        SPRC.TDT_ADAPT_USE_SPECIFIED, key TdtDateTime = {Year, Month, Day, Hour, Minute, Second}.
    """
    client = get_client()
    client.set_tdt_adapt_pars(tdt_adapt_pars)
    return {"status": "ok"}


@mcp.tool()
def set_playout_state_sfn(playout_state: int, sfn_start_time: int = 0) -> dict:
    """Start/stop SFN-synchronised playout with an absolute GPS start time.

    Args:
        playout_state: SPRC.STATE_PLAY=1 or SPRC.STATE_STOP=2.
        sfn_start_time: GPS start time in ns, 0..999,999,999 (ignored on stop).
    """
    client = get_client()
    client.set_playout_state_sfn(playout_state, sfn_start_time)
    return {"status": "ok", "playout_state": playout_state, "sfn_start_time": sfn_start_time}


@mcp.tool()
def wait_for_condition(condition: int, timeout_ms: int = -1) -> dict:
    """Block until the playout server reports a condition, or the timeout elapses.

    Args:
        condition: SPRC.COND_STOPPED=1 (player is in stopped state).
        timeout_ms: Wait timeout in ms; -1 (default) waits forever.

    Warning: this call blocks the MCP server until the condition is met.
    """
    client = get_client()
    client.wait_for_condition(condition, timeout_ms)
    return {"status": "ok", "condition": condition}


# ── Launch tool ──

@mcp.tool()
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    at the repository root, starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with connect.
    """
    return launch_streamxpress(load_config())

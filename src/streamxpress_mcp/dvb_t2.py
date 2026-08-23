"""Everyday DVB-T2 preset helpers: human-readable aliases to DTAPI constants."""

from .sprc_import import DTAPI

# Keys are matched after strip/upper and removing spaces and hyphens.
# Underscores and slashes are kept so "1/128" and "1_128" stay distinct.
_BANDWIDTH = {
    "1.7MHZ": DTAPI.DVBT2_1_7MHZ,
    "1.7": DTAPI.DVBT2_1_7MHZ,
    "DVBT2_1_7MHZ": DTAPI.DVBT2_1_7MHZ,
    "5MHZ": DTAPI.DVBT2_5MHZ,
    "5": DTAPI.DVBT2_5MHZ,
    "DVBT2_5MHZ": DTAPI.DVBT2_5MHZ,
    "6MHZ": DTAPI.DVBT2_6MHZ,
    "6": DTAPI.DVBT2_6MHZ,
    "DVBT2_6MHZ": DTAPI.DVBT2_6MHZ,
    "7MHZ": DTAPI.DVBT2_7MHZ,
    "7": DTAPI.DVBT2_7MHZ,
    "DVBT2_7MHZ": DTAPI.DVBT2_7MHZ,
    "8MHZ": DTAPI.DVBT2_8MHZ,
    "8M": DTAPI.DVBT2_8MHZ,
    "8": DTAPI.DVBT2_8MHZ,
    "DVBT2_8MHZ": DTAPI.DVBT2_8MHZ,
    "10MHZ": DTAPI.DVBT2_10MHZ,
    "10": DTAPI.DVBT2_10MHZ,
    "DVBT2_10MHZ": DTAPI.DVBT2_10MHZ,
}

_FFT_MODE = {
    "1K": DTAPI.DVBT2_FFT_1K,
    "FFT_1K": DTAPI.DVBT2_FFT_1K,
    "DVBT2_FFT_1K": DTAPI.DVBT2_FFT_1K,
    "2K": DTAPI.DVBT2_FFT_2K,
    "FFT_2K": DTAPI.DVBT2_FFT_2K,
    "DVBT2_FFT_2K": DTAPI.DVBT2_FFT_2K,
    "4K": DTAPI.DVBT2_FFT_4K,
    "FFT_4K": DTAPI.DVBT2_FFT_4K,
    "DVBT2_FFT_4K": DTAPI.DVBT2_FFT_4K,
    "8K": DTAPI.DVBT2_FFT_8K,
    "FFT_8K": DTAPI.DVBT2_FFT_8K,
    "DVBT2_FFT_8K": DTAPI.DVBT2_FFT_8K,
    "16K": DTAPI.DVBT2_FFT_16K,
    "FFT_16K": DTAPI.DVBT2_FFT_16K,
    "DVBT2_FFT_16K": DTAPI.DVBT2_FFT_16K,
    "32K": DTAPI.DVBT2_FFT_32K,
    "32": DTAPI.DVBT2_FFT_32K,
    "FFT_32K": DTAPI.DVBT2_FFT_32K,
    "DVBT2_FFT_32K": DTAPI.DVBT2_FFT_32K,
}

_GUARD = {
    "1/128": DTAPI.DVBT2_GI_1_128,
    "1:128": DTAPI.DVBT2_GI_1_128,
    "1_128": DTAPI.DVBT2_GI_1_128,
    "GI_1_128": DTAPI.DVBT2_GI_1_128,
    "DVBT2_GI_1_128": DTAPI.DVBT2_GI_1_128,
    "1/32": DTAPI.DVBT2_GI_1_32,
    "1:32": DTAPI.DVBT2_GI_1_32,
    "1_32": DTAPI.DVBT2_GI_1_32,
    "GI_1_32": DTAPI.DVBT2_GI_1_32,
    "DVBT2_GI_1_32": DTAPI.DVBT2_GI_1_32,
    "1/16": DTAPI.DVBT2_GI_1_16,
    "1:16": DTAPI.DVBT2_GI_1_16,
    "1_16": DTAPI.DVBT2_GI_1_16,
    "GI_1_16": DTAPI.DVBT2_GI_1_16,
    "DVBT2_GI_1_16": DTAPI.DVBT2_GI_1_16,
    "19/256": DTAPI.DVBT2_GI_19_256,
    "19:256": DTAPI.DVBT2_GI_19_256,
    "19_256": DTAPI.DVBT2_GI_19_256,
    "GI_19_256": DTAPI.DVBT2_GI_19_256,
    "DVBT2_GI_19_256": DTAPI.DVBT2_GI_19_256,
    "1/8": DTAPI.DVBT2_GI_1_8,
    "1:8": DTAPI.DVBT2_GI_1_8,
    "1_8": DTAPI.DVBT2_GI_1_8,
    "GI_1_8": DTAPI.DVBT2_GI_1_8,
    "DVBT2_GI_1_8": DTAPI.DVBT2_GI_1_8,
    "19/128": DTAPI.DVBT2_GI_19_128,
    "19:128": DTAPI.DVBT2_GI_19_128,
    "19_128": DTAPI.DVBT2_GI_19_128,
    "GI_19_128": DTAPI.DVBT2_GI_19_128,
    "DVBT2_GI_19_128": DTAPI.DVBT2_GI_19_128,
    "1/4": DTAPI.DVBT2_GI_1_4,
    "1:4": DTAPI.DVBT2_GI_1_4,
    "1_4": DTAPI.DVBT2_GI_1_4,
    "GI_1_4": DTAPI.DVBT2_GI_1_4,
    "DVBT2_GI_1_4": DTAPI.DVBT2_GI_1_4,
}

_CONSTELLATION = {
    "BPSK": DTAPI.DVBT2_BPSK,
    "DVBT2_BPSK": DTAPI.DVBT2_BPSK,
    "QPSK": DTAPI.DVBT2_QPSK,
    "DVBT2_QPSK": DTAPI.DVBT2_QPSK,
    "16QAM": DTAPI.DVBT2_QAM16,
    "QAM16": DTAPI.DVBT2_QAM16,
    "16": DTAPI.DVBT2_QAM16,
    "DVBT2_QAM16": DTAPI.DVBT2_QAM16,
    "64QAM": DTAPI.DVBT2_QAM64,
    "QAM64": DTAPI.DVBT2_QAM64,
    "64": DTAPI.DVBT2_QAM64,
    "DVBT2_QAM64": DTAPI.DVBT2_QAM64,
    "256QAM": DTAPI.DVBT2_QAM256,
    "QAM256": DTAPI.DVBT2_QAM256,
    "256": DTAPI.DVBT2_QAM256,
    "DVBT2_QAM256": DTAPI.DVBT2_QAM256,
}


def _norm_key(value: str) -> str:
    return value.strip().upper().replace(" ", "").replace("-", "")


def _lookup(value: str | int, table: dict[str, int], kind: str) -> int:
    allowed_ints = set(table.values())
    if isinstance(value, bool):
        raise ValueError(f"invalid {kind}: {value!r}")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"invalid {kind}: {value!r}")
        value = int(value)
    if isinstance(value, int):
        if value in allowed_ints:
            return value
        raise ValueError(f"invalid {kind} constant: {value!r}")
    if not isinstance(value, str):
        raise ValueError(f"invalid {kind}: {value!r}")
    key = _norm_key(value)
    if key in table:
        return table[key]
    raise ValueError(
        f"invalid {kind}: {value!r}. Use a label (e.g. 8MHz, 32K, 1/128, 256QAM) "
        f"or a DTAPI.DVBT2_* constant"
    )


def parse_dvbt2_bandwidth(value: str | int) -> int:
    return _lookup(value, _BANDWIDTH, "bandwidth")


def parse_dvbt2_fft_mode(value: str | int) -> int:
    return _lookup(value, _FFT_MODE, "fft_mode")


def parse_dvbt2_guard_interval(value: str | int) -> int:
    return _lookup(value, _GUARD, "guard_interval")


def parse_dvbt2_constellation(value: str | int) -> int:
    return _lookup(value, _CONSTELLATION, "constellation")


def parse_frequency_hz(value: int | float) -> int:
    if isinstance(value, bool):
        raise ValueError(f"invalid frequency_hz: {value!r}")
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"invalid frequency_hz: {value!r}")
        value = int(value)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"frequency_hz must be a positive integer, got {value!r}")
    return value


def parse_cell_id(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"invalid cell_id: {value!r}")
    if value < 0 or value > 0xFFFF:
        raise ValueError(f"cell_id must be 0..65535, got {value!r}")
    return value

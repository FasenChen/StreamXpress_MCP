# StreamXpress MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python MCP server that wraps DekTec StreamXpress's SpRcApi (SOAP Remote Control API), allowing an AI agent to control TS (Transport Stream) playout — scanning devices, selecting ports, loading files, setting TS-over-IP parameters, and managing playback — all via MCP tools.

**Architecture:** A FastMCP server (`mcp` Python SDK) exposes ~10 tools. Each tool delegates to a singleton client wrapper (`StreamXpressClient`) that manages a `SPRC_client` SOAP session. The official `SpRcImport` package (SPRC_client.py + SPRC_types.py + SPRC_constants.py + DTAPI_constants.py + SpRc.wsdl) is vendored into the project as `src/streamxpress_mcp/sprc_import/`. Tests use pytest with a mock SPRC_client — no real StreamXpress or DekTec hardware required for CI.

**Tech Stack:** Python 3.14, `mcp[cli]` (FastMCP), `zeep` (SOAP), pytest

## Global Constraints

- Python >= 3.10 (tested on 3.14)
- All MCP tools return JSON-serializable responses (dict / list / str / int / float / bool)
- Tool names prefixed with `streamxpress_` to avoid name collisions in MCP namespace
- Connection state is managed server-side — tools fail gracefully with a clear error message if not connected
- No hardcoded credentials or IPs — all connection params come from environment variables or tool arguments
- Each task ends with a focused git commit; commit messages follow `type(scope): description` convention

---

## File Structure

```
StreamXpress_MCP/
├── src/
│   └── streamxpress_mcp/
│       ├── __init__.py           # Package marker, re-exports
│       ├── __main__.py           # Entry point: python -m streamxpress_mcp
│       ├── server.py             # FastMCP instance + all @mcp.tool() registrations
│       ├── client.py             # StreamXpressClient: singleton wrapper around SPRC_client
│       └── sprc_import/          # Vendored from official SpRcPythonExamples
│           ├── __init__.py
│           ├── SPRC_client.py
│           ├── SPRC_types.py
│           ├── SPRC_constants.py
│           ├── DTAPI_constants.py
│           └── SpRc.wsdl
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures: mock_sprc_client
│   └── test_server.py            # Unit tests for all MCP tools
├── docs/superpowers/plans/
│   └── 2026-08-06-streamxpress-mcp.md  # This plan
├── pyproject.toml                # Project metadata, dependencies, scripts
├── README.md                     # Usage + MCP client config example
└── .gitignore                    # Python + IDE ignores
```

---

### Task 1: Initialize project skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/streamxpress_mcp/__init__.py`
- Create: `tests/__init__.py`

**Interfaces:**
- Produces: `pyproject.toml` with project name `streamxpress-mcp`, dependencies `mcp[cli]>=1.0`, `zeep>=4.2`
- Produces: `.gitignore` covering `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`, `.pytest_cache/`, `dist/`

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "streamxpress-mcp"
version = "0.1.0"
description = "MCP server for DekTec StreamXpress remote control via SpRcApi"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0",
    "zeep>=4.2",
]

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
streamxpress-mcp = "streamxpress_mcp.__main__:main"

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Write .gitignore**

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/
dist/
.pytest_cache/
*.wsdl      # Temporary WSDL files generated at runtime
```

- [ ] **Step 3: Write empty __init__.py files**

```python
# src/streamxpress_mcp/__init__.py
```

```python
# tests/__init__.py
```

- [ ] **Step 4: Install dependencies and verify**

Run:
```powershell
cd D:\Code\StreamXpress_MCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -c "import mcp; print('mcp', mcp.__version__)"
python -c "import zeep; print('zeep', zeep.__version__)"
```

Expected: Both imports succeed with version numbers printed.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml .gitignore src/streamxpress_mcp/__init__.py tests/__init__.py
git commit -m "chore: initialize project skeleton with pyproject.toml and .gitignore"
```

---

### Task 2: Vendor official SpRcImport package

**Files:**
- Create: `src/streamxpress_mcp/sprc_import/__init__.py`
- Create: `src/streamxpress_mcp/sprc_import/SPRC_client.py`
- Create: `src/streamxpress_mcp/sprc_import/SPRC_types.py`
- Create: `src/streamxpress_mcp/sprc_import/SPRC_constants.py`
- Create: `src/streamxpress_mcp/sprc_import/DTAPI_constants.py`
- Create: `src/streamxpress_mcp/sprc_import/SpRc.wsdl`
- Source: `StreamXpress_Official_Data/SpRcPythonExamples/SpRcPythonExamples/SpRcImport/`

**Interfaces:**
- Produces: `sprc_import.SPRC_client` (class), `sprc_import.SPRC_types` (dataclasses), `sprc_import.SPRC_constants` (class), `sprc_import.DTAPI_constants` (class), `sprc_import.SpRc.wsdl` (WSDL template)

- [ ] **Step 1: Copy all SpRcImport files**

Run:
```powershell
Copy-Item -Path "StreamXpress_Official_Data/SpRcPythonExamples/SpRcPythonExamples/SpRcImport/*" -Destination "src/streamxpress_mcp/sprc_import/" -Recurse -Force
```

- [ ] **Step 2: Update __init__.py to re-export key symbols**

Write `src/streamxpress_mcp/sprc_import/__init__.py`:

```python
from .SPRC_client import SPRC_client
from .SPRC_types import (
    SpRcAsiPars,
    SpRcModPars,
    SpRcPortDesc,
    SpRcPlayoutInfo,
    SpRcPlayoutStatus,
    SpRcRfPars,
    SpRcTsoipPars,
    SpRcVersion,
    SpRcException,
    SPRC_RESULT,
)
from .SPRC_constants import SPRC
from .DTAPI_constants import DTAPI

__all__ = [
    "SPRC_client",
    "SpRcAsiPars", "SpRcModPars", "SpRcPortDesc",
    "SpRcPlayoutInfo", "SpRcPlayoutStatus",
    "SpRcRfPars", "SpRcTsoipPars", "SpRcVersion",
    "SpRcException", "SPRC_RESULT",
    "SPRC", "DTAPI",
]
```

- [ ] **Step 3: Update package __init__.py to re-export sprc_import**

Write `src/streamxpress_mcp/__init__.py`:

```python
from .sprc_import import (
    SPRC_client, SPRC, DTAPI,
    SpRcAsiPars, SpRcModPars, SpRcPortDesc,
    SpRcPlayoutInfo, SpRcPlayoutStatus,
    SpRcRfPars, SpRcTsoipPars, SpRcVersion,
    SpRcException, SPRC_RESULT,
)

from .client import StreamXpressClient
from .server import mcp

__all__ = [
    "SPRC_client", "SPRC", "DTAPI",
    "SpRcAsiPars", "SpRcModPars", "SpRcPortDesc",
    "SpRcPlayoutInfo", "SpRcPlayoutStatus",
    "SpRcRfPars", "SpRcTsoipPars", "SpRcVersion",
    "SpRcException", "SPRC_RESULT",
    "StreamXpressClient", "mcp",
]
```

- [ ] **Step 4: Smoke-test the import**

Run:
```powershell
python -c "from streamxpress_mcp.sprc_import import SPRC_client, SPRC, SpRcTsoipPars; print('import OK')"
```

Expected: `import OK` (note: `zeep` is required at import time — this verifies our dependency install from Task 1 works).

- [ ] **Step 5: Commit**

```bash
git add src/streamxpress_mcp/sprc_import/ src/streamxpress_mcp/__init__.py
git commit -m "feat: vendor official SpRcImport package from StreamXpress Python examples"
```

---

### Task 3: Implement StreamXpressClient singleton wrapper

**Files:**
- Create: `src/streamxpress_mcp/client.py`
- Modify: `src/streamxpress_mcp/__init__.py` (already imports from `client`, no change needed)

**Interfaces:**
- Produces: `StreamXpressClient` class with methods `connect(host, port) -> None`, `disconnect() -> None`, `_ensure_connected() -> None`, `scan_ports() -> list[SpRcPortDesc]`, `select_port(serial, port, modulation) -> None`, `open_file(filepath) -> None`, `start() -> None`, `stop() -> None`, `get_status() -> dict`, `set_rate(bps) -> None`, `set_tsoip_params(...) -> None`, `set_rf_params(freq_hz, level_dbm) -> None`, `set_asi_params(remux, playout_rate, tx_mode) -> None`, `close() -> None`
- Consumes: `sprc_import.SPRC_client`, `sprc_import.SPRC_types`, `sprc_import.SPRC_constants`, `sprc_import.SPRC_RESULT`, `sprc_import.SpRcException`

- [ ] **Step 1: Write the failing test for connect/disconnect**

Write `tests/conftest.py`:

```python
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_sprc():
    """Return a MagicMock that mimics SPRC_client."""
    return MagicMock()


@pytest.fixture
def client(mock_sprc):
    """Return a StreamXpressClient with SPRC_client patched."""
    with patch(
        "streamxpress_mcp.client.SPRC_client", return_value=mock_sprc
    ):
        from streamxpress_mcp.client import StreamXpressClient

        return StreamXpressClient()
```

Write `tests/test_server.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```powershell
pytest tests/test_server.py::TestStreamXpressConnect -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'streamxpress_mcp.client'`

- [ ] **Step 3: Write StreamXpressClient implementation**

Write `src/streamxpress_mcp/client.py`:

```python
"""StreamXpressClient: singleton wrapper around SPRC_client for MCP server use."""

from .sprc_import import SPRC_client, SpRcPortDesc, SpRcException, SPRC_RESULT
from .sprc_import import SpRcAsiPars, SpRcTsoipPars, SpRcRfPars, SpRcModPars
from .sprc_import import SPRC, DTAPI


class StreamXpressClient:
    """Thin wrapper managing a single SPRC_client SOAP session."""

    def __init__(self):
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
        self._sprc = SPRC_client()
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
            "file_name": info.FileName,
            "ts_rate_bps": info.TsRateBps,
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```powershell
pytest tests/test_server.py::TestStreamXpressConnect -v
```

Expected: 4 PASS

- [ ] **Step 5: Add tests for all other client methods**

Append to `tests/test_server.py`:

```python
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
            PosRel=0.5, NumWraps=0, PosAbs=0, NativeRate=0, OutRate=0
        )
        mock_sprc.get_playout_info.return_value = SpRcPlayoutInfo(
            PlayoutState=1, FileName="test.ts", TsRateBps=25_000_000
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
```

- [ ] **Step 6: Run all client tests**

Run:
```powershell
pytest tests/test_server.py -v
```

Expected: ALL PASS (8+ tests)

- [ ] **Step 7: Commit**

```bash
git add src/streamxpress_mcp/client.py tests/conftest.py tests/test_server.py
git commit -m "feat(client): add StreamXpressClient singleton wrapper with tests"
```

---

### Task 4: Implement MCP server with connection-management tools

**Files:**
- Create: `src/streamxpress_mcp/server.py`
- Modify: `tests/test_server.py` (add server-level tests)

**Interfaces:**
- Produces: `mcp` (FastMCP instance), tools: `streamxpress_connect`, `streamxpress_disconnect`
- Consumes: `StreamXpressClient` from `client.py`

- [ ] **Step 1: Write failing server tests**

Append to `tests/test_server.py`:

```python
from unittest.mock import patch


class TestServerConnectTool:
    @patch("streamxpress_mcp.server.get_client")
    def test_connect_tool_succeeds(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_connect

        result = streamxpress_connect(host="http://localhost", port=5000)
        assert result["status"] == "connected"
        mock_client.connect.assert_called_once_with(host="http://localhost", port=5000)

    @patch("streamxpress_mcp.server.get_client")
    def test_disconnect_tool_succeeds(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_disconnect

        result = streamxpress_disconnect()
        assert result["status"] == "disconnected"
        mock_client.disconnect.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```powershell
pytest tests/test_server.py::TestServerConnectTool -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'streamxpress_mcp.server'`

- [ ] **Step 3: Write server.py with connect/disconnect tools**

Write `src/streamxpress_mcp/server.py`:

```python
"""StreamXpress MCP Server — FastMCP instance with tool registrations."""

from mcp.server.fastmcp import FastMCP

from .client import StreamXpressClient

# ── FastMCP application ──

mcp = FastMCP("streamxpress-mcp")

# ── Global client singleton ──

_client: StreamXpressClient | None = None


def get_client() -> StreamXpressClient:
    """Return the global singleton client, creating it if needed."""
    global _client
    if _client is None:
        _client = StreamXpressClient()
    return _client


# ── Connection tools ──

@mcp.tool()
def streamxpress_connect(host: str, port: int) -> dict:
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
def streamxpress_disconnect() -> dict:
    """Disconnect from the StreamXpress remote-control session."""
    client = get_client()
    client.disconnect()
    return {"status": "disconnected"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```powershell
pytest tests/test_server.py::TestServerConnectTool -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add src/streamxpress_mcp/server.py tests/test_server.py
git commit -m "feat(server): add MCP server with connect/disconnect tools"
```

---

### Task 5: Add port-discovery and file-loading tools

**Files:**
- Modify: `src/streamxpress_mcp/server.py` (add new tools)
- Modify: `tests/test_server.py` (add tests for new tools)

**Interfaces:**
- Produces: `streamxpress_scan_ports() -> list[dict]`, `streamxpress_select_port(serial, port_num, modulation) -> dict`, `streamxpress_open_file(filepath) -> dict`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_server.py`:

```python
class TestServerPortTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_scan_ports_returns_port_list(self, mock_get_client):
        from streamxpress_mcp.sprc_import import SpRcPortDesc

        mock_client = MagicMock()
        mock_client.scan_ports.return_value = [
            SpRcPortDesc(
                Serial=217400001, TypeNumber=2174, Ip=bytes(4), Mac=bytes(6),
                FirmwareVersion=100, FirmwareVariant=0, Port=1,
                OutputType=0x00001, Capabilities=0, InUse=0,
            )
        ]
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_scan_ports
        result = streamxpress_scan_ports()

        assert len(result) == 1
        assert result[0]["serial"] == 217400001
        assert result[0]["type_number"] == 2174
        assert "ASI" in result[0]["output_types"]

    @patch("streamxpress_mcp.server.get_client")
    def test_select_port_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_select_port
        result = streamxpress_select_port(serial=217400001, port_num=1, modulation=0)

        assert result["status"] == "ok"
        mock_client.select_port.assert_called_once_with(217400001, 1, 0)

    @patch("streamxpress_mcp.server.get_client")
    def test_open_file_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_open_file
        result = streamxpress_open_file("C:\\Streams\\test.ts")

        assert result["status"] == "ok"
        mock_client.open_file.assert_called_once_with("C:\\Streams\\test.ts")
```

- [ ] **Step 2: Run to verify tests fail**

Run:
```powershell
pytest tests/test_server.py::TestServerPortTools -v
```

Expected: FAIL (tools not defined in server.py)

- [ ] **Step 3: Add tools to server.py**

Append to `src/streamxpress_mcp/server.py` (after the disconnect tool):

```python
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


def _describe_output_type(flags: int) -> list[str]:
    """Convert OutputType bitmask to human-readable labels."""
    labels = []
    for mask, name in OUTPUT_TYPE_LABELS.items():
        if flags & mask:
            labels.append(name)
    return labels


@mcp.tool()
def streamxpress_scan_ports() -> list[dict]:
    """Scan for available output ports on the connected StreamXpress.

    Returns a list of port descriptors with serial, type, and output capabilities.
    """
    client = get_client()
    ports = client.scan_ports()
    return [
        {
            "serial": p.Serial,
            "type_number": p.TypeNumber,
            "port": p.Port,
            "output_types": _describe_output_type(p.OutputType),
            "in_use": p.InUse != 0,
        }
        for p in ports
    ]


@mcp.tool()
def streamxpress_select_port(serial: int, port_num: int, modulation: int = 0) -> dict:
    """Select a physical output port for playout.

    Args:
        serial: Device serial number (from scan_ports)
        port_num: Physical port number on the device
        modulation: Initial modulation standard (0=none, use SPRC.MOD_* constants)
    """
    client = get_client()
    client.select_port(serial, port_num, modulation)
    return {"status": "ok", "serial": serial, "port": port_num}


@mcp.tool()
def streamxpress_open_file(filepath: str) -> dict:
    """Open a TS file for playout.

    Args:
        filepath: Full path to the .ts file or StreamXpress .xml settings file
    """
    client = get_client()
    client.open_file(filepath)
    return {"status": "ok", "file": filepath}
```

- [ ] **Step 4: Run tests**

Run:
```powershell
pytest tests/test_server.py::TestServerPortTools -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/streamxpress_mcp/server.py tests/test_server.py
git commit -m "feat(server): add port-discovery and file-loading tools"
```

---

### Task 6: Add playback-control and status tools

**Files:**
- Modify: `src/streamxpress_mcp/server.py` (add tools)
- Modify: `tests/test_server.py` (add tests)

**Interfaces:**
- Produces: `streamxpress_start() -> dict`, `streamxpress_stop() -> dict`, `streamxpress_get_status() -> dict`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_server.py`:

```python
class TestServerPlayoutTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_start_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_start
        result = streamxpress_start()

        assert result["status"] == "playing"
        mock_client.start.assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_stop_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_stop
        result = streamxpress_stop()

        assert result["status"] == "stopped"
        mock_client.stop.assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_get_status_returns_dict(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.get_status.return_value = {
            "position_percent": 75.5,
            "num_wraps": 2,
            "playout_state": 1,
            "file_name": "test.ts",
            "ts_rate_bps": 25_000_000,
        }
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_get_status
        result = streamxpress_get_status()

        assert result["position_percent"] == 75.5
        assert result["file_name"] == "test.ts"
```

- [ ] **Step 2: Run to verify tests fail**

Run:
```powershell
pytest tests/test_server.py::TestServerPlayoutTools -v
```

Expected: FAIL

- [ ] **Step 3: Add tools to server.py**

Append to `src/streamxpress_mcp/server.py`:

```python
# ── Playback control tools ──

@mcp.tool()
def streamxpress_start() -> dict:
    """Start TS playout on the selected port."""
    client = get_client()
    client.start()
    return {"status": "playing"}


@mcp.tool()
def streamxpress_stop() -> dict:
    """Stop TS playout."""
    client = get_client()
    client.stop()
    return {"status": "stopped"}


@mcp.tool()
def streamxpress_get_status() -> dict:
    """Get current playout status including position, wraps, filename, and bitrate."""
    client = get_client()
    return client.get_status()
```

- [ ] **Step 4: Run tests**

Run:
```powershell
pytest tests/test_server.py::TestServerPlayoutTools -v
```

Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add src/streamxpress_mcp/server.py tests/test_server.py
git commit -m "feat(server): add playback-control and status tools"
```

---

### Task 7: Add parameter-setting tools

**Files:**
- Modify: `src/streamxpress_mcp/server.py` (add tools)
- Modify: `tests/test_server.py` (add tests)

**Interfaces:**
- Produces: `streamxpress_set_rate(bps) -> dict`, `streamxpress_set_tsoip_params(dest_ip, dest_port, ...) -> dict`, `streamxpress_set_rf_params(frequency_hz, level_dbm) -> dict`, `streamxpress_set_asi_params(remux, playout_rate, tx_mode) -> dict`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_server.py`:

```python
class TestServerParamTools:
    @patch("streamxpress_mcp.server.get_client")
    def test_set_rate_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_set_rate
        result = streamxpress_set_rate(25_000_000)

        assert result["status"] == "ok"
        assert result["rate_bps"] == 25_000_000
        mock_client.set_rate.assert_called_once_with(25_000_000)

    @patch("streamxpress_mcp.server.get_client")
    def test_set_tsoip_params_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_set_tsoip_params
        result = streamxpress_set_tsoip_params(
            dest_ip="239.1.1.1", dest_port=1234,
            num_tp_per_ip=7, protocol="UDP", ttl=64,
        )

        assert result["status"] == "ok"
        assert result["dest_ip"] == "239.1.1.1"
        mock_client.set_tsoip_params.assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_set_rf_params_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_set_rf_params
        result = streamxpress_set_rf_params(frequency_hz=500_000_000, level_dbm=-37.5)

        assert result["status"] == "ok"
        assert result["frequency_hz"] == 500_000_000
        mock_client.set_rf_params.assert_called_once()

    @patch("streamxpress_mcp.server.get_client")
    def test_set_asi_params_returns_ok(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        from streamxpress_mcp.server import streamxpress_set_asi_params
        result = streamxpress_set_asi_params(remux=True, playout_rate=20_000_000, tx_mode=0)

        assert result["status"] == "ok"
        mock_client.set_asi_params.assert_called_once()
```

- [ ] **Step 2: Run to verify tests fail**

Run:
```powershell
pytest tests/test_server.py::TestServerParamTools -v
```

Expected: FAIL

- [ ] **Step 3: Add tools to server.py**

Append to `src/streamxpress_mcp/server.py`:

```python
# ── Parameter tools ──

@mcp.tool()
def streamxpress_set_rate(rate_bps: int) -> dict:
    """Set the TS playout bitrate in bits per second (188-byte packets).

    Args:
        rate_bps: Target bitrate, e.g. 25_000_000 for 25 Mbps
    """
    client = get_client()
    client.set_rate(rate_bps)
    return {"status": "ok", "rate_bps": rate_bps}


@mcp.tool()
def streamxpress_set_tsoip_params(
    dest_ip: str,
    dest_port: int,
    num_tp_per_ip: int = 7,
    protocol: str = "UDP",
    ttl: int = 64,
    fec_rows: int = 0,
    fec_cols: int = 0,
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
    )
    return {
        "status": "ok",
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "protocol": protocol,
    }


@mcp.tool()
def streamxpress_set_rf_params(frequency_hz: int, level_dbm: float) -> dict:
    """Set RF output frequency and level (modulator ports only).

    Args:
        frequency_hz: Center frequency in Hz, e.g. 500_000_000 for 500 MHz
        level_dbm: Output level in dBm, e.g. -37.5
    """
    client = get_client()
    client.set_rf_params(frequency_hz, level_dbm)
    return {"status": "ok", "frequency_hz": frequency_hz, "level_dbm": level_dbm}


@mcp.tool()
def streamxpress_set_asi_params(
    remux: bool = True,
    playout_rate: int = 0,
    tx_mode: int = 0,
) -> dict:
    """Set ASI output parameters.

    Args:
        remux: Enable real-time remultiplexing (add null packets to match output rate)
        playout_rate: Output rate in bps (0 = use file native rate)
        tx_mode: 0=188-byte packets, 2=204-byte (Add16), 3=188-from-204 (Min16)
    """
    client = get_client()
    client.set_asi_params(remux=remux, playout_rate=playout_rate, tx_mode=tx_mode)
    return {"status": "ok"}
```

- [ ] **Step 4: Run all tests**

Run:
```powershell
pytest tests/ -v
```

Expected: ALL PASS (>15 tests)

- [ ] **Step 5: Commit**

```bash
git add src/streamxpress_mcp/server.py tests/test_server.py
git commit -m "feat(server): add parameter-setting tools (rate, TSoIP, RF, ASI)"
```

---

### Task 8: Add __main__.py entry point

**Files:**
- Create: `src/streamxpress_mcp/__main__.py`

**Interfaces:**
- Produces: `main()` function that runs `mcp.run()` via stdio transport
- Consumes: `server.mcp` from `server.py`

- [ ] **Step 1: Write __main__.py**

Write `src/streamxpress_mcp/__main__.py`:

```python
"""Entry point: python -m streamxpress_mcp

Starts the StreamXpress MCP server on stdio transport.
Configure in your MCP client (e.g. Claude Desktop) as:

{
  "mcpServers": {
    "streamxpress": {
      "command": "python",
      "args": ["-m", "streamxpress_mcp"]
    }
  }
}
"""

from .server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the entry point works**

Run:
```powershell
python -m streamxpress_mcp --help 2>&1
```

Expected: FastMCP help text (or a clear error about missing server — at minimum, no import errors).

- [ ] **Step 3: Commit**

```bash
git add src/streamxpress_mcp/__main__.py
git commit -m "feat: add __main__.py entry point for stdio MCP transport"
```

---

### Task 9: Write README with setup and MCP client config

**Files:**
- Create: `README.md`

**Interfaces:**
- Produces: User-facing documentation

- [ ] **Step 1: Write README.md**

Write `README.md`:

````markdown
# StreamXpress MCP Server

MCP (Model Context Protocol) server for [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/), allowing AI agents to control TS (Transport Stream) playout via the SpRcApi remote-control interface.

## Prerequisites

- **StreamXpress** v3.x installed with a **DTC-302-RC license** (remote control)
- A DekTec output adapter with **DTC-300-SP** (playback) or **DTC-300-NICP** (IP via local NIC)
- Python 3.10+

## Quick Start

```powershell
# 1. Clone and install
git clone <repo-url>
cd StreamXpress_MCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# 2. Start StreamXpress in remote-control mode
StreamXpress.exe -rc 5000

# 3. Run the MCP server
python -m streamxpress_mcp
```

## MCP Client Configuration

Add to your MCP client's config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "streamxpress": {
      "command": "python",
      "args": ["-m", "streamxpress_mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

| Tool | Description |
|---|---|
| `streamxpress_connect` | Connect to StreamXpress RC session |
| `streamxpress_disconnect` | Disconnect from session |
| `streamxpress_scan_ports` | List available output ports |
| `streamxpress_select_port` | Select an output port for playout |
| `streamxpress_open_file` | Load a TS file |
| `streamxpress_start` | Start playout |
| `streamxpress_stop` | Stop playout |
| `streamxpress_get_status` | Get playout progress and info |
| `streamxpress_set_rate` | Set TS bitrate (bps) |
| `streamxpress_set_tsoip_params` | Configure UDP/RTP TS-over-IP output |
| `streamxpress_set_rf_params` | Set RF frequency and level |
| `streamxpress_set_asi_params` | Set ASI remux and packet mode |

## Example AI Interaction

```
User: Push C:\Streams\news.ts to multicast 239.1.1.1:1234 at 25 Mbps

AI uses:
  1. streamxpress_connect(host="http://localhost", port=5000)
  2. streamxpress_scan_ports() → pick a TS-over-IP port
  3. streamxpress_select_port(serial=..., port_num=1)
  4. streamxpress_set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="UDP")
  5. streamxpress_set_rate(rate_bps=25_000_000)
  6. streamxpress_open_file(filepath="C:\\Streams\\news.ts")
  7. streamxpress_start()
  8. streamxpress_get_status() → monitor progress
```

## License

This project wraps the DekTec SpRcApi. You must hold valid DekTec licenses (DTC-300-SP + DTC-302-RC) to use this software with StreamXpress.
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup, config, and usage examples"
```

---

### Task 10: Final verification and cleanup

**Files:**
- Verify: `src/streamxpress_mcp/` all files present
- Verify: `tests/` all tests pass

- [ ] **Step 1: Run full test suite**

Run:
```powershell
pytest tests/ -v --tb=short
```

Expected: ALL PASS (all tests green)

- [ ] **Step 2: Verify package structure**

Run:
```powershell
python -c "
from streamxpress_mcp.server import mcp
tools = [t for t in dir(mcp) if not t.startswith('_')]
print('MCP tools available:', len([t for t in mcp._tool_manager._tools]))
"
```

- [ ] **Step 3: Verify git log is clean**

Run:
```powershell
git log --oneline
```

Expected: 9-10 commits with incremental feature messages.

- [ ] **Step 4: Final commit (if anything changed)**

```bash
git status
# If clean, no commit needed. Otherwise:
git add -A
git commit -m "chore: final cleanup after verification"
```

---

## Self-Review Checklist

### 1. Spec Coverage

| Requirement | Task |
|---|---|
| MCP server wrapping SpRcApi | Tasks 3-8 |
| CLI-style codec push (TS-over-IP) | Task 7 (`set_tsoip_params`) + Task 6 (`start/stop`) |
| Device port scanning | Task 5 (`scan_ports`, `select_port`) |
| File loading | Task 5 (`open_file`) |
| Rate control | Task 7 (`set_rate`) |
| ASI output config | Task 7 (`set_asi_params`) |
| RF output config | Task 7 (`set_rf_params`) |
| Git version management | Every task ends with a git commit |
| Tests (unit + integration) | Tasks 3-8 all include pytest tests |
| README / docs | Task 9 |

### 2. Placeholder Scan

No "TBD", "TODO", "implement later" found. All code is concrete. All test code is concrete.

### 3. Type Consistency Check

- `StreamXpressClient` methods match server tool parameter names (e.g. `connect(host, port)` → `streamxpress_connect(host, port)`)
- `get_status()` returns `dict` with keys `position_percent`, `num_wraps`, `playout_state`, `file_name`, `ts_rate_bps` — consistent between `client.py` and test assertions
- `set_tsoip_params` parameter names consistent: `dest_ip`, `dest_port`, `num_tp_per_ip`, `protocol`, `ttl`, `fec_rows`, `fec_cols`
- All tool return types are `dict` or `list[dict]` (JSON-serializable)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

MCP (Model Context Protocol) server that lets AI clients drive **DekTec StreamXpress** TS playout via its SOAP-based `SpRcApi` remote-control interface. The MCP process only speaks HTTP/SOAP to StreamXpress — the two can live on different machines. StreamXpress itself must be started in remote-control mode (`StreamXpress.exe -rc <port>`), which requires DekTec hardware with the `DTC-302-RC` license burned in.

Primary reference: [README.md](README.md) (Chinese; treat as authoritative for licensing constraints and client-setup gotchas).

## Common commands

Install for development (see README for why venv-based installs need extra care in MCP client configs):

```powershell
pip install -e ".[dev]"
```

Run the MCP server on stdio (what MCP clients invoke):

```powershell
python -m streamxpress_mcp
```

Tests (pytest, `testpaths = ["tests"]`):

```powershell
pytest                                # full suite
pytest tests/test_server.py           # one file
pytest tests/test_server.py::test_x   # one test
pytest -k connect                     # by keyword
```

There is no linter/formatter configured — match surrounding style.

## Architecture

Four-layer stack, top to bottom:

1. **MCP tool surface** — [src/streamxpress_mcp/server.py](src/streamxpress_mcp/server.py): a single `FastMCP("streamxpress-mcp")` instance with `@mcp.tool()` functions (`connect`, `disconnect`, `scan_ports`, `select_port`, `open_file`, `start`, `stop`, `get_status`, `set_rate`, `set_tsoip_params`, `set_rf_params`, `set_asi_params`, `launch`). Tool names are **unprefixed** — MCP clients add their own `streamxpress_` prefix at display time. Renaming any tool is a breaking change for connected clients.
2. **Client wrapper** — [src/streamxpress_mcp/client.py](src/streamxpress_mcp/client.py): `StreamXpressClient` holds one `SPRC_client` session, tracks `_connected`, and translates Python-friendly arguments (dotted IP strings, `"UDP"`/`"RTP"` strings, bool flags) into the C-style structs the SOAP layer wants (`SpRcTsoipPars`, `SpRcAsiPars`, `SpRcRfPars`, `DTAPI.*` constants). Injectable via `sprc_factory=` for tests.
3. **Singleton wiring** — `server.py:get_client()` lazily builds the `StreamXpressClient` on first tool call, using `resolve_wsdl_path(load_config())` to decide whether to pass a custom `wsdl_template` to `SPRC_client`. The whole server is stateful around this one client instance.
4. **Vendored SOAP layer** — [src/streamxpress_mcp/sprc_import/](src/streamxpress_mcp/sprc_import/): DekTec-supplied `SPRC_client.py` (zeep-based), types, and `SpRc.wsdl`. Do **not** hand-edit these files; treat them as third-party. The `.wsdl` ships as package data (see `pyproject.toml` `[tool.setuptools.package-data]`). `SPRC_client.__init__` accepts an optional `wsdl_template` path — this is how a user-supplied `sprc_api_path` in `config.json` overrides the bundled WSDL.

Two side utilities:

- [config.py](src/streamxpress_mcp/config.py) — resolves `config.json` in this order: `$STREAMXPRESS_MCP_CONFIG` → `<project root>/config.json` → defaults. Missing file or missing fields is not an error. `PROJECT_ROOT` walks up two parents from the module file, so **non-editable installs (`pip install .`) break the project-root fallback** — users must set the env var. Keep this contract if you touch `config.py`.
- [launcher.py](src/streamxpress_mcp/launcher.py) — the `launch` tool spawns `streamxpress_path -rc <rc_port>` with `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` (Windows-only flags) and polls TCP `127.0.0.1:<port>` for readiness. Not portable to non-Windows without changing the `creationflags`.

## Tests

- [tests/conftest.py](tests/conftest.py) provides a `mock_sprc` MagicMock and a `client` fixture that injects it via `sprc_factory=`. Prefer this fixture over patching module globals — the DI hook exists specifically for tests.
- [tests/test_server.py](tests/test_server.py) exercises the FastMCP tool functions directly (not through the MCP protocol). Reset the module singleton `server._client` between tests when adding new server-level tests.
- Real SOAP calls are never made in tests; the vendored `SPRC_client` is fully stubbed.

## Config file (`config.json`)

Ships in the repo root with empty values — users edit it in place. Recommend `git update-index --skip-worktree config.json` so local edits stay out of git. Fields:

| field | effect |
|---|---|
| `streamxpress_path` | Full path to `StreamXpress.exe`/`StreamXpress64.exe`. Only used by the `launch` tool. |
| `sprc_api_path` | Optional. If set and `<sprc_api_path>/WSDL/SpRc.wsdl` exists, that WSDL replaces the bundled one. |
| `rc_port` | RC listener port for the `launch` tool. Default `5000`. |

## Gotchas

- **StreamXpress.exe is not on PATH** — always invoke with the absolute path (or via the `launch` tool).
- **MCP client `command` gotcha** — if the user installed into a venv, their `mcp.json`/`claude_desktop_config.json` must point `command` at the venv's `python.exe` absolute path; a bare `"python"` will use the system interpreter and fail with `ModuleNotFoundError`.
- **Tool name breaking change** — tools used to be `streamxpress_connect` etc. and are now the unprefixed names above. Don't reintroduce the prefix at the server layer.
- **Launcher is Windows-specific** — the `subprocess.Popen` flags won't work on Linux/macOS.

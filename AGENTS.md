# Repository Guidelines

## Project Structure & Module Organization

Python 3.10+ MCP server that drives DekTec StreamXpress over SpRcApi (HTTP/SOAP).

- `src/streamxpress_mcp/` — `server.py` (6 unprefixed FastMCP tools: launch/connect/play/stop/get_status/disconnect), `client.py` (`StreamXpressClient`), `config.py`, `launcher.py` (Windows-only).
- `src/streamxpress_mcp/sprc_import/` — vendored SOAP client, types, constants, and `SpRc.wsdl`. Treat as third-party; do not hand-edit.
- `tests/` — pytest (`test_server.py`, `test_client.py`, `test_config.py`, `test_launcher.py`, `test_sprc_wsdl.py`).
- `SpRcApi/` — official SDK. Constant values come from `Include/SpRcApi.h` and `DTAPI.h`.
- `docs/` — Markdown API specs, plans, and modulation GUI notes.
- `config.json` — shipped blank; `launch` reads `streamxpress_path` / `rc_port`.

## Build, Test, and Development Commands

```powershell
pip install -e ".[dev]"          # editable install + pytest
python -m streamxpress_mcp       # stdio MCP server
pytest                           # full suite
pytest tests/test_client.py      # one file
pytest tests/test_client.py::TestStreamXpressConnect::test_connect_creates_session
pytest -k connect                # keyword filter
```

StreamXpress must already be running as `StreamXpress.exe -rc <port>` (default 5000), or use the `launch` tool after filling `config.json`. If an MCP client uses a venv, set `command` to that venv's `python.exe`.

## Coding Style & Naming Conventions

4-space indent; Python 3.10+ type hints (`X | None`). Modules and functions `snake_case`, classes `PascalCase`. Tool names stay unprefixed (`connect`, not `streamxpress_connect`). No linter is configured — match nearby files. Route every vendored SOAP call through `StreamXpressClient._sprc_call`; do not call `self._sprc` or wrap one client method inside another.

## Testing Guidelines

pytest only (`testpaths = ["tests"]`). Inject `sprc_factory` via the `client` / `mock_sprc` fixtures; patch `streamxpress_mcp.server.get_client` for tool tests. No live SOAP except `tests/test_sprc_wsdl.py`. The MCP tool surface is the 6-tool preset player (`launch`, `connect`, `play`, `stop`, `get_status`, `disconnect`). Adding or renaming a tool requires updating `EXPECTED_TOOL_NAMES` in `tests/test_server.py` and the README tool table.

## Commit & Pull Request Guidelines

History uses Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`. Example: `fix: release session lock during in-flight SOAP calls`. PRs should state intent, list tool-surface changes, and keep `server.py`, `EXPECTED_TOOL_NAMES`, and README in lockstep. Do not commit local `config.json` paths (`git update-index --skip-worktree config.json`).

## Security & Configuration Tips

Lookup: `STREAMXPRESS_MCP_CONFIG` → repo-root `config.json` → defaults. Vendored types track SpRcApi v1.11; do not expose v1.12-only fields missing from `SPRC_types.py`.

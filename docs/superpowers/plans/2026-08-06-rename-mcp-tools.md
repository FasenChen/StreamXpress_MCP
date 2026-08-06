# MCP 工具命名去重（streamxpress_streamxpress_* → streamxpress_*）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除 MCP 工具名的重复前缀——把 `server.py` 中 12 个工具函数名去掉 `streamxpress_` 前缀，使 WorkBuddy 等客户端显示 `streamxpress_connect` 而非 `streamxpress_streamxpress_connect`。

**Architecture:** fastmcp 的 `@mcp.tool()` 默认以 Python 函数名注册工具；WorkBuddy/Claude Desktop 等客户端会在工具名前加 MCP server 名前缀（本项目 server 名为 `streamxpress-mcp`，前缀为 `streamxpress`）。当前函数名自带 `streamxpress_` 前缀导致双重前缀。修复 = 工具函数名去掉前缀，与 `client.py` 中 `StreamXpressClient` 的方法名（`connect`、`scan_ports` 等）保持一致。

**Tech Stack:** Python 3.10+、fastmcp 3.4.6、pytest 8

## Global Constraints

- Python `>=3.10`；依赖保持 `fastmcp>=3.0`、`zeep>=4.2`，**不新增任何依赖**（回归测试用 `asyncio.run` 包装 `mcp.list_tools()`，不引入 pytest-asyncio）。
- 工具注册名 = Python 函数名（`@mcp.tool()` 默认行为），因此函数名本身不得再含 `streamxpress_` 前缀。
- `src/streamxpress_mcp/client.py`（`StreamXpressClient`）**不改**——其方法名已是无前缀形式。
- `docs/superpowers/plans/2026-08-06-streamxpress-mcp.md`（历史实现计划）**不改**——它记录当初的构建过程，保留原名以保持历史一致。
- 重命名映射（12 个，`server.py` 工具函数 → 新名）：

| 旧名 | 新名 |
|---|---|
| `streamxpress_connect` | `connect` |
| `streamxpress_disconnect` | `disconnect` |
| `streamxpress_scan_ports` | `scan_ports` |
| `streamxpress_select_port` | `select_port` |
| `streamxpress_open_file` | `open_file` |
| `streamxpress_start` | `start` |
| `streamxpress_stop` | `stop` |
| `streamxpress_get_status` | `get_status` |
| `streamxpress_set_rate` | `set_rate` |
| `streamxpress_set_tsoip_params` | `set_tsoip_params` |
| `streamxpress_set_rf_params` | `set_rf_params` |
| `streamxpress_set_asi_params` | `set_asi_params` |

---

### Task 1: 重命名 server.py 工具函数并同步测试

**Files:**
- Modify: `src/streamxpress_mcp/server.py`（12 个 `@mcp.tool()` 函数定义改名）
- Modify: `tests/test_server.py`（12 处 `from streamxpress_mcp.server import streamxpress_*` 更新为无前缀名；文件末尾新增回归测试类）
- Test: `tests/test_server.py`

**Interfaces:**
- Consumes: `streamxpress_mcp.client.StreamXpressClient`（`connect(host, port)`、`disconnect()`、`scan_ports()`、`select_port(serial, port_num, modulation)`、`open_file(filepath)`、`start()`、`stop()`、`get_status()`、`set_rate(bps)`、`set_tsoip_params(...)`、`set_rf_params(frequency_hz, level_dbm)`、`set_asi_params(remux, playout_rate, tx_mode)`）——**不变**。
- Produces: `server.py` 暴露 12 个无前缀工具函数（签名不变，仅函数名去掉 `streamxpress_` 前缀）：`connect(host: str, port: int) -> dict`、`disconnect() -> dict`、`scan_ports() -> list[dict]`、`select_port(serial: int, port_num: int, modulation: int = 0) -> dict`、`open_file(filepath: str) -> dict`、`start() -> dict`、`stop() -> dict`、`get_status() -> dict`、`set_rate(rate_bps: int) -> dict`、`set_tsoip_params(dest_ip: str, dest_port: int, num_tp_per_ip: int = 7, protocol: str = "UDP", ttl: int = 64, fec_rows: int = 0, fec_cols: int = 0) -> dict`、`set_rf_params(frequency_hz: int, level_dbm: float) -> dict`、`set_asi_params(remux: bool = True, playout_rate: int = 0, tx_mode: int = 0) -> dict`；`mcp` 注册工具名与函数名相同。

- [ ] **Step 1: 新增回归测试（先红）**

在 `tests/test_server.py` 末尾追加：

```python
EXPECTED_TOOL_NAMES = {
    "connect", "disconnect", "scan_ports", "select_port", "open_file",
    "start", "stop", "get_status", "set_rate", "set_tsoip_params",
    "set_rf_params", "set_asi_params",
}


class TestToolNaming:
    """工具注册名不得再带 streamxpress_ 前缀（客户端会自行加 server 名前缀）。"""

    def test_registered_tool_names_have_no_streamxpress_prefix(self):
        import asyncio

        from streamxpress_mcp.server import mcp

        tools = asyncio.run(mcp.list_tools())
        names = {t.name for t in tools}
        assert EXPECTED_TOOL_NAMES <= names, f"缺少工具: {EXPECTED_TOOL_NAMES - names}"
        assert not any(n.startswith("streamxpress_") for n in names), (
            f"工具名仍带前缀: {sorted(n for n in names if n.startswith('streamxpress_'))}"
        )
```

- [ ] **Step 2: 运行测试确认新测试失败**

Run: `.venv/Scripts/python.exe -m pytest tests/test_server.py::TestToolNaming -v`
Expected: FAIL —— `test_registered_tool_names_have_no_streamxpress_prefix` 断言失败，提示工具名仍带前缀（此时注册名是 `streamxpress_connect` 等 12 个带前缀名，`EXPECTED_TOOL_NAMES` 中无前缀名缺失）。

- [ ] **Step 3: 重命名 server.py 的 12 个工具函数**

对 `src/streamxpress_mcp/server.py` 逐处把 `def streamxpress_*` 改为 `def *`（按 Global Constraints 的重命名映射；函数体、docstring、`@mcp.tool()` 装饰器均不动）。示例（实际共 12 处）：

```python
@mcp.tool()
def connect(host: str, port: int) -> dict:
    """Connect to a StreamXpress instance running in remote-control mode.
    ...
    """
```

- [ ] **Step 4: 更新 tests/test_server.py 中 12 处 import**

`tests/test_server.py` 中 12 处 `from streamxpress_mcp.server import streamxpress_connect`（及 `streamxpress_disconnect`、`streamxpress_scan_ports`、`streamxpress_select_port`、`streamxpress_open_file`、`streamxpress_start`、`streamxpress_stop`、`streamxpress_get_status`、`streamxpress_set_rate`、`streamxpress_set_tsoip_params`、`streamxpress_set_rf_params`、`streamxpress_set_asi_params`）中的符号名去掉 `streamxpress_` 前缀；对应函数调用处同步改名。例如第 142-146 行：

```python
from streamxpress_mcp.server import connect

result = connect(host="http://localhost", port=5000)
```

- [ ] **Step 5: 运行全部测试确认通过**

Run: `.venv/Scripts/python.exe -m pytest tests/ -v`
Expected: 全部 PASS（原有 server 工具测试 + 新增 `TestToolNaming`）。

- [ ] **Step 6: Commit**

```bash
git add src/streamxpress_mcp/server.py tests/test_server.py
git commit -m "refactor: remove streamxpress_ prefix from MCP tool names"
```

---

### Task 2: 更新 README 文档

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 产出的 12 个无前缀工具名。
- Produces: 文档中工具名与注册名一致（裸名），并说明客户端前缀显示规则。

- [ ] **Step 1: 更新"可用工具"表**

把 `README.md` 第 57-68 行的工具表改为（表前加一行说明）：

```markdown
> 工具注册名如左（不带前缀）。MCP 客户端（WorkBuddy、Claude Desktop 等）通常会在工具名前加上 MCP server 名前缀，例如 `connect` 在客户端中显示为 `streamxpress_connect`。

| 工具 | 说明 |
|---|---|
| `connect` | 连接 StreamXpress RC 会话 |
| `disconnect` | 断开连接 |
| `scan_ports` | 扫描可用输出端口 |
| `select_port` | 选择输出端口 |
| `open_file` | 加载 TS 文件 |
| `start` | 开始播放 |
| `stop` | 停止播放 |
| `get_status` | 查询播放进度和状态 |
| `set_rate` | 设置 TS 码率（bps） |
| `set_tsoip_params` | 配置 UDP/RTP TS-over-IP 输出参数 |
| `set_rf_params` | 设置 RF 频率和电平 |
| `set_asi_params` | 设置 ASI 重复用和包模式 |
```

- [ ] **Step 2: 更新"前置条件"第 13 行的 `streamxpress_connect` 引用**

`README.md` 第 13 行（"只需在 `streamxpress_connect` 工具中指定…"）中的 `streamxpress_connect` 改为 `connect`。

- [ ] **Step 3: 更新"AI 交互示例"第 76-83 行**

把 8 处调用名去掉 `streamxpress_` 前缀（`streamxpress_connect(...)` → `connect(...)`，`streamxpress_scan_ports()` → `scan_ports()`，`streamxpress_select_port(...)` → `select_port(...)`，`streamxpress_set_tsoip_params(...)` → `set_tsoip_params(...)`，`streamxpress_set_rate(...)` → `set_rate(...)`，`streamxpress_open_file(...)` → `open_file(...)`，`streamxpress_start()` → `start()`，`streamxpress_get_status()` → `get_status()`）。示例：

```
用户: 把 C:\Streams\news.ts 以 25 Mbps 推送到组播地址 239.1.1.1:1234

AI 依次调用:
  1. connect(host="http://localhost", port=5000)
  2. scan_ports() → 选择一个 TS-over-IP 端口
  3. select_port(serial=..., port_num=1)
  4. set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="UDP")
  5. set_rate(rate_bps=25_000_000)
  6. open_file(filepath="C:\\Streams\\news.ts")
  7. start()
  8. get_status() → 监控播放进度
```

- [ ] **Step 4: 校验文档一致性并运行测试**

Run: `grep -n "streamxpress_connect\|streamxpress_scan_ports\|streamxpress_select_port\|streamxpress_open_file\|streamxpress_start\|streamxpress_stop\|streamxpress_get_status\|streamxpress_set_rate\|streamxpress_set_tsoip_params\|streamxpress_set_rf_params\|streamxpress_set_asi_params\|streamxpress_disconnect" README.md src/ tests/`
Expected: 除 `docs/superpowers/plans/2026-08-06-streamxpress-mcp.md`（历史文档，有意保留）外，无残留旧名。

Run: `.venv/Scripts/python.exe -m pytest tests/ -v`
Expected: 全部 PASS。

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: update README tool names after removing streamxpress_ prefix"
```

---

## 验收清单

- [ ] `src/streamxpress_mcp/server.py` 12 个工具函数名无 `streamxpress_` 前缀；`client.py` 未改动。
- [ ] `mcp.list_tools()` 返回的工具名 = `{connect, disconnect, scan_ports, select_port, open_file, start, stop, get_status, set_rate, set_tsoip_params, set_rf_params, set_asi_params}`，无任何 `streamxpress_` 开头的注册名。
- [ ] `tests/` 全部通过（含新增 `TestToolNaming`）。
- [ ] README 工具表、示例、说明均已同步；除历史计划文档外无旧名残留。
- [ ] WorkBuddy 中重新导入后工具显示为 `streamxpress_connect` 等（不再双前缀）。

# 配置文件 + StreamXpress 启动工具 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增项目配置文件（`config.json` + `config.example.json`），让用户在使用 MCP 前集中填写 StreamXpress 可执行文件路径与 SpRcApi 路径；新增 `launch` MCP 工具按配置启动 StreamXpress（`-rc` 远程控制模式），并支持自定义 SpRcApi 路径作为 wsdl 来源（默认回退包内）。

**Architecture:** `config.py`（dataclass + 加载 + wsdl 解析）→ `launcher.py`（subprocess 启动 + TCP 端口探测）→ `server.py` 新增 `launch` 工具并组装 wsdl 工厂 → `sprc_import/SPRC_client.py` 最小改动支持 `wsdl_template` 参数。全部无新依赖（标准库 `json`/`subprocess`/`socket`/`dataclasses`）。

**Tech Stack:** Python 3.10+、fastmcp 3.4.6、pytest 8；Windows（StreamXpress 仅 Windows，启动用 `DETACHED_PROCESS`）。

## Global Constraints

- Python `>=3.10`；**不新增任何依赖**（只用标准库）。
- 工具注册名 = Python 函数名（`@mcp.tool()` 默认行为），新工具 `launch` **不带前缀**（延续上轮命名约定，客户端显示为 `streamxpress_launch`）。
- `sprc_import/SPRC_client.py` 是 DekTec 生成代码（文件头有 `(C) 2024 DekTec`），**只做最小改动**：`__init__` 加 `wsdl_template` 可选参数 + `__create_wsdl_file_for_service` 模板定位处。
- `src/streamxpress_mcp/client.py` **不改**（`StreamXpressClient(sprc_factory=None)` DI 模式已够用）。
- `config.json` 加入 `.gitignore` **不进 git**；`config.example.json` 进 git。
- 配置文件查找顺序：环境变量 `STREAMXPRESS_MCP_CONFIG` → 项目根 `config.json` → 全部缺失用默认值（不报错）。
- 测试**不联网、不启动真实进程**：mock `subprocess.Popen`、`socket`、`zeep`。
- 项目根定位：`Path(__file__).resolve().parents[2]`（`src/streamxpress_mcp/config.py` 向上两级）。

---

### Task 1: config.py 配置模块 + 模板文件 + gitignore

**Files:**
- Create: `src/streamxpress_mcp/config.py`
- Create: `config.example.json`（项目根）
- Create: `tests/test_config.py`
- Modify: `.gitignore`（末尾加 `config.json`）

**Interfaces:**
- Consumes: 无（第一个任务）。
- Produces:
  - `StreamXpressConfig` dataclass：`streamxpress_path: str = ""`、`sprc_api_path: str = ""`、`rc_port: int = 5000`
  - `load_config() -> StreamXpressConfig`
  - `resolve_wsdl_path(cfg: StreamXpressConfig) -> str | None`
  - 模块常量 `PROJECT_ROOT: Path`、`DEFAULT_CONFIG_PATH: Path`、`ENV_VAR: str = "STREAMXPRESS_MCP_CONFIG"`

- [ ] **Step 1: 写失败测试**

创建 `tests/test_config.py`：

```python
import json
import pytest
from streamxpress_mcp import config as config_mod


def test_load_config_defaults_when_no_file(monkeypatch, tmp_path):
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", tmp_path / "config.json")
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == ""
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 5000


def test_load_config_from_env_path(monkeypatch, tmp_path):
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(
        json.dumps({"streamxpress_path": "C:/sx.exe", "rc_port": 6000}),
        encoding="utf-8",
    )
    monkeypatch.setenv(config_mod.ENV_VAR, str(cfg_file))
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == "C:/sx.exe"
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 6000


def test_load_config_from_project_root(monkeypatch, tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"sprc_api_path": "D:/SpRcApi"}), encoding="utf-8")
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", cfg_file)
    cfg = config_mod.load_config()
    assert cfg.sprc_api_path == "D:/SpRcApi"


def test_load_config_invalid_json_raises(monkeypatch, tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{not json", encoding="utf-8")
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", cfg_file)
    with pytest.raises(ValueError, match="配置文件解析失败"):
        config_mod.load_config()


def test_resolve_wsdl_path_empty_returns_none():
    cfg = config_mod.StreamXpressConfig(sprc_api_path="")
    assert config_mod.resolve_wsdl_path(cfg) is None


def test_resolve_wsdl_path_missing_returns_none(tmp_path):
    cfg = config_mod.StreamXpressConfig(sprc_api_path=str(tmp_path))
    assert config_mod.resolve_wsdl_path(cfg) is None


def test_resolve_wsdl_path_found(tmp_path):
    wsdl_dir = tmp_path / "WSDL"
    wsdl_dir.mkdir()
    (wsdl_dir / "SpRc.wsdl").write_text("x", encoding="utf-8")
    cfg = config_mod.StreamXpressConfig(sprc_api_path=str(tmp_path))
    assert config_mod.resolve_wsdl_path(cfg) == str(wsdl_dir / "SpRc.wsdl")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/Scripts/python.exe -m pytest tests/test_config.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'streamxpress_mcp.config'`）。

- [ ] **Step 3: 实现 config.py**

创建 `src/streamxpress_mcp/config.py`：

```python
"""Configuration loading for the StreamXpress MCP server.

Users copy `config.example.json` to `config.json` at the project root and
fill in the StreamXpress executable path (and optionally a custom SpRcApi
path used as the WSDL source). Lookup order:
  1. file path from env var STREAMXPRESS_MCP_CONFIG
  2. <project root>/config.json
  3. defaults (no file -> empty paths, rc_port=5000)
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"
ENV_VAR = "STREAMXPRESS_MCP_CONFIG"


@dataclass
class StreamXpressConfig:
    streamxpress_path: str = ""
    sprc_api_path: str = ""
    rc_port: int = 5000


def _find_config_file() -> Path | None:
    env_path = os.environ.get(ENV_VAR)
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p
        raise ValueError(f"{ENV_VAR} 指定的配置文件不存在: {env_path}")
    if DEFAULT_CONFIG_PATH.is_file():
        return DEFAULT_CONFIG_PATH
    return None


def load_config() -> StreamXpressConfig:
    cfg_file = _find_config_file()
    if cfg_file is None:
        return StreamXpressConfig()
    try:
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"配置文件解析失败: {cfg_file} — {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"配置文件格式错误（应为 JSON 对象）: {cfg_file}")
    return StreamXpressConfig(
        streamxpress_path=str(data.get("streamxpress_path", "")),
        sprc_api_path=str(data.get("sprc_api_path", "")),
        rc_port=int(data.get("rc_port", 5000)),
    )


def resolve_wsdl_path(cfg: StreamXpressConfig) -> str | None:
    """Return <sprc_api_path>/WSDL/SpRc.wsdl if it exists, else None."""
    if not cfg.sprc_api_path:
        return None
    candidate = Path(cfg.sprc_api_path) / "WSDL" / "SpRc.wsdl"
    if candidate.is_file():
        return str(candidate)
    return None
```

- [ ] **Step 4: 创建 config.example.json 并更新 .gitignore**

创建 `config.example.json`：

```json
{
  "_说明": "复制本文件为 config.json 后填写。streamxpress_path 必填；sprc_api_path 留空则用包内默认 wsdl；rc_port 默认 5000",
  "streamxpress_path": "C:\\Program Files\\DekTec\\StreamXpress\\StreamXpress64.exe",
  "sprc_api_path": "",
  "rc_port": 5000
}
```

`.gitignore` 末尾追加一行：

```
config.json
```

- [ ] **Step 5: 运行测试确认通过**

Run: `.venv/Scripts/python.exe -m pytest tests/test_config.py -v`
Expected: 7 passed。

- [ ] **Step 6: Commit**

```bash
git add src/streamxpress_mcp/config.py config.example.json tests/test_config.py .gitignore
git commit -m "feat: add config module with streamxpress path and sprc api path"
```

---

### Task 2: launcher.py + launch 工具

**Files:**
- Create: `src/streamxpress_mcp/launcher.py`
- Create: `tests/test_launcher.py`
- Modify: `src/streamxpress_mcp/server.py`（新增 `launch` 工具 + import）

**Interfaces:**
- Consumes: `StreamXpressConfig`、`load_config`（Task 1）。
- Produces:
  - `launcher.launch_streamxpress(cfg: StreamXpressConfig) -> dict`：返回 `{"ok": True, "pid": int, "port": int, "ready": bool}` 或 `{"ok": False, "error": str}`
  - `server.launch() -> dict`（MCP 工具，无参数）

- [ ] **Step 1: 写失败测试**

创建 `tests/test_launcher.py`：

```python
from unittest.mock import patch, MagicMock
import subprocess
from streamxpress_mcp.config import StreamXpressConfig
from streamxpress_mcp import launcher


def test_launch_returns_error_when_path_empty():
    result = launcher.launch_streamxpress(StreamXpressConfig())
    assert result["ok"] is False
    assert "streamxpress_path" in result["error"]


def test_launch_returns_error_when_exe_missing(tmp_path):
    cfg = StreamXpressConfig(streamxpress_path=str(tmp_path / "nope.exe"))
    result = launcher.launch_streamxpress(cfg)
    assert result["ok"] is False
    assert "不存在" in result["error"]


@patch("streamxpress_mcp.launcher._port_open")
@patch("streamxpress_mcp.launcher.subprocess.Popen")
def test_launch_starts_with_rc_args_and_probes_port(mock_popen, mock_port_open, tmp_path):
    exe = tmp_path / "StreamXpress64.exe"
    exe.write_text("", encoding="utf-8")
    proc = MagicMock()
    proc.pid = 12345
    mock_popen.return_value = proc
    mock_port_open.side_effect = [False, False, True]  # 第 3 次探测成功

    cfg = StreamXpressConfig(streamxpress_path=str(exe), rc_port=5000)
    with patch("streamxpress_mcp.launcher.time.sleep"):
        result = launcher.launch_streamxpress(cfg)

    mock_popen.assert_called_once_with(
        [str(exe), "-rc", "5000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}
```

在 `tests/test_server.py` 末尾追加：

```python
class TestLaunchTool:
    @patch("streamxpress_mcp.server.launch_streamxpress")
    def test_launch_tool_returns_launcher_result(self, mock_launch):
        mock_launch.return_value = {"ok": True, "pid": 12345, "port": 5000, "ready": True}

        from streamxpress_mcp.server import launch

        result = launch()
        assert result == {"ok": True, "pid": 12345, "port": 5000, "ready": True}
        assert mock_launch.call_count == 1
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/Scripts/python.exe -m pytest tests/test_launcher.py tests/test_server.py::TestLaunchTool -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'streamxpress_mcp.launcher'` / `ImportError: cannot import name 'launch'`）。

- [ ] **Step 3: 实现 launcher.py**

创建 `src/streamxpress_mcp/launcher.py`：

```python
"""Launch StreamXpress in remote-control mode from configuration."""

import socket
import subprocess
import time
from pathlib import Path

from .config import StreamXpressConfig


def _port_open(port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def launch_streamxpress(cfg: StreamXpressConfig) -> dict:
    """Start `streamxpress_path -rc <rc_port>` and probe the port.

    Returns {"ok": True, "pid", "port", "ready"} on success, or
    {"ok": False, "error"} when not configured / executable missing.
    """
    if not cfg.streamxpress_path:
        return {
            "ok": False,
            "error": "config.json 未配置 streamxpress_path，请先复制 config.example.json 为 config.json 并填写",
        }
    exe = cfg.streamxpress_path
    if not Path(exe).is_file():
        return {"ok": False, "error": f"StreamXpress 可执行文件不存在: {exe}"}

    proc = subprocess.Popen(
        [exe, "-rc", str(cfg.rc_port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    ready = False
    for _ in range(10):
        time.sleep(0.5)
        if _port_open(cfg.rc_port):
            ready = True
            break
    return {"ok": True, "pid": proc.pid, "port": cfg.rc_port, "ready": ready}
```

- [ ] **Step 4: 在 server.py 注册 launch 工具**

在 `src/streamxpress_mcp/server.py` 顶部 import 区追加：

```python
from .config import load_config
from .launcher import launch_streamxpress
```

在文件末尾（`set_asi_params` 工具之后）追加：

```python
# ── Launch tool ──

@mcp.tool()
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    (see config.example.json), starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with streamxpress_connect.
    """
    return launch_streamxpress(load_config())
```

- [ ] **Step 5: 运行测试确认通过**

Run: `.venv/Scripts/python.exe -m pytest tests/test_launcher.py tests/test_server.py::TestLaunchTool -v`
Expected: 全部 PASS。

- [ ] **Step 6: 运行全量测试确认无回归**

Run: `.venv/Scripts/python.exe -m pytest tests/ -q`
Expected: 27 + 新增 = 全部 PASS。

- [ ] **Step 7: Commit**

```bash
git add src/streamxpress_mcp/launcher.py src/streamxpress_mcp/server.py tests/test_launcher.py tests/test_server.py
git commit -m "feat: add launch tool to start StreamXpress from config"
```

---

### Task 3: SPRC_client 自定义 wsdl 模板 + get_client 组装

**Files:**
- Modify: `src/streamxpress_mcp/sprc_import/SPRC_client.py`（`__init__` 加参数、模板定位处）
- Modify: `src/streamxpress_mcp/server.py`（`get_client` 组装 wsdl 工厂 + import）
- Create: `tests/test_sprc_wsdl.py`
- Modify: `tests/test_server.py`（追加 get_client wsdl 测试）

**Interfaces:**
- Consumes: `resolve_wsdl_path`、`StreamXpressConfig`、`load_config`（Task 1）。
- Produces:
  - `SPRC_client(wsdl_template: str | None = None)`：新可选构造参数；`self._wsdl_template` 保存模板路径
  - `server.get_client()`：`resolve_wsdl_path` 非 None 时用 `StreamXpressClient(sprc_factory=lambda: SPRC_client(wsdl_template=wsdl))`，否则保持默认

- [ ] **Step 1: 写失败测试**

创建 `tests/test_sprc_wsdl.py`：

```python
from pathlib import Path
from streamxpress_mcp.sprc_import import SPRC_client


def test_custom_wsdl_template_used(tmp_path):
    custom = tmp_path / "SpRc.wsdl"
    custom.write_text("CUSTOM-MARKER-123", encoding="utf-8")
    spr = SPRC_client(wsdl_template=str(custom))

    wsdl_file = spr._SPRC_client__create_wsdl_file_for_service(5000, "http://localhost")
    try:
        content = Path(wsdl_file).read_text(encoding="utf-8")
        assert "CUSTOM-MARKER-123" in content
    finally:
        Path(wsdl_file).unlink(missing_ok=True)


def test_default_template_used_when_not_specified():
    spr = SPRC_client()

    wsdl_file = spr._SPRC_client__create_wsdl_file_for_service(5000, "http://localhost")
    try:
        content = Path(wsdl_file).read_text(encoding="utf-8")
        assert "<definitions" in content
    finally:
        Path(wsdl_file).unlink(missing_ok=True)
```

在 `tests/test_server.py` 末尾追加（注意重置全局单例，避免跨测试污染）：

```python
class TestGetClientWsdl:
    @pytest.fixture(autouse=True)
    def reset_client_singleton(self):
        import streamxpress_mcp.server as server_mod

        server_mod._client = None
        yield
        server_mod._client = None

    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.resolve_wsdl_path")
    def test_custom_wsdl_used_when_configured(self, mock_resolve, mock_load):
        from streamxpress_mcp.config import StreamXpressConfig
        from streamxpress_mcp.server import get_client

        mock_load.return_value = StreamXpressConfig(sprc_api_path="D:/SpRcApi")
        mock_resolve.return_value = "D:/SpRcApi/WSDL/SpRc.wsdl"

        client = get_client()
        sprc = client._sprc_factory()
        assert sprc._wsdl_template == "D:/SpRcApi/WSDL/SpRc.wsdl"

    @patch("streamxpress_mcp.server.load_config")
    @patch("streamxpress_mcp.server.resolve_wsdl_path")
    def test_default_factory_when_no_custom_wsdl(self, mock_resolve, mock_load):
        from streamxpress_mcp.config import StreamXpressConfig
        from streamxpress_mcp.server import get_client

        mock_load.return_value = StreamXpressConfig()
        mock_resolve.return_value = None

        client = get_client()
        sprc = client._sprc_factory()
        assert sprc._wsdl_template is None
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv/Scripts/python.exe -m pytest tests/test_sprc_wsdl.py tests/test_server.py::TestGetClientWsdl -v`
Expected: FAIL（`TypeError: __init__() got an unexpected keyword argument 'wsdl_template'`）。

- [ ] **Step 3: 修改 SPRC_client.py（最小改动）**

`__init__` 改为：

```python
    def __init__(self, wsdl_template: str | None = None):
        """ Constructor """
        self._zeep_client = None
        self._wsdl_file = ''
        self._wsdl_template = wsdl_template
```

`__create_wsdl_file_for_service` 内模板定位（当前第 488 行 `orig_wsdl = Path(__file__).parent.joinpath('SpRc.wsdl')`）改为：

```python
        if self._wsdl_template:
            orig_wsdl = Path(self._wsdl_template)
        else:
            orig_wsdl = Path(__file__).parent.joinpath('SpRc.wsdl')
```

其余不动。

- [ ] **Step 4: 修改 server.py 的 get_client**

`server.py` import 区追加：

```python
from .config import load_config, resolve_wsdl_path
from .sprc_import import SPRC_client
```

`get_client` 改为：

```python
def get_client() -> StreamXpressClient:
    """Return the global singleton client, creating it if needed."""
    global _client
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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `.venv/Scripts/python.exe -m pytest tests/test_sprc_wsdl.py tests/test_server.py::TestGetClientWsdl -v`
Expected: 全部 PASS。

- [ ] **Step 6: 运行全量测试确认无回归**

Run: `.venv/Scripts/python.exe -m pytest tests/ -q`
Expected: 全部 PASS（含原有 27 个 + 新增）。

- [ ] **Step 7: Commit**

```bash
git add src/streamxpress_mcp/sprc_import/SPRC_client.py src/streamxpress_mcp/server.py tests/test_sprc_wsdl.py tests/test_server.py
git commit -m "feat: support custom SpRcApi wsdl template via config"
```

---

### Task 4: README 更新

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: `config.example.json` 字段、`launch` 工具（Task 1-2 产出）。
- Produces: 文档与实现一致的配置说明。

- [ ] **Step 1: 新增"配置文件"章节**

在"快速开始"之前插入（紧跟"前置条件"之后）：

```markdown
## 配置文件

MCP 支持通过项目根目录的 `config.json` 集中配置，在使用前填写：

1. 复制 `config.example.json` 为 `config.json`（`config.json` 已被 git 忽略，不会提交）。
2. 按需填写字段：

| 字段 | 说明 |
|---|---|
| `streamxpress_path` | StreamXpress 可执行文件的完整路径（如 `C:\Program Files\DekTec\StreamXpress\StreamXpress64.exe`），`launch` 工具用它启动 |
| `sprc_api_path` | SpRcApi 目录路径，默认留空（使用包内自带 wsdl）；若填写，运行时优先使用 `<sprc_api_path>\WSDL\SpRc.wsdl` 作为 wsdl 来源 |
| `rc_port` | 远程控制端口，默认 `5000` |

查找顺序：环境变量 `STREAMXPRESS_MCP_CONFIG` 指定的文件 → 项目根 `config.json` → 默认值。配置文件缺失或字段留空时不报错，使用默认值。
```

- [ ] **Step 2: 更新"快速开始"第 2 步**

把第 2 步注释与命令改为：

```powershell
# 2. 以远程控制模式启动 StreamXpress
#    可执行文件不在 PATH 中；先在 config.json 里填好 streamxpress_path（见"配置文件"章节），
#    然后可用 MCP 的 launch 工具启动；也可手动用完整路径启动：
& "C:\Program Files\DekTec\StreamXpress\StreamXpress64.exe" -rc 5000
```

- [ ] **Step 3: 更新"可用工具"表 + "AI 交互示例"**

工具表新增一行（放在 `connect` 之前）：

```markdown
| `launch` | 按 config.json 启动 StreamXpress（-rc 模式）并探测端口 |
```

"AI 交互示例"开头插入 launch 步骤并让 connect 使用其返回端口：

```
用户: 把 C:\Streams\news.ts 以 25 Mbps 推送到组播地址 239.1.1.1:1234

AI 依次调用:
  1. launch() → 按 config.json 启动 StreamXpress，得到 port（默认 5000）
  2. connect(host="http://localhost", port=<launch 返回的 port>)
  3. scan_ports() → 选择一个 TS-over-IP 端口
  4. select_port(serial=..., port_num=1)
  5. set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="UDP")
  6. set_rate(rate_bps=25_000_000)
  7. open_file(filepath="C:\\Streams\\news.ts")
  8. start()
  9. get_status() → 监控播放进度
  10. stop()
  11. disconnect()
```

- [ ] **Step 4: 校验文档与代码一致并跑测试**

Run: `grep -n "launch" README.md src/streamxpress_mcp/server.py | head`
Expected: README 工具表、快速开始、示例均含 `launch`；server.py 有 `def launch` 与 `@mcp.tool()`。

Run: `.venv/Scripts/python.exe -m pytest tests/ -q`
Expected: 全部 PASS。

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: document config file and launch tool"
```

---

## 验收清单

- [ ] `config.example.json` 进仓库；`config.json` 在 `.gitignore`。
- [ ] `load_config` 支持 env 文件、项目根文件、默认值三态；JSON 损坏报错含路径。
- [ ] `resolve_wsdl_path`：空/不存在 → `None`；存在 → 返回 `<path>/WSDL/SpRc.wsdl`。
- [ ] `launch` 工具：按配置启动 `-rc <port>`、TCP 探测、未配置/文件不存在返回清晰错误；不启动真实进程（测试全 mock）。
- [ ] `SPRC_client(wsdl_template=...)` 自定义模板生效，默认回退包内 `SpRc.wsdl`；`client.py` 未改。
- [ ] `get_client` 按 `resolve_wsdl_path` 结果组装工厂；无自定义时行为与原来一致。
- [ ] README 有配置文件章节、快速开始引用配置、工具表含 `launch`、AI 示例含 launch→connect 衔接。
- [ ] 全量测试通过（原 27 个不回归，新增 ~12 个）。

# 配置文件 + StreamXpress 启动工具 设计文档

> 日期：2026-08-06
> 状态：已获用户批准（brainstorming 呈现后确认）

## 目标

让用户在使用 MCP 前通过项目内一个配置文件集中填写 StreamXpress 可执行文件路径和 SpRcApi 路径（默认项目内 `SpRcApi/`，可自定义），并提供 `launch` 工具按配置启动 StreamXpress（`-rc` 远程控制模式），避免 README 里手动改路径的样板操作。

## 关键决策（经澄清问题确定）

1. **StreamXpress 路径用途**：新增 MCP 工具 `launch`，调用时读配置里的 exe 路径 + `-rc` 端口启动 StreamXpress（显式可控，而非 server 启动时自动拉起）。
2. **SpRcApi 路径含义**：作为 wsdl 来源——运行时优先用 `<sprc_api_path>/WSDL/SpRc.wsdl`，不存在或留空则回退包内 `sprc_import/SpRc.wsdl`（保持 pip 安装后自包含）。
3. **配置格式**：JSON + `config.example.json` 模板（零依赖，标准库 `json`）。

## 组件与文件布局

```
StreamXpress_MCP/
├── config.example.json       ← 进仓库，模板（含字段说明）
├── config.json               ← 用户本地填写，加入 .gitignore
└── src/streamxpress_mcp/
    ├── config.py             ← 新建：加载配置
    ├── launcher.py           ← 新建：启动 StreamXpress 进程
    ├── server.py             ← 修改：新增 launch 工具 + 组装 wsdl 来源
    └── sprc_import/SPRC_client.py ← 修改（最小侵入）：支持自定义 wsdl 模板
```

### 配置文件

`config.example.json`（JSON 无注释，用 `_说明` 字段；空串 = 未设置/用默认）：

```json
{
  "_说明": "复制本文件为 config.json 后填写。streamxpress_path 必填；sprc_api_path 留空则用包内默认 wsdl；rc_port 默认 5000",
  "streamxpress_path": "C:\\Program Files\\DekTec\\StreamXpress\\StreamXpress64.exe",
  "sprc_api_path": "",
  "rc_port": 5000
}
```

**查找顺序**：
1. 环境变量 `STREAMXPRESS_MCP_CONFIG` 指定的文件路径；
2. 项目根 `config.json`（项目根 = `Path(__file__).resolve().parents[2]`，即 `src/streamxpress_mcp/config.py` 向上两级）；
3. 都找不到 → 全部用默认值（`streamxpress_path=""`、`sprc_api_path=""`、`rc_port=5000`），不报错。

### config.py（新建）

- `@dataclass StreamXpressConfig`：
  - `streamxpress_path: str = ""`
  - `sprc_api_path: str = ""`
  - `rc_port: int = 5000`
- `load_config() -> StreamXpressConfig`：按上述查找顺序加载；JSON 解析失败抛 `ValueError`（信息含文件路径）；字段缺失/类型不符用默认值。
- `resolve_wsdl_path(cfg: StreamXpressConfig) -> str | None`：`cfg.sprc_api_path` 非空且 `Path(cfg.sprc_api_path) / "WSDL" / "SpRc.wsdl"` 是文件 → 返回该路径；否则返回 `None`（表示用包内默认）。

### launcher.py（新建）

- `launch_streamxpress(cfg: StreamXpressConfig) -> dict`：
  - `cfg.streamxpress_path` 为空或路径不存在 → 返回 `{"ok": False, "error": "...提示填写 config.json..."}`；
  - 否则 `subprocess.Popen([cfg.streamxpress_path, "-rc", str(cfg.rc_port)], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)`（Windows）；
  - 启动后 TCP 探测 `localhost:rc_port`（socket 连接，0.5s 间隔重试，最多约 10 次 / 5 秒），返回 `{"ok": True, "pid": int, "port": int, "ready": bool}`。
- 进程句柄不持有（分离启动，用户自行用 `disconnect`/系统任务管理器结束）。

### server.py（修改）

- 新增工具（无前缀，与现有命名一致）：

```
launch() -> dict
  读配置（load_config），调 launcher.launch_streamxpress，
  返回启动结果（pid/port/ready 或错误信息）
```

- `get_client()` 组装 wsdl：`load_config()` → `resolve_wsdl_path(cfg)`；非 `None` 时以 `StreamXpressClient(sprc_factory=lambda: SPRC_client(wsdl_template=wsdl))` 创建；`None` 时保持现状（默认 `SPRC_client()`）。

### sprc_import/SPRC_client.py（修改，最小侵入）

- `__init__(self, wsdl_template: str | None = None)`：新增可选参数，存入 `self._wsdl_template`（默认 `None`）。
- `__create_wsdl_file_for_service` 内模板定位改为：

```python
if self._wsdl_template:
    orig_wsdl = Path(self._wsdl_template)
else:
    orig_wsdl = Path(__file__).parent.joinpath('SpRc.wsdl')
```

- 其余逻辑（生成临时 wsdl、替换 server location、zeep 加载、清理）不变。该文件是 DekTec 生成代码，只做这一处最小改动。

### client.py（不改）

`StreamXpressClient(sprc_factory=None)` 的 DI 模式已支持注入带 `wsdl_template` 的工厂，无需改动。

### .gitignore（修改）

新增一行 `config.json`（用户本地配置不入库）。

### README.md（修改）

- 新增"配置文件"章节：复制 `config.example.json` → `config.json`、各字段说明、查找顺序。
- 快速开始第 2 步改为引用配置：填好 `config.json` 后可用 `launch` 工具启动（或按原方式手动启动）。
- MCP 工具表新增 `launch` 一行。
- "AI 交互示例"开头加 `launch()` 步骤，并用其返回的 `port` 调用 `connect(host="http://localhost", port=<launch 返回的 port>)`，说明两个工具的衔接。

## 测试

- `tests/test_config.py`（新建）：
  - `load_config` 默认值（无文件、无 env）；
  - env `STREAMXPRESS_MCP_CONFIG` 指定文件时读取；
  - 项目根 `config.json` 读取；
  - JSON 损坏 → `ValueError`（信息含路径）；
  - 字段缺失用默认值；
  - `resolve_wsdl_path`：空路径 → `None`；路径不存在 → `None`；路径存在 → 返回该 wsdl 路径。
- `tests/test_server.py`（扩展）：
  - `launch` 工具：mock `launcher.launch_streamxpress`（成功 / 路径未配置返回错误）；
  - `get_client` wsdl 组装：mock config 使 `resolve_wsdl_path` 返回路径 → factory 传入 `wsdl_template`；返回 `None` → 默认工厂。
- `tests/test_sprc_wsdl.py`（新建）：
  - `SPRC_client(wsdl_template=<临时文件>)` 的 `__create_wsdl_file_for_service` 生成临时 wsdl 内容基于自定义模板（替换 host/port 后含自定义模板特征串）；
  - 不传 `wsdl_template` 时回退包内 `SpRc.wsdl`（生成文件存在）。

## 验收清单

- [ ] `config.example.json` 进仓库，`config.json` 被 gitignore。
- [ ] `load_config` / `resolve_wsdl_path` 按设计工作并有测试覆盖。
- [ ] `launch` 工具按配置启动 StreamXpress 并探测端口，未配置时返回清晰错误。
- [ ] 自定义 `sprc_api_path` 时 wsdl 取自 `<path>/WSDL/SpRc.wsdl`，否则回退包内；pip 安装自包含不破坏。
- [ ] README 有配置文件章节与 launch 工具说明。
- [ ] 全量测试通过（新增 ~3 个测试文件/类，原有 27 个不回归）。

# 直接提供 config.json（去除模板）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用一个字段留空的 `config.json` 直接进仓库，代替原来的「复制 `config.example.json` → `config.json`」模板流程；用户开箱只需编辑仓库里那份 `config.json`，配以 `git update-index --skip-worktree config.json` 屏蔽本地路径修改。

**Architecture:** 纯文档/静态资源整理：删除 `config.example.json`，新增字段留空的 `config.json`；`.gitignore` 移除 `config.json` 忽略规则；`config.py` / `launcher.py` / `server.py` 里三处对 `config.example.json` 的文案引用改为直接编辑 `config.json`；README 与 CLAUDE.md 的「配置文件」章节改写并新增 skip-worktree 提示。运行时行为不变——`load_config()` 的三级查找顺序（env var → 项目根 `config.json` → 默认值）保持不动。

**Tech Stack:** Python 3.10+、pytest 8；无新依赖。

## Global Constraints

- Python `>=3.10`；**不新增任何依赖**。
- `load_config()` 已有查找顺序不变：`STREAMXPRESS_MCP_CONFIG` → `<project root>/config.json` → 默认值。
- `config.json` 的字段留空（`streamxpress_path=""`、`sprc_api_path=""`、`rc_port=5000`）——加载后必须与「文件缺失时的默认值」严格等价，避免用户拉下仓库直接跑就变成非默认行为。
- 保留 [.gitignore:12-15](.gitignore#L12-L15) 中对 `*.wsdl` 的白名单规则；这次只删「本地 per-user 配置 → `config.json`」两行（[.gitignore:27-28](.gitignore#L27-L28)）。
- `config.py` 的项目根定位公式 `Path(__file__).resolve().parents[2]` 不变；非 editable 安装场景下用户仍需设 `STREAMXPRESS_MCP_CONFIG`。
- **不改** `src/streamxpress_mcp/client.py`。
- **不改** `src/streamxpress_mcp/sprc_import/` 下任何 DekTec 内置文件。
- 现有测试全部保留；新增一条回归测试确认「仓库自带的 `config.json` 加载后等价于默认配置」。
- 用户对本地路径修改的处理方式：**README 里指导 `git update-index --skip-worktree config.json`**（不设脚本、不设 hook）。

---

### Task 1: 用空值 `config.json` 替换模板 + 同步所有引用

**Files:**
- Delete: `config.example.json`
- Create: `config.json`
- Modify: `.gitignore`（移除末尾 `# Local per-user configuration` 与 `config.json` 两行）
- Modify: `src/streamxpress_mcp/config.py`（模块 docstring，1-9 行）
- Modify: `src/streamxpress_mcp/launcher.py`（错误消息，28 行）
- Modify: `src/streamxpress_mcp/server.py`（`launch` 工具 docstring，246-250 行）
- Modify: `README.md`（配置文件章节，19-34 行）
- Modify: `CLAUDE.md`（Config file 章节，55-65 行）
- Modify: `tests/test_config.py`（追加一条回归测试）

**Interfaces:**
- Consumes: `config_mod.load_config()`、`config_mod.DEFAULT_CONFIG_PATH: Path` — 已在 [src/streamxpress_mcp/config.py:15-17](src/streamxpress_mcp/config.py#L15-L17) 与 [src/streamxpress_mcp/config.py:40-61](src/streamxpress_mcp/config.py#L40-L61) 中定义，本任务不改签名。
- Produces: 仓库根新文件 `config.json`，加载后 `StreamXpressConfig(streamxpress_path="", sprc_api_path="", rc_port=5000)`。

- [ ] **Step 1: 追加失败测试**

在 [tests/test_config.py](tests/test_config.py) 末尾追加：

```python
def test_repo_root_config_json_loads_as_defaults(monkeypatch):
    """仓库自带的 config.json 必须字段留空、等价于文件缺失时的默认值。"""
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    assert config_mod.DEFAULT_CONFIG_PATH.is_file(), (
        f"仓库根 config.json 不存在: {config_mod.DEFAULT_CONFIG_PATH}"
    )
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == ""
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 5000
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_config.py::test_repo_root_config_json_loads_as_defaults -v`
Expected: FAIL — `AssertionError: 仓库根 config.json 不存在: ...`

- [ ] **Step 3: 新建 `config.json`**

在项目根创建 `config.json`，字段留空、`rc_port` 保留 5000（写字符串注释字段留个提示，`config.py` 只取 3 个字段，多余字段会被忽略）：

```json
{
  "_说明": "用户请直接编辑本文件填入路径；不想让本地修改进入 git，请执行: git update-index --skip-worktree config.json",
  "streamxpress_path": "",
  "sprc_api_path": "",
  "rc_port": 5000
}
```

- [ ] **Step 4: 删除模板文件**

```bash
rm config.example.json
```

- [ ] **Step 5: 更新 `.gitignore`**

删除末尾两行（[.gitignore:27-28](.gitignore#L27-L28)）：

```
# Local per-user configuration
config.json
```

删完后 `.gitignore` 末尾应停在「Git worktrees / `.worktrees/`」那一段。

- [ ] **Step 6: 改 `config.py` 模块 docstring**

将 [src/streamxpress_mcp/config.py:1-9](src/streamxpress_mcp/config.py#L1-L9) 整段替换为：

```python
"""Configuration loading for the StreamXpress MCP server.

`config.json` ships in the repository root with empty values — users
edit it in place (and typically run `git update-index --skip-worktree
config.json` so local path edits stay out of git). Lookup order:
  1. file path from env var STREAMXPRESS_MCP_CONFIG
  2. <project root>/config.json
  3. defaults (no file -> empty paths, rc_port=5000)
"""
```

- [ ] **Step 7: 改 `launcher.py` 错误消息**

编辑 [src/streamxpress_mcp/launcher.py:26-29](src/streamxpress_mcp/launcher.py#L26-L29)：

```python
    if not cfg.streamxpress_path:
        return {
            "ok": False,
            "error": "config.json 未配置 streamxpress_path，请编辑项目根 config.json 填写 StreamXpress 可执行文件路径",
        }
```

- [ ] **Step 8: 改 `server.py` 的 `launch` 工具 docstring**

编辑 [src/streamxpress_mcp/server.py:244-250](src/streamxpress_mcp/server.py#L244-L250)：

```python
def launch() -> dict:
    """Launch StreamXpress in remote-control mode using config.json settings.

    Reads streamxpress_path and rc_port from the project config.json
    at the repository root, starts StreamXpress with `-rc <port>`, and
    probes the port until the RC service is ready. Returns pid, port and
    readiness; use the returned port with connect.
    """
```

- [ ] **Step 9: 运行整套测试**

Run: `pytest -v`
Expected: 全部 PASS，新增测试 `test_repo_root_config_json_loads_as_defaults` 也过。原有 `test_launch_returns_error_when_path_empty`（[tests/test_launcher.py:7-10](tests/test_launcher.py#L7-L10)）只断言 `"streamxpress_path" in result["error"]`，不受消息文案改动影响。

- [ ] **Step 10: 改写 README 配置文件章节**

将 [README.md:19-34](README.md#L19-L34) 整段替换为：

```markdown
## 配置文件

MCP 通过项目根目录的 `config.json` 集中配置，本仓库已直接携带一份字段留空的 `config.json`——**编辑它即可**，无需复制模板：

| 字段 | 说明 |
|---|---|
| `streamxpress_path` | StreamXpress 可执行文件的完整路径（如 `C:\Program Files\DekTec\StreamXpress\StreamXpress64.exe`），`launch` 工具用它启动 |
| `sprc_api_path` | SpRcApi 目录路径，默认留空（使用包内自带 wsdl）；若填写，运行时优先使用 `<sprc_api_path>\WSDL\SpRc.wsdl` 作为 wsdl 来源 |
| `rc_port` | 远程控制端口，默认 `5000` |

查找顺序：环境变量 `STREAMXPRESS_MCP_CONFIG` 指定的文件 → 项目根 `config.json` → 默认值。字段留空时使用默认值，不报错。

> **让本地路径修改不进 git**：`config.json` 现在被 git 跟踪，直接编辑会出现在 `git status`。执行下面这一条即可让 git 忽略本地改动（仍保留仓库版本）：
>
> ```powershell
> git update-index --skip-worktree config.json
> ```
>
> 想取消：`git update-index --no-skip-worktree config.json`。

> 若以非 editable 方式安装（`pip install .`），项目根定位不适用，请用环境变量 `STREAMXPRESS_MCP_CONFIG` 指定配置文件路径。
```

- [ ] **Step 11: 改 CLAUDE.md 配置文件段落**

将 [CLAUDE.md:55-65](CLAUDE.md#L55-L65)（"## Config file (`config.json`)" 整段）替换为：

```markdown
## Config file (`config.json`)

Ships in the repo root with empty values — users edit it in place. Recommend `git update-index --skip-worktree config.json` so local edits stay out of git. Fields:

| field | effect |
|---|---|
| `streamxpress_path` | Full path to `StreamXpress.exe`/`StreamXpress64.exe`. Only used by the `launch` tool. |
| `sprc_api_path` | Optional. If set and `<sprc_api_path>/WSDL/SpRc.wsdl` exists, that WSDL replaces the bundled one. |
| `rc_port` | RC listener port for the `launch` tool. Default `5000`. |
```

- [ ] **Step 12: 提交**

```bash
git add config.json .gitignore src/streamxpress_mcp/config.py src/streamxpress_mcp/launcher.py src/streamxpress_mcp/server.py tests/test_config.py README.md CLAUDE.md
git rm config.example.json
git commit -m "refactor: ship blank config.json instead of a template

config.json is now committed with empty values; users edit it in place
and run `git update-index --skip-worktree config.json` to keep local
path edits out of git. Drops the copy-example step and syncs the three
docstring/error-message references and both README/CLAUDE.md sections.
Adds a regression test asserting the shipped config.json loads as
defaults."
```

---

## Self-Review

**1. Spec coverage:**
- 用户诉求「直接提供配置文件，不是模板，需要用户填写的内容留空」→ Step 3 建 `config.json` 空值 + Step 4 删模板 ✓
- 用户选择「文档提示 skip-worktree」→ Step 10（README）与 Step 11（CLAUDE.md）都写入 skip-worktree 提示 ✓
- 所有对 `config.example.json` 的引用（3 处 Python + 2 处文档）都在任务里点名 ✓

**2. Placeholder scan:**
- 每一步都有具体命令或代码；无 "TBD"、"handle appropriately"、"similar to Task N" 之类占位。
- Step 3 的 JSON 内容完整；Step 5 的 gitignore 删除范围精确到两行；Step 6-8 都是完整替换段。

**3. Type consistency:**
- 只依赖 `config_mod.load_config()`、`config_mod.DEFAULT_CONFIG_PATH`、`config_mod.ENV_VAR` 三个已存在符号，签名不动。
- 新增测试的三条断言（`streamxpress_path == ""`、`sprc_api_path == ""`、`rc_port == 5000`）与 [tests/test_config.py:9-12](tests/test_config.py#L9-L12) 中「文件缺失」用例断言一致。

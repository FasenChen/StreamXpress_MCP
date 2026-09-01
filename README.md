# StreamXpress MCP Server

**当前版本：** `0.2.0`（未发布）

基于 [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/) 的 MCP（Model Context Protocol）服务，让 AI 能够通过 SpRcApi 远程控制接口来操控 TS（Transport Stream）码流推送。

## 版本与发布

- 版本号唯一来源是 `pyproject.toml` 的 `project.version`，采用 Semantic Versioning。
- 在 1.0.0 之前，`MINOR` 表示新增或调整兼容行为，`PATCH` 表示缺陷修复；破坏性变更会提升 `MINOR` 并在 README 中明确说明。
- 每个版本的用户可见变更记录在 `CHANGELOG.md`；发布前把 `Unreleased` 改成日期、更新 README 当前版本、跑完整测试，然后提交 `chore: release vX.Y.Z` 并打 `vX.Y.Z` tag。

## 前置条件

- **StreamXpress** v3.x 已安装
- 一块 DekTec 输出适配器（如 DTU-315），其硬件中烧录了相应授权：
  - **DTC-302-RC**（远程控制授权，`-rc` 远程控制模式必需）
  - **DTC-300-SP**（播放许可）或 **DTC-300-NICP**（本机网卡 IP 推送许可）

  > 这些许可证固化在 DekTec 设备硬件中，插入设备后 StreamXpress 会自动识别（设备信息中可见 `Remote-control license: Yes`），无需单独激活或配置文件。
- Python 3.10+

> **关于 StreamXpress 的安装位置**：StreamXpress 由 DekTec 安装程序安装，默认位于 `C:\Program Files\DekTec\StreamXpress\`，**不在系统 PATH 中**，不能直接在任意目录下执行 `StreamXpress.exe`。另外，可执行文件名可能是 `StreamXpress.exe`（v3.x）或 `StreamXpress64.exe`（部分版本），请以实际安装为准，用完整路径调用。
>
> MCP 服务本身**不需要**把 StreamXpress 加进 PATH。`launch` / `play` 通过 `config.json` 的 `streamxpress_path` 启动本机 StreamXpress，再经 SpRcApi（`http://localhost:<rc_port>`）控制它。当前用法是**本机 DTU-315 RF 出流**：SOAP 只打 localhost，不做 TS-over-IP 远程推流。

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

## 快速开始

MCP 客户端（WorkBuddy、Claude Desktop 等）会用配置里的 `command`（默认 `python`）启动本服务，而客户端解析到的 `python` 通常**不是**项目 venv 里的 python。因此**最简单的方式是直接把包装到当前 Python 环境，不使用 venv**：

```powershell
# 1. 克隆并安装（装到当前 Python 环境，不使用 venv）
git clone <repo-url>
cd StreamXpress_MCP
pip install -e ".[dev]"

# 2. 以远程控制模式启动 StreamXpress
#    可执行文件不在 PATH 中；先在 config.json 里填好 streamxpress_path（见"配置文件"章节），
#    然后可用 MCP 的 launch 工具启动；也可手动用完整路径启动：
& "C:\Program Files\DekTec\StreamXpress\StreamXpress64.exe" -rc 5000

# 3. 运行 MCP 服务
python -m streamxpress_mcp
```

> **想用 venv 隔离？** 可以，但注意：MCP 客户端配置里的 `command` 必须指向 **venv 里的 python.exe 绝对路径**（如 `C:\...\StreamXpress_MCP\.venv\Scripts\python.exe`），不能写裸的 `python`——否则客户端会用系统 Python 启动进程，因找不到 `streamxpress_mcp` 模块而立即退出，表现为 `ModuleNotFoundError` 或 `MCP error -32000: Connection closed`。

## MCP 客户端配置

在 MCP 客户端的配置文件中添加（如 WorkBuddy 的 `mcp.json`、Claude Desktop 的 `claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "streamxpress": {
      "command": "python",
      "args": ["-m", "streamxpress_mcp"]
    }
  }
}
```

> 前提：`command` 里指定的 `python` 必须已安装本包（即执行过上面的 `pip install -e "./[dev]"`）。按上方“不使用 venv”的方式安装则保持 `"python"` 即可；若包装在 venv 里，则必须把 `command` 改为该 venv 的 `python.exe` 绝对路径。

## 可用工具

> 工具注册名如左（不带前缀）。MCP 客户端（WorkBuddy、Claude Desktop 等）通常会在工具名前加上 MCP server 名前缀，例如 `connect` 在客户端中显示为 `streamxpress_connect`。
>
> **破坏性变更：** 工具面从 62 个 SpRcApi 透传/参数 setter 收成本机预设播放器工具（当前 9 个）。升级后请在 MCP 客户端重连/重启会话以刷新工具列表。
>
> 播放语义对齐 Dolby STAMP 的 DekTec handler：`OpenFile(xml)` → `OpenFile(码流)` → `Play`。XML 是 StreamXpress `File → Save Settings` 的调制/射频快照（一群码流可共用一份）；码流路径由 `play` 显式传入，MCP 不做自动匹配。

| 工具 | 说明 |
|---|---|
| `launch` | 按 config.json 启动本机 StreamXpress（`-rc` 模式）并探测端口 |
| `connect` | 连接 StreamXpress RC 会话。默认 `host=http://localhost`，`port` 默认为 config.json 的 `rc_port` |
| `play` | 主入口：加载 settings XML → 加载码流 → 开播。未连接时会先连 localhost（必要时 `launch`），并自动选 DTU-315 |
| `pause` | 暂停播放并保留当前位置 |
| `resume` | 从暂停位置继续播放，不重新加载 XML 或码流 |
| `stop` | 停止播放 |
| `get_status` | 查询播放状态、进度、循环/速率信息、FIFO/下溢计数和健康摘要 |
| `clear_errors` | 清除播放错误计数 |
| `disconnect` | 断开 RC 会话 |

### MCP 静态描述

下表是 FastMCP 从 `server.py` 函数 docstring 生成并通过 MCP 暴露给客户端的静态 tool description。为避免翻译造成语义漂移，这里保留实际描述原文；参数名称、类型和默认值另由 input schema 自动生成。

| 工具 | 静态描述 |
|---|---|
| `launch` | Launch StreamXpress in remote-control mode using config.json settings. Reads streamxpress_path and rc_port from the project config.json at the repository root, starts StreamXpress with `-rc <port>`, and probes the port until the RC service is ready. Returns pid, port and readiness; use the returned port with connect. |
| `connect` | Connect to a StreamXpress instance running in remote-control mode. The StreamXpress must be started with: StreamXpress.exe -rc <port>. Defaults are this machine (`http://localhost`) and `rc_port` from config.json. |
| `play` | Play a stream using a StreamXpress settings XML preset. Loads the XML first (modulation / RF / loop flags), then the stream file, then starts playout. One XML can be reused by a group of streams. Auto-connects to localhost StreamXpress and selects the DTU-315 (or the unique idle port) before opening files. |
| `pause` | Pause playout and preserve the current file position. Use resume() to continue from this position. Pause is not equivalent to stop(): stop exits hold mode, while pause keeps the player in hold mode. |
| `resume` | Resume playout from pause without reloading the stream or preset. |
| `stop` | Stop playout. |
| `get_status` | Get current playout state, progress, counters, and health summary. |
| `clear_errors` | Clear the StreamXpress playout error counter. |
| `disconnect` | Disconnect from the StreamXpress remote-control session. |

`play(settings_xml, stream, loop=True)` 要求：

- XML 根元素必须是 `StreamXpressSettings`（StreamXpress 保存的设置快照；Atsc3Xpress XML 不支持）
- `settings_xml` 与 `stream` 都是 **StreamXpress 所在机器**（本机）上的绝对路径

> **关于 XML 里的 `<Filename>`**：StreamXpress 的 `OpenFile(xml)` 会尝试打开 XML 内 `<Filename>` 指向的文件，该值留空会让 `OpenFile` 直接报 `E_FILE_CANT_FIND (8195)`。因此 `play` 会在调用前自动把码流路径注入一份临时 XML 副本（原文件不动，用完即删）——你无需手动编辑 XML 的 Filename 字段，直接把 StreamXpress 保存的设置 XML 传进来即可。

## AI 交互示例

```
用户: 用 DVB-T2 474 MHz 那份预设播 SGP_SIPSI_1a.ts

AI 调用:
  1. play(
       settings_xml="D:\\SX_presets\\dvbt2_uhf_474m.xml",
       stream="D:\\Test_ts\\SGP_SIPSI_1a.ts"
     )
     # 内部：launch/连 localhost（若需要）→ 选 315 → OpenFile(xml) → OpenFile(ts) → PLAY
  2. get_status()
  3. pause()
  4. get_status()          # playout_state = PAUSE，position_percent 保持
  5. resume()
  6. get_status()          # health.num_errors / fifo_load 可用于监测下溢
  7. clear_errors()        # 需要重新开始错误观测窗口时使用
  8. stop()
  9. disconnect()
```

一群码流共用同一份 XML 时，只换 `stream` 路径即可。制式/频点/电平都在 XML 里，不在对话里现拼。

XML 用 StreamXpress GUI 调通一次后 `File → Save Settings` 生成。

## 许可证

本项目封装了 DekTec SpRcApi。使用本软件配合 StreamXpress 进行码流推送，需要 DekTec 设备提供相应授权：**DTC-300-SP/NICP**（播放授权）与 **DTC-302-RC**（远程控制授权）。这些许可证固化在 DekTec 设备硬件中，插入设备即可使用，无需单独购买或激活许可证文件。

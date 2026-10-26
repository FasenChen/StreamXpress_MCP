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
> **破坏性变更：** 工具面从 62 个 SpRcApi 透传/参数 setter 收成本机预设播放器工具（当前 10 个）。升级后请在 MCP 客户端重连/重启会话以刷新工具列表。
>
> 播放语义对齐 Dolby STAMP 的 DekTec handler：`OpenFile(xml)` → `OpenFile(码流)` → `Play`。XML 是 StreamXpress `File → Save Settings` 的调制/射频快照（一群码流可共用一份）；码流路径由 `play` 显式传入，MCP 不做自动匹配。

| 工具 | 说明 |
|---|---|
| `launch` | 按指定 `rc_port` 启动本机 StreamXpress，检查端口占用与新进程监听归属 |
| `connect` | 连接 StreamXpress RC 会话。默认 `host=http://localhost`，`port` 默认为 config.json 的 `rc_port` |
| `play` | 加载 settings XML → 加载码流 → 开播。用 `rc_port` 指定实例、`serial` 指定设备；默认选择空闲或当前 DTU-315 |
| `pause` | 暂停播放并保留当前位置 |
| `resume` | 从暂停位置继续播放，不重新加载 XML 或码流 |
| `stop` | 停止播放 |
| `get_status` | 查询播放状态、进度、循环/速率信息、FIFO/下溢计数和健康摘要 |
| `clear_errors` | 清除播放错误计数 |
| `disconnect` | 断开 RC 会话 |
| `close` | 按配置路径和 `rc_port` 正常关闭单个本机实例，确认进程退出；同端口多进程时拒绝关闭 |

`launch`、`play`、`get_status`、`pause`、`resume`、`stop`、`clear_errors`、`close` 都接受可选 `rc_port`，默认读取 config.json。显式传入时，播放和控制调用定向到本机对应实例；省略时可复用当前 stdio 进程内的已有连接，新的 stdio 进程使用配置端口。多实例操作必须每次传入相同的目标 `rc_port`，不能依赖前一次 `connect(host, port)` 在下次独立调用中保留连接。状态和控制工具不会自动启动播放器、选择输出设备或加载文件。`E_NO_PORT` 表示目标实例尚未选择输出设备，应核对目标并完成该实例的 `play`，不通过查询或停止工具自动抢占设备。

收尾使用 `stop(rc_port=目标端口)` → `close(rc_port=目标端口)`。`close` 仅匹配 `streamxpress_path` 的完整绝对路径及进程命令行中的 `-rc 目标端口`，只断开此目标的当前 RC 会话，正常关闭窗口并等待最多 5 秒；不会关闭其他端口的播放器。同路径、同 RC 端口出现多个进程时返回失败，避免误关；无 RC 参数的手动窗口也不会被关闭。成功返回 `ok=true, status=closed, running=false, pids=[退出的进程ID]`；没有匹配进程时返回 `status=not_running, running=false, pids=[]`。无法核实进程身份、无法关闭窗口或退出超时返回 `ok=false`，不能据此认定应用已退出。它不会自动连接、启动或强制结束播放器。`stop` / `disconnect` 本身仍不代表应用退出；关闭后不要再对该实例查询或播放。本工具只作用于本机，不关闭远程应用。

`launch` 遇到 RC 端口已占用时直接失败，不重复启动；确认已有实例可用后应直接调用该端口的 `play`。启动成功必须由本次新建的 PID 监听指定端口，不能拿其他进程的监听状态作为证据。启动超时或监听归属不符返回 `ok=false, ready=false`，保留返回的 PID 供诊断，不自动结束进程。

Windows 下 `launch`（包括 `play` 的自动启动）通过系统 PowerShell 调用本机 `Win32_Process.Create` 创建独立播放器，避免播放器随 stdio MCP 会话的 Windows Job Object 一并退出。此启动方式依赖本机 PowerShell 和 WMI；创建失败会报告错误，不回退到随会话清理的子进程。参见 [Microsoft Job Objects 文档](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects#managing-processes-in-jobs)。

### MCP 静态描述

下表是 FastMCP 从 `server.py` 函数 docstring 生成并通过 MCP 暴露给客户端的静态 tool description。为避免翻译造成语义漂移，这里保留实际描述原文；参数名称、类型和默认值另由 input schema 自动生成。

| 工具 | 静态描述 |
|---|---|
| `launch` | Launch StreamXpress in remote-control mode using config.json settings. Reads streamxpress_path from config.json; rc_port overrides its default. Rejects an occupied TCP port before starting. Ready is true only when the new process owns the RC listener. Use distinct ports for multiple instances and repeat rc_port on every play/control/close call. |
| `connect` | Connect to a StreamXpress instance running in remote-control mode. The StreamXpress must be started with: StreamXpress.exe -rc <port> Defaults are this machine (`http://localhost`) and `rc_port` from config.json. |
| `play` | Play a stream using a StreamXpress settings XML preset. Loads the XML first (modulation / RF / loop flags), then the stream file, then starts playout. One XML can be reused by a group of streams. Auto-connects to the local rc_port (default from config.json). Use distinct rc_port and serial values for simultaneous instances; repeat rc_port on every later control/status call. Validates files before connecting/launching. |
| `pause` | Pause playout and preserve the current file position. Use resume() to continue from this position. Pause is not equivalent to stop(): stop exits hold mode, while pause keeps the player in hold mode. Auto-connects to the local rc_port (default config.json); never launches. |
| `resume` | Resume playout from pause without reloading the stream or preset. Auto-connects to the local rc_port (default config.json); never launches. |
| `stop` | Stop playout on rc_port (default config.json); never launches or selects a device. |
| `get_status` | Get current playout state, progress, counters, and health summary. Auto-connects to the local rc_port (default config.json); never launches or selects a device. E_NO_PORT means this instance has no selected output. |
| `clear_errors` | Clear the StreamXpress playout error counter. Auto-connects to the local rc_port (default config.json); never launches. |
| `disconnect` | Disconnect from the StreamXpress remote-control session. |
| `close` | Gracefully close local StreamXpress and verify its processes have exited. Targets the configured executable and rc_port (default from config.json), including across fresh stdio sessions. Multiple processes with the same rc_port are ambiguous and will not be closed. Never connects or launches. Stop playout on the same rc_port before calling this tool. Returns ok, status (closed or not_running), running=false and process IDs only after confirming exit. A blocked window or timeout returns ok=false; it never force-kills the player. Do not call play/get_status after closing. |

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
  9. close()               # 断开会话并正常关闭应用，确认 running=false；不再调用 get_status
```

一群码流共用同一份 XML 时，只换 `stream` 路径即可。制式/频点/电平都在 XML 里，不在对话里现拼。

XML 用 StreamXpress GUI 调通一次后 `File → Save Settings` 生成。

### 两路同时出流

每个实例使用不同 RC 端口和不同设备序列号。以下 `设备A序列号` / `设备B序列号` 必须替换为实际 DTU-315 的整数序列号；RC 端口与返回的物理设备 `port` 是不同概念。资源完整路径、实例端口和设备分配必须进入各执行任务，不能只保留在规划额外输入或 setup_steps 中。

```python
launch(rc_port=5000)  # 已监听时不重复 launch
launch(rc_port=5001)
play(settings_xml=r"D:\Resource\MALAYSIA\MYS_SIPSI.xml",
     stream=r"D:\Resource\MALAYSIA\2.0 LCN Test\MYS_SIPSI_2.1b.ts",
     rc_port=5000, serial=设备A序列号)
play(settings_xml=r"D:\Resource\MALAYSIA\MYS_SIPSI_2.xml",
     stream=r"D:\Resource\MALAYSIA\2.0 LCN Test\FGN_SIPSI_2.2.ts",
     rc_port=5001, serial=设备B序列号)
get_status(rc_port=5000)
get_status(rc_port=5001)  # 合理间隔后分别复查推进，两个实例持续 PLAY
stop(rc_port=5000)
stop(rc_port=5001)
close(rc_port=5000)
close(rc_port=5001)
```

`serial=0`（默认）会排除其他应用占用的端口，并优先复用当前 315；定向双路用例应明确指定两台设备。指定的 serial 被占用时会报告错误及端口状态，不会换用其他设备。

## 许可证

本项目封装了 DekTec SpRcApi。使用本软件配合 StreamXpress 进行码流推送，需要 DekTec 设备提供相应授权：**DTC-300-SP/NICP**（播放授权）与 **DTC-302-RC**（远程控制授权）。这些许可证固化在 DekTec 设备硬件中，插入设备即可使用，无需单独购买或激活许可证文件。

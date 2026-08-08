# StreamXpress MCP Server

基于 [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/) 的 MCP（Model Context Protocol）服务，让 AI 能够通过 SpRcApi 远程控制接口来操控 TS（Transport Stream）码流推送。

## 前置条件

- **StreamXpress** v3.x 已安装
- 一块 DekTec 输出适配器（如 DTU-315），其硬件中烧录了相应授权：
  - **DTC-302-RC**（远程控制授权，`-rc` 远程控制模式必需）
  - **DTC-300-SP**（播放许可）或 **DTC-300-NICP**（本机网卡 IP 推送许可）

  > 这些许可证固化在 DekTec 设备硬件中，插入设备后 StreamXpress 会自动识别（设备信息中可见 `Remote-control license: Yes`），无需单独激活或配置文件。
- Python 3.10+

> **关于 StreamXpress 的安装位置**：StreamXpress 由 DekTec 安装程序安装，默认位于 `C:\Program Files\DekTec\StreamXpress\`，**不在系统 PATH 中**，不能直接在任意目录下执行 `StreamXpress.exe`。另外，可执行文件名可能是 `StreamXpress.exe`（v3.x）或 `StreamXpress64.exe`（部分版本），请以实际安装为准，用完整路径调用。
>
> MCP 服务本身**不需要**配置 StreamXpress 的安装位置——它通过 SpRcApi（HTTP/SOAP）远程控制接口连接 StreamXpress，只需在 `connect` 工具中指定 StreamXpress 所在主机的地址和 `-rc` 监听端口（默认 `http://localhost:5000`）。MCP 与 StreamXpress 可以分处两台机器。

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
> 这是破坏性变更：工具名已从 `streamxpress_connect` 等改为无前缀的 `connect` 等。升级后请在各 MCP 客户端（WorkBuddy、Claude Desktop 等）重新连接/重启会话以刷新工具列表，旧名不再注册。
>
> 新增的 `launch` 工具同样无前缀，客户端中显示为 `streamxpress_launch`。
>
> 当前共注册 **59** 个工具（13 个基础 + 46 个 SpRcApi 接口透传）。

| 工具 | 说明 |
|---|---|
| `launch` | 按 config.json 启动 StreamXpress（-rc 模式）并探测端口 |
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
| `get_remote_version` | 获取服务器端 SpRcApi 版本 |
| `get_remote_dtapi_version` | 获取服务器端 DTAPI 版本 |
| `get_app_info` | 获取应用名称与版本 |
| `show_window` | 显示/隐藏 StreamXpress 窗口 |
| `clear_errors` | 清除播放错误计数器 |
| `get_asi_pars` | 读取 DVB-ASI 参数 |
| `get_cmmb_pars` | 读取 CMMB 调制参数 |
| `get_mod_pars` | 读取调制参数（ModType/SymRate 等） |
| `get_rf_pars` | 读取 RF 参数（频率/电平/SpecInv/CW） |
| `get_tsoip_pars` | 读取 TS-over-IP 参数 |
| `get_spi_pars` | 读取 DVB-SPI 参数 |
| `get_hw_noise_pars` | 读取硬件噪声参数（DTA-107/DTA-2107） |
| `get_iq_gain` | 读取 IQ 增益（0.1 dB） |
| `get_signal_source` | 读取信号源（文件/测试信号发生器） |
| `get_use_nit` | 读取是否使用 NIT 推导调制参数 |
| `get_channel_modelling_pars` | 读取信道建模参数（噪声+多径） |
| `get_dvb_t2_group` | 读取 DVB-T2 参数组选择 |
| `get_dvb_t2_pars` | 读取 DVB-T2 调制参数 |
| `get_isdb_t_pars` | 读取 ISDB-T 调制参数 |
| `get_tdt_adapt_pars` | 读取 TDT/TOT 适配参数 |
| `get_tsg_pars` | 读取测试信号发生器参数 |
| `get_sfn_status` | 读取 GPS 与 SFN 播放状态 |
| `open_channel_modelling_file` | 打开信道建模文件（.chmx） |
| `save_channel_modelling_settings` | 保存信道建模设置（.chmx） |
| `save_settings` | 保存全部设置（.xml） |
| `normalise` | 归一化多径信道建模增益 |
| `set_loop_flags` | 设置循环适配标志（CC/PCR/TDT/Wrap） |
| `set_iq_gain` | 设置 IQ 增益（0.1 dB） |
| `set_remux` | 开关实时重复用 |
| `set_signal_source` | 设置信号源（文件/测试信号发生器） |
| `set_use_nit` | 设置是否使用 NIT 推导调制参数 |
| `set_sfn_mode` | 设置 SFN 模式（禁用/1PPS） |
| `set_sub_loop_pars` | 设置文件子循环位置 |
| `select_dta_plus` | 选择 DtaPlus 衰减器设备 |
| `set_cmmb_pars` | 设置 CMMB 调制参数 |
| `set_hw_noise_pars` | 设置硬件噪声参数 |
| `set_spi_pars` | 设置 DVB-SPI 传输参数 |
| `set_tsg_pars` | 设置测试信号发生器参数 |
| `set_dvb_t2_group` | 选择 DVB-T2 参数组 |
| `set_mod_pars` | 设置调制参数 |
| `set_channel_modelling_pars` | 设置信道建模参数（噪声+多径） |
| `set_dvb_t2_pars` | 设置 DVB-T2 调制参数 |
| `set_isdb_t_pars` | 设置 ISDB-T 调制参数 |
| `set_tdt_adapt_pars` | 设置 TDT/TOT 适配参数 |
| `set_playout_state_sfn` | SFN 同步播放/停止（带 GPS 开始时间） |
| `wait_for_condition` | 阻塞等待播放条件（如停止） |

## AI 交互示例

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

## 许可证

本项目封装了 DekTec SpRcApi。使用本软件配合 StreamXpress 进行码流推送，需要 DekTec 设备提供相应授权：**DTC-300-SP/NICP**（播放授权）与 **DTC-302-RC**（远程控制授权）。这些许可证固化在 DekTec 设备硬件中，插入设备即可使用，无需单独购买或激活许可证文件。

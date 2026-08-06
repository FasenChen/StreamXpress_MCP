# StreamXpress MCP Server

基于 [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/) 的 MCP（Model Context Protocol）服务，让 AI 能够通过 SpRcApi 远程控制接口来操控 TS（Transport Stream）码流推送。

## 前置条件

- **StreamXpress** v3.x 已安装，且持有 **DTC-302-RC 许可证**（远程控制授权）
- 一块 DekTec 输出适配器，持有 **DTC-300-SP**（播放许可）或 **DTC-300-NICP**（本机网卡 IP 推送许可）
- Python 3.10+

> **关于 StreamXpress 的安装位置**：StreamXpress 由 DekTec 安装程序安装，默认位于 `C:\Program Files\DekTec\StreamXpress\`，**不在系统 PATH 中**，不能直接在任意目录下执行 `StreamXpress.exe`。另外，可执行文件名可能是 `StreamXpress.exe`（v3.x）或 `StreamXpress64.exe`（部分版本），请以实际安装为准，用完整路径调用。
>
> MCP 服务本身**不需要**配置 StreamXpress 的安装位置——它通过 SpRcApi（HTTP/SOAP）远程控制接口连接 StreamXpress，只需在 `connect` 工具中指定 StreamXpress 所在主机的地址和 `-rc` 监听端口（默认 `http://localhost:5000`）。MCP 与 StreamXpress 可以分处两台机器。

## 快速开始

MCP 客户端（WorkBuddy、Claude Desktop 等）会用配置里的 `command`（默认 `python`）启动本服务，而客户端解析到的 `python` 通常**不是**项目 venv 里的 python。因此**最简单的方式是直接把包装到当前 Python 环境，不使用 venv**：

```powershell
# 1. 克隆并安装（装到当前 Python 环境，不使用 venv）
git clone <repo-url>
cd StreamXpress_MCP
pip install -e ".[dev]"

# 2. 以远程控制模式启动 StreamXpress
#    可执行文件不在 PATH 中，需用完整路径；文件名可能是 StreamXpress.exe 或
#    StreamXpress64.exe，以实际安装为准（也可先把其目录加入 PATH 再直接调用）
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

## AI 交互示例

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
  9. stop()
  10. disconnect()
```

## 许可证

本项目封装了 DekTec SpRcApi。使用本软件配合 StreamXpress 进行码流推送，需要持有有效的 DekTec 许可证（DTC-300-SP + DTC-302-RC）。

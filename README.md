# StreamXpress MCP Server

基于 [DekTec StreamXpress](https://www.dektec.com/products/applications/StreamXpress/) 的 MCP（Model Context Protocol）服务，让 AI 能够通过 SpRcApi 远程控制接口来操控 TS（Transport Stream）码流推送。

## 前置条件

- **StreamXpress** v3.x 已安装，且持有 **DTC-302-RC 许可证**（远程控制授权）
- 一块 DekTec 输出适配器，持有 **DTC-300-SP**（播放许可）或 **DTC-300-NICP**（本机网卡 IP 推送许可）
- Python 3.10+

## 快速开始

```powershell
# 1. 克隆并安装
git clone <repo-url>
cd StreamXpress_MCP
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 2. 以远程控制模式启动 StreamXpress
StreamXpress.exe -rc 5000

# 3. 运行 MCP 服务
python -m streamxpress_mcp
```

## MCP 客户端配置

在 MCP 客户端的配置文件中添加（如 Claude Desktop 的 `claude_desktop_config.json`）：

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

## 可用工具

| 工具 | 说明 |
|---|---|
| `streamxpress_connect` | 连接 StreamXpress RC 会话 |
| `streamxpress_disconnect` | 断开连接 |
| `streamxpress_scan_ports` | 扫描可用输出端口 |
| `streamxpress_select_port` | 选择输出端口 |
| `streamxpress_open_file` | 加载 TS 文件 |
| `streamxpress_start` | 开始播放 |
| `streamxpress_stop` | 停止播放 |
| `streamxpress_get_status` | 查询播放进度和状态 |
| `streamxpress_set_rate` | 设置 TS 码率（bps） |
| `streamxpress_set_tsoip_params` | 配置 UDP/RTP TS-over-IP 输出参数 |
| `streamxpress_set_rf_params` | 设置 RF 频率和电平 |
| `streamxpress_set_asi_params` | 设置 ASI 重复用和包模式 |

## AI 交互示例

```
用户: 把 C:\Streams\news.ts 以 25 Mbps 推送到组播地址 239.1.1.1:1234

AI 依次调用:
  1. streamxpress_connect(host="http://localhost", port=5000)
  2. streamxpress_scan_ports() → 选择一个 TS-over-IP 端口
  3. streamxpress_select_port(serial=..., port_num=1)
  4. streamxpress_set_tsoip_params(dest_ip="239.1.1.1", dest_port=1234, protocol="UDP")
  5. streamxpress_set_rate(rate_bps=25_000_000)
  6. streamxpress_open_file(filepath="C:\\Streams\\news.ts")
  7. streamxpress_start()
  8. streamxpress_get_status() → 监控播放进度
```

## 许可证

本项目封装了 DekTec SpRcApi。使用本软件配合 StreamXpress 进行码流推送，需要持有有效的 DekTec 许可证（DTC-300-SP + DTC-302-RC）。

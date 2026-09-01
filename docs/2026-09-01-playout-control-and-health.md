# 播放控制与健康监测开发说明

日期：2026-09-01

## 目标

在保留现有“预设播放器”使用方式的前提下，补齐播放开始后的两个小能力：

1. **暂停/继续**：暂停时保留文件位置，继续时不重新加载 settings XML 和码流。
2. **状态与健康监测**：在一次 `get_status` 调用中返回官方播放状态、进度、循环/速率、缓冲与错误计数，并提供保守的健康摘要；同时允许清除错误计数。

官方依据：SpRcApi V5 规格中的 `SetPlayoutState`、`GetPlayoutInfo`、`GetPlayoutStatus`、`ClearErrors`（见 `docs/SpRcApi_spec_md/SpRcApi_V5_zh.md`）。

## MCP 工具面

| 工具 | 参数 | 返回 | 行为 |
|---|---:|---|---|
| `pause` | 无 | `{"status":"paused"}` | 调用 SOAP `SetPlayoutState(SPRC.STATE_PAUSE)` |
| `resume` | 无 | `{"status":"playing"}` | 调用 SOAP `SetPlayoutState(SPRC.STATE_PLAY)`，不重选端口、不重开文件 |
| `get_status` | 无 | 播放状态与健康信息字典 | 依次调用 `GetPlayoutStatus`、`GetPlayoutInfo`，合并为稳定 schema |
| `clear_errors` | 无 | `{"status":"ok"}` | 调用 SOAP `ClearErrors`，清除官方下溢错误计数 |

`stop` 和 `play` 语义保持稳定：`stop` 停止播放；`play` 仍是加载 XML 与码流并开播的主入口。若调用 `play` 时处于 `PLAY` 或 `PAUSE`，先进入 `STOP`，再执行原有的选端口、加载 XML、加载码流和开播流程。

## `get_status` schema

`get_status` 保留全部既有键，并补充官方 `SpRcPlayoutInfo` 中此前缺失的 5 个字段：

- `file_offset_start`
- `file_offset_end`
- `file_played_bytes`
- `time_loop_begin`
- `time_loop_end`

新增 `health` 对象：

```json
{
  "healthy": false,
  "warnings": ["FILE_NOT_READABLE", "UNDERFLOW_ERRORS"],
  "num_errors": 3,
  "fifo_load": 37,
  "total_mem_load": 2048,
  "file_can_be_read": false
}
```

健康规则刻意保持保守：

- `FileCanBeRead == false` => `FILE_NOT_READABLE`
- `NumErrors > 0` => `UNDERFLOW_ERRORS`
- `healthy = len(warnings) == 0`
- `fifo_load`、`total_mem_load` 只如实上报，不自动判定异常；官方文档未给出通用告警阈值，不同设备与码流的合理阈值不同。

`playout_state` 使用官方三态：`PAUSE`、`PLAY`、`STOP`，同时保留 `playout_state_raw`。

## 实现约束

- 所有新增客户端方法必须通过 `StreamXpressClient._sprc_call` 调 vendored SOAP 客户端。
- `pause` 与 `resume` 不做本地状态预判，由 StreamXpress 作为唯一状态源；调用后可用 `get_status` 验证。
- `resume` 不自动连接或自动开播；未连接时沿用现有 `_sprc_call` 错误路径。
- 本功能不暴露 `WaitForCondition`。官方 `WaitForCondition(-1)` 可无限等待，直接作为 MCP 工具容易长时间占用调用线程；如未来需要，必须强制有限超时并单独评审锁与超时行为。

## 测试要求

`pytest` 覆盖以下场景，全部使用 mock，不访问真实 SOAP：

- `pause` 调用 `set_playout_state(SPRC.STATE_PAUSE)`。
- `resume` 调用 `set_playout_state(SPRC.STATE_PLAY)`。
- `clear_errors` 调用底层 `clear_errors()`。
- `get_status` 在 `PAUSE` 状态下返回可读状态名和原始值。
- `get_status` 补齐 5 个缺失字段，并正确合并 `health`。
- `FILE_NOT_READABLE` 与 `UNDERFLOW_ERRORS` 同时出现时 `healthy=false`。
- MCP 注册名精确等于 9 个工具：`launch`、`connect`、`play`、`pause`、`resume`、`stop`、`get_status`、`clear_errors`、`disconnect`。
- README 工具表与 `EXPECTED_TOOL_NAMES` 同步。

推荐命令：

```powershell
pytest tests/test_client.py tests/test_server.py
pytest
```

## 兼容性与运维说明

- 这是工具面追加，不改名、不改变既有 `play` / `stop` / `get_status` 参数。
- `get_status` 既有键全部保留；新增字段和 `health` 为增量。
- MCP 客户端升级后需要重连/重启会话以刷新工具列表。
- `clear_errors` 只重置计数，不修复已经发生的下溢；清除后应继续用 `get_status` 观测新窗口。

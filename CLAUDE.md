# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指引。

## 项目概述

一个 MCP（Model Context Protocol）服务，让 AI 客户端通过 **DekTec StreamXpress** 的 SOAP 远程控制接口 `SpRcApi` 驱动 TS 码流播出。MCP 进程只与 StreamXpress 说 HTTP/SOAP，两者可以分处不同机器。StreamXpress 本身必须以远程控制模式启动（`StreamXpress.exe -rc <port>`），这要求 DekTec 硬件中烧录了 `DTC-302-RC` 许可。

主要参考：[README.md](README.md)（中文；许可约束和客户端配置陷阱以它为准）。

## 常用命令

开发安装（README 里说明了为什么 venv 安装会让 MCP 客户端配置变复杂）：

```powershell
pip install -e ".[dev]"
```

以 stdio 运行 MCP 服务（MCP 客户端实际调用的方式）：

```powershell
python -m streamxpress_mcp
```

测试（pytest，`testpaths = ["tests"]`）：

```powershell
pytest                                # 全套
pytest tests/test_client.py           # 单个文件
pytest tests/test_client.py::TestStreamXpressConnect::test_connect_creates_session
pytest -k connect                     # 按关键字
```

未配置 linter/formatter —— 请与周围代码风格保持一致。

## 架构

自上而下四层：

1. **MCP 工具面** —— [src/streamxpress_mcp/server.py](src/streamxpress_mcp/server.py)：单个 `FastMCP("streamxpress-mcp")` 实例，**6 个 `@mcp.tool()` 函数**：`launch` / `connect` / `play` / `stop` / `get_status` / `disconnect`。主路径是 `play(settings_xml, stream)`：`OpenFile(xml)` → `OpenFile(码流)` → `Play`，自动连 localhost 并选 DTU-315。工具名**不带前缀**。新增或改名要同步三处：代码、[tests/test_server.py](tests/test_server.py) 里的 `EXPECTED_TOOL_NAMES`、以及 README 工具表。
2. **客户端包装层** —— [src/streamxpress_mcp/client.py](src/streamxpress_mcp/client.py)：`StreamXpressClient` 持有单个 `SPRC_client` 会话，跟踪 `_connected`，把 Python 风格的参数翻译成 SOAP 层要的 C 风格结构体。通过 `sprc_factory=` 注入以便测试。
3. **单例接线** —— `server.py:get_client()` 在首次工具调用时惰性构建 `StreamXpressClient`，用 `resolve_wsdl_path(load_config())` 决定是否给 `SPRC_client` 传自定义 `wsdl_template`。整个服务的状态都围绕这一个客户端实例。
4. **Vendored SOAP 层** —— [src/streamxpress_mcp/sprc_import/](src/streamxpress_mcp/sprc_import/)：DekTec 提供的 `SPRC_client.py`（基于 zeep）、类型、常量和 `SpRc.wsdl`。**不要**手工编辑这些文件，视为第三方代码。`.wsdl` 作为包数据分发（见 `pyproject.toml` 的 `[tool.setuptools.package-data]`）。`SPRC_client.__init__` 接受可选的 `wsdl_template` 路径 —— 这就是 `config.json` 里用户提供的 `sprc_api_path` 覆盖内置 WSDL 的机制。

### 工具层与客户端层之间的约定

- **每次 vendored 调用都要走 `_sprc_call(fn)`**（[client.py](src/streamxpress_mcp/client.py)），它是错误转换边界。新方法里不要直接碰 `self._sprc`，也不要在一个包装方法内部调用另一个包装方法 —— 读和写都要经由**同一次** `_sprc_call`，这样错误转换和会话失效检测才能覆盖整个操作。它做三件事：在锁内解析会话、把 `SpRcException` 转成带错误码名与数值的 `RuntimeError`（vendored 异常的 `str()` 是空的，否则错误码就丢了）、以及在传输层故障时把会话标记失效。
- **锁只在解析会话引用时持有，绝不跨 SOAP 调用。** 跨调用持锁会串行化所有工具，把一个慢调用变成整个服务器挂死且无恢复路径 —— 连 `disconnect` 都会被挡住。`_mark_stale(sprc)` 会短暂重新取锁，且只在 `self._sprc is sprc` 时才清 `_connected`，这样一个迟到失败的在途调用就不会误杀用户此后重连出来的新会话。
- **FastMCP 把同步工具卸载到 AnyIO 工作线程**，所以两次工具调用会真正重叠，并发是真实的。这正是会话状态变更需要加锁的原因：`_sprc_call` 在锁内解析会话引用，避免一个 `disconnect` 和另一个 `play` 交错时拿到失效的 `self._sprc`。
- **`_ensure_connected()` 守卫每一次调用**，抛 `RuntimeError("not connected — call connect() first")`。它和 `SpRcException` 都不在工具层捕获，所以故障会以异常形式暴露给 MCP 客户端。
- **`connect` 近似幂等**：工具会先 best-effort `disconnect()`（并压掉错误），因为 `StreamXpressClient.connect` 在已连接时会抛异常。

两个辅助工具：

- [config.py](src/streamxpress_mcp/config.py) —— 按此顺序解析 `config.json`：`$STREAMXPRESS_MCP_CONFIG` → `<项目根>/config.json` → 默认值。文件缺失或字段缺失都不算错误，但 `$STREAMXPRESS_MCP_CONFIG` 指向的路径不存在、JSON 无法解析、或顶层不是对象，都会抛 `ValueError`（消息是中文）。`PROJECT_ROOT` 从模块文件往上走两级，所以**非 editable 安装（`pip install .`）会破坏项目根回退** —— 用户必须设环境变量。改 `config.py` 时请保持这个契约。
- [launcher.py](src/streamxpress_mcp/launcher.py) —— `launch` 工具以 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`（Windows 专有标志）启动 `streamxpress_path -rc <rc_port>`，并轮询 TCP `127.0.0.1:<port>` 最多 10×0.5 秒等待就绪。未配置或可执行文件不存在时返回 `{"ok": False, "error": ...}` 而非抛异常。不改 `creationflags` 无法移植到非 Windows。

## 测试

- [tests/conftest.py](tests/conftest.py) 提供 `mock_sprc`（MagicMock）和 `client` fixture，后者通过 `sprc_factory=` 注入前者。优先用这个 fixture 而不是 patch 模块全局 —— 那个 DI 钩子就是为测试准备的。
- 两种风格，按被测层次选择：**client 层**测试在 [tests/test_client.py](tests/test_client.py) 里用 `client`/`mock_sprc` fixture，断言 vendored 调用。**server 层**测试在 [tests/test_server.py](tests/test_server.py) 里用 `@patch("streamxpress_mcp.server.get_client")` 并直接 import 工具函数 —— 在 fastmcp 3.x 下 `@mcp.tool()` 会保留原函数可导入，所以 `connect(host=..., port=...)` 不必走 MCP 协议。patch `get_client` 比重置 `server._client` 单例更可取。
- **断言要能失败。** 只断言 `{"status": "ok"}` 而 client 是 MagicMock 的测试**永远不可能失败** —— 无论工具往下传了什么。构造结构体的测试要从 `call_args[0][0]` 取出结构体并检查字段。另外注意测试数据本身：如果传的值恰好等于 bug 会产生的值（比如传 `0` 而 bug 是硬编码 `0`），断言再对也抓不到。同一 fixture 里的多个字段应取不同的值，否则字段串位无法被发现。
- 测试中从不发起真实 SOAP 调用，vendored 的 `SPRC_client` 被完全 stub。例外是 [tests/test_sprc_wsdl.py](tests/test_sprc_wsdl.py)，它调用私有的 `_SPRC_client__create_wsdl_file_for_service` 来验证自定义 WSDL 与内置 WSDL 的选择逻辑。

## 配置文件（`config.json`）

仓库根目录自带一份字段留空的版本 —— 用户直接编辑它。建议执行 `git update-index --skip-worktree config.json` 让本地改动不进 git。字段：

| 字段 | 作用 |
|---|---|
| `streamxpress_path` | `StreamXpress.exe`/`StreamXpress64.exe` 的完整路径。仅 `launch` 工具使用。 |
| `sprc_api_path` | 可选。若设置且 `<sprc_api_path>/WSDL/SpRc.wsdl` 存在，则用它替换内置 WSDL。 |
| `rc_port` | `launch` 工具用的 RC 监听端口。默认 `5000`。 |

## 参考资料

- `SpRcApi/` —— DekTec 提供的厂商 SDK 原始包：`Doc/SpRcApi.pdf`、`Include/SpRcApi.h` + `DTAPI.h`（**常量取值以头文件为准**）、`WSDL/`。常量含义不清时查头文件。
- `docs/SpRcApi_spec_md/` —— 转成 Markdown 的 API 规格（英文 + 中文）。比 PDF 好 grep。
- `docs/superpowers/plans/` —— 各功能的实现计划，含 46 工具补全那次的约束记录。
- `docs/制式/` —— 各制式（DVB-T2 等）的 StreamXpress GUI 配置截图，用于把界面字段对应到 `SpRc*Pars` 结构体字段。

## 坑

- **StreamXpress.exe 不在 PATH 里** —— 始终用绝对路径调用（或用 `launch` 工具）。
- **vendored 层是 SpRcApi v1.11，而文档是 v1.12** —— v1.12 新增的字段在 `SPRC_types.py` 里不存在，不能暴露。信规格之前先看 dataclass。反过来也有陷阱：v1.12 的某些"新增"其实只是**改名**（`SPRC_TSG_TYPE_SDI_STATIC` 就是 `RP198`，同一个值 7），所以功能本身在 v1.11 就能用，只需用老名字 —— 判断是否真的被 SDK 卡住，要查头文件。
- **MCP 客户端 `command` 的坑** —— 若用户装在 venv 里，其 `mcp.json`/`claude_desktop_config.json` 的 `command` 必须指向 venv 内 `python.exe` 的绝对路径；写裸的 `"python"` 会用系统解释器并以 `ModuleNotFoundError` 失败。
- **工具名破坏性变更** —— 工具以前叫 `streamxpress_connect` 之类，现在是上面那些无前缀名。不要在 server 层重新引入前缀。
- **launcher 是 Windows 专有的** —— 那些 `subprocess.Popen` 标志在 Linux/macOS 上无效。

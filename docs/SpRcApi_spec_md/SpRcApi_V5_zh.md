# StreamXpress 远程控制 API（SpRcApi）

## 功能特性（Features）

• 可在同一台 PC 或网络上的其他 PC 远程控制 StreamXpress 功能

• 客户端与 StreamXpress 之间使用业界标准的 SOAP 消息进行通信

• 通过 WSDL 文件可自动生成 SOAP 代理（Proxy）

• 运行 StreamXpress 的 DekTec 设备上需要具备远程控制（RC）许可证

## SpRcApi – 修订历史（Revision History）

| 版本 | 日期 | 变更说明 |
| --- | --- | --- |
| v1.12.0.21 | 2026.04.14 | 新增手动指定 AWGN 噪声发生器种子（seed）的选项 |
| v1.12.0.20 | 2024.11.25 | 新增对 SMPTE RP-198 和 RP-219-1 高清彩条测试图案的支持 |
| v1.11.0.19 | 2024.05.31 | 新增 GetSfnStatus()、SetPlayoutStateSfn() 和 SetSfnMode() 以控制单频网（SFN）播放；新增 GetTdtAdaptPars()/SetTdtAdaptPars() 以设置修改 TDT/TOT 中的时间；可按需提供 Phyton 示例 RC 客户端代码；不再分发 Visual Studio 2015 库 |
| v1.10.1.18 | 2023.03.10 | 与 StreamXpress v3.31.0.772 及更新版本同步，SpRcTsoIpPars 有细微变化 |
| v1.10.0.17 | 2021.12.17 | 新增对 VC17（Visual Studio 2022）库的支持；新增对 64 位 Visual Studio 库的支持；新增 SetSubLoopPars 函数用于设置文件播放的相对起始与停止位置；不再分发 Visual Studio 2010、2012 和 2013 库 |
| v1.9.0.16 | 2021.03.16 | 新增对 VC16（Visual Studio 2019）库的支持；新增对 ATSC3.0 STLTP（演播室到发射机链路传输协议）的支持；新增对 Digital Radio Mondial（DRM/DRM+）的支持；新增对 DVB-T2 版本配置的支持 |
| v1.7.0.14 | 2019.08.05 | 新增对 VC11、V12、VC14 和 VC15 库的支持；新增对 ISDB-S3 的支持 |
| v1.6.0.13 | 2015.01.08 | 新增 GetTsgPars()/SetTsgPars() 以控制测试信号发生器选项 |
| v1.5.0.12 | 2014.06.25 | 扩展 SpRcTsoipPars 以支持 DTA-2162 上的双缓冲；新增 GetIqGain()/SetIqGain() 函数，允许在播放 IQ 信号时改变 IQ 增益；新增 GetRemoteDtapiVersion() 以检查构建 StreamXpress 所使用的 DTAPI 版本 |
| v1.4.3.10 | 2014.04.24 | 新增对 DVB-S2X 和 S2L3 的支持 |
| v1.4.2.9 | 2014.02.13 | 修复链接问题的错误修复版本 |
| v1.4.1.8 | 2013.03.01 | 新增对 DtaPlus 设备的支持；新增 SetRemux() 函数以控制调制器端口上的重复用（remultiplexing） |
| v1.3.0.6 | 2012.05.15 | 新增 Normalise 函数；新增 Open 和 SaveChannelModellingSettings 函数；新增 Set 和 GetSignalSource 函数；新增 Set 和 GetUseNit 函数；RfPars 结构体新增变量：SpecInv、CW、RfEnabledOnStop；新增 SaveSettings 函数 |
| v1.2.0.5 | 2011.09.27 | 新增 Set 和 GetCmmbPars 函数；新增 Set 和 GetDvbT2Group 函数；新增 Set 和 GetHwNoisePars 函数；WSDL 命名空间，移除 &quot;http://localhost:80/SpRc.wsdl&quot;；新增 SpRcApiNET .NET WSDL 代理包装器示例代码；文档与 SpRc 源代码同步 |
| v1.1.0.4 | 2010.12.08 | 新增 Set 和 GetChannelModellingPars 函数；发布符合 WS-I Basic Profile 1.0a 的 WSDL 描述，用于自动生成代理（例如供 Visual Studio.NET 和 LabView 等工具使用）；新增 ShowWindow 函数用于隐藏/显示 StreamXpress 窗口 |
| v1.0.0.1 | 2009.02.16 | 首次对外发布 |

------

## 1. 使用 SpRcApi

### 1.1. 简介

StreamXpress 远程控制 API（SpRcApi）使客户端应用程序能够远程控制 StreamXpress，以实现流的自动化播放。客户端可以运行在与 StreamXpress 相同的 PC 上，也可以运行在网络中的另一台 PC 上。StreamXpress GUI 中可用的大部分功能同样可以通过 SpRcApi 使用。

在本文档中，被远程控制的 StreamXpress 将交替称为“服务器”（server）、“播放服务器”（playout server）或“StreamXpress”。

客户端是希望远程控制 StreamXpress 的应用程序。

### 1.2. 运行 StreamXpress

要将 StreamXpress 作为播放服务器运行，需要满足以下条件：

1. 用于 StreamXpress 播放的 DekTec 设备包含远程控制（RC）许可证；

2. 以 –rc 选项启动 StreamXpress，后跟用于连接的 TCP 端口号，例如 –rc 9000。

### 1.3. 客户端-服务器通信

客户端和服务器通过 IP 网络上的 SOAP 调用进行通信，或使用本地主机（local host）通信。SOAP 是一种标准化协议，使用 XML 格式的消息来执行远程过程调用。

目前，SpRcApi 支持 SOAP 协议 1.1 版本。

### 1.4. 使用 SpRcApi

基本上有 4 种方式部署 SpRcApi：

- 在可导入 WSDL 文件的应用程序中使用 WSDL 文件，例如 Labview。
- 使用 WSDL 文件自动生成客户端代码，通常称为“代理”（proxy）。通过代理可以调用 API 方法。第 2 节描述了使用 Visual Studio 创建代理的示例。
- 使用 SpRcApiNET 示例代码，其中包含针对 WSDL 生成的代理代码的 .NET“包装器”（wrapper）。
- 对于使用 C++ 编写的客户端，提供了一个库，使远程控制方法可以作为 C++ 方法使用。详见第 3 节。

本文档的主要部分以 C++ 语法描述 SpRcApi 中的类和 API 调用。C++ 描述很容易映射到等效的 SOAP 调用，因为 WSDL API 的结构类似。有一个例外：不能直接使用 SpRcClient 常量，应使用等效的整数值。

## 2. 从 WSDL 创建代理（Creating a Proxy from WSDL）

### 2.1. SpRc.wsdl

WSDL 包含在 SpRc.wsdl 文件中，该文件可在 SpRcApi.zip 中获得。

SpRc.wsdl 描述是符合 WS-I Basic Profile 1.0a 的 Web 服务描述。该文件可用于多种工具来自动生成客户端代理代码。例如，LabView 和 Visual Studio 都支持导入 WSDL 文件。

### 2.2. 生成代理（Generating the Proxy）

以下步骤描述如何在 Visual Studio 环境的 C# 程序中生成代理代码并使用该代码：

1. 创建 C# 项目后，右键单击“引用”（References），然后选择“添加服务引用…”（Add Service Reference…）。

2. 在“添加服务引用”对话框中，选择 SpRc.wsdl 的位置，更改命名空间（Namespace），然后单击“确定”按钮。这将开始代理代码生成。

![1](assets/1.png)

有些工具不接受文件位置，对于这些工具，可以使用以下地址定位 SpRc.wsdl：http://www.dektec.com/Products/Apps/DTC-300/SpRc.wsdl 

3. 调整生成的 'app.config' 文件，改为正确的远程 IP 地址和使用的端口号。

```xml
<client>
    <endpoint
    address = "http://localhost:9000"
    binding = "basicHttpBinding"
    bindingConfiguration = "SpRc"
    contract = "SpRc.SpRcPortType"
    name = "SpRc" />
</client>
```

4. 下面的 C# 代码演示了如何实例化生成的远程控制客户端代理，以及如何执行一些远程控制调用。

   接口调用和结构体与所述的 SpRcClient API 类似，但存在一些差异：

   1. 结果代码可以通过 out 参数返回，参数可以通过返回值返回。
   2. 不能使用 SpRcClient 常量，应使用等效的整数值。

```cpp
// Instantiate .NET generated RC client（实例化 .NET 生成的 RC 客户端）
SpRc.SpRcPortTypeClient cl =
    newSpRc.SpRcPortTypeClient();

// Open a session（打开会话）
uint res = cl.OpenSession();

// Scan Ports（扫描端口）
SpRc.PortDesc[] ports =
    cl.ScanPorts(out res);

// Select DVB-C Modulation（选择 DVB-C 调制）
// (9 : SPRC_MOD_J83A)
res = cl.SelectPort(ports[0].Serial,
    ports[0].Port, 9, out status);
```

## 3. 使用静态链接库（Using the Static Link Library）

### 3.1. 包含和链接 SpRcApi

有四种 SpRcApi 配置可用于静态链接：SpRcApi.lib、SpRcApid.lib、SpRcApiMD.lib 和 SpRcApiMDd.lib。

末尾带小写 'd' 的文件是 DTAPI 库的调试版本。

SpRcApi(d).lib 在编译时将 VC++ 中的 C/C++ 代码生成选项（Code-Generation Options）设置为：“使用运行时库：多线程”（Use run-time library: Multithreaded）。在编译器命令行中，这对应于 /MT 选项。

SpRcApiMD(d).lib 在编译时将 VC++ 中的 C/C++ 代码生成选项设置为：“使用运行时库：多线程 DLL”（Use run-time library: Multithreaded DLL）。在编译器命令行中，这对应于 /MD 选项。

由于 SpRcApi.h 中的 pragma 指令，会自动链接正确版本的 SpRcApi 库文件。

可以通过定义 \_SPRCAPI\_DISABLE\_AUTO\_LINK 来禁用自动链接（使用 #define 或在预处理器定义中）。

因此，要使用 SpRcApi 的静态链接库，请按照以下步骤操作：

1. 将 SpRcApi.h、DTAPI.h 以及 SpRcApi(d).lib 或 SpRcApiMD(d).lib 复制到您的项目中，或复制到 VC++ 可见的标准位置。

2. 在使用 SpRcApi 函数的每个文件中添加 #include “SpRcApi.h”。

3. 使用多线程 DLL（编译器开关 /MD）或静态（编译器开关 /MT）版本的 C 运行时库编译应用程序。

### 注意事项（Notes）

\- 静态库文件适用于 VC14、VC15、VC16 和 VC17。

在主应用程序的调试版本中使用静态链接库的发布版本可能会导致应用程序崩溃。这是因为 STL 在调试和发布构建中使用了不同长度的数据结构。

### 3.2. 检查返回代码

使用 SpRcApi 时，每次调用 SpRcApi 函数后都必须检查返回值。与 StreamXpress 播放服务器的连接可能随时中断，因此每个方法调用都可能失败。唯一的例外是 GetVersion，它不会失败。

为保持代码清晰，下面的示例没有检查方法调用的返回值。但在生产级代码中，务必添加此类检查。

### 3.3. 连接到 StreamXpress

以下代码建立与 StreamXpress 的连接。

```cpp
// Create remote-control client（创建远程控制客户端）
SpRcClient* SpRc;
SpRc = SpRcClient::CreateSpRcClient();

// Open a session（打开会话）
unsigned char Ip[] = {127, 0, 0, 1};
SpRc->OpenSession(Ip, 9000);
```
​				图 1. 连接到 StreamXpress。

第一步是创建一个 SpRcClient 对象，它表示与播放服务器的连接。

下一步是使用 OpenSession 与播放服务器打开会话。在此例中，使用本地回环地址 127.0.0.1，与客户端应用程序运行在同一台 PC 上的 StreamXpress 建立连接。可以通过指定 IP 地址访问网络上的其他 PC。

### 3.4. 播放文件

SpRcApi 中的其他方法可用于设置参数并播放文件。在很大程度上它们不言自明。

下面的代码禁用循环、打开文件、开始播放并等待播放完成。

```cpp
SpRc->SetLoopFlags(0);
SpRc->OpenFile(L"C:\\Stream.ts");
SpRc->SetPlayoutState(SPRC_STATE_PLAY);
SpRc->WaitForCondition(
SPRC_COND_STOPPED, -1);
```

文件是在播放服务器的环境中打开的，这意味着 C: 是播放服务器上的 C 盘，而不是客户端上的。

下面的代码块播放文件 10 秒。

```cpp
SpRc->SetPlayoutState(SPRC_STATE_PLAY);
Sleep(10000);
SpRc->SetPlayoutState(SPRC_STATE_STOP);
```

### 3.5. 同步传输（SFN 操作）

SpRcApi 可用于 SFN 和多天线传输，例如用于具有多个发射天线的 MIMO 测试。

输出设备必须同步到 10MHz 和 1pps 参考信号。

![2](assets/2.png)

在示意图的示例中，使用了两台 StreamXpress，每台播放一个文件。通过 SpRcApi，使用一个“ControlApp”（控制应用程序）向两台 StreamXpress 播放器发送启动命令。启动命令包含相对于 GPS 时间的启动时间。

通过 SpRcApi，ControlApp 还可以访问 GPS 时间，因此可以在一个明确定义的时刻发送启动时间，例如提前 500ms。这避免了竞争条件。

SpRcApi 中的其他方法可用于设置参数和输入文件。

下面的代码启用 SFN 操作，确定安全的启动时间，并开始播放；10 秒后停止播放并禁用 SFN 操作。

```cpp
// Switch to SFN operation（切换到 SFN 操作）
SpRc1->SetSfnMode(SPRC_SFN_MODE_1PPS);
SpRc2->SetSfnMode(SPRC_SFN_MODE_1PPS);
// Get the current GPS time（获取当前 GPS 时间）
SpRc1->GetSfnStatus(Status);
// Start time is 500ms in the future（启动时间为 500ms 之后）
int StartTime = (Status.m_GpsTime + 500'000'000)%1'000'000'000;
// Start synchronous playout（开始同步播放）
SpRc1->SetPlayoutStateSfn(
{SPRC_STATE_PLAY, StartTime});
SpRc2->SetPlayoutStateSfn(
{SPRC_STATE_PLAY, StartTime});

Sleep(10000);

// Stop playout（停止播放）
SpRc1->SetPlayoutStateSfn(
{SPRC_STATE_STOP, 0});
SpRc1->SetPlayoutStateSfn(
{SPRC_STATE_STOP, 0});
// Disable SFN operation（禁用 SFN 操作）
SpRc1->SetSfnMode(
SPRC_SFN_MODE_DISABLE);
SpRc2->SetSfnMode(
SPRC_SFN_MODE_DISABLE);
```

---

## SpRcClient – 会话接口（Session Interface）

### SpRcClient::CloseSession

关闭与播放服务器的会话。

```cpp
SPRC_RESULT CloseSession();
```

#### 参数（Parameters）

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 与播放服务器的会话已成功关闭 |

#### 备注（Remarks）



### SpRcClient::CreateSpRcClient

创建用于向播放服务器发出远程控制命令的客户端对象。

```cpp
static SpRcClient* CreateSpRcClient();
```

#### 参数（Parameters）

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| NULL | 无法创建远程控制对象 |
| pointer | 指向 StreamXpress 远程控制客户端的指针 |

#### 备注（Remarks）

SpRcApi 通过类似于以下的代码进行初始化：

```cpp
SpRcClient* SpRcApi = SpRcClient::CreateSpRcClient();
SPRC_RESULT Result = SpRcApi->OpenSession(IpAddr, PortNr);
```

创建客户端对象并打开会话后，所有远程控制命令都通过远程控制对象 SpRcApi 发出。

### SpRcClient::GetRemoteVersion

获取播放服务器中使用的 SpRcApi 版本号。

```cpp
virtual void SpRcClient::GetRemoteVersion(
 [out] int& Major // 主版本号
 [out] int& Minor // 次版本号
 [out] int& BugFix // 错误修复号
 [out] int& Build // 构建号
);
```

#### 参数（Parameters）

*Major, Minor, BugFix, Build*

StreamXpress 中使用的 SpRcApi 库的版本号。有关 SpRcApi 版本编号的说明，请参阅 ***SpRcClient::GetVersion***。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 远程版本号已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetRemoteDtapiVersion

获取构建 StreamXpress 所用的 DTAPI 版本号。

```cpp
virtual void SpRcClient::GetRemoteDtapiVersion(
[out] int& Major // 主版本号
[out] int& Minor // 次版本号
[out] int& BugFix // 错误修复号
[out] int& Build // 构建号
);
```

#### 参数（Parameters）

*Major, Minor, BugFix, Build*

StreamXpress 构建中使用的 DTAPI 库的版本号。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 远程 Dtapi 版本号已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetVersion

获取 SpRcApi 客户端库的版本号。

```cpp
virtual void SpRcClient::GetVersion(
[out] int& Major // 主版本号
[out] int& Minor // 次版本号
[out] int& BugFix // 错误修复号
[out] int& Build // 构建号
);
```

#### 参数（Parameters）

- Major ：主版本号。当 StreamXpress 远程控制 API 引入不向后兼容的更改时，此数字递增。
- Minor ：次版本号。当以向后兼容的方式向 StreamXpress 远程控制 API 添加方法时，此数字递增。例如，版本号为 1.3.x.x 的客户端将能够与 API 版本为 1.4.x.x 的 StreamXpress 互操作。
- BugFix ：当 SpRcApi 库中的错误被修复（不包含功能增强）时，此数字递增。
- Build ：构建号是一个冗余的版本号，每次发布 SpRcApi 库的新版本时都会递增。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
|  | 无返回值 |

#### 备注（Remarks）

### SpRcClient::OpenSession

与播放服务器建立会话。

```cpp
SPRC_RESULT SpRcClient::OpenSession(
 [in] unsigned char IpAddr[4], // IP 地址
 [in] unsigned short PortNr // 端口号
);
```

#### 参数（Parameters）

- IpAddr ：播放服务器的 IP 地址。如果 StreamXpress 运行在同一台机器上，则为 127.0.0.1
- PortNr ：访问播放服务器的端口号。端口号应与启动 StreamXpress 时在 –rc 端口选项中指定的端口一致。


#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_NO_LICK | 该端口未正确许可用于播放和远程控制 |
| SPRC_OK | 与播放服务器的会话已成功打开 |
| SPRC_VERSION_CONFLICT | 已与播放服务器打开会话，但检测到客户端 SpRcApi 版本与服务器 SpRcApi 版本之间存在版本冲突 |

#### 备注（Remarks）

SpRcClient 对象支持单个会话。如果需要多个会话，必须创建多个 SpRcClient 对象。

---

## SpRcClient – 应用程序公共接口（Application Common Interface）

### SpRcClient::GetAppInfo

获取有关应用程序的信息。

```cpp
virtual SPRC_RESULT SpRcClient::GetAppInfo(
    [out] std::wstring& AppName, // 应用程序名称
    [out] Int& MajorVersion, // 主版本号
    [out] Int& MinorVersion, // 次版本号
    [out] Int& BugFixVersion, // 错误修复版本号
    [out] Int& BuildNumber // 构建号
);
```

#### 参数（Parameters）

- AppName ：Unicode 字符串形式的应用程序名称。目前，唯一支持 SpRcApi 的应用程序是 StreamXpress。
- MajorVersion ：主版本号。当应用程序实现了重要的新功能时，此数字递增。
- MinorVersion ：次版本号。当应用程序实现了较小的功能更新（可能同时包含错误修复）时，此数字递增。
- BugFixVersion ：错误修复版本号。当相对于应用程序上一版本唯一的变化是错误修复时，此数字递增。
- BuildNumber ：构建号。应用程序每次新构建时此数字递增。它永远不会重置为零，因此应用程序的每个版本都有不同的构建号。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 应用程序信息已成功返回 |

#### 备注（Remarks）

### SpRcClient::ShowWindow

显示或隐藏 StreamXpress 应用程序窗口。

```cpp
virtual SPRC_RESULT SpRcClient::ShowWindow(
    [in] bool Show // 显示或隐藏
);
```

#### 参数（Parameters）

- Show ：显示或隐藏 StreamXpress 应用程序窗口。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 显示或隐藏操作已成功执行 |

#### 备注（Remarks）

## SpRcClient – 端口选择接口（Port Selection Interface）

### Struct PortDesc（端口描述结构体）

描述物理播放端口的结构体。

```cpp
struct PortDesc {
    __int64 m_Serial; // 设备的唯一序列号
    int m_TypeNumber; // 设备类型号
    int m_Ip[4]; // IP 地址（仅适用于 IP 端口）
    int m_Mac[6]; // MAC 地址（仅适用于 IP 端口）
    int m_FirmwareVersion; // 固件版本
    int m_FirmwareVariant; // 固件变体
    int m_Port; // 物理端口号
    int m_OutputType; // 输出类型（可 OR 组合的标志）
    int m_Capabilities; // 能力标志（可 OR 组合的标志）
    int m_InUse; // 输出端口是否已在使用？
};

typedef std::vector<SpRcPortDesc> SpRcPortDescs;
typedef SpRcPortDescs::iterator SpRcPortDescIt;
```

#### 成员（Members）

- m\_Serial ：唯一标识承载播放端口的 DekTec 设备的序列号。
- m\_TypeNumber ：此整数与设备类型号中的数字对应，例如 DTU-245 为 245。
- m\_Ip ：如果播放端口是 IP 网络端口，此成员标识 IP 地址。否则，此成员的值未定义。
- m\_Mac ：如果播放端口是 IP 网络端口，此成员标识 MAC 地址。否则，此成员的值未定义。
- m\_FirmwareVersion ：承载播放端口的设备上加载的固件版本号。
- m\_FirmwareVariant ：承载播放端口的设备上加载的固件变体。某些 DekTec 设备可能支持具有不同功能的多个固件变体。
- m\_Port ：此整数标识与此功能关联的物理端口号。有关每个设备物理端口号的概述，请参阅 DekTec 的 DTAPI 文档。
- m\_OutputType ：此字段描述可以在此播放端口上生成的流类型。输出类型编码在标志中，这些标志可以 OR 组合，以指示该端口支持多种类型。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_OTYPE_ASI | DVB-ASI |
| SPRC_OTYPE_ATSC | ATSC（VSB）调制 |
| SPRC_OTYPE_CMMB | CMMB 调制 |
| SPRC_OTYPE_DTMB | DTMB 调制 |
| SPRC_OTYPE_DVBS | DVB-S 调制 |
| SPRC_OTYPE_DVBS2 | DVB-S.2 调制 |
| SPRC_OTYPE_DVBT | DVB-T 调制，包括 DVB-H |
| SPRC_OTYPE_DVBT2 | DVB-T2 调制 |
| SPRC_OTYPE_DVBT2MI | DVB-T2MI |
| SPRC_OTYPE_IQ | IQ 采样 |
| SPRC_OTYPE_ISDBS | ISDB-S 调制 |
| SPRC_OTYPE_ISDBT | ISDB-T 调制 |
| SPRC_OTYPE_QAM_A | QAM 调制，ITU-T J.83 Annex A（DVB-C） |
| SPRC_OTYPE_QAM_B | QAM 调制，ITU-T J.83 Annex B（美国） |
| SPRC_OTYPE_QAM_C | QAM 调制，ITU-T J.83 Annex C（日本） |
| SPRC_OTYPE_SDSDI | 标清 SDI |
| SPRC_OTYPE_SPI | DVB-SPI |
| SPRC_OTYPE_TSOIP | TS-over-IP |
| SPRC_OTYPE_ISDBS3 | ISDB-S3 调制 |
| SPRC_OTYPE_DRM | DRM 调制 |
| SPRC_OTYPE_ATSC3_STLTP | ATSC 3.0 STLTP 调制 |

- m\_Capabilities ：此字段描述播放端口的更多能力。能力编码在标志中，这些标志可以 OR 组合，以指示该端口支持多种能力。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_CAP_ADJLVL | 调制器端口具有可调输出电平 |
| SPRC_CAP_CM | 调制器端口支持信道建模 |
| SPRC_CAP_DIGIQ | 调制器端口具有数字 IQ 输出 |
| SPRC_CAP_IF | 调制器端口具有 IF 输出 |
| SPRC_CAP_LBAND | 调制器端口可上变频至 L 波段 950 .. 2150MHz |
| SPRC_CAP_SFN | 调制器端口支持单频网（SFN）操作。选择外部 RF 时钟源时支持此功能。 |
| SPRC_CAP_UHF | 调制器端口可上变频至 UHF 波段 400 .. 862MHz |
| SPRC_CAP_VHF | 调制器端口可上变频至 VHF 波段 47 .. 470MHz |

- m\_InUse ：此状态标志指示播放端口当前是否正在使用。“使用中”状态是当前情况的快照。由于与其他应用程序的竞争条件，连接到一个未使用的播放端口也可能会失败。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_PORT_CURR | 端口是此远程控制会话中当前选定的播放端口 |
| SPRC_PORT_UNUSED | 端口未使用 |
| SPRC_PORT_USED | 端口正被其他应用程序使用 |

### SpRcClient::ScanPorts

获取可用于播放的端口信息。

```cpp
virtual SPRC_RESULT SpRcClient::ScanPorts(
    [out] SpRcPortDesc& PortDescs // 播放端口列表
);
```

#### 参数（Parameters）

- PortDescs ：播放端口列表。有关每个端口属性的描述，请参阅 Struct PortDesc。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 应用程序信息已成功返回 |

#### 备注（Remarks）

### SpRcClient::SelectPort

选择用于播放的物理端口。

```cpp
virtual SPRC_RESULT SpRcClient::SelectPort(
    [in] __int64 Serial, // 要选择的设备序列号
    [in] int Port; // 要选择的物理端口号
    [in] int Modulation; // 初始调制标准
);
```

#### 参数（Parameters）

- Serial ：标识要选择的 DekTec 设备的序列号。
- Port ：要选择的端口的物理端口号。
- Modulation ：仅适用于调制器：初始调制标准。使用 SPRC\_MOD\_XXX 常量之一。否则设置为 0。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_MOD_STANDARD | 调制器端口不支持初始调制标准 Modulation |
| SPRC_E_NO_LICK | 该端口未正确许可用于播放和远程控制 |
| SPRC_E_NOT_FOUND | 找不到由 Serial 和 Port 标识的播放端口 |
| SPRC_E_PORT_USED | 无法选择该端口，因为它正被另一个 StreamXpress 实例或其他应用程序使用 |
| SPRC_OK | 播放端口已成功选择 |

#### 备注（Remarks）

播放服务器将在未选择文件的情况下启动，参数设置为该端口的默认值。

可以使用 SpRcClient::ScanPorts 获取可用于播放的物理端口列表。

### SpRcClient::SelectDtaPlus

选择用作衰减器的 DtaPlus 设备。

```cpp
virtual SPRC_RESULT SpRcClient::SelectDtaPlus(
    [in] bool UseDtaPlus, // 是否应使用 dta-plus
    [in] __int64 Serial // 要选择的 DtaPlus 序列号
);
```

#### 参数（Parameters）

- UseDtaPlus ：设置为 true 以实际开始使用 Dta-plus。
- Serial ：标识要选择的 DekTec 设备的序列号。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NOT_FOUND | 找不到由 Serial 标识的 Dta-plus 端口 |
| SPRC_E_PORT_USED | 无法选择 Dta-plus，因为它正被另一个 StreamXpress 实例或其他应用程序使用 |
| SPRC_OK | Dta-plus 端口已成功选择 |

#### 备注（Remarks）

## SpRcClient – 播放接口（Playout Interface）

### Struct SpRcAsiPars

DVB-ASI 输出端口的播放参数。

```cpp
struct SpRcAsiPars {
    bool m_Remux; // 重复用 是/否
    int m_PlayoutRate; // 仅在重复用开启时使用
    bool m_BurstMode; // DVB-ASI 突发模式
    int m_TxMode; // 传输模式
    int m_Polarity; // ASI 信号的物理极性
};
```

#### 成员（Members）

- m\_Remux ：打开（true）或关闭（false）重复用。如果重复用打开，StreamXpress 会添加空包并调整定时信息，使流以 m\_PlayoutRate 播放。如果重复用关闭，流以传输流速率播放，且不使用 m\_Playout。
- m\_PlayoutRate ：DVB-ASI 播放速率。
- m\_BurstMode ：打开（true）或关闭（false）DVB-ASI 突发模式。
- m\_TxMode ：传输模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_TXMODE_188 | 假定传输包为 188 字节，并以 188 字节包播放。 |
| DTAPI_TXMODE_204 | 假定传输包为 204 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_ADD16 | 假定传输包为 188 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_MIN16 | 假定传输包为 204 字节，并以 188 字节包播放。 |
| DTAPI_TXMODE_RAW | 不对包结构做任何假设。流中的字节原样传输。不能应用空包填充。 |

- m\_Polarity ：DVB-ASI 信号的极性。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_TXPOL_NORMAL | 生成“正常”ASI 信号 |
| DTAPI_TXPOL_INVERTED | 生成反相 ASI 信号 |

### Struct SpRcCmmbPars

CMMB 参数。

```cpp
struct SpRcCmmbPars {
    int m_Bandwidth; // CMMB 带宽
    int m_AreaId; // 区域 ID（0..127）
    int m_TxId; // 发射机 ID（128..255）
};
```

#### 成员（Members）

- m\_Bandwidth ：CMMB 带宽。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_CMMB_BW_2MHZ | CMMB 2MHz 带宽 |
| DTAPI_CMMB_BW_8MHz | CMMB 8MHz 带宽 |

- m\_AreaId ：区域 ID（0..127）。
- m\_TxId ：发射机 ID（128..255）。

### Struct SpRcCmPars

信道建模参数。

```cpp
struct SpRcCmPars {
    bool m_CmEnable; // 启用信道建模
    bool m_AwgnEnable; // 启用噪声注入
    bool m_PathsEnable; // 启用传输路径仿真
    double m_Snr; // 信噪比（dB）
    bool m_UseManualSeed; // 为 AWGN 使用用户定义的种子
    int m_ManualSeed; // 种子值（m_UseManualSeed=true 时使用）
    std::vector<SpRcCmPath> m_Paths; // 传输路径列表
};
```

#### 成员（Members）

- m\_CmEnable ：如果为 true，则根据此结构体中的其他值执行信道建模。如果为 false，则禁用信道建模并忽略其他结构体值。
- m\_AwgnEnable ：启用白噪声注入；m\_Snr 指定信噪比。
- m\_PathsEnable ：启用多径回波仿真。
- m\_Snr ：噪声功率相对于调制器一个想象的 0dB 输出信号来定义。这意味着仅当 m\_Paths 中路径的累积功率为 0dB 时，m\_Snr 才是真实的信噪比。
- m\_UseManualSeed ：启用使用用户定义的种子进行 AWGN 噪声发生器，而不是随机生成的种子。
- m\_ManualSeed ：AWGN 噪声发生器的用户定义种子值。仅当 m\_UseManualSeed 设置为 true 时才使用此值。
- m\_Paths ：传输路径描述列表（最多 32 条）。请参阅 struct SpRcCmPath。

### Struct SpRcCmPaths

单条路径的信道建模参数。

```cpp
struct SpRcCmPath {
    int m_Type; // 路径衰落类型
    double m_Attenuation; // 衰减（dB）
    double m_Delay; // 延迟（us）
    double m_Phase; // 相移（度）
    double m_Doppler; // 多普勒频率（Hz）
};
```

#### 成员（Members）

- m\_Type ：传输路径的类型值：

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_CONSTANT_DELAY | 恒定延迟和相位 |
| SPRC_CONSTANT_DOPPLER | 恒定频移 |
| SPRC_RAYLEIGH_JAKES | 具有 Jakes 功率谱密度的瑞利衰落（移动路径模型） |
| SPRC_RAYLEIGH_GAUSSIAN | 具有高斯功率谱密度的瑞利衰落（电离层路径模型） |

- m\_Attenuation ：衰减（dB）。为避免信道模拟器溢出，所有路径的总衰减不得超过 0dB。
- m\_Delay ：延迟（us）。8MHz 信道的最大延迟为 896us。
- m\_Phase ：相移（度）（对于类型 RAYLEIGH\_JAKES 和 RAYLEIGH\_GAUSSIAN，该值被忽略）。
- m\_Doppler ：多普勒频率（Hz）（对于类型 CONSTANT\_DELAY，该值被忽略）。对应的速度（m/s）为：Speed = f<sub>doppler</sub> \* 3.10<sup>8</sup>/f<sub>RF</sub>。

### Struct SpRcDateTime

指定日期和时间。

```cpp
struct SpRcDateTime {
    int m_Year; // 年份 1900-2100
    int m_Month; // 月份 1-12
    int m_Day; // 日 1-31
    int m_Hour; // 小时 0-23
    int m_Minute; // 分钟 0-59
    int m_Second; // 秒 0-59
};
```

#### 成员（Members）

- m\_Year ：年份。有效值为 1900 – 2100。
- m\_Month ：月份。有效值为 1 – 12。
- m\_Day ：日。有效值为 1 – 31。
- m\_Hour ：小时。有效值为 0 – 23。
- m\_Minute ：分钟。有效值为 0 – 59。
- m\_Second ：秒。有效值为 0 – 59。

### Struct SpRcDvbT2Group

指定标准 DVB-T2 参数集组的参数

```cpp
struct SpRcDvbT2Group {
    std::wstring m_GroupName; // DVB-T2 组名称
    std::wstring m_GroupRefName; // 组中的特定集
};
```

#### 成员（Members）

- m\_GroupName ：DVB-T2 组名称，例如 “VV1xx”。
- m\_GroupRefName ：组中的特定集，例如 “VV100”。

### Struct SpRcDvbT2Pars

描述 DVB-T2 调制参数的结构体。

```cpp
struct SpRcDvbT2Pars {
    int m_T2Version; // DVB-T2 版本 DTAPI_DVBT2_VERSION_x
    int m_Bandwidth; // 信道带宽 DTAPI_DVBT2_8MHZ/...
    int m_FftMode; // FFT 模式（或大小）DTAPI_DVBT2_FFT_x
    int m_Miso; // MISO 模式 DTAPI_DVBT2_MISO_x
    int m_GuardInterval; // 保护间隔 DTAPI_DVBT2_GI_x
    int m_Papr; // PAPR 降低模式 DTAPI_DVBT2_PAPR_x
    int m_BwtExt; // 带宽扩展 0 或 1
    int m_PilotPattern; // 导频图案 1 到 8
    int m_NumT2Frames; // 一个超帧中的 T2 帧数
    int m_NumDataSyms; // 每个 T2 帧的数据 OFDM 符号数
    int m_L1Modulation; // L1 调制类型 DTAPI_DVBT2_BPSK/...
    bool m_FefEnable; // 插入 FEF（是/否）
    int m_FefType; // FEF 类型 0 ... 15
    int m_FefLength; // FEF 长度
    int m_FefS1; // FEF S1 字段值 2 <= FefS1 <= 7
    int m_FefS2; // FEF S2 字段值 0 <= FefS2 <= 15
    int m_FefInterval; // FEF 间隔
    int m_FefSignal; // FEF 期间内的信号类型
    int m_CellId; // 小区 ID
    int m_NetworkId; // 网络 ID
    int m_T2SystemId; // T2 系统 ID
    int m_Frequency; // L1-post 频率字段值
    // PLP#0 参数
    bool m_Hem; // 高效模式（是/否）
    bool m_Npd; // 空包删除（是/否）
    bool m_IssyEnabled; // 启用 ISSY（是/否）
    int m_Id; // PLP ID
    int m_GroupId; // PLP 组 ID
    int m_Type; // PLP 类型 DTAPI_DVBT2_PLP_TYPE_x
    int m_CodeRate; // 码率
    int m_Modulation; // 调制类型 DTAPI_DVBT2_BPSK/...
    bool m_Rotation; // 星座旋转（是/否）
    int m_FecType; // FEC 类型 0=LDPC 16K, 1=LDPC 64K
    int m_TimeIlLength; // 时间交织长度 0..255
    int m_TimeIlType; // 时间交织类型 0 或 1
    bool m_InBandFlag; // 带内信令信息（是/否）
    bool m_NumBlocks; // 每个 IL 帧的 FEC 块数
    int m_FollowMode; // 计算 NumDataSyms/NumBlocks 的模式
};
```

#### 成员（Members）

- m\_T2Version, m\_Bandwidth, m\_FftMode, m\_Miso, m\_GuardInterval, m\_Papr, m\_BwtExt, m\_PilotPattern, m\_NumT2Frames, m\_NumDataSyms, m\_L1Modulation, m\_FefEnable, m\_FefType, m\_FefLength, m\_FefS1, m\_FefS2, m\_FefInterval, m\_FefSignal, m\_CellId, m\_NetworkId, m\_T2SystemId, m\_Frequency ：整体 DVB-T2 调制参数，不特定于单个 PLP。有关这些参数的描述，请参阅 DTAPI 规范中描述 DtDvbT2Pars 的章节。
- m\_Hem, m\_Npd, m\_IssyEnabled, m\_Id, m\_GroupId, m\_Type, m\_CodeRate, m\_Modulation, m\_Rotation, m\_FecType, m\_TimeIlLength, m\_TimeIlType, m\_InBandFlag, m\_NumBlocks ：PLP 0（唯一的 PLP）的参数。有关这些参数的描述，请参阅 DTAPI 规范中描述 struct DtDvbT2PlpPars 的章节。
- m\_FollowMode ：此参数指定 StreamXpress 如何计算或复制 NUM\_DATA\_SYMBOLS（每个 T2 帧的数据 OFDM 符号数）和 PLP\_NUM\_BLOCKS（每个交织帧的 FEC 块数）。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_T2_FOLLOW_OFF | 不进行自动计算。NUM_DATA_SYMBOLS 从 m_NumDataSyms 复制，PLP_NUM_BLOCKS 从 m_NumBlocks 复制 |
| SPRC_T2_FOLLOW_OPT1 | 计算 NUM_DATA_SYMBOLS 和 PLP_NUM_BLOCKS。给定 SpRcDvbT2Pars 中的 DVB-T2 调制参数，StreamXpress 优化 NUM_DATA_SYMBOLS 和 PLP_NUM_BLOCKS。不使用 m_NumDataSyms 和 m_NumBlocks 中的值。 |
| SPRC_T2_FOLLOW_OPT2 | 计算 PLP_NUM_BLOCKS。给定 SpRcDvbT2Pars 中的 DVB-T2 调制参数（包括 m_NumDataSyms），StreamXpress 优化 PLP_NUM_BLOCKS。不使用 m_NumBlocks 中的值。NUM_DATA_SYMBOLS 从 m_NumDataSyms 复制。 |

### Struct SpRcHwNoisePars

调制器 DTA-107 和 DTA-2107 的噪声参数。

```cpp
struct SpRcHwNoisePars {
    bool m_SnrOn; // 启用噪声发生器
    double m_Snr; // 信噪比
};
```

#### 成员（Members）

- m\_SnrOn ：启用噪声发生器。
- m\_Snr ：信噪比（dB）。

### Struct SpRcIsdbtLayerPars

描述一个分层（hierarchical layer）的 ISDB-T 调制参数的结构体。该结构体在 SpRcIsdbtPars 中以三个结构体组成的数组使用，分别对应 A、B 和 C 层。

```cpp
struct SpRcIsdbtLayerPars {
    int m_NumSegments; // 段数
    int m_Modulation; // 调制类型
    int m_CodeRate; // 码率
    int m_TimeInterleave; // 时间交织
};
```

#### 成员（Members）

- m\_NumSegments ：此层中使用的段数。m\_NumSegment 的总和必须为 13。
- m\_Modulation ：应用于此层段落的调制类型。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_ISDBT_MOD_DQPSK | DQPSK |
| DTAPI_ISDBT_MOD_QPSK | QPSK |
| DTAPI_ISDBT_MOD_QAM16 | 16-QAM |
| DTAPI_ISDBT_MOD_QAM64 | 64-QAM |

- m\_CodeRate ：应用于此层段落的卷积编码速率。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_ISDBT_RATE_1_2 | 1/2 |
| DTAPI_ISDBT_RATE_2_3 | 2/3 |
| DTAPI_ISDBT_RATE_3_4 | 3/4 |
| DTAPI_ISDBT_RATE_5_6 | 5/6 |
| DTAPI_ISDBT_RATE_7_8 | 7/8 |

- m\_TimeInterleave ：时间交织的编码长度。下表定义了 m\_TimeInterleave 到时间交织过程中参数 I 的映射。

| 值（Value） | 模式 1（Mode 1） | 模式 2（Mode 2） | 模式 3（Mode 3） |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 1 | 4 | 2 | 1 |
| 2 | 8 | 4 | 2 |
| 3 | 16 | 8 | 4 |

### Struct SpRcIsdbtPars

ISDB-T 的调制参数。

```cpp
struct SpRcIsdbtPars {
    bool m_DoMux; // 分层复用 是/否
    int m_BType; // 广播类型
    int m_Mode; // 传输模式
    int m_Guard; // 保护间隔
    int m_PartialRx; // 部分接收
    int m_Emergency; // 紧急广播的开关控制
    int m_IipPid; // 用于复用 IIP 包的 PID
    SpRcIsdbtLayerPars m_LayerPars[3]; // 层-A/B/C 参数
    std::map<int, int> m_Pid2Layer; // PID 到层映射
    int m_LayerOther; // 其他 PID 映射到此层
    int m_ParXtra0; // 额外参数
    int m_Virtual13Segm; // 虚拟 13 段模式
};

struct SpRcIsdbtLayerPars {
    int m_NumSegment; // 段数
    int m_Modulation; // 调制类型
    int m_CodeRate; // 码率
    int m_TimeInterleave; // 时间交织
};
```

#### 成员（Members）

- m\_DoMux ：如果为 true，则根据此结构体中明确定义的 ISDB-T 参数执行分层复用。如果为 false，则 ISDB-T 调制参数由 204 字节包中 16 个额外字节的 TMCC 信息间接指定。
- m\_BType ：广播类型。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_ISDBT_BTYPE_TV | 电视广播；可用于任意数量的段 |
| DTAPI_ISDBT_BTYPE_RAD1 | 1 段广播；总段数必须为 1 |
| DTAPI_ISDBT_BTYPE_RAD3 | 3 段广播；总段数必须为 3 |

- m\_Mode ：传输模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| 1 | 模式 1：2k |
| 2 | 模式 2：4k |
| 3 | 模式 3：8k |

- m\_Guard ：保护间隔长度。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_ISDBT_GUARD_1_32 | 1/32 |
| DTAPI_ISDBT_GUARD_1_16 | 1/16 |
| DTAPI_ISDBT_GUARD_1_8 | 1/8 |
| DTAPI_ISDBT_GUARD_1_4 | 1/4 |

- m\_PartialRx ：指示层 A 是否用于部分接收的标志：0 = 无部分接收，1 = 部分接收开启。
- m\_Emergency ：指示紧急广播的开关控制标志是否应打开：0 = 关闭，1 = 打开。
- m\_IipPid ：用于复用 IIP 包的 PID 值。
- m\_LayerPars ：分层 A（元素 0）、B（1）和 C（2）的调制参数。
- m\_Pid2Layer ：指定基本流应映射到哪个分层（或哪些层）的映射。映射中的键是基本流的 PID。映射中存储的值是下表中列出的一个或多个标志的 OR。值为 0 表示应丢弃该基本流。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_ISDBT_LAYER_A | 将基本流映射到层 A |
| DTAPI_ISDBT_LAYER_B | 将基本流映射到层 B |
| DTAPI_ISDBT_LAYER_C | 将基本流映射到层 C |

- m\_LayerOther ：将 m\_Pid2Layer 中未包含的 PID 的流映射到此层。
- m\_ParXtra0 ：编码带宽、采样率和段数的额外参数。此参数的编码方式与 SetModControl 中 ModType 为 DTAPI\_MOD\_ISDBT 时的 ParXtra0 相同。
- m\_Virtual13Segm ：使用虚拟 13 段模式。层 B 中的段数被“伪造”为 12。

### Struct SpRcModPars

除 DVB-T2 和 ISDB-T 之外所有调制标准的调制参数。

```cpp
struct SpRcModPars {
    int m_ModType; // 调制类型
    int m_ParXtra0; // 额外调制参数 0
    int m_ParXtra1; // 额外调制参数 1
    int m_ParXtra2; // 额外调制参数 2
    int m_SymRate; // 符号率（bd）
};
```

#### 成员（Members）

- m\_ModType ：调制类型，请参阅 DTAPI\_MOD\_XXX 常量。
- m\_ParXtra0, m\_ParXtra1, m\_ParXtra2 ：调制参数，请参阅 DTAPI 文档（SetModControl）。
- m\_SymRate ：符号率（波特）。对于需要符号率的调制标准（如 DVB-S），此成员为必填。如果不需要符号率，此成员应设置为 -1。

### Struct SpRcPlayoutInfo

描述静态播放信息的结构体。

```cpp
struct SpRcPlayoutInfo {
    bool m_BurstMode; // DVB-ASI 突发模式
    bool m_ExtClock; // 使用外部时钟
    bool m_FileCanBeRead; // 已选择可读取的文件
    std::wstring m_Filename; // 当前选定的文件名
    long m_FileOffsetEnd; // 文件末尾未使用的字节数
    long m_FileOffsetStart; // 文件开头未使用的字节数
    long m_FilePlayedBytes; // 文件长度减去开头和结尾的字节数
    int m_FileRateEst; // TS：估计文件速率
    long m_FileSize; // 文件大小
    int m_FileType; // 文件中的数据类型：RAW/TS/SDI
    double m_LoopBeginRel; // 子循环，开始位置（相对 0..1）
    double m_LoopEndRel; // 子循环，结束位置（相对 0..1）
    int m_LoopFlags; // 适配 CC/PCR/TDT 和环绕标志
    int m_PlayoutState; // HOLD/PLAYING
    int m_PlayoutRate; // 播放速率 @188
    boolean m_Remux; // 重复用模式
    int m_SymRate; // 调制器：符号率
    double m_TimeLoopBegin; // 与循环开始对应的时间
    double m_TimeLoopEnd; // 与循环结束对应的时间
    int m_TimeOffset; // 添加到播放时间的偏移量
    int m_TsRate; // TS：TS 速率 @188
    int m_TpSize; // TS：包大小
    int m_TxPolarity; // ASI 信道的传输极性
};
```

#### 成员（Members）

- m\_BurstMode ：对于 ASI 信道：是否以突发模式发送 DVB-ASI。
- m\_ExtClock ：传输流取自外部时钟输入。
- m\_FileCanBeRead ：当前选择的文件有效。
- m\_Filename ：当前在 StreamXpress 中选择的文件名称。
- m\_FileOffsetEnd ：文件末尾未使用的字节数。
- m\_FileOffsetStart ：文件开头未使用的字节数。
- m\_FilePlayedBytes ：实际播放的文件字节数（文件长度减去开头和结尾未使用的字节数）。
- m\_FileRateEst ：TS：估计文件速率。
- m\_FileSize ：文件大小。
- m\_FileType ：文件中的数据类型：原始数据、传输流或 SDI。
- m\_LoopBeginRel ：子循环的开始位置，为 0 到 1 之间的相对数。如果不使用子循环，则该值为 0。
- m\_LoopEndRel ：子循环的结束位置，为 0 到 1 之间的相对数。如果不使用子循环，则该值为 0。
- m\_LoopFlags ：循环适配标志：CC、PCR、TDT 和环绕标志的适配。
- m\_PlayoutState ：指示 StreamXpress 是暂停（保持模式）还是播放。
- m\_PlayoutRate ：流播放的速率。对于传输流，即使流包含 204 字节的传输包，也使用 188 字节每包的速率。
- m\_Remux ：仅适用于传输流：指示传输流是否被重复用到另一个速率。
- m\_SymRate ：仅适用于调制器：符号率。
- m\_TimeLoopBegin ：与循环开始对应的播放时间。
- m\_TimeLoopEnd ：与循环结束对应的播放时间。
- m\_TimeOffset ：添加到播放时间的偏移量。
- m\_TsRate ：传输流的速率。对于传输流，即使文件包含 204 字节的传输包，也使用 188 字节每包的速率。
- m\_TpSize ：仅适用于传输流：传输包的大小。
- m\_TxPolarity ：ASI 信道的传输极性。

### Struct SpRcPlayoutStatus

描述动态播放状态的结构体。

```cpp
struct SpRcPlayInfo {
    int m_FifoLoad; // 当前 FIFO 负载
    int m_NumErrors; // 错误数（下溢）
    int m_NumWraps; // 环绕次数
    double m_PosRel; // 子循环中的相对位置（0..1）
    int m_TotalMemLoad; // DiskBuffer+MemBuffer 中的字节数（快照）
};
```

#### 成员（Members）

- m\_FifoLoad ：输出 FIFO 的当前负载。
- m\_NumErrors ：自上次开始播放以来的下溢错误数。
- m\_NumWraps ：自上次开始播放以来文件环绕的次数。
- m\_PosRel ：子循环中的相对位置。客户端可以使用 m\_PosRel 将滑块与 StreamXpress 中的滑块同步。
- m\_TotalMemLoad ：存储在磁盘和内存缓冲区中的数据字节数快照。

### Struct SpRcSfnStatus

描述动态 GPS 和 SFN 状态的结构体。

```cpp
struct SpRcSfnStatus {
    int m_GpsStatus; // 10MHz 和 1PPS 输入信号的状态
    int m_GpsTime; // 当前 GPS 时间
    int m_SfnMode; // 当前 SFN 模式
    int m_SfnStatus; // SFN 播放状态
};
```

#### 成员（Members）

- m\_GpsStatus ：10MHz 和 1pps 输入信号的状态标志。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_GPS_STATUS_10MHZ_NO_SIGNAL | 无（有效的）10MHz 时钟输入信号 |
| SPRC_GPS_STATUS_10MHZ_OUT_RANGE | 10MHz 输入信号频率超出范围 |
| SPRC_GPS_STATUS_10MHZ_SYNC | GPS 时间已频率锁定到 10MHz 输入信号 |
| SPRC_GPS_STATUS_10MHZ_1PPS_SYNC | GPS 时间已锁定到 10MHz 和 1pps 输入信号 |

- m\_GpsTime ：以纳秒为单位的当前 GPS 时间；范围 0 … 999.999.999。如果没有 10MHz 同步，GPS 时间为 0。
- m\_SfnMode ：当前 SFN 模式：

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_SFN_MODE_DISABLE | SFN 操作已禁用 |
| SPRC_SFN_MODE_1PPS | SFN 使用 1PPS 模式。播放相对于 1pps 信号开始。 |

- m\_SfnStatus ：SFN 操作的状态

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_SFN_STATUS_DISABLED | 未在 SFN 模式下运行 |
| SPRC_SFN_STATUS_HOLD | SFN 播放已就绪，正在等待播放命令及伴随的开始时间 |
| SPRC_SFN_STATUS_STARTING | SFN 播放正在启动（已收到播放命令），到达开始时间时播放开始 |
| SPRC_SFN_STATUS_IN_SYNC | SFN 播放正在运行且已同步 |
| SPRC_SFN_STATUS_ERROR | 发生 SFN 播放错误且未同步，需要重新启动 SFN 播放 |

### Struct SpRcPlayoutSfnPars

用于控制 SFN 播放的结构体。

```cpp
struct SpRcPlayoutSfnPars {
    int m_PlayoutState; // 播放状态
    int m_SfnStartTime; // SFN 播放 GPS 开始时间
};
```

#### 成员（Members）

- m\_PlayoutState ：新的播放状态。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_STATE_PLAY | 播放 |
| SPRC_STATE_STOP | 停止 |

- m\_SfnStartTime ：以纳秒为单位的 GPS 时间播放开始时间；范围 0 … 999.999.999。在停止的情况下，开始时间无关紧要。

### Struct SpRcRfPars

描述调制器 RF 参数的结构体。

```cpp
struct SpRcRfPars {
    __int64 m_Frequency; // RF 频率（Hz）
    double m_Level; // RF 输出电平（dBm）
    bool m_SpecInv; // RF 频谱反转
    bool m_CW; // RF CW 模式
    bool m_RfEnabledOnStop; // 停止时 RF 输出是否启用
};
```

#### 成员（Members）

- m\_Frequency ：上变频信号的中心频率（Hz）。
- m\_Level ：主输出信号的电平（dBm）。
- m\_SpecInv ：频谱反转。
- m\_CW ：CW。
- m\_RfEnabledOnStop ：播放停止时 RF 输出是否静音。

### Struct SpRcSpiPars

DVB-SPI 输出端口的播放参数。

```cpp
struct SpRcSpiPars {
    bool m_Remux; // 重复用 是/否
    int m_PlayoutRate; // 仅在重复用开启时使用
    int m_TxMode; // 传输模式
    bool m_Power; // 为外部适配器打开/关闭电源
};
```

#### 成员（Members）

- m\_Remux ：打开（true）或关闭（false）重复用。如果重复用打开，StreamXpress 会添加空包并调整定时信息，使流以 m\_PlayoutRate 播放。如果重复用关闭，流以传输流速率播放，且不使用 m\_Playout。
- m\_PlayoutRate ：DVB-SPI 播放速率。
- m\_TxMode ：传输模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_TXMODE_188 | 假定传输包为 188 字节，并以 188 字节包播放。 |
| DTAPI_TXMODE_192 | 192 字节模式（仅 DTA-102）假定传输包为 192 字节，并以 192 字节包播放。 |
| DTAPI_TXMODE_204 | 假定传输包为 204 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_ADD16 | 假定传输包为 188 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_MIN16 | 假定传输包为 204 字节，并以 188 字节包播放。 |
| DTAPI_TXMODE_RAW | 不对包结构做任何假设。流中的字节原样传输。不能应用空包填充。 |

- m\_Power ：外部适配器的电源打开或关闭。

### Struct SpRcSubLoopPars

用于配置文件子循环的播放参数。

```cpp
struct SpRcSubLoopPars {
    bool m_UseSubLoop; // 子循环 是/否
    double m_LoopBeginRel; // 文件中的相对开始位置
    double m_LoopEndRel; // 文件中的相对结束位置
};
```

#### 成员（Members）

- m\_UseSubLoop ：打开（true）或关闭（false）子循环。
- m\_LoopBeginRel ：文件中的相对开始位置，值在 0 到 1 之间。
- m\_LoopEndRel ：文件中的相对结束位置，值在 0 到 1 之间。

### Struct SpRcTdtAdaptPars

用于指定 TDT/TOT 适配的参数。

```cpp
struct SpRcTdtAdaptPars {
    int m_TdtAdaptMode; // TOT/TDT 适配模式
    SpRcDateTime m_TdtDateTime; // 指定要使用的时间
};
```

#### 成员（Members）

- m\_TdtAdaptMode ：TDT/TOT 适配的类型：

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_TDT_ADAPT_NOT_1ST_LOOP | 在第一个循环后适配 TDT/TOT |
| SPRC_TDT_ADAPT_CURRENT_UTC | 使用当前 UTC 时间 |
| SPRC_TDT_ADAPT_CURRENT_JST | 使用当前 JST 时间 |
| SPRC_TDT_ADAPT_USE_SPECIFIED | 使用 m_TdtDateTime 中指定的时间 |

- m\_TdtDateTime ：如果 m\_TdtAdaptMode 为 SPRC\_TDT\_ADAPT\_USE\_SPECIFIED，则为要在 TDT/TOT 中使用的日期和时间，否则该值无关紧要。

### Struct SpRcTsgPars

测试信号发生器的参数。

```cpp
struct SpRcTsgPars {
    int m_Type; // 要使用的信号发生器类型
    int m_Pid; // 用于 TS 模式承载信号的 PID
    int m_VidStd; // SDI 模式的视频标准
    int m_Flags; // 保留，设置为 0
};
```

#### 成员（Members）

- m\_Type ：要使用的信号发生器类型：

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_TSG_TYPE_PRBS7 | PRBS-7 TS 发生器 |
| SPRC_TSG_TYPE_PRBS15 | PRBS-15 TS 发生器 |
| SPRC_TSG_TYPE_PRBS23 | PRBS-23 TS 发生器 |
| SPRC_TSG_TYPE_PRBS31 | PRBS-31 TS 发生器 |
| SPRC_TSG_TYPE_RP198_NO_AUDIO | 无音频的 SMPTE RP198 视频图案 |
| SPRC_TSG_TYPE_RP198 | SMPTE RP198 视频图案 |
| SPRC_TSG_TYPE_RP219_1_NO_AUDIO | 无音频的 SMPTE RP219-1 视频图案 |
| SPRC_TSG_TYPE_RP219_1 | SMPTE RP219-1 视频图案 |
| SPRC_TSG_TYPE_DYNAMIC_NO_AUDIO | 无音频的 DekTec 弹跳块（bouncing blocks） |
| SPRC_TSG_TYPE_DYNAMIC | DekTec 弹跳块 |

- m\_Pid ：承载 PRBS 包的 PID。在 SDI 模式下忽略。
- m\_VidStd ：用于 SDI 信号发生器的视频标准。在传输流模式下忽略。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_VIDSTD_525I59_94 | 525i/59.94 |
| SPRC_VIDSTD_625I50 | 625i/50 |
| SPRC_VIDSTD_720P23_98 | 720p/23.98 |
| SPRC_VIDSTD_720P24 | 720p/24 |
| SPRC_VIDSTD_720P25 | 720p/25 |
| SPRC_VIDSTD_720P29_97 | 720p/29.97 |
| SPRC_VIDSTD_720P30 | 720p/30 |
| SPRC_VIDSTD_720P50 | 720p/50 |
| SPRC_VIDSTD_720P59_94 | 720p/59.94 |
| SPRC_VIDSTD_720P60 | 720p/60 |
| SPRC_VIDSTD_1080I50 | 1080i/50 |
| SPRC_VIDSTD_1080I59_94 | 1080i/59.94 |
| SPRC_VIDSTD_1080I60 | 1080i/60 |
| SPRC_VIDSTD_1080P23_98 | 1080p/23.98 |
| SPRC_VIDSTD_1080P24 | 1080p/24 |
| SPRC_VIDSTD_1080P25 | 1080p/25 |
| SPRC_VIDSTD_1080P29_97 | 1080p/29.97 |
| SPRC_VIDSTD_1080P30 | 1080p/30 |
| SPRC_VIDSTD_1080P50 | 1080p/50 |
| SPRC_VIDSTD_1080P59_94 | 1080p/59.94 |
| SPRC_VIDSTD_1080P60 | 1080p/60 |
| SPRC_VIDSTD_2160P23_98 | 2160p/23.98 |
| SPRC_VIDSTD_2160P24 | 2160p/24 |
| SPRC_VIDSTD_2160P25 | 2160p/25 |
| SPRC_VIDSTD_2160P29_97 | 2160p/29.97 |
| SPRC_VIDSTD_2160P30 | 2160p/30 |
| SPRC_VIDSTD_2160P50 | 2160p/50 |
| SPRC_VIDSTD_2160P59_94 | 2160p/59.94 |
| SPRC_VIDSTD_2160P60 | 2160p/60 |

- m\_Flags ：保留，设置为 0。

### Struct SpRcTsoipPars

传输流-over-IP 端口的参数。

```cpp
struct SpRcTsoipPars {
    int m_TxMode; // 传输模式（188, 204, Add16, ...）
    unsigned char m_Ip[4]; // IP 地址
    int m_Port; // 端口号
    bool m_EnaFailover; // 启用 IP 双缓冲
    unsigned char m_Ip2[4]; // 第 2 个 IP 地址，用于双缓冲
    int m_Port2; // 第 2 个端口号，用于双缓冲
    int m_TimeToLive; // TTL
    int m_NumTpPerIp; // 每个 IP 包中的传输包数
    int m_Protocol; // 协议：UDP/RTP
    int m_DiffServ; // 区分服务
    int m_FecMode; // 纠错模式
    int m_FecNumRows; // ‘D’ = FEC 矩阵行数
    int m_FecNumCols; // ‘L’ = FEC 矩阵列数
};
```

#### 成员（Members）

- m\_TxMode ：传输模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_TXMODE_188 | 假定传输包为 188 字节，并以 188 字节包播放。 |
| DTAPI_TXMODE_204 | 假定传输包为 204 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_ADD16 | 假定传输包为 188 字节，并以 204 字节包播放。 |
| DTAPI_TXMODE_MIN16 | 假定传输包为 204 字节，并以 188 字节包播放。 |

- m\_Ip[4] ：目标 IP 地址。如果 IP 地址在组播范围内，播放服务器会自动加入和退出组播组的成员身份。
- m\_Port ：目标端口号。
- m\_EnaFailover ：启用冗余 IP 端口。目前仅在 DTA-2162 上支持。第二个 IP 端口将播放信号的副本，接收器可以使用该副本来隐藏两条传输路径中任一条的错误。
- m\_Ip2[4], m\_Port2 ：请参阅 m\_Ip 和 m\_Port。当 m\_EnaFailover 为 true 时用于配置第二个 IP 端口。
- m\_TimeToLive ：用于组播传输的生存时间（TTL）值。当 m\_Ttl 为 0 时，使用默认值。
- m\_NumTpPerIp ：一个 IP 包中存储的传输包（TP）数量。范围为 1..7。
- m\_Protocol ：封装传输包所期望的协议。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_PROTO_UDP | UDP |
| DTAPI_PROTO_RTP | RTP |

- m\_DiffServ ：放入 IP 头中区分服务字段（以前称为服务类型）的值。
- m\_FecMode ：纠错模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| DTAPI_FEC_DISABLE | 无 FEC |
| DTAPI_FEC_2D | RFC2733 奇偶校验 FEC，带二维扩展，如《实践规范 #3》（Code of Practice #3）中所述 |

- m\_FecNumRows, m\_FecNumCols ：FEC 矩阵中的行数和列数。在 COP #3 中，这些参数分别称为 D 和 L。对 L 和 D 有以下限制：

$$
4 \leq_ {D} \leq 2 0, \quad 1 \leq_ {L} \leq 2 0 \quad \text { and } \quad L ^ {*} D \leq 1 0 0
$$

### SpRcClient::ClearErrors

清除错误计数器。

```cpp
virtual SPRC_RESULT SpRcClient::ClearErrors();
```

#### 参数（Parameters）

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 错误已成功清除 |

#### 备注（Remarks）

### SpRcClient::GetAsiPars

获取 DVB-ASI 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetAsiPars(
    [out] SpRcAsiPars& AsiPars // ASI 参数
);
```

#### 参数（Parameters）

- AsiPars ：DVB-ASI 传输参数，请参阅 Struct SpRcAsiPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_ASI | 无效操作，因为该端口不是 ASI 端口或正在以 SDI 模式运行 |
| SPRC_OK | DVB-ASI 传输参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetChannelModellingPars

获取信道建模参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetChannelModellingPars(
    [out] SpRcCmPars& CmPars // 信道建模参数
);
```

#### 参数（Parameters）

- CmPars ：信道建模参数，请参阅 Struct SpRcCmPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 信道建模参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetCmmbPars

获取 CMMB 参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetCmmbPars(
    [out] SpRcCmmbPars& CmmbPars // CMMB 参数
);
```

#### 参数（Parameters）

- CmmbPars ：CMMB 参数，请参阅 Struct SpRcCmmbPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_CMMB | 无效操作，因为未配置 CMMB 调制 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetDvbT2Group

获取当前 DVB-T2 组选择。

```cpp
virtual SPRC_RESULT SpRcClient::GetDvbT2Group(
    [out] SpRcDvbT2Group& DvbT2Group // DVB-T2 组
);
```

#### 参数（Parameters）

- DvbT2Group ：DVB-T2 组，请参阅 Struct SpRcDvbT2Group。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_DVBT2 | 无效操作，因为未配置 DVB-T2 调制 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetDvbT2Pars

获取 DVB-T2 参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetDvbT2Pars(
    [out] SpRcDvbT2Pars& DvbT2Pars // DVB-T2 参数
);
```

#### 参数（Parameters）

- DvbT2Pars ：DVB-T2 参数，请参阅 Struct SpRcDvbT2Pars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_DVBT2 | 无效操作，因为未配置 DVB-T2 调制 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetHwNoisePars

获取调制器 DTA-107 和 DTA-2107 的噪声参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetHwNoisePars(
    [out] SpRcHwNoisePars& HwNoisePars // 硬件噪声参数
);
```

#### 参数（Parameters）

- HwNoisePars ：噪声参数，请参阅 Struct SpRcHwNoisePars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetIqGain

获取 IQ 增益参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetIqGain(
    [out] int& IqGain // IQ 增益
);
```

#### 参数（Parameters）

- IqGain ：IQ 信号的增益，单位为 0.1dB

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetIsdbtPars

获取 ISDB-T 调制参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetIsdbtPars(
    [out] SpRcIsdbtPars& IsdbtPars // ISDB-T 参数
);
```

#### 参数（Parameters）

- IsdbtPars ：ISDB-T 调制参数，请参阅 Struct SpRcIsdbtPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_ISDBT | 无效操作，因为该端口以 ISDB-T 调制模式运行 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetModPars

获取调制参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetModPars(
    [out] SpRcModPars& ModPars // 调制参数
);
```

#### 参数（Parameters）

- ModPars ：调制参数，请参阅 Struct SpRcModPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetPlayoutInfo

获取静态播放信息。

```cpp
virtual SPRC_RESULT SpRcClient::GetPlayoutInfo(
    [out] SpRcPlayoutInfo& PoInfo // 静态播放信息
);
```

#### 参数（Parameters）

- PoInfo ：播放信息，请参阅 Struct SpRcPlayoutInfo。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 播放信息已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetPlayoutStatus

获取动态播放状态。

```cpp
virtual SPRC_RESULT SpRcClient::GetPlayoutStatus(
    [out] SpRcPlayoutStatus& PoStatus // 动态播放状态
);
```

#### 参数（Parameters）

- PoInfo ：播放信息，请参阅 Struct SpRcPlayoutInfo。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 播放状态已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetRfPars

获取 RF 参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetRfPars(
    [out] SpRcRfPars& RfPars // RF 参数
);
```

#### 参数（Parameters）

- RfPars ：RF 参数，请参阅 Struct SpRcRfPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | RF 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetSfnStatus

获取动态 GPS 和 SFN 状态。

```cpp
virtual SPRC_RESULT SpRcClient::GetSfnStatus(
    [out] SpRcSfnStatus& SfnStatus // GPS 和 SFN 状态
);
```

#### 参数（Parameters）

- SfnStatus ：播放信息，请参阅 Struct SpRcSfnStatus。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_SFN | 无效操作，因为该端口没有 SFN 能力（或选择了内部 RF 时钟源） |
| SPRC_OK | SFN 状态已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetSignalSource

获取当前信号源（来自文件 / 测试信号发生器）。

```cpp
virtual SPRC_RESULT SpRcClient::GetSignalSource(
    [out] int& SignalSource // 信号源
);
```

#### 参数（Parameters）

- SignalSource ：当前信号源。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_FROM_FILE | 从文件读取数据 |
| SPRC_TEST_GENERATOR | 使用测试信号发生器生成输出信号 |

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 信号源已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetSpiPars

获取 DVB-SPI 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetSpiPars(
    [out] SpRcSpiPars& SpiPars // DVB-SPI 参数
);
```

#### 参数（Parameters）

- SpiPars ：DVB-SPI 传输参数，请参阅 Struct SpRcSpiPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_SPI | 无效操作，因为该端口不是 DVB-SPI 端口 |
| SPRC_OK | DVB-SPI 传输参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetTdtAdaptPars

获取 TDT/TOT 适配参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetTdtAdaptPars(
    [in] SpRcTdtAdaptPars& TdtAdaptPars // TDT/TOT 适配参数
);
```

#### 参数（Parameters）

- TdtAdaptPars ：TDT/TOT 适配参数，请参阅 Struct SpRcTdtAdaptPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 循环适配标志已成功设置 |

#### 备注（Remarks）

### SpRcClient::GetTsgPars

获取测试信号发生器参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetTsgPars(
    [out] SpRcTsgPars& TsgPars // 测试信号发生器参数
);
```

#### 参数（Parameters）

- TsgPars ：测试信号发生器参数，请参阅 Struct SpRcTsgPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_OP_NOT_SUPPORTED | 无效操作，因为 StreamXpress 当前未以测试信号发生器模式运行 |
| SPRC_OK | 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetTsoipPars

获取 TSoIP 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetTsoipPars(
    [out] SpRcTsoipPars& TsoipPars // TSoIP 参数
);
```

#### 参数（Parameters）

- TsoipPars ：TSoIP 传输参数，请参阅 Struct SpRcTsoipPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_TSOIP | 无效操作，因为该端口不是 TSoIP 端口 |
| SPRC_OK | TSoIP 传输参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::GetUseNit

检查是否使用 NIT 来推导参数。

```cpp
virtual SPRC_RESULT SpRcClient::GetUseNit(
    [out] bool& UseNit
);
```

#### 参数（Parameters）

- UseNit ：当且仅当 StreamXpress 将尝试使用 NIT 来设置调制参数时为 true。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | UseNit 参数已成功读取 |

#### 备注（Remarks）

### SpRcClient::Normalise

归一化多径信道建模。

```cpp
virtual SPRC_RESULT SpRcClient::Normalise();
```

#### 参数（Parameters）

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 信道建模设置已归一化 |

#### 备注（Remarks）

### SpRcClient::OpenChannelModellingFile

打开包含信道建模设置的文件。

```cpp
virtual SPRC_RESULT SpRcClient::OpenChannelModellingFile(
    [in] std::wstring& Filename // 文件名
);
```

#### 参数（Parameters）

- Filename ：要打开的文件名。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_FILE_CANT_FIND | 找不到具有指定文件名的文件 |
| SPRC_E_FILE_SYNTAX_ERROR | 指定的文件包含语法错误 |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 信道建模设置文件已成功加载 |

#### 备注（Remarks）

### SpRcClient::OpenFile

打开用于播放的文件。

```cpp
virtual SPRC_RESULT SpRcClient::OpenFile(
    [in] std::wstring& Filename // 文件名
);
```

#### 参数（Parameters）

- Filename ：要打开的文件名。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_FILE_CANT_FIND | 找不到具有指定文件名的文件 |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 播放文件已成功打开 |

#### 备注（Remarks）

### SpRcClient::SaveChannelModellingSettings

将信道建模设置保存到文件。

```cpp
virtual SPRC_RESULT SpRcClient::SaveChannelModellingSettings(
    [in] std::wstring& Filename // 文件名
);
```

#### 参数（Parameters）

- Filename ：要打开的文件名。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_FILE_CANT_CREATE | 打开文件进行写入时出错 |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 信道建模设置已成功保存 |

#### 备注（Remarks）

### SpRcClient::SaveSettings

将设置保存到文件。

```cpp
virtual SPRC_RESULT SpRcClient::SaveSettings(
    [in] std::wstring& Filename // 文件名
);
```

#### 参数（Parameters）

- Filename ：要打开的文件名。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_FILE_CANT_CREATE | 打开文件进行写入时出错 |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_OK | 设置已成功保存 |

#### 备注（Remarks）

### SpRcClient::SetAsiPars

设置 DVB-ASI 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetAsiPars(
    [in] SpRcAsiPars AsiPars // ASI 参数
);
```

#### 参数（Parameters）

- AsiPars ：DVB-ASI 传输参数，请参阅 Struct SpRcAsiPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_ASI | 无效操作，因为该端口不是 ASI 端口或正在以 SDI 模式运行 |
| SPRC_E_POLARITY | AsiPars 中指定的极性不受设备支持 |
| SPRC_E_TXMODE | AsiPars 中指定的传输模式与传输流文件不兼容 |
| SPRC_OK | DVB-ASI 传输参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetChannelModellingPars

设置信道建模参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetChannelModellingPars(
    [in] SpRcCmPars CmPars // 信道建模参数
);
```

#### 参数（Parameters）

- CmPars ：信道建模参数，请参阅 Struct SpRcCmPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 信道建模参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetCmmbPars

设置 CMMB 参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetCmmbPars(
    [in] SpRcCmmbPars CmmbPars // CMMB 参数
);
```

#### 参数（Parameters）

- CmmbPars ：CMMB 参数，请参阅 Struct SpRcCmmbPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_E_NOT_CMMB | 无效操作，因为未配置 CMMB 调制 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetDvbT2Group

设置 DVB-T2 标准参数集；例如 'VV125' 参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetDvbT2Group(
    [in] SpRcDvbT2Group DvbT2Group // DVB-T2 参数集
);
```

#### 参数（Parameters）

- DvbT2Group ：DVB-T2 标准参数集，请参阅 Struct SpRcDvbT2Group。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_E_NOT_DVB-T2 | 无效操作，因为未配置 DVB-T2 调制 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetDvbT2Pars

设置 DVB-T2 参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetDvbT2Pars(
    [in] SpRcDvbT2Pars DvbT2Pars // DVB-T2 参数
);
```

#### 参数（Parameters）

- DvbT2Pars ：DVB-T2 参数，请参阅 Struct SpRcDvbT2Pars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_E_NOT_DVB-T2 | 无效操作，因为未配置 DVB-T2 调制 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetHwNoisePars

设置调制器 DTA-107 和 DTA-2107 的噪声参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetHwNoisePars(
    [in] SpRcHwNoisePars HwNoisePars // 噪声参数
);
```

#### 参数（Parameters）

- HwNoisePars ：噪声参数，请参阅 Struct SpRcHwNoisePars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetIsdbtPars

设置 ISDB-T 调制参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetIsdbtPars(
    [in] SpRcIsdbtPars IsdbtPars // ISDB-T 参数
);
```

#### 参数（Parameters）

- IsdbtPars ：ISDB-T 调制参数，请参阅 Struct SpRcIsdbtPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_ISDBT | 无效操作，因为该端口以 ISDB-T 调制模式运行 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetIqGain

设置 IQ 增益参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetIqGain(
    [in] int IqGain // IQ 增益
);
```

#### 参数（Parameters）

- IqGain ：IQ 信号的增益。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetLoopFlags

设置循环适配标志。

```cpp
virtual SPRC_RESULT SpRcClient::SetLoopFlags(
    [in] int LoopFlags // 循环适配标志
);
```

#### 参数（Parameters）

- LoopFlags ：循环适配标志，编码为可以 OR 组合的标志。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_LOOP_CC | 适配连续计数器 |
| SPRC_LOOP_PCR | 适配 PCR |
| SPRC_LOOP_TDT | 适配 TDT |
| SPRC_LOOP_WRAP | 自动环绕 |

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 循环适配标志已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetModPars

为除 ISDB-T 和 DVB-T2 之外的所有调制标准设置调制参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetModPars(
    [in] SpRcModPars ModPars // 调制参数
);
```

#### 参数（Parameters）

- ModPars ：调制参数，请参阅 Struct SpRcModPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 调制参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetPlayoutState

设置播放状态（播放/暂停/停止）。

```cpp
virtual SPRC_RESULT SpRcClient::SetPlayoutState(
    [in] int PlayoutState // 播放状态
);
```

#### 参数（Parameters）

- PlayoutState ：新的播放状态。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_STATE_PAUSE | 暂停 |
| SPRC_STATE_PLAY | 播放 |
| SPRC_STATE_STOP | 停止 |

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_INV_IN_SFN | SFN 模式激活时不允许 |
| SPRC_E_INV_STATE | 无效的播放状态 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 播放状态已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetPlayoutStateSfn

为 SFN 设置播放状态（播放/停止）。

```cpp
virtual SPRC_RESULT SpRcClient::SetPlayoutStateSfn(
    [in] SpRcPlayoutSfnPars PlayoutPars // SFN 播放参数
);
```

#### 参数（Parameters）

- PlayoutPars ：SFN 播放参数，请参阅 Struct SpRcPlayoutSfnPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_INV_STATE | 无效的播放状态 |
| SPRC_E_INV_PARS | 无效的开始时间 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_SFN | SFN 模式禁用时不允许 |
| SPRC_OK | 调制参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetRemux

在调制器端口上设置重复用开/关。

```cpp
virtual SPRC_RESULT SpRcClient::SetRemux(
    [in] bool Remux // 重复用 开/关
);
```

#### 参数（Parameters）

- Remux ：是否应在调制器端口上应用重复用。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | 重复用状态已成功设置 |

#### 备注（Remarks）

> 注意：此函数存在于官方 SDK（SpRcApi.h / SpRc.wsdl，自 v1.4.1.8 起）中，但官方 PDF 未对其记录。上面的返回值代码是根据类似的调制器端口函数推断的。

### SpRcClient::SetRfPars

设置 RF 参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetRfPars(
    [in] SpRcRfPars RfPars // RF 参数
);
```

#### 参数（Parameters）

- RfPars ：RF 参数，请参阅 Struct SpRcPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_INV_FREQ | 此调制器上的上变频器不支持 RfPars 中的中心频率 |
| SPRC_E_INV_LEVEL | 此调制器不支持 RfPars 中的电平 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_MOD | 无效操作，因为该端口不是调制端口 |
| SPRC_OK | RF 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetSfnMode

更改 SFN 模式。

```cpp
virtual SPRC_RESULT SpRcClient::SetSfnMode(
    [in] int SfnMode // SFN 模式
);
```

#### 参数（Parameters）

- SfnMode ：新的 SFN 模式。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_SFN_MODE_DISABLE | 禁用 SFN |
| SPRC_SFN_MODE_1PPS | SFN 1PPS 模式。播放相对于 1 pps 信号开始 |

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_INV_STATE | StreamXpress 正在播放时无效操作 |
| SPRC_E_NOT_SFN | 无效操作，因为该端口没有 SFN 能力 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 信号源已成功更改 |

#### 备注（Remarks）

### SpRcClient::SetSignalSource

更改信号源（来自文件 / 测试信号发生器）。

```cpp
virtual SPRC_RESULT SpRcClient::SetSignalSource(
    [in] int SignalSource // 信号源
);
```

#### 参数（Parameters）

- SignalSource ：新的信号源。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_FROM_FILE | 从文件读取数据 |
| SPRC_TEST_GENERATOR | 使用测试信号发生器生成输出信号 |

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_OP_NOT_SUPPORTED | 当前调制类型不受支持 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 信号源已成功更改 |

#### 备注（Remarks）

### SpRcClient::SetSpiPars

设置 DVB-SPI 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetSpiPars(
    [in] SpRcSpiPars SpiPars // DVB-SPI 参数
);
```

#### 参数（Parameters）

- SpiPars ：DVB-SPI 传输参数，请参阅 Struct SpRcSpiPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_SPI | 无效操作，因为该端口不是 DVB-SPI 端口 |
| SPRC_E_TXMODE | SpiPars 中指定的传输模式与传输流文件不兼容 |
| SPRC_OK | DVB-SPI 传输参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetSubLoopPars

配置文件子循环。

```cpp
virtual SPRC_RESULT SpRcClient::SetSubLoopPars(
    [in] SpRcSubLoopPars SubLoopPars // 子循环参数
);
```

#### 参数（Parameters）

- SubLoopPars ：子循环参数，请参阅 Struct SpRcSubLoopPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_INV_PARS | 子循环参数无效；请确保值在 0 和 1 之间 |
| SPRC_OK | 子循环参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetTdtAdaptPars

设置 TDT/TOT 适配参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetTdtAdaptPars(
    [in] SpRcTdtAdaptPars TdtAdaptPars // TDT/TOT 适配参数
);
```

#### 参数（Parameters）

- TdtAdaptPars ：TDT/TOT 适配参数，请参阅 Struct SpRcTdtAdaptPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 循环适配标志已成功设置 |

#### 备注（Remarks）

仅当设置了 TDT 循环标志时，设置 TOT/TOT 适配参数才有效，请参阅 SpRcClient::SetLoopFlags。

### SpRcClient::SetTsgPars

设置测试信号生成参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetTsgPars(
    [in] SpRcTsgPars TsgPars // 测试信号生成参数
);
```

#### 参数（Parameters）

- TsgPars ：测试信号生成参数，请参阅 Struct SpRcTsgPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_OP_NOT_SUPPORTED | 无效操作，因为 StreamXpress 当前未以测试信号发生器模式运行 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetTsoipPars

设置 TSoIP 传输参数。

```cpp
virtual SPRC_RESULT SpRcClient::SetTsoipPars(
    [in] SpRcTsoipPars TsoipPars // TSoIP 参数
);
```

#### 参数（Parameters）

- TsoipPars ：TSoIP 传输参数，请参阅 Struct SpRcTsoipPars。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_E_NOT_TSOIP | 无效操作，因为该端口不是 TSoIP 端口 |
| SPRC_OK | TSoIP 传输参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetTsRate

设置传输流速率

```cpp
virtual SPRC_RESULT SpRcClient::SetTsRate(
    [in] Int TsRate // 传输流速率
);
```

#### 参数（Parameters）

- TsRate ：传输流速率，单位为比特每秒；每个传输包 188 字节

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 速率已成功设置 |

#### 备注（Remarks）

### SpRcClient::SetUseNit

启用或禁用使用 NIT 推导调制参数

```cpp
virtual SPRC_RESULT SpRcClient::SetUseNit(
    [in] Bool UseNit
);
```

#### 参数（Parameters）

- UseNit ：是否应使用 NIT。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_NO_PORT | 无效操作，因为未选择端口 |
| SPRC_OK | 参数已成功设置 |

#### 备注（Remarks）

### SpRcClient::WaitForCondition

等待某个条件。

```cpp
virtual SPRC_RESULT SpRcClient::WaitForCondition(
    [in] int Condition, // 要等待的播放状态
    [in] int TimeOut // 最长等待时间（ms）
);
```

#### 参数（Parameters）

- Condition ：要等待的条件。

| 值（Value） | 含义（Meaning） |
| --- | --- |
| SPRC_COND_STOPPED | 播放服务器处于停止状态；在此上下文中，暂停不被视为停止状态 |

- TimeOut ：超时时间（ms）。如果此参数为 -1，则不应用超时。

#### 返回值（Result）

| SPRC_RESULT | 含义（Meaning） |
| --- | --- |
| SPRC_E_COMMUNICATION | 与播放服务器通信时发生错误 |
| SPRC_E_INV_CONDITION | 指定了无效的条件 |
| SPRC_OK | 条件已发生 |
| SPRC_TIME_OUT | 已触发超时 |

#### 备注（Remarks）

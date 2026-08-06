//#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#* SpRcApi.h *#*#*#*#*#*#*#*#*# (C) 2008-2024 DekTec
//
// SpRcApi - StreamXpress Remote Control API - C++ encapsulation header file
//
// To be included by C++ clients that want to remotely control a play-out server

#ifndef SPRCAPI_H
#define SPRCAPI_H


//.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.- Include files -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-

// Include DTAPI.h
#include "DTAPI.h"

#ifdef _WIN32

#ifndef _LIB  // Do not link libraries into SpRcApi itself
#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "ws2_32.lib")
#endif
    
#ifndef _SPRCAPI_DISABLE_AUTO_LINK
    // Are we using multi-threaded-DLL or static runtime libraries?
    #ifdef _DLL
        // Link with DLL runtime version (/MD)
        #ifdef _DEBUG
            #ifdef _WIN64
                #pragma comment(lib, "SpRcApi64MDd.lib")    // Debug 64bit
                #pragma message("Automatically linking with SpRcApi64MDd.lib") 
            #else
                #pragma comment(lib, "SpRcApiMDd.lib")    // Debug 32bit
                #pragma message("Automatically linking with SpRcApiMDd.lib") 
            #endif
        #else
            #ifdef _WIN64
                #pragma comment(lib, "SpRcApi64MD.lib")     // Release 64bit
                #pragma message("Automatically linking with SpRcApi64MD.lib") 
            #else
                #pragma comment(lib, "SpRcApiMD.lib")     // Release 32bit
                #pragma message("Automatically linking with SpRcApiMD.lib") 
            #endif
        #endif
    #else
        // Link to static runtime version (/MT)
        #ifdef _DEBUG
            #ifdef _WIN64
                #pragma comment(lib, "SpRcApi64MTd.lib")      // Debug 64bit
                #pragma message("Automatically linking with SpRcApi64MTd.lib") 
            #else
                #pragma comment(lib, "SpRcApiMTd.lib")      // Debug 32bit
                #pragma message("Automatically linking with SpRcApiMTd.lib") 
            #endif
        #else
            #ifdef _WIN64
                #pragma comment(lib, "SpRcApi64MT.lib")       // Release 64bit
                #pragma message("Automatically linking with SpRcApi64MT.lib") 
            #else
                #pragma comment(lib, "SpRcApiMT.lib")       // Release 32bit
                #pragma message("Automatically linking with SpRcApiMT.lib") 
            #endif
        #endif
    #endif
#endif
#endif  // #ifdef _WIN32


// STL includes
#include <list>
#include <map>
#include <vector>
#include <sys\timeb.h>

// Elementary Types
typedef unsigned int  SPRC_RESULT;


//.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.- Structures -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.

// ASI parameters for GetAsiPars/SetAsiPars
struct SpRcAsiPars
{
    bool  m_Remux;                  // Remultiplex yes/no
    int  m_PlayoutRate;             // Only used if Remux is on
    bool  m_BurstMode;              // DVB-ASI burst mode
    int  m_TxMode;                  // Transmit mode
    int  m_Polarity;                // Physical polarity of the ASI signal
};

// Channel Modelling Path struct
struct SpRcCmPath
{
    int  m_Type;                    // Type of path fading:
                                    //  SPRC_CONSTANT_DELAY,
                                    //  SPRC_CONSTANT_DOPPLER
                                    //  SPRC_RAYLEIGH_JAKES
                                    //  SPRC_RAYLEIGH_GAUSSIAN
    double  m_Attenuation;          // Attenuation in dB
    double  m_Delay;                // Delay in us
    double  m_Phase;                // Phase shift in degrees for CONSTANT_DELAY paths
    double  m_Doppler;              // Doppler frequency in Hz
};

// CMMB Parameters struct
struct SpRcCmmbPars
{
    int  m_Bandwidth;               // CMMB Bandwitdh
    int  m_AreaId;                  // Area ID (0..127)
    int  m_TxId;                    // Transmitter ID (128..255)
};

// Channel Modelling Parameters struct
struct SpRcCmPars
{
    bool  m_CmEnable;               // Enable Channel Modelling 
    bool  m_AwgnEnable;             // Enable noise injection
    bool  m_PathsEnable;            // Enable transmission paths simulation
    double  m_Snr;                  // Signal-to-noise ratio in dB
    bool m_UseManualSeed{false};    // Use fixed seed for AWGN noise generator
    int  m_ManualSeed{0};           // Seed value (used if m_UseManualSeed = true)
    // List of transmission paths  
    std::vector<SpRcCmPath>  m_Paths;
};


// DVB-T2 group 
struct SpRcDvbT2Group
{
    std::wstring  m_GroupName;      // Name of the DVB-T2 group, e.g. "VV1xx"
    std::wstring  m_GroupRefName;   // Specific set in group, e.g. "VV100"
};

// DVB-T2 parameters
struct SpRcDvbT2Pars
{
    int  m_T2Version;               // See DTAPI_DVBT2_VERSION_x
    int  m_Bandwidth;               // See DTAPI_DVBT2_8MHZ/...
    int  m_FftMode;                 // See DTAPI_DVBT2_FFT_x
    int  m_Miso;                    // See DTAPI_DVBT2_MISO_x
    int  m_GuardInterval;           // Guard interval, see DTAPI_DVBT2_GI_x
    int  m_Papr;                    // See DTAPI_DVBT2_PAPR_x
    int  m_BwtExt;                  // 0 or 1, bandwidth extension
    int  m_PilotPattern;            // 1 to 8
    int  m_NumT2Frames;             // T2 frames per super frame (1 ... 255)
    int  m_NumDataSyms;             // Symbols per frame
    int  m_L1Modulation;            // See DTAPI_DVBT2_BPSK/..., 0 ... 3
    bool  m_FefEnable;              // Enable FEF
    int  m_FefType;                 // 0 ... 15
    int  m_FefLength;               // FEF length in T units
    int  m_FefS1;                   // 2 <= FefS1 <= 7
    int  m_FefS2;                   // 0 <= FefS2 <= 15 and (FefS2 & 1) != 0
    int  m_FefInterval;             // If FEF is enabled
                                    //  m_Requires: (NumT2Frames % FefInterval) == 0
    int  m_FefSignal;               // Selects the type of signal generated during the
                                    // FEF period (see DTAPI_DVBT2_FEF_XXX)
    int  m_CellId;
    int  m_NetworkId;
    int  m_T2SystemId;
    int  m_Frequency;               // Only used to fill the L1 post frequency field
    // PLP#0 parameters
    bool  m_Hem;                    // HEM - High Efficiency Mode
    bool  m_Npd;                    // NPD - Null-Packet Detection
    bool  m_IssyEnabled;            // ISSY Enabled yes/no
    int  m_Id;                      // PLP_ID
    int  m_GroupId;                 // PLP_GROUP_ID
    int  m_Type;                    // PLP_TYPE - See DTAPI_DVBT2_PLP_TYPE_x
    int  m_CodeRate;                // PLP_COD - Code rate, see DTAPI_DVBT2_COD_x
    int  m_Modulation;              // PLP_MOD - See DTAPI_DVBT2_BPSK/...
    bool  m_Rotation;               // PLP_ROTATION - 0 or 1
    int  m_FecType;                 // PLP_FEC_TYPE - 0=LDPC 16K, 1=LDPC 64K
    int  m_TimeIlLength;            // TIME_IL_LENGTH - 0..255
    int  m_TimeIlType;              // TIME_IL_TYPE - 0 or 1
    bool  m_InBandFlag;             // IN_BAND_FLAG - 0 or 1
    int  m_NumBlocks;               // Number of FEC blocks contained in one IL frame
    int  m_FollowMode;              // SPRC_T2_FOLLOW_OFF / SPRC_T2_FOLLOW_OPT1/2
};

// ISDB-T parameters
struct SpRcIsdbtLayerPars
{
    int  m_NumSegments;             // Number of segments
    int  m_Modulation;              // Modulation type
    int  m_CodeRate;                // Code rate
    int  m_TimeInterleave;          // Time interleaving
};
struct SpRcIsdbtPars
{
    bool  m_DoMux;                  // Hierarchical multiplexing yes/no
    int  m_BType;                   // Broadcast type
    int  m_Mode;                    // Transmission mode
    int  m_Guard;                   // Guard interval
    int  m_PartialRx;               // Partial reception
    int  m_Emergency;               // Switch-on control for emergency broadcast
    int  m_IipPid;                  // PID used for multiplexing IIP packet
    struct SpRcIsdbtLayerPars  m_LayerPars[3];
                                    // Layer-A/B/C parameters
    std::map<int, int>  m_Pid2Layer;// PID-to-layer mapping
    int  m_LayerOther;              // Other PIDs are mapped to this layer
    int  m_ParXtra0;                // Extra parameters encoded like ParXtra0 in
                                    // SetModControl for DTAPI_MOD_ISDBT
    int  m_Virtual13Segm;           // Virtual 13-segment mode
};
struct SpRcHwNoisePars
{
    bool    m_SnrOn;                // Enable
    double  m_Snr;                  // Snr value
};

// Modulation parameters for GetModPars/SetModPars (See DTAPI SetModControl)
struct SpRcModPars
{
    int  m_ModType;                 // Modulation type 
    int  m_ParXtra0;                // Extra modulation parameter 0
    int  m_ParXtra1;                // Extra modulation parameter 1
    int  m_ParXtra2;                // Extra modulation parameter 2
    int  m_SymRate;                 // Symbol rate (if required, set to -1 otherwise)
};

// Static playout information
struct SpRcPlayoutInfo
{
    bool  m_BurstMode;              // Burst mode
    bool  m_ExtClock;               // Use external clock
    bool  m_FileCanBeRead;          // A file has been selected that can be read
    std::wstring  m_Filename;       // Currently selected filename
    __int64  m_FileOffsetEnd;       // Number of unused bytes at end of file
    __int64  m_FileOffsetStart;     // Number of unused bytes at start of file
    __int64  m_FilePlayedBytes;     // File length minus bytes at start and end
    int  m_FileRateEst;             // TS: Estimated file rate
    __int64  m_FileSize;            // Size of the file
    int  m_FileType;                // Type of data in file: RAW/TS/SDI
    double  m_LoopBeginRel;         // Subloop, begin position (relative 0..1)
    double  m_LoopEndRel;           // Subloop, end position (relative 0..1)
    int  m_LoopFlags;               // Adapt CC/PCR/TDT and wrap-around flags
    int  m_PlayoutState;            // HOLD/PLAYING
    int  m_PlayoutRate;             // Playout rate @188
    bool  m_Remux;                  // Remultiplex mode
    int  m_SymRate;                 // Modulators: Symbol rate
    double  m_TimeLoopBegin;        // Time corresponding to beginning of loop
    double  m_TimeLoopEnd;          // Time corresponding to end of loop
    int  m_TimeOffset;              // Offset added to playout time
    int  m_TsRate;                  // TS: TS rate @188
    int  m_TpSize;                  // TS: packet size
    int  m_TxPolarity;              // Transmit polarity for ASI channels
};

// Subloop parameters
struct SpRcSubLoopPars
{
    bool  m_UseSubLoop;             // Enable Subloop
    double  m_LoopBeginRel;         // Subloop, begin position (relative 0..1)
    double  m_LoopEndRel;           // Subloop, end position (relative 0..1)
};

// Current playout status
struct SpRcPlayoutStatus
{
    int  m_FifoLoad;                // Current FIFO load
    int  m_NumErrors;               // Number of errors (underflows)
    int  m_NumWraps;                // #wraps
    double  m_PosRel;               // Relative position in subloop (0..1)
    int  m_TotalMemLoad;            // #words in DiskBuffer+MemBuffer (snapshot)
};

// SFN status
struct SpRcSfnStatus
{
    int  m_GpsStatus;               // Status of 10MHz and 1PPS
    int  m_GpsTime;                 // Current GPS-time 0 - 999.999.999
    int  m_SfnMode;                 // Current SFN-mode
    int  m_SfnStatus;               // Disabled, In-Hold, Starting, In-Sync, Error
};

// SpRcPlayoutSfnPars
struct SpRcPlayoutSfnPars
{
    int  m_PlayoutState;            // Playout state
    int  m_SfnStartTime;            // SFN start time
};

// Physical output port descriptor
struct SpRcPortDesc
{
    __int64  m_Serial;              // Serial number of the device hosting the port
    int  m_TypeNumber;              // Device type number
    unsigned char  m_Ip[4];         // IP address (only valid for IP ports)
    int  m_Mac[6];                  // MAC address (only valid for IP ports)
    int  m_FirmwareVersion;         // Firmware version
    int  m_FirmwareVariant;         // Firmware variant
    int  m_Port;                    // Physical port number
    int  m_OutputType;              // Output type
    int  m_Capabilities;            // Capability flags
    int  m_InUse;                   // Output port already in use?
};
typedef std::vector<SpRcPortDesc>  SpRcPortDescs;

// RF parameters for GetRfPars/SetRfPars
struct SpRcRfPars
{
    __int64  m_Frequency;           // RF frequency (Hz)
    double  m_Level;                // RF output level (dBm)
    bool  m_SpecInv;                // RF Spectral inversion
    bool  m_CW;                     // RF CW mode
    bool  m_RfEnabledOnStop;        // RF output enabled on stop
};

// DVB-SPI parameters for GetSpiPars/SetSpiPars
struct SpRcSpiPars
{
    bool  m_Remux;                  // Remultiplex yes/no
    int  m_PlayoutRate;             // Only used if Remux is on
    int  m_TxMode;                  // Transmit mode
    bool  m_Power;                  // Power on/off (DTA-102)
};

// TOT/TDT adaptation parameters for GetTdtAdaptPars/SetTdtAdaptPars
struct SpRcDateTime
{
    int m_Year;                     // Year e.g. 2024
    int m_Month;                    // Month 1-12
    int m_Day;                      // Day 1-31
    int m_Hour;                     // Hour 0-23
    int m_Minute;                   // Minute 0-59
    int m_Second;                   // Second 0-59
};

// TDT/TOT adaptation mode
#define SPRC_TDT_ADAPT_NOT_1ST_LOOP     1   // Adapt TDT after fist loop
#define SPRC_TDT_ADAPT_CURRENT_UTC      2   // Use current UTC time
#define SPRC_TDT_ADAPT_CURRENT_JST      3   // Use current JST time
#define SPRC_TDT_ADAPT_USE_SPECIFIED    4   // Use specified time

// TDT/TOT adaptation parameters
struct SpRcTdtAdaptPars
{
    int  m_TdtAdaptMode;            // TDT/TOT adaptation mode
    SpRcDateTime  m_TdtDateTime;    // Only used if adaptation mode is
                                    // SPRC_TDT_ADAPT_USE_SPECIFIED
};

#define SPRC_TSG_TYPE_PRBS7         0     // PRBS-7 TS generator
#define SPRC_TSG_TYPE_PRBS15        1     // PRBS-15 TS generator
#define SPRC_TSG_TYPE_PRBS23        2     // PRBS-23 / O.151 TS generator
#define SPRC_TSG_TYPE_PRBS31        3     // PRBS-31 TS generator
#define SPRC_TSG_TYPE_TS_CNT        4     // DekTec internal


#define SPRC_TSG_TYPE_RP198_NO_AUDIO 5    // Video generator (RP198 pattern, no audio)
#define SPRC_TSG_TYPE_DYNAMIC_NO_AUDIO 6  // Video generator (dynamic pattern, no audio)
#define SPRC_TSG_TYPE_RP198         7     // Video generator (RP198 pattern)
#define SPRC_TSG_TYPE_DYNAMIC       8     // Video generator (dynamic pattern)
#define SPRC_TSG_TYPE_RP219_1_NO_AUDIO 9  // Video generator (RP 219-1 pattern, no audio)
#define SPRC_TSG_TYPE_RP219_1       10    // Video generator (RP 219-1 pattern)


#define SPRC_TSG_TYPE_SDI_STATIC_NO_AUDIO   SPRC_TSG_TYPE_RP198_NO_AUDIO
#define SPRC_TSG_TYPE_SDI_DYNAMIC_NO_AUDIO  SPRC_TSG_TYPE_DYNAMIC_NO_AUDIO
#define SPRC_TSG_TYPE_SDI_STATIC            SPRC_TSG_TYPE_RP198
#define SPRC_TSG_TYPE_SDI_DYNAMIC           SPRC_TSG_TYPE_DYNAMIC


#define SPRC_VIDSTD_525I59_94    0x01
#define SPRC_VIDSTD_625I50       0x02
#define SPRC_VIDSTD_720P23_98    0x03
#define SPRC_VIDSTD_720P24       0x04
#define SPRC_VIDSTD_720P25       0x05
#define SPRC_VIDSTD_720P29_97    0x06
#define SPRC_VIDSTD_720P30       0x07
#define SPRC_VIDSTD_720P50       0x08
#define SPRC_VIDSTD_720P59_94    0x09
#define SPRC_VIDSTD_720P60       0x0A
#define SPRC_VIDSTD_1080I50      0x0B
#define SPRC_VIDSTD_1080I59_94   0x0C
#define SPRC_VIDSTD_1080I60      0x0D
#define SPRC_VIDSTD_1080P23_98   0x0E
#define SPRC_VIDSTD_1080P24      0x0F
#define SPRC_VIDSTD_1080P25      0x10
#define SPRC_VIDSTD_1080P29_97   0x11
#define SPRC_VIDSTD_1080P30      0x12
#define SPRC_VIDSTD_1080P50      0x13
#define SPRC_VIDSTD_1080P59_94   0x14
#define SPRC_VIDSTD_1080P60      0x15
#define SPRC_VIDSTD_1080PSF23_98 0x16
#define SPRC_VIDSTD_1080PSF24    0x17
#define SPRC_VIDSTD_1080PSF25    0x18
#define SPRC_VIDSTD_1080PSF29_97 0x19
#define SPRC_VIDSTD_1080PSF30    0x1A
#define SPRC_VIDSTD_1080P50B     0x1B
#define SPRC_VIDSTD_1080P59_94B  0x1C
#define SPRC_VIDSTD_1080P60B     0x1D
#define SPRC_VIDSTD_2160P23_98   0x1F
#define SPRC_VIDSTD_2160P24      0x20
#define SPRC_VIDSTD_2160P25      0x21
#define SPRC_VIDSTD_2160P29_97   0x22
#define SPRC_VIDSTD_2160P30      0x23
#define SPRC_VIDSTD_2160P50      0x24
#define SPRC_VIDSTD_2160P50B     0x25
#define SPRC_VIDSTD_2160P59_94   0x26
#define SPRC_VIDSTD_2160P59_94B  0x27
#define SPRC_VIDSTD_2160P60      0x28
#define SPRC_VIDSTD_2160P60B     0x29

#define SPRC_TSG_FLAG_SDI_FRM_CNT   0x01

// Test-signal generator parameters
struct SpRcTsgPars
{
    int  m_Type;                    // One of SPRC_TSG_TYPE_*
    int  m_Pid;                     // Pid that will carry the TS packets
    int  m_VidStd;                  // SPRC_VIDSTD_*, only for SPRC_TSG_TYPE_SDI_XXX
    int  m_Flags;                   // Internal use, set to 0.
};

// TSoIP parameters for GetTsoipPars/SetTsoipPars
struct SpRcTsoipPars
{
    int  m_TxMode;                  // Transmission mode (188, 204, Add16, ...)
    unsigned char  m_Ip[4];         // IP address
    int  m_Port;                    // IP port
    bool  m_EnaFailover;            // Enable IP double-buffering
    unsigned char  m_Ip2[4];        // 2nd IP address
    int  m_Port2;                   // 2nd IP port
    int  m_TimeToLive;              // TTL
    int  m_NumTpPerIp;              // #TPs per IP packet
    int  m_Protocol;                // Protocol: UDP/RTP
    int  m_DiffServ;                // Differentiated services
    int  m_FecMode;                 // Error correction mode
    int  m_FecNumRows;              // ‘D’ = #rows in FEC matrix
    int  m_FecNumCols;              // ‘L’ = #columns in FEC matrix
};


//=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ SpRcClient +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
//
// Class implementing remote-control client API
//
class SpRcClient
{
protected:
    SpRcClient();

public:
    // General
    virtual  ~SpRcClient();
    static SpRcClient*  CreateSpRcClient();
    static void  GetVersion(int& Major, int& Minor, int& BugFix, int& Build);

    // Session Interface
    virtual SPRC_RESULT  OpenSession(unsigned char Ip[4], unsigned short PortNr);
    virtual SPRC_RESULT  CloseSession();

    // Application common interface
    virtual SPRC_RESULT  GetAppInfo(std::wstring& AppName,
              int& MajorVersion, int& MinorVersion, int& BugFixVersion, int& BuildNumber);
    virtual SPRC_RESULT  GetRemoteVersion(int& MajorVersion, int& MinorVersion,
                                                    int& BugFixVersion, int& BuildNumber);
    virtual SPRC_RESULT  GetRemoteDtapiVersion(int& MajorVersion, int& MinorVersion,
                                                    int& BugFixVersion, int& BuildNumber);

    // Port selection interface
    virtual SPRC_RESULT  ScanPorts(SpRcPortDescs& PortDescs);
    virtual SPRC_RESULT  SelectPort(__int64 Serial, int Port, int Modulation);
    virtual SPRC_RESULT  SelectDtaPlus(bool UseDtaPlus, __int64 Serial);

    // Playout interface
    virtual SPRC_RESULT  ClearErrors();
    virtual SPRC_RESULT  GetAsiPars(SpRcAsiPars&);
    virtual SPRC_RESULT  GetChannelModellingPars(SpRcCmPars&); 
    virtual SPRC_RESULT  GetCmmbPars(SpRcCmmbPars&);
    virtual SPRC_RESULT  GetDvbT2Group(SpRcDvbT2Group&);
    virtual SPRC_RESULT  GetDvbT2Pars(SpRcDvbT2Pars&);
    virtual SPRC_RESULT  GetHwNoisePars(SpRcHwNoisePars&);
    virtual SPRC_RESULT  GetIsdbtPars(SpRcIsdbtPars&);
    virtual SPRC_RESULT  GetIqGain(int&);
    virtual SPRC_RESULT  GetModPars(SpRcModPars&);
    virtual SPRC_RESULT  GetPlayoutInfo(SpRcPlayoutInfo&);
    virtual SPRC_RESULT  GetPlayoutStatus(SpRcPlayoutStatus&);
    virtual SPRC_RESULT  GetSfnStatus(SpRcSfnStatus&);
    virtual SPRC_RESULT  GetRfPars(SpRcRfPars&);
    virtual SPRC_RESULT  GetSignalSource(int&);
    virtual SPRC_RESULT  GetSpiPars(SpRcSpiPars&);
    virtual SPRC_RESULT  GetTdtAdaptPars(SpRcTdtAdaptPars&);
    virtual SPRC_RESULT  GetTsgPars(SpRcTsgPars&);
    virtual SPRC_RESULT  GetTsoipPars(SpRcTsoipPars&);
    virtual SPRC_RESULT  GetUseNit(bool&);
    virtual SPRC_RESULT  Normalise();
    virtual SPRC_RESULT  OpenChannelModellingFile(wchar_t* Filename);
    virtual SPRC_RESULT  OpenFile(wchar_t* Filename);
    virtual SPRC_RESULT  SaveChannelModellingSettings(wchar_t* Filename);
    virtual SPRC_RESULT  SaveSettings(wchar_t* Filename);
    virtual SPRC_RESULT  SetAsiPars(SpRcAsiPars);
    virtual SPRC_RESULT  SetChannelModellingPars(SpRcCmPars);
    virtual SPRC_RESULT  SetCmmbPars(SpRcCmmbPars);
    virtual SPRC_RESULT  SetDvbT2Group(SpRcDvbT2Group);
    virtual SPRC_RESULT  SetDvbT2Pars(SpRcDvbT2Pars);
    virtual SPRC_RESULT  SetHwNoisePars(SpRcHwNoisePars);
    virtual SPRC_RESULT  SetIsdbtPars(SpRcIsdbtPars);
    virtual SPRC_RESULT  SetIqGain(int);
    virtual SPRC_RESULT  SetLoopFlags(int LoopFlags);
    virtual SPRC_RESULT  SetModPars(SpRcModPars);
    virtual SPRC_RESULT  SetPlayoutState(int);
    virtual SPRC_RESULT  SetPlayoutStateSfn(SpRcPlayoutSfnPars);
    virtual SPRC_RESULT  SetRemux(bool);
    virtual SPRC_RESULT  SetRfPars(SpRcRfPars);
    virtual SPRC_RESULT  SetSfnMode(int);
    virtual SPRC_RESULT  SetSignalSource(int);
    virtual SPRC_RESULT  SetSpiPars(SpRcSpiPars);
    virtual SPRC_RESULT  SetSubLoopPars(SpRcSubLoopPars);
    virtual SPRC_RESULT  SetTdtAdaptPars(SpRcTdtAdaptPars);
    virtual SPRC_RESULT  SetTsgPars(SpRcTsgPars);
    virtual SPRC_RESULT  SetTsoipPars(SpRcTsoipPars);
    virtual SPRC_RESULT  SetTsRate(int);
    virtual SPRC_RESULT  SetUseNit(bool);
    virtual SPRC_RESULT  ShowWindow(bool);
    virtual SPRC_RESULT  WaitForCondition(int, int);
};


//.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.- Constants -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-

// Capability flags
#define SPRC_CAP_ADJLVL       0x01  // Adjustable output level
#define SPRC_CAP_CM           0x02  // Supports channel modelling
#define SPRC_CAP_DIGIQ        0x04  // Has a digital IQ output
#define SPRC_CAP_IF           0x08  // Has an IF output
#define SPRC_CAP_LBAND        0x10  // Can upconvert to L-Band 950 ..  2150 MHz
#define SPRC_CAP_UHF          0x20  // Can upconvert to UHF Band 400 .. 862 MHz
#define SPRC_CAP_VHF          0x40  // Can upconvert to VHF Band 47 .. 470 MHz
#define SPRC_CAP_SFN          0x80  // Supports Single Frequency Network operation

// Channel Modelling transmission path types
#define SPRC_CONSTANT_DELAY      0  // Constant phase
#define SPRC_CONSTANT_DOPPLER    1  // Constant frequency shift
#define SPRC_RAYLEIGH_JAKES      2  // Rayleigh fading with Jakes power spectral 
                                    // density (mobile path model)
#define SPRC_RAYLEIGH_GAUSSIAN   3  // Rayleigh fading with Gaussian power spectral
                                    // density (ionospheric path model)

// Conditions
#define SPRC_COND_STOPPED        1  // Player is in stopped state

// DVB-T2 follow modes
#define SPRC_T2_FOLLOW_OFF       0  // No following
#define SPRC_T2_FOLLOW_OPT1      1  // Follow optimum1
#define SPRC_T2_FOLLOW_OPT2      2  // Follow optimum2

// File type
#define SPRC_FTYPE_SDSDI         1  // SD-SDI

// Loop-adaptation flags
#define SPRC_LOOP_CC             1  // Adapt continuity counters
#define SPRC_LOOP_PCR            2  // Adapt PCR
#define SPRC_LOOP_TDT            4  // Adapt TDT
#define SPRC_LOOP_WRAP           8  // Auto wrap-around

// Modulation standards
#define SPRC_MOD_ADTBT           0  // ADTB-T
#define SPRC_MOD_ATSC            1  // ATSC VSB
#define SPRC_MOD_CMMB            2  // CMMB
#define SPRC_MOD_DTMB            3  // DTMB
#define SPRC_MOD_DVBH            4  // DVB-H
#define SPRC_MOD_DVBS            5  // DVB-S
#define SPRC_MOD_DVBS2           6  // DVB-S2
#define SPRC_MOD_DVBT            7  // DVB-T
#define SPRC_MOD_DVBT2           8  // DVB-T2
#define SPRC_MOD_DVBT2MI         9  // DVB T2-MI
#define SPRC_MOD_IQ             10  // IQ
#define SPRC_MOD_ISDBS          11  // ISDB-S
#define SPRC_MOD_ISDBT          12  // ISDB-T
#define SPRC_MOD_J83A           13  // J.83 annex A (DVB-C)
#define SPRC_MOD_J83B           14  // J.83 annex B ("American QAM")
#define SPRC_MOD_J83C           15  // J.83 annex C ("Japanese DVB-C")
#define SPRC_MOD_DAB            16  // DAB
#define SPRC_MOD_ATSC_MH        17  // ATSC-MH
#define SPRC_MOD_S2L3           18  // DVB-S2 L3
#define SPRC_MOD_DVBS2X         19  // DVB-S2X
#define SPRC_MOD_ISDBS3         20  // ISDB-S3
#define SPRC_MOD_DRM            21  // DRM
#define SPRC_MOD_ATSC3_STLTP    22  // ATSC 3.0 STLTP
#define SPRC_MOD_DVBS2X_GSELITEHEM 23  // DVB-S2X GSE-Lite HEM

// Output type flags
#define SPRC_OTYPE_ASI     0x00001  // DVB-ASI
#define SPRC_OTYPE_ATSC    0x00002  // ATSC (VSB) modulation
#define SPRC_OTYPE_CMMB    0x00004  // CMMB modulation
#define SPRC_OTYPE_DTMB    0x00008  // DTMB modulation
#define SPRC_OTYPE_DVBS    0x00010  // DVB-S modulation
#define SPRC_OTYPE_DVBS2   0x00020  // DVB-S.2 modulation
#define SPRC_OTYPE_DVBT    0x00040  // DVB-T modulation, includes DVB-H
#define SPRC_OTYPE_DVBT2   0x00080  // DVB-T2 modulation
#define SPRC_OTYPE_DVBT2MI 0x00100  // DVB T2-MI
#define SPRC_OTYPE_IQ      0x00200  // IQ
#define SPRC_OTYPE_ISDBS   0x00400  // ISDB-S modulation
#define SPRC_OTYPE_ISDBT   0x00800  // ISDB-T modulation
#define SPRC_OTYPE_QAM_A   0x01000  // QAM modulation, ITU-T J.83 Annex A (DVB-C)
#define SPRC_OTYPE_QAM_B   0x02000  // QAM modulation, ITU-T J.83 Annex B (US)
#define SPRC_OTYPE_QAM_C   0x04000  // QAM modulation, ITU-T J.83 Annex C (Japan)
#define SPRC_OTYPE_SDSDI   0x08000  // Standard-definition SDI
#define SPRC_OTYPE_SPI     0x10000  // DVB-SPI
#define SPRC_OTYPE_TSOIP   0x20000  // TS-over-IP
#define SPRC_OTYPE_ISDBS3  0x40000  // ISDB-S3 modulation
#define SPRC_OTYPE_DRM     0x80000  // DRM modulation
#define SPRC_OTYPE_ATSC3_STLTP     0x100000  // ATSC 3.0 STLTP modulation


// Port-in-use values
#define SPRC_PORT_UNUSED         0  // Port is not used
#define SPRC_PORT_CURR           1  // Port is currently selected play-out port
#define SPRC_PORT_USED           2  // Port is used by another application

// Playout state
#define SPRC_STATE_PAUSE         0  // Pause
#define SPRC_STATE_PLAY          1  // Playing
#define SPRC_STATE_STOP          2  // Stop

// Signal source
#define SPRC_FROM_FILE           0  // Use transport stream file as input
#define SPRC_TEST_GENERATOR      1  // Test signal generator provides data stream

// SFN mode
#define SPRC_SFN_MODE_DISABLE    0  // SFN operation disabled
#define SPRC_SFN_MODE_1_PPS      1  // SFN operation using 1-PPS mode

// GPS status
#define SPRC_GPS_STATUS_10MHZ_NO_SIGNAL 0x00    // No 10MHz input reference signal
#define SPRC_GPS_STATUS_10MHZ_OUT_RANGE 0x01    // 10MHz input signal is out of range
#define SPRC_GPS_STATUS_10MHZ_SYNC      0x02    // GPS time counter is frequency-locked to
                                                // the 10MHz clock input signal.
#define SPRC_GPS_STATUS_10MHZ_1PPS_SYNC 0x03    // GPS-time is phase-locked 10MHz and 
                                                // to the 1pps input signal

// SFN status
#define SPRC_SFN_STATUS_DISABLED 1  // Not operating in SFN-mode
#define SPRC_SFN_STATUS_HOLD     2  // SFN playout is ready, waiting for a play command
                                    // and accompanying start time
#define SPRC_SFN_STATUS_STARTING 3  // SFN playout is starting, playout starts when 
                                    // the start time is reached
#define SPRC_SFN_STATUS_IN_SYNC  4  // SFN playout is running and in sync
#define SPRC_SFN_STATUS_ERROR    5  // SFN playout error has occurred, restart of
                                    // SFN playout is necessary      

//-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.- Return Codes -.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
//
#define  SPRC_OK                    0
#define  SPRC_TIME_OUT              1
#define  SPRC_E                     0x2000
#define  SPRC_E_CALLBACK_NOT_SET    (SPRC_E + 0)    // Callback function not set
#define  SPRC_E_COMMUNICATION       (SPRC_E + 1)
#define  SPRC_E_CONN_OPEN_ERROR     (SPRC_E + 2)
#define  SPRC_E_FILE_CANT_FIND      (SPRC_E + 3)    // Can't find file
#define  SPRC_E_ITF_NOT_SUPPORTED   (SPRC_E + 4)
#define  SPRC_E_INV_CONDITION       (SPRC_E + 5)    // Invalid condition
#define  SPRC_E_INV_FREQ            (SPRC_E + 6)    // Invalid RF frequency
#define  SPRC_E_INV_LEVEL           (SPRC_E + 7)    // Invalid output level
#define  SPRC_E_INV_PARS            (SPRC_E + 8)    // Invalid parameters
#define  SPRC_E_INV_STATE           (SPRC_E + 9)    // Invalid state
#define  SPRC_E_MOD_STANDARD        (SPRC_E + 10)   // Illegal modulation standard
#define  SPRC_E_NO_LICK             (SPRC_E + 11)   // No license key available
#define  SPRC_E_NO_PORT             (SPRC_E + 12)   // No port is selected
#define  SPRC_E_NOT_ASI             (SPRC_E + 13)   // Port is not an ASI port or is
                                                    // operating in SDI mode
#define  SPRC_E_NOT_FOUND           (SPRC_E + 14)   // Cannot find the playout port
#define  SPRC_E_NOT_DVBT2           (SPRC_E + 15)   // Not operating in DVB-T2 mode
#define  SPRC_E_NOT_ISDBT           (SPRC_E + 16)   // Not operating in ISDB-T mode
#define  SPRC_E_NOT_MOD             (SPRC_E + 17)   // Port is not a modulator
#define  SPRC_E_NOT_SPI             (SPRC_E + 18)   // Port is not a DVB-SPI port
#define  SPRC_E_NOT_TSOIP           (SPRC_E + 19)   // Port is not a TSoIP port
#define  SPRC_E_OP_NOT_SUPPORTED    (SPRC_E + 20)
#define  SPRC_E_POLARITY            (SPRC_E + 21)   // ASI polarity not supported
#define  SPRC_E_PORT_USED           (SPRC_E + 22)   // Port in use by another application
#define  SPRC_E_SERVER_NOT_FOUND    (SPRC_E + 23)
#define  SPRC_E_SESSION_NOT_OPEN    (SPRC_E + 24)   // No session is open
#define  SPRC_E_SESSION_OPEN        (SPRC_E + 25)   // A session is already open
#define  SPRC_E_TXMODE              (SPRC_E + 26)   // Tx mode incompatible with file
#define  SPRC_E_NOT_CMMB            (SPRC_E + 27)   // Not operating in CMMB mode
#define  SPRC_E_INV_DVBT2_GROUP     (SPRC_E + 28)   // Unknown DVB-T2 group(ref)name 
#define  SPRC_E_FILE_SYNTAX_ERROR   (SPRC_E + 29)   // Syntax error in chmx file
#define  SPRC_E_FILE_CANT_CREATE    (SPRC_E + 30)   // Cannot create file
#define  SPRC_E_REGRTEST_ONLY       (SPRC_E + 31)   // Invalid pars: for internal use only
#define  SPRC_E_NOT_SFN             (SPRC_E + 32)   // SFN conditions are not met
#define  SPRC_E_INV_IN_SFN          (SPRC_E + 33)   // Invalid operation in SFN mode

#endif  // SPRCAPI_H

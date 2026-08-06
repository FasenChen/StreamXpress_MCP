# #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#* SPRC_types.py *#*#*#*#*#*#*#*#*#*#* (C) 2024 DekTec
#
#
""" This file contains the Python SPRC type that are used in the SPRC functions. 
    These types are similar to the types used in the SpRcApi. 
    See also the SpRcApi documentation 
    Based on SpRcApi v1.11.0.19.
    Note that the field names must exactly match to the names used in the SOAP-messages 
    and must not be renamed.
"""

from dataclasses import dataclass,field
from enum import Enum

from .DTAPI_constants import DTAPI
from .SPRC_constants import SPRC

    
@dataclass
class SpRcVersion :
    MajorVersion: int               # Major version number
    MinorVersion: int               # Minor version number
    BugFixVersion: int              # Bugfix version number
    BuildNumber: int                # Build number

@dataclass 
class SpRcAsiPars:
    Remux: bool                     # Remultiplex yes/no
    PlayoutRate: int                # Only used if Remux is on
    BurstMode: bool = False         # DVB-ASI burst mode
    TxMode: int = DTAPI.TXMODE_188  # Transmit mode
    Polarity: int = DTAPI.TXPOL_NORMAL  # Physical polarity of the ASI signal

@dataclass
class  SpRcCmPath:
    Type: int                       # Type of path fading:
                                    # SPRC.CONSTANT_DELAY,
                                    # SPRC.CONSTANT_DOPPLER
                                    # SPRC.RAYLEIGH_JAKES
                                    # SPRC.RAYLEIGH_GAUSSIAN
    Attenuation: float              # Attenuation in dB
    Delay: float                    # Delay in us
    Phase: float                    # Phase shift in degrees for CONSTANT_DELAY paths
    Doppler: float                  # Doppler frequency in Hz

@dataclass 
class SpRcCmmbPars:
    Bandwidth: int                  # CMMB bandwitdh
    AreaId: int                     # Area ID (0..127)
    TxId: int                       # Transmitter ID (128..255)

@dataclass 
class SpRcCmPars:
    CmEnable: bool                  # Enable Channel Modelling
    AwgnEnable: bool                # Enable noise injection
    Snr: float                      # Signal-to-noise ratio in dB
    PathsEnable: bool = False       # Enable transmission paths simulation
    Paths: list[SpRcCmPath] = field(default_factory=list) # List of transmission paths

@dataclass 
class SpRcDvbT2Group:
    GroupName: str                  # Name of the DVB-T2 group, e.g. "VV1xx"
    GroupRefName: str               # Specific set in group, e.g. "VV100"

@dataclass 
class SpRcDvbT2Pars:
    T2Version: int                  # See DTAPI.DVBT2_VERSION_x
    Bandwidth: int                  # See DTAPI.DVBT2_8MHZ/...
    FftMode: int                    # See DTAPI.DVBT2_FFT_x
    Miso: int                       # See DTAPI.DVBT2_MISO_x
    GuardInterval: int              # Guard interval, see DTAPI.DVBT2_GI_x
    Papr: int                       # See DTAPI.DVBT2_PAPR_x
    BwtExt: int                     # 0 or 1, bandwidth extension
    PilotPattern: int               # 1 to 8
    NumT2Frames: int                # T2 frames per super frame (1 ... 255)
    NumDataSyms: int                # Symbols per frame
    L1Modulation: int               # See DTAPI.DVBT2_BPSK/..., 0 ... 3
    FefEnable: bool                 # Enable FEF
    FefType: int                    # 0 ... 15
    FefLength: int                  # FEF length in T units
    FefS1: int                      # 2 <= FefS1 <= 7
    FefS2: int                      # 0 <= FefS2 <= 15 and (FefS2 & 1) != 0
    FefInterval: int                # If FEF is enabled
                                    # Requires: (NumT2Frames % FefInterval) == 0
    FefSignal: int                  # Selects the type of signal generated during the
                                    # FEF period (see DTAPI.DVBT2_FEF_XXX)
    CellId: int
    NetworkId: int
    T2SystemId: int
    Frequency: int                  # Only used to fill the L1 post frequency field
    # PLP#0 parameters
    Hem: bool                       # HEM - High Efficiency Mode, True or False
    Npd: bool                       # NPD - Null-Packet Detection, True or False
    IssyEnabled: bool               # ISSY Enabled, True or False
    Id: int                         # PLP_ID
    GroupId: int                    # PLP_GROUP_ID
    Type: int                       # PLP_TYPE - See DTAPI.DVBT2_PLP_TYPE_x
    CodeRate: int                   # PLP_COD - Code rate, see DTAPI.DVBT2_COD_x
    Modulation: int                 # PLP_MOD - See DTAPI.DVBT2_BPSK/...
    Rotation: bool                  # PLP_ROTATION - True or False
    FecType: int                    # PLP_FEC_TYPE - 0=LDPC 16K, 1=LDPC 64K
    TimeIlLength: int               # TIME_IL_LENGTH - 0..255
    TimeIlType: int                 # TIME_IL_TYPE - 0 or 1
    InBandFlag: bool                # IN_BAND_FLAG - True or False
    NumBlocks: int                  # Number of FEC blocks contained in one IL frame
    FollowMode: int = SPRC.T2_FOLLOW_OFF  # SPRC.T2_FOLLOW_OFF / SPRC.T2_FOLLOW_OPT1/2

@dataclass 
class SpRcIsdbtLayerPars:
    NumSegments: int                # Number of segments
    Modulation: int                 # Modulation type
    CodeRate: int                   # Code rate
    TimeInterleave: int             # Time interleaving

@dataclass 
class SpRcIsdbtPars:
    DoMux: bool                     # Hierarchical multiplexing, True or False
    BType: int                      # Broadcast type
    Mode: int                       # Transmission mode
    Guard: int                      # Guard interval
    PartialRx: int                  # Partial reception, 0 or 1
    Emergency: int                  # Switch-on control for emergency broadcast, 0 or 1
    IipPid: int                     # PID used for multiplexing IIP packet
    LayerPars: list [SpRcIsdbtLayerPars] # Layer-A/B/C parameters
    Pid2Layer: dict [int, int]      # PID-to-layer mapping
    LayerOther: int                 # Other PIDs are mapped to this layer
    ParXtra0: int                   # Extra parameters encoded like ParXtra0 in
                                    # SetModControl for DTAPI.MOD_ISDBT
    Virtual13Segm: int = 0          # Virtual 13-segment mode 0 or 1

@dataclass 
class SpRcHwNoisePars:
    SnrOn: bool                     # Enable
    Snr: float                      # Snr value

@dataclass 
class SpRcModPars:
    ModType: int                    # Modulation type
    ParXtra0: int                   # Extra modulation parameter 0
    ParXtra1: int                   # Extra modulation parameter 1
    ParXtra2: int                   # Extra modulation parameter 2
    SymRate: int  = -1              # Symbol rate (if required, set to -1 otherwise)

@dataclass 
class SpRcPlayoutInfo:
    BurstMode: bool                 # Burst mode
    ExtClock: bool                  # Use external clock
    FileCanBeRead: bool             # A file has been selected that can be read
    Filename: str                   # Currently selected filename
    FileOffsetEnd: int              # Number of unused bytes at end of file
    FileOffsetStart: int            # Number of unused bytes at start of file
    FilePlayedBytes: int            # File length minus bytes at start and end
    FileRateEst: int                # TS: Estimated file rate
    FileSize: int                   # Size of the file
    FileType: int                   # Type of data in file: RAW/TS/SDI
    LoopBeginRel: float             # Subloop, begin position (relative 0..1)
    LoopEndRel: float               # Subloop, end position (relative 0..1)
    LoopFlags: int                  # Adapt CC/PCR/TDT and wrap-around flags
    PlayoutState: int               # HOLD/PLAYING
    PlayoutRate: int                # Playout rate @188
    Remux: bool                     # Remultiplex mode
    SymRate: int                    # Modulators: Symbol rate
    TimeLoopBegin: float            # Time corresponding to beginning of loop
    TimeLoopEnd: float              # Time corresponding to end of loop
    TimeOffset: int                 # Offset added to playout time
    TsRate: int                     # TS: TS rate @188
    TpSize: int                     # TS: packet size
    TxPolarity: int                 # Transmit polarity for ASI channels

@dataclass 
class SpRcRemuxPars:
    Remux: bool                     # Remultiplex mode

@dataclass 
class SpRcSubLoopPars:
    UseSubLoop: bool                # Enable Subloop
    LoopBeginRel: float             # Subloop, begin position (relative 0..1)
    LoopEndRel: float               # Subloop, end position (relative 0..1)

@dataclass 
class SpRcPlayoutStatus:
    FifoLoad: int                   # Current FIFO load
    NumErrors: int                  # Number of errors (underflows)
    NumWraps: int                   # #wraps
    PosRel: float                   # Relative position in subloop (0..1)
    TotalMemLoad: int               # #words in DiskBuffer+MemBuffer (snapshot)

@dataclass 
class SpRcSfnStatus:
    GpsStatus: int                  # Status of 10MHz and 1PPS
    GpsTime: int                    # Current GPS-time 0 - 999.999.999
    SfnMode: int                    # Current SFN-mode
    SfnStatus: int                  # Disabled, In-Hold, Starting, In-Sync, Error

@dataclass 
class SpRcPlayoutSfnPars:
    PlayoutState: int               # Playout state
    SfnStartTime: int  = 0          # SFN start time

@dataclass 
class SpRcPortDesc:
    Serial: int                     # Serial number of the device hosting the port
    TypeNumber: int                 # Device type number
    Ip : bytes                      # IP address (only valid for IP ports)
    Mac: bytes                      # MAC address (only valid for IP ports)
    FirmwareVersion: int            # Firmware version
    FirmwareVariant: int            # Firmware variant
    Port: int                       # Physical port number
    OutputType: int                 # Output type
    Capabilities: int               # Capability flags
    InUse: int                      # Output port already in use?

@dataclass 
class SpRcRfPars:
    Frequency: int                  # RF frequency (Hz)
    Level: float                    # RF output level (dBm)
    SpecInv: bool = False           # RF Spectral inversion
    CW: bool = False                # RF CW mode
    RfEnabledOnStop: bool = False   # RF output enabled on stop

@dataclass 
class SpRcSpiPars:
    Remux: bool                     # Remultiplex yes/no
    PlayoutRate: int                # Only used if Remux is on
    TxMode: int  = DTAPI.TXMODE_188 # Transmit mode
    Power: bool  = False            # Power on/off (DTA-102)

@dataclass 
class SpRcDateTime:
    Year: int = 0                   # Year e.g. 2024
    Month: int = 0                  # Month 1-12
    Day: int = 0                    # Day 1-31
    Hour: int = 0                   # Hour 0-23
    Minute: int = 0                 # Minute 0-59
    Second: int = 0                 # Second 0-59

@dataclass 
class SpRcTdtAdaptPars:
    TdtAdaptMode: int               # TDT/TOT adaptation mode
    TdtDateTime: SpRcDateTime       # Only used if adaptation mode is
                                    # SPRC.TDT_ADAPT_USE_SPECIFIED

@dataclass 
class  SpRcTsgPars:
    Type: int                       # One of SPRC.TSG_TYPE_*
    Pid: int                        # Pid that will carry the TS packets
    VidStd: int                     # SPRC.VIDSTD_*, only for SPRC.TSG_TYPE_SDI_XXX
    Flags: int = 0                  # Internal use, set to 0.

@dataclass 
class  SpRcTsoipPars:
    TxMode: int                     # Transmission mode (188, 204, Add16, ...)
    Ip: bytes                       # IP address
    Port: int                       # IP port
    EnaFailover: bool               # Enable IP double-buffering
    Ip2: bytes                      # IP address
    Port2: int                      # 2nd IP port
    TimeToLive: int                 # TTL
    NumTpPerIp: int                 # #TPs per IP packet
    Protocol: int                   # Protocol: UDP/RTP
    DiffServ: int                   # Differentiated services
    FecMode: int                    # Error correction mode
    FecNumRows: int                 #  D  = #rows in FEC matrix
    FecNumCols: int                 #  L  = #columns in FEC matrix


# SPRC result codes
class SPRC_RESULT(Enum):
    OK                  = 0
    TIME_OUT            = 1
    ERROR               = 0x2000
    E_CALLBACK_NOT_SET  = (ERROR + 0)    # Callback function not set
    E_COMMUNICATION     = (ERROR + 1)
    E_CONN_OPEN_ERROR   = (ERROR + 2)
    E_FILE_CANT_FIND    = (ERROR + 3)    # Can't find file
    E_ITF_NOT_SUPPORTED = (ERROR + 4)
    E_INV_CONDITION     = (ERROR + 5)    # Invalid condition
    E_INV_FREQ          = (ERROR + 6)    # Invalid RF frequency
    E_INV_LEVEL         = (ERROR + 7)    # Invalid output level
    E_INV_PARS          = (ERROR + 8)    # Invalid parameters
    E_INV_STATE         = (ERROR + 9)    # Invalid state
    E_MOD_STANDARD      = (ERROR + 10)   # Illegal modulation standard
    E_NO_LICK           = (ERROR + 11)   # No license key available
    E_NO_PORT           = (ERROR + 12)   # No port is selected
    E_NOT_ASI           = (ERROR + 13)   # Port is not an ASI port or is
                                         # operating in SDI mode
    E_NOT_FOUND         = (ERROR + 14)   # Cannot find the playout port
    E_NOT_DVBT2         = (ERROR + 15)   # Not operating in DVB-T2 mode
    E_NOT_ISDBT         = (ERROR + 16)   # Not operating in ISDB-T mode
    E_NOT_MOD           = (ERROR + 17)   # Port is not a modulator
    E_NOT_SPI           = (ERROR + 18)   # Port is not a DVB-SPI port
    E_NOT_TSOIP         = (ERROR + 19)   # Port is not a TSoIP port
    E_OP_NOT_SUPPORTED  = (ERROR + 20)
    E_POLARITY          = (ERROR + 21)   # ASI polarity not supported
    E_PORT_USED         = (ERROR + 22)   # Port in use by another application
    E_SERVER_NOT_FOUND  = (ERROR + 23)
    E_SESSION_NOT_OPEN  = (ERROR + 24)   # No session is open
    E_SESSION_OPEN      = (ERROR + 25)   # A session is already open
    E_TXMODE            = (ERROR + 26)   # Tx mode incompatible with file
    E_NOT_CMMB          = (ERROR + 27)   # Not operating in CMMB mode
    E_INV_DVBT2_GROUP   = (ERROR + 28)   # Unknown DVB-T2 group(ref)name 
    E_FILE_SYNTAX_ERROR = (ERROR + 29)   # Syntax error in chmx file
    E_FILE_CANT_CREATE  = (ERROR + 30)   # Cannot create file
    E_REGRTEST_ONLY     = (ERROR + 31)   # Invalid pars: for internal use only
    E_NOT_SFN           = (ERROR + 32)   # SFN conditions are not met
    E_INV_IN_SFN        = (ERROR + 33)   # Invalid operation in SFN mode

# SPRC exception
class SpRcException(Exception):
    ErrorCode : SPRC_RESULT = SPRC_RESULT.OK
    def __init__(self, error_code : SPRC_RESULT, message : str = ''):
        self.ErrorCode = error_code
        super().__init__(message)
        
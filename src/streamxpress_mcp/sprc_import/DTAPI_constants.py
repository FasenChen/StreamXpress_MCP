# #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#* DTAPI_constants.py *#*#*#*#*#*#*#*#*# (C) 2024 DekTec
#
#
""" This file contains the DTAPI definitions that are used in the SPRC functions.
    See also DTAPI Reference – Core Classes documentation.
    Based on DTAPI v6.3.2.224 """
    
class DTAPI:
#
# Transmit mode for Transport Streams - Modes
    TXMODE_TS           =  0x10
    TXMODE_TS_MODE_BITS =  0x0F
    TXMODE_188          =  (    TXMODE_TS | 0x01)
    TXMODE_192          =  (    TXMODE_TS | 0x02)
    TXMODE_204          =  (    TXMODE_TS | 0x03)
    TXMODE_ADD16        =  (    TXMODE_TS | 0x04)
    TXMODE_MIN16        =  (    TXMODE_TS | 0x05)
    TXMODE_IPRAW        =  (    TXMODE_TS | 0x06)
    TXMODE_RAW          =  (    TXMODE_TS | 0x07)
    TXMODE_RAWASI       =  (    TXMODE_TS | 0x08)
    TXMODE_TS_MASK      =  (    TXMODE_TS |     TXMODE_TS_MODE_BITS)

# Transmit polarity
    TXPOL_NORMAL       =  0
    TXPOL_INVERTED     =  1


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ CMMB Parameters +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
# CMMB - Bandwidth
    CMMB_BW_2MHZ       =  0x00000000
    CMMB_BW_8MHZ       =  0x00000001

# =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ DVB-T2 Parameters +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+

# DVB-T2 Maximum
    DVBT2_NUM_PLP_MAX   = 255          # Maximum number of PLPs
    DVBT2_NUM_RF_MAX    = 7            # Maximum number of RF output signals

# PLP IDs
    DVBT2_PLP_ID_NONE   = -1           # No PLP selected
    DVBT2_PLP_ID_AUTO   = -2           # Automatic PLP selection

# Issy
    DVBT2_ISSY_NONE     = 0            # No ISSY field is used
    DVBT2_ISSY_SHORT    = 1            # 2-byte ISSY field is used
    DVBT2_ISSY_LONG     = 2            # 3-byte ISSY field is used

# Bandwidth
    DVBT2_1_7MHZ        = 0            # 1.7 MHz
    DVBT2_5MHZ          = 1            # 5 MHz
    DVBT2_6MHZ          = 2            # 6 MHz
    DVBT2_7MHZ          = 3            # 7 MHz
    DVBT2_8MHZ          = 4            # 8 MHz
    DVBT2_10MHZ         = 5            # 10 MHz
    DVBT2_BW_UNK        = -1           # Unknown bandwith
    DVBT2MI_BW_MSK      = 0xF          # Mask for T2MI ParXtra2
    DVBT2MI_BW_UNK      = 0xF          #Val in ParXtra2 if not set, map to 8MHz

# FftMode
# Warning: the codes are different from the corresponding L1 field
    DVBT2_FFT_1K        = 0            # 1K FFT
    DVBT2_FFT_2K        = 1            # 2K FFT
    DVBT2_FFT_4K        = 2            # 4K FFT
    DVBT2_FFT_8K        = 3            # 8K FFT
    DVBT2_FFT_16K       = 4            # 16K FFT
    DVBT2_FFT_32K       = 5            # 32K FFT
    DVBT2_FFT_UNK       = -1           # Unknown FFT mode

# Miso
    DVBT2_MISO_OFF      = 0            # No MISO
    DVBT2_MISO_TX1      = 1            # TX1 only
    DVBT2_MISO_TX2      = 2            # TX2 only
    DVBT2_MISO_TX1TX2   = 3            # TX1+TX2 Legacy
    DVBT2_MISO_SUM      = 3            # TX1+TX2
    DVBT2_MISO_BOTH     = 4            # TX1 and TX2

# Guard - Guard interval
# Warning: the codes are different from the corresponding L1 field
    DVBT2_GI_1_128      = 0            # 1/128
    DVBT2_GI_1_32       = 1            # 1/32
    DVBT2_GI_1_16       = 2            # 1/16
    DVBT2_GI_19_256     = 3            # 19/256
    DVBT2_GI_1_8        = 4            # 1/8
    DVBT2_GI_19_128     = 5            # 19/128
    DVBT2_GI_1_4        = 6            # 1/4
    DVBT2_GI_UNK        = -1           # Unknown guard interval

# Papr - PAPR - Peak to Average Power Reduction
    DVBT2_PAPR_NONE     = 0
    DVBT2_PAPR_ACE      = 1            # ACE - Active Constellation Extension
    DVBT2_PAPR_TR       = 2            # TR - PAPR using reserved carriers
    DVBT2_PAPR_ACE_TR   = 3            # ACE and TR

# BwtExt - Bandwidth extension
    DVBT2_BWTEXT_OFF    = False        # No bandwidth extension
    DVBT2_BWTEXT_ON     = True         # Bandwidth extension on

# PilotPattern
# Warning: the codes are different from the corresponding L1 field
    DVBT2_PP_1          = 1            # PP1
    DVBT2_PP_2          = 2            # PP2
    DVBT2_PP_3          = 3            # PP3
    DVBT2_PP_4          = 4            # PP4
    DVBT2_PP_5          = 5            # PP5
    DVBT2_PP_6          = 6            # PP6
    DVBT2_PP_7          = 7            # PP7
    DVBT2_PP_8          = 8            # PP8

# CodeRate - Code rate
    DVBT2_COD_1_2       = 0            # 1/2
    DVBT2_COD_3_5       = 1            # 3/5
    DVBT2_COD_2_3       = 2            # 2/3
    DVBT2_COD_3_4       = 3            # 3/4
    DVBT2_COD_4_5       = 4            # 4/5 not for T2 lite
    DVBT2_COD_5_6       = 5            # 5/6 not for T2 lite
    DVBT2_COD_1_3       = 6            # 1/3 only for T2 lite
    DVBT2_COD_2_5       = 7            # 2/5 only for T2 lite

# FefSignal - Type of signal generated during the FEF period
    DVBT2_FEF_ZERO      = 0            # Use zero I/Q samples during FEF
    DVBT2_FEF_1K_OFDM   = 1            # 1K OFDM symbols with 852 active
                                       # carriers containing BPSK symbols
                                       # (same PRBS as the T2 dummy cells,
                                       # not reset between symbols)
    DVBT2_FEF_1K_OFDM_384 = 2          # 1K OFDM symbols with 384 active
                                       #  carriers containing BPSK symbols

# PlpConstel and L1Constel - Modulation constellation
    DVBT2_BPSK          = 0            # BPSK
    DVBT2_QPSK          = 1            # QPSK
    DVBT2_QAM16         = 2            # 16-QAM
    DVBT2_QAM64         = 3            # 64-QAM
    DVBT2_QAM256        = 4            # 256-QAM

# Type - PLP type
    DVBT2_PLP_TYPE_COMM = 0            # Common PLP
    DVBT2_PLP_TYPE_1    = 1            # PLP type 1
    DVBT2_PLP_TYPE_2    = 2            # PLP type 2

# FecType - PLP FEC type
    DVBT2_LDPC_16K      = 0            # 16K LDPC
    DVBT2_LDPC_64K      = 1            # 64K LDPC

# TimeIlType - Time interleaving type
    DVBT2_IL_ONETOONE   = 0            # Interleaving frame in one T2 frame
    DVBT2_IL_MULTI      = 1            # Interleaving frame in multiple frames

# TimeStamping - Type of timestamps in T2MI
    DVBT2MI_TIMESTAMP_NULL = 0         # No timestamping
    DVBT2MI_TIMESTAMP_REL  = 1         # Relative timestamps. Use Subseconds
    DVBT2MI_TIMESTAMP_ABS  = 2         # Absolute timestamps. Use T2miUtco,
                                       # SecSince2000, Subseconds,

# T2Version - DVB-T2 specification version
    DVBT2_VERSION_1_1_1  = 0           # DVB-T2 version 1.1.1
    DVBT2_VERSION_1_2_1  = 1           # DVB-T2 version 1.2.1
    DVBT2_VERSION_1_3_1  = 2           # DVB-T2 version 1.3.1

# T2Profile - DVB-T2 profile
    DVBT2_PROFILE_BASE  = 0         
    DVBT2_PROFILE_LITE  = 1            # Requires DVB-T2 version 1.3.1

# BiasBalancing
    DVBT2_BIAS_BAL_OFF  = 0            # No L1 bias compensation
    DVBT2_BIAS_BAL_ON   = 1            # Modify L1 reserved fields and L1 ext.
                                       # field padding to compensate L1 bias
# GseLabelType - DVB-T2 GSE Label size
    DVBT2_GSE_LABEL_6BYTE  = 0        # 6 Byte GSE label
    DVBT2_GSE_LABEL_3BYTE  = 1        # 3 Byte GSE label
    DVBT2_GSE_LABEL_NONE   = 2        # No GSE label

    TXSIG_FEF_LEN_MIN  = 162212       # Min. FEF length for FEF TX sgnalling


# =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ ISDB-T Parameters +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+

# PID-to-layer mapping
    ISDBT_LAYER_A       = 1
    ISDBT_LAYER_B       = 2
    ISDBT_LAYER_C       = 4

# IsdbtPars.BType - Broadcast type
    ISDBT_BTYPE_TV      = 0            # 1/3/13-segment TV broadcast
    ISDBT_BTYPE_RAD1    = 1            # 1-segment radio broadcast
    ISDBT_BTYPE_RAD3    = 2            # 3-segment radio broadcast

# IsdbtPars.Guard - Guard interval
    ISDBT_GUARD_1_32    = 0
    ISDBT_GUARD_1_16    = 1
    ISDBT_GUARD_1_8     = 2
    ISDBT_GUARD_1_4     = 3

# IsdbtLayerPars.Modulation - Modulation type
    ISDBT_MOD_DQPSK     = 0
    ISDBT_MOD_QPSK      = 1
    ISDBT_MOD_QAM16     = 2
    ISDBT_MOD_QAM64     = 3

# IsdbtLayerPars.CodeRate - Code rate
    ISDBT_RATE_1_2      = 0
    ISDBT_RATE_2_3      = 1
    ISDBT_RATE_3_4      = 2
    ISDBT_RATE_5_6      = 3
    ISDBT_RATE_7_8      = 4

# ISDB-T - Number of Segments
    ISDBT_SEGM_1        = 0x00000001
    ISDBT_SEGM_3        = 0x00000003
    ISDBT_SEGM_13       = 0x0000000D
    ISDBT_SEGM_MSK      = 0x0000000F

# ISDB-T - Bandwidth
    ISDBT_BW_5MHZ       = 0x00000010
    ISDBT_BW_6MHZ       = 0x00000020
    ISDBT_BW_7MHZ       = 0x00000030
    ISDBT_BW_8MHZ       = 0x00000040
    ISDBT_BW_MSK        = 0x000000F0

# ISDB-T - Sample Rate
    ISDBT_SRATE_1_1     = 0x00000100
    ISDBT_SRATE_1_2     = 0x00000200
    ISDBT_SRATE_1_4     = 0x00000300
    ISDBT_SRATE_1_8     = 0x00000400
    ISDBT_SRATE_27_32   = 0x00000500
    ISDBT_SRATE_135_64  = 0x00000600
    ISDBT_SRATE_MSK     = 0x00000F00

# ISDB-T - Sub Channel
    ISDBT_SUBCH_MSK     = 0x0003F000
    ISDBT_SUBCH_SHIFT   = 12

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+ Other Modulation Parameters +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

# Modulation types
    MOD_DVBS_QPSK       = 0            # Native DVB-S on DTA-107
    MOD_DVBS_BPSK       = 1
    MOD_QAM4            = 3
    MOD_QAM16           = 4
    MOD_QAM32           = 5
    MOD_QAM64           = 6
    MOD_QAM128          = 7
    MOD_QAM256          = 8
    MOD_DVBT            = 9
    MOD_ATSC            = 10
    MOD_DVBT2           = 11
    MOD_ISDBT           = 12
    MOD_ISDBS           = 13
    MOD_IQDIRECT        = 15
    MOD_IQ_2131         = 16           # DTA-2131 specific (de)modulation
    MOD_DVBS2_QPSK      = 32
    MOD_DVBS2_8PSK      = 33
    MOD_DVBS2_16APSK    = 34
    MOD_DVBS2_32APSK    = 35
    MOD_DVBS2_L3        = 36     
    MOD_DVBS2           = 37
    MOD_DMBTH           = 48
    MOD_ADTBT           = 49
    MOD_CMMB            = 50
    MOD_T2MI            = 51
    MOD_DVBC2           = 52   
    MOD_DAB             = 53   
    MOD_QAM_AUTO        = 54   
    MOD_ATSC_MH         = 55
    MOD_ISDBTMM         = 56
# Modulation types DVB-S2X specific
    MOD_S2X_QPSK_VLSNR  = 57           # DVB-S2X, QPSK, very low SNR
    MOD_S2X_BPSK_VLSNR  = 58           # DVB-S2X, BPSK, very low SNR
    MOD_S2X_BPSK_S_VLSNR= 59           # DVB-S2X, BPSK-S, very low SNR
    MOD_S2X_8APSK_L     = 60           # DVB-S2X, 8APSK-L
    MOD_S2X_16APSK_L    = 61           # DVB-S2X, 16APSK-L
    MOD_S2X_32APSK_L    = 62           # DVB-S2X, 32APSK-L
    MOD_S2X_64APSK      = 63           # DVB-S2X, 64APSK
    MOD_S2X_64APSK_L    = 64           # DVB-S2X, 64APSK-L
    MOD_S2X_128APSK     = 65           # DVB-S2X, 128APSK
    MOD_S2X_256APSK     = 66           # DVB-S2X, 256APSK-L
    MOD_S2X_256APSK_L   = 67           # DVB-S2X, 256APSK
    MOD_DVBS2X_L3       = 68           # L3 modulation with S2X support
    MOD_ATSC3           = 69           # ATSC 3.0
    MOD_ISDBS3          = 70           # ISDB-S3
    MOD_DRM             = 71           # DRM(+)
    MOD_ATSC3_STLTP     = 72           # ATSC 3.0 STLTP
    MOD_TYPE_AUTO       = -1           # Auto detect modulation type
    MOD_TYPE_UNK        = -1           # Unknown modulation type

# Modulation parameters - Common - ParXtra2
    MOD_SYMRATE_AUTO    = -1           # Auto detect symbol rate
    MOD_SYMRATE_UNK     = -1           # Symbol rate if unknown

# Modulation parameters - ATSC - ParXtra0
    MOD_ATSC_VSB8       = 0x00000000   # 8-VSB, 10.762MBd, 19.392Mbps
    MOD_ATSC_VSB16      = 0x00000001   # 16-VSB, 10.762MBd, 38.785Mbps
    MOD_ATSC_VSB_AUTO   = 0x00000003   # Auto detect constellation
    MOD_ATSC_VSB_UNK    = 0x00000003   # Unknown constellation
    MOD_ATSC_VSB_MSK    = 0x00000003   # Constellation mask

# Modulation parameters - DTMB - Bandwidth
    MOD_DTMB_5MHZ       = 0x00000001
    MOD_DTMB_6MHZ       = 0x00000002
    MOD_DTMB_7MHZ       = 0x00000003
    MOD_DTMB_8MHZ       = 0x00000004
    MOD_DTMB_BW_AUTO    = 0x0000000F   # Auto detect
    MOD_DTMB_BW_UNK     = 0x0000000F   # Unknown
    MOD_DTMB_BW_MSK     = 0x0000000F

# Modulation parameters - DTMB - Code rate
    MOD_DTMB_0_4        = 0x00000100   # 0.4
    MOD_DTMB_0_6        = 0x00000200   # 0.6
    MOD_DTMB_0_8        = 0x00000300   # 0.8
    MOD_DTMB_RATE_AUTO  = 0x00000F00   # Auto detect
    MOD_DTMB_RATE_UNK   = 0x00000F00   # Unknown
    MOD_DTMB_RATE_MSK   = 0x00000F00   # Mask

# Modulation parameters - DTMB - Constellation
    MOD_DTMB_QAM4NR     = 0x00001000   # 4-QAM-NR
    MOD_DTMB_QAM4       = 0x00002000   # 4-QAM
    MOD_DTMB_QAM16      = 0x00003000   # 16-QAM
    MOD_DTMB_QAM32      = 0x00004000   # 32-QAM
    MOD_DTMB_QAM64      = 0x00005000   # 64-QAM
    MOD_DTMB_CO_AUTO    = 0x0000F000   # Auto detect
    MOD_DTMB_CO_UNK     = 0x0000F000   # Unknown
    MOD_DTMB_CO_MSK     = 0x0000F000   # Mask

# Modulation parameters - DTMB - Frame header mode
    MOD_DTMB_PN420      = 0x00010000   # PN420
    MOD_DTMB_PN595      = 0x00020000   # PN595
    MOD_DTMB_PN945      = 0x00030000   # PN945
    MOD_DTMB_PN_AUTO    = 0x000F0000   # Auto detect
    MOD_DTMB_PN_UNK     = 0x000F0000   # Unknown
    MOD_DTMB_PN_MSK     = 0x000F0000   # Mask

# Modulation parameters - DTMB - Interleaver mode
    MOD_DTMB_IL_1       = 0x00100000   # Interleaver mode 1: B=54, M=240
    MOD_DTMB_IL_2       = 0x00200000   # Interleaver mode 2: B=54, M=720
    MOD_DTMB_IL_NONE    = 0x00300000   # Interleaver mode none (non-standard)
    MOD_DTMB_IL_AUTO    = 0x00F00000   # Auto detect
    MOD_DTMB_IL_UNK     = 0x00F00000   # Unknown
    MOD_DTMB_IL_MSK     = 0x00F00000   # Mask

# Modulation parameters - DTMB - pilots
    MOD_DTMB_NO_PILOTS  = 0x01000000   # No pilots
    MOD_DTMB_PILOTS     = 0x02000000   # Pilots, C=1 only
    MOD_DTMB_PIL_AUTO   = 0x0F000000   # Auto detect
    MOD_DTMB_PIL_UNK    = 0x0F000000   # Unknown
    MOD_DTMB_PIL_MSK    = 0x0F000000   # Mask

# Modulation parameters - DTMB - Use frame numbering
    MOD_DTMB_NO_FRM_NO  = 0x10000000   # No frame numbering
    MOD_DTMB_USE_FRM_NO = 0x20000000   # Use frame numbers
    MOD_DTMB_UFRM_AUTO  = 0xF0000000   # Auto detect
    MOD_DTMB_UFRM_UNK   = 0xF0000000   # Unknown
    MOD_DTMB_UFRM_MSK   = 0xF0000000   # Mask

# Modulation parameters - DVB-S, DVB-S2
    MOD_1_2             = 0x0          # Code rate 1/2
    MOD_2_3             = 0x1          # Code rate 2/3
    MOD_3_4             = 0x2          # Code rate 3/4
    MOD_4_5             = 0x3          # Code rate 4/5
    MOD_5_6             = 0x4          # Code rate 5/6
    MOD_6_7             = 0x5          # Code rate 6/7
    MOD_7_8             = 0x6          # Code rate 7/8
    MOD_1_4             = 0x7          # Code rate 1/4
    MOD_1_3             = 0x8          # Code rate 1/3
    MOD_2_5             = 0x9          # Code rate 2/5
    MOD_3_5             = 0xA          # Code rate 3/5
    MOD_8_9             = 0xB          # Code rate 8/9
    MOD_9_10            = 0xC          # Code rate 9/10
    MOD_CR_AUTO         = 0xF          # Auto detect code rate
    MOD_CR_UNK          = 0xF          # Unknown code rate
#Coderates DVB-S2X specific
    MOD_1_5             = 0x10         # Code rate 1/5
    MOD_2_9             = 0x11         # Code rate 2/9
    MOD_11_45           = 0x12         # Code rate 11/45
    MOD_4_15            = 0x13         # Code rate 4/15
    MOD_13_45           = 0x14         # Code rate 13/45
    MOD_14_45           = 0x15         # Code rate 14/45
    MOD_9_20            = 0x16         # Code rate 9/20
    MOD_7_15            = 0x17         # Code rate 7/15
    MOD_8_15            = 0x18         # Code rate 8/15
    MOD_11_20           = 0x19         # Code rate 11/20
    MOD_5_9             = 0x1A         # Code rate 5/9
    MOD_26_45           = 0x1B         # Code rate 26/45
    MOD_28_45           = 0x1C         # Code rate 28/45
    MOD_23_36           = 0x1D         # Code rate 23/36
    MOD_29_45           = 0x1E         # Code rate 29/45
    MOD_31_45           = 0x1F         # Code rate 31/45
    MOD_25_36           = 0x20         # Code rate 25/36
    MOD_32_45           = 0x21         # Code rate 32/45
    MOD_13_18           = 0x22         # Code rate 13/18
    MOD_11_15           = 0x23         # Code rate 11/15
    MOD_7_9             = 0x24         # Code rate 7/9
    MOD_77_90           = 0x25         # Code rate 77/90

# Modulation parameters - DVB-S, DVB-S2 - ParXtra1
    MOD_S_S2_SPECNONINV  =0x00         # No spectrum inversion detected
    MOD_S_S2_SPECINV     =0x10         # Spectrum inversion detected
    MOD_S_S2_SPECINV_AUTO=0x30         # Auto detect spectral inversion
    MOD_S_S2_SPECINV_UNK =0x30         # Spectral inversion is unknown
    MOD_S_S2_SPECINV_MSK =0x30         # Mask for spectrum inversion field

# Modulation parameters - DVB-S2 - ParXtra1 - Pilots
    MOD_S2_NOPILOTS     = 0x00         # Pilots disabled
    MOD_S2_PILOTS       = 0x01         # Pilots enabled
    MOD_S2_PILOTS_AUTO  = 0x03         # Auto detect pilots
    MOD_S2_PILOTS_UNK   = 0x03         # State of pilots unknown
    MOD_S2_PILOTS_MSK   = 0x03         # Mask for pilots field

# Modulation parameters - DVB-S2 - ParXtra1 - FEC frame length
    MOD_S2_LONGFRM      = 0x00         # Long FECFRAME
    MOD_S2_MEDIUMFRM    = 0x04         # Medium FECFRAME
    MOD_S2_SHORTFRM     = 0x08         # Short FECFRAME
    MOD_S2_FRM_AUTO     = 0x0C         # Auto detect frame size
    MOD_S2_FRM_UNK      = 0x0C         # Frame size unknown
    MOD_S2_FRM_MSK      = 0x0C         # Mask for FECFRAME field

# Modulation parameters - DVB-S2(X) - ParXtra1 - Constellation amplitude for 16-, 32-APSK
    MOD_S2_CONST_AUTO   = 0x00         # Default constellation amplitude
    MOD_S2_CONST_E_1    = 0x40         # E=1; Average symbol energy is constant
    MOD_S2_CONST_R_1    = 0x80         # R=1; Radius of outer ring is constant
    MOD_S2_CONST_MSK    = 0xC0         # Mask for constellation shape

# Modulation parameters - DVB-S(X) - ParXtra1 - Modulator to be used for DVB-S2
    MOD_S2_MOD_MSK      = 0x30000      # Mask for modulator usage
    MOD_S2_MOD_AUTO     = 0x00000      # Modulator depends on modcod and rolloff
    MOD_S2_MOD_S2X      = 0x10000      # DVB-S2X modulator is used for DVB-S2

# Modulation parameters - ISDB-S - Input stream
    MOD_ISDBS_STREAMTYPE_RAW  = 0x00    # Raw stream with TMCC in sync bytes
    MOD_ISDBS_STREAMTYPE_B15  = 0x01    # TMCC data following each TS packet
    MOD_ISDBS_STREAMTYPE_AUTO = 0x07    # Default (raw) isdb-s input stream
    MOD_ISDBS_STREAMTYPE_MASK = 0x07    # Mask for input stream type

# Modulation parameters - DVB-T - Bandwidth
    MOD_DVBT_5MHZ       = 0x00000001
    MOD_DVBT_6MHZ       = 0x00000002
    MOD_DVBT_7MHZ       = 0x00000003
    MOD_DVBT_8MHZ       = 0x00000004
    MOD_DVBT_BW_UNK     = 0x0000000F   # Unknown bandwidth
    MOD_DVBT_BW_MSK     = 0x0000000F

# Modulation parameters - DVB-T - Constellation
    MOD_DVBT_QPSK       = 0x00000010
    MOD_DVBT_QAM16      = 0x00000020
    MOD_DVBT_QAM64      = 0x00000030
    MOD_DVBT_CO_AUTO    = 0x000000F0   # Auto detect constellation
    MOD_DVBT_CO_UNK     = 0x000000F0   # Unknown constellation
    MOD_DVBT_CO_MSK     = 0x000000F0

# Modulation parameters - DVB-T - Guard interval
    MOD_DVBT_G_1_32     = 0x00000100
    MOD_DVBT_G_1_16     = 0x00000200
    MOD_DVBT_G_1_8      = 0x00000300
    MOD_DVBT_G_1_4      = 0x00000400
    MOD_DVBT_GU_AUTO    = 0x00000F00   # Auto detect guard interval
    MOD_DVBT_GU_UNK     = 0x00000F00   # Unknown guard interval
    MOD_DVBT_GU_MSK     = 0x00000F00

# DVB-T TPS information - DVB-T Hierarchical layer
    MOD_DVBT_HARCHY_NONE= 0x00000000
    MOD_DVBT_HARCHY_A1  = 0x01000000
    MOD_DVBT_HARCHY_A2  = 0x02000000
    MOD_DVBT_HARCHY_A4  = 0x03000000
    MOD_DVBT_HARCHY_MSK = 0x0F000000
# Modulation parameters - DVB-T - Interleaver mode
    MOD_DVBT_INDEPTH    = 0x00001000
    MOD_DVBT_NATIVE     = 0x00002000
    MOD_DVBT_IL_AUTO    = 0x0000F000   # Auto detect interleaver depth
    MOD_DVBT_IL_UNK     = 0x0000F000   # Unknown interleaver depth
    MOD_DVBT_IL_MSK     = 0x0000F000

# Modulation parameters - DVB-T - FFT size
    MOD_DVBT_2K         = 0x00010000
    MOD_DVBT_4K         = 0x00020000
    MOD_DVBT_8K         = 0x00030000
    MOD_DVBT_MD_AUTO    = 0x000F0000   # Auto detect mode
    MOD_DVBT_MD_UNK     = 0x000F0000   # Unknown mode
    MOD_DVBT_MD_MSK     = 0x000F0000

# Modulation parameters - DVB-T - s48
    MOD_DVBT_S48_OFF    = 0x00000000
    MOD_DVBT_S48        = 0x00100000
    MOD_DVBT_S48_MSK    = 0x00100000

# Modulation parameters - DVB-T - s49
    MOD_DVBT_S49_OFF    = 0x00000000
    MOD_DVBT_S49        = 0x00200000
    MOD_DVBT_S49_MSK    = 0x00200000

# Modulation parameters - DVB-T - s48s49
    MOD_DVBT_ENA4849    = 0x00000000
    MOD_DVBT_DIS4849    = 0x00400000
    MOD_DVBT_4849_MSK   = 0x00400000

# Modulation parameters - IQ - ParXtra0
    MOD_INTERPOL_RAW    = 0            # Raw mode, no interpolation
    MOD_INTERPOL_OFDM   = 1            # Use OFDM interpolation
    MOD_INTERPOL_QAM    = 2            # Use QAM interpolation

# Modulation parameters - IQ - ParXtra2 Packing
    MOD_IQPCK_AUTO      = 0x00000000   # Auto IQ-sample packin
    MOD_IQPCK_NONE      = 0x00000001   # No IQ-sample packing
    MOD_IQPCK_PCKD      = 0x00000002   # IQ-samples are already packed
    MOD_IQPCK_12B       = 0x00000003   # IQ-samples packed in 12-bit
    MOD_IQPCK_10B       = 0x00000004   # IQ-samples packed in 10-bit
    MOD_IQPCK_UNK       = 0x000000FF   # Unknown (= use auto)
    MOD_IQPCK_MSK       = 0x000000FF

# Modulation parameters - Roll-off factor ParXtra1 (DVB-S2), ParXtra2 (IQ) and
#                         Low pass filters ParXtra2 (IQ) 
    MOD_ROLLOFF_AUTO    = 0x00000000   # Default roll-off factor
    MOD_ROLLOFF_NONE    = 0x00000100   # No roll-off
    MOD_ROLLOFF_3       = 0x00000200   # 3% roll-off for ISDB-S3
    MOD_ROLLOFF_5       = 0x00000300   # 5% roll-off for DVB-S2X
    MOD_ROLLOFF_10      = 0x00000400   # 10% roll-off for DVB-S2X
    MOD_ROLLOFF_15      = 0x00000500   # 15% roll-off for DVB-S2X
    MOD_ROLLOFF_20      = 0x00000600   # 20% roll-off for DVB-S2
    MOD_ROLLOFF_25      = 0x00000700   # 25% roll-off for DVB-S2
    MOD_ROLLOFF_35      = 0x00000800   # 35% roll-off for DVB-S/S2
# Pre-defined low pass filters
    MOD_LPF_0_614       = 0x00000900   # Passband up to samplerate*0.614,
                                         # used for 2MHz CMMB
    MOD_LPF_0_686       = 0x00000A00   # Passband up to samplerate*0.686,
                                         # used for ISDB-T/Tmm/Tsb
    MOD_LPF_0_754       = 0x00000B00   # Passband up to samplerate*0.754,
                                         # used for 8MHz CMMB, DAB
    MOD_LPF_0_833       = 0x00000C00   # Passband up to samplerate*0.833,
                                         # used for DVB-C2/T/T2
    MOD_LPF_0_850       = 0x00000D00   # Passband up to samplerate*0.850,
                                         # used for DVB-T2 extended bandwidth and
                                         # ATSC 3.0
    MOD_ROLLOFF_UNK     = 0x0000FF00   # Unknown (= use default)
    MOD_ROLLOFF_MSK     = 0x0000FF00

# Modulation parameters - DVB-T2-MI - ParXtra0 used for T2-MI bitrate

# Modulation parameters - DVB-T2-MI - ParXtra1
    MOD_T2MI_PID1_MSK   = 0x1FFF
    MOD_T2MI_PID1_SHFT  = 0
    MOD_T2MI_PID2_MSK   = 0x1FFF0000
    MOD_T2MI_PID2_SHFT  = 16
    MOD_T2MI_MULT_DIS   = 0x00000000   # Single Profile
    MOD_T2MI_MULT_ENA   = 0x20000000   # Multi Profile
    MOD_T2MI_MULT_MSK   = 0x20000000   # Multi Profile mask

# Modulation parameters - QAM - ParXtra0 - J.83 Annex
    MOD_J83_MSK         = 0x000F
    MOD_J83_UNK         = 0x000F       # Unknown annex
    MOD_J83_AUTO        = 0x000F       # Auto detect annex
    MOD_J83_A           = 0x0002       # J.83 annex A (DVB-C)
    MOD_J83_B           = 0x0003       # J.83 annex B (\93American QAM\94)
    MOD_J83_C           = 0x0001       # J.83 annex C (\93Japanese QAM\94)

# Modulation parameters - QAM - ParXtra1 - QAM-B interleaver mode
    MOD_QAMB_I128_J1D   = 0x1
    MOD_QAMB_I64_J2     = 0x3
    MOD_QAMB_I32_J4     = 0x5
    MOD_QAMB_I16_J8     = 0x7
    MOD_QAMB_I8_J16     = 0x9
    MOD_QAMB_I128_J1    = 0x0
    MOD_QAMB_I128_J2    = 0x2
    MOD_QAMB_I128_J3    = 0x4
    MOD_QAMB_I128_J4    = 0x6
    MOD_QAMB_I128_J5    = 0x8
    MOD_QAMB_I128_J6    = 0xA
    MOD_QAMB_I128_J7    = 0xC
    MOD_QAMB_I128_J8    = 0xE
    MOD_QAMB_IL_UNK     = 0xF          # Unknown interleaver mode
    MOD_QAMB_IL_AUTO    = 0xF          # Auto detect interleaver mode
    MOD_QAMB_IL_MSK     = 0xF

# =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+ IP Parameters +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+

# IP protocol (IpPars::Protocol)
    PROTO_UDP           = 0            # UDP
    PROTO_RTP           = 1            # RTP

# IP error correction modes (IpPars::m_FecMode)
    FEC_DISABLE         = 0            # No FEC
    FEC_2D              = 1            # FEC reconstruction
    

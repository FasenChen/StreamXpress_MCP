# *#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#* SPRC_constants.py *#*#*#*#*#*#*#*#*# (C) 2024 DekTec
#
#
""" This file contains the SPRC definitions that are used in the SPRC functions. 
    See also the SpRcApi documentation.
    Based on SpRcApi v1.11.0.19.
    """

class SPRC:
    # Capability flags
    CAP_ADJLVL    = 0x01            # Adjustable output level
    CAP_CM        = 0x02            # Supports channel modelling
    CAP_DIGIQ     = 0x04            # Has a digital IQ output
    CAP_IF        = 0x08            # Has an IF output
    CAP_LBAND     = 0x10            # Can upconvert to L-Band 950 ..  2150 MHz
    CAP_UHF       = 0x20            # Can upconvert to UHF Band 400 .. 862 MHz
    CAP_VHF       = 0x40            # Can upconvert to VHF Band 47 .. 470 MHz
    CAP_SFN       = 0x80            # Supports Single Frequency Network operation

    # Channel Modelling transmission path types
    CONSTANT_DELAY    = 0           # Constant phase
    CONSTANT_DOPPLER  = 1           # Constant frequency shift
    RAYLEIGH_JAKES    = 2           # Rayleigh fading with Jakes power spectral 
                                    # density (mobile path model)
    RAYLEIGH_GAUSSIAN = 3           # Rayleigh fading with Gaussian power spectral
                                    # density (ionospheric path model)

    # Conditions
    COND_STOPPED      = 1           # Player is in stopped state

    # DVB-T2 follow modes
    T2_FOLLOW_OFF     = 0           # No following
    T2_FOLLOW_OPT1    = 1           # Follow optimum1
    T2_FOLLOW_OPT2    = 2           # Follow optimum2

    # File type
    FTYPE_SDSDI       = 1           # SD-SDI

    # Loop-adaptation flags
    LOOP_CC           = 1           # Adapt continuity counters
    LOOP_PCR          = 2           # Adapt PCR
    LOOP_TDT          = 4           # Adapt TDT
    LOOP_WRAP         = 8           # Auto wrap-around

    # TDT/TOT adaptation mode
    TDT_ADAPT_NOT_1ST_LOOP  = 1     # Adapt TDT after fist loop
    TDT_ADAPT_CURRENT_UTC   = 2     # Use current UTC time
    TDT_ADAPT_CURRENT_JST   = 3     # Use current JST time
    TDT_ADAPT_USE_SPECIFIED = 4     # Use specified time

    # Modulation standards
    MOD_ADTBT        =  0           # ADTB-T
    MOD_ATSC         =  1           # ATSC VSB
    MOD_CMMB         =  2           # CMMB
    MOD_DTMB         =  3           # DTMB
    MOD_DVBH         =  4           # DVB-H
    MOD_DVBS         =  5           # DVB-S
    MOD_DVBS2        =  6           # DVB-S2
    MOD_DVBT         =  7           # DVB-T
    MOD_DVBT2        =  8           # DVB-T2
    MOD_DVBT2MI      =  9           # DVB T2-MI
    MOD_IQ           = 10           # IQ
    MOD_ISDBS        = 11           # ISDB-S
    MOD_ISDBT        = 12           # ISDB-T
    MOD_J83A         = 13           # J.83 annex A (DVB-C)
    MOD_J83B         = 14           # J.83 annex B ("American QAM")
    MOD_J83C         = 15           # J.83 annex C ("Japanese DVB-C")
    MOD_DAB          = 16           # DAB
    MOD_ATSC_MH      = 17           # ATSC-MH
    MOD_S2L3         = 18           # DVB-S2 L3
    MOD_DVBS2X       = 19           # DVB-S2X
    MOD_ISDBS3       = 20           # ISDB-S3
    MOD_DRM          = 21           # DRM
    MOD_ATSC3_STLTP  = 22           # ATSC 3.0 STLTP
    MOD_DVBS2X_GSELITEHEM = 23      # DVB-S2X GSE-Lite HEM

    # Output type flags
    OTYPE_ASI   = 0x00001           # DVB-ASI
    OTYPE_ATSC  = 0x00002           # ATSC (VSB) modulation
    OTYPE_CMMB  = 0x00004           # CMMB modulation
    OTYPE_DTMB  = 0x00008           # DTMB modulation
    OTYPE_DVBS  = 0x00010           # DVB-S modulation
    OTYPE_DVBS2 = 0x00020           # DVB-S.2 modulation
    OTYPE_DVBT  = 0x00040           # DVB-T modulation, includes DVB-H
    OTYPE_DVBT2 = 0x00080           # DVB-T2 modulation
    OTYPE_DVBT2MI=0x00100           # DVB T2-MI
    OTYPE_IQ    = 0x00200           # IQ
    OTYPE_ISDBS = 0x00400           # ISDB-S modulation
    OTYPE_ISDBT = 0x00800           # ISDB-T modulation
    OTYPE_QAM_A = 0x01000           # QAM modulation, ITU-T J.83 Annex A (DVB-C)
    OTYPE_QAM_B = 0x02000           # QAM modulation, ITU-T J.83 Annex B (US)
    OTYPE_QAM_C = 0x04000           # QAM modulation, ITU-T J.83 Annex C (Japan)
    OTYPE_SDSDI = 0x08000           # Standard-definition SDI
    OTYPE_SPI   = 0x10000           # DVB-SPI
    OTYPE_TSOIP = 0x20000           # TS-over-IP
    OTYPE_ISDBS3= 0x40000           # ISDB-S3 modulation
    OTYPE_DRM   = 0x80000           # DRM modulation
    OTYPE_ATSC3_STLTP   = 0x100000  # ATSC 3.0 STLTP modulation


    # Port-in-use values
    PORT_UNUSED       = 0           # Port is not used
    PORT_CURR         = 1           # Port is currently selected play-out port
    PORT_USED         = 2           # Port is used by another application

    # Playout state
    STATE_PAUSE       = 0           # Pause
    STATE_PLAY        = 1           # Playing
    STATE_STOP        = 2           # Stop

    # Signal source
    FROM_FILE         = 0           # Use transport stream file as input
    TEST_GENERATOR    = 1           # Test signal generator provides data stream

    # SFN mode
    SFN_MODE_DISABLE  = 0           # SFN operation disabled
    SFN_MODE_1_PPS    = 1           # SFN operation using 1-PPS mode

    # GPS status
    GPS_STATUS_10MHZ_NO_SIGNAL = 0x00   # No 10MHz input reference signal
    GPS_STATUS_10MHZ_OUT_RANGE = 0x01   # 10MHz input signal is out of range
    GPS_STATUS_10MHZ_SYNC      = 0x02   # GPS time counter is frequency-locked to
                                        # the 10MHz clock input signal.
    GPS_STATUS_10MHZ_1PPS_SYNC = 0x03   # GPS-time is phase-locked 10MHz and 
                                        # to the 1pps input signal
    # SFN status
    SFN_STATUS_DISABLED=1           # Not operating in SFN-mode
    SFN_STATUS_HOLD    =2           # SFN playout is ready, waiting for a play command
                                    # and accompanying start time
    SFN_STATUS_STARTING=3           # SFN playout is starting, playout starts when 
                                    # the start time is reached
    SFN_STATUS_IN_SYNC =4           # SFN playout is running and in sync
    SFN_STATUS_ERROR   =5           # SFN playout error has occurred, restart of
                                    # SFN playout is necessary      
    # Test pattern generator
    TSG_TYPE_PRBS7       = 0        # PRBS-7 TS generator
    TSG_TYPE_PRBS15      = 1        # PRBS-15 TS generator
    TSG_TYPE_PRBS23      = 2        # PRBS-23 / O.151 TS generator
    TSG_TYPE_PRBS31      = 3        # PRBS-31 TS generator
    TSG_TYPE_TS_CNT      = 4        # DekTec internal
    TSG_TYPE_SDI_STATIC_NO_AUDIO = 5   # SDI generator (static pattern, no audio)
    TSG_TYPE_SDI_DYNAMIC_NO_AUDIO = 6  # SDI generator (dynamic pattern, no audio)
    TSG_TYPE_SDI_STATIC  = 7        # SDI generator (static pattern, video+audio)
    TSG_TYPE_SDI_DYNAMIC = 8        # SDI generator (dynamic pattern, video+audio)

    # Video standard
    VIDSTD_525I59_94    = 0x01
    VIDSTD_625I50       = 0x02
    VIDSTD_720P23_98    = 0x03
    VIDSTD_720P24       = 0x04
    VIDSTD_720P25       = 0x05
    VIDSTD_720P29_97    = 0x06
    VIDSTD_720P30       = 0x07
    VIDSTD_720P50       = 0x08
    VIDSTD_720P59_94    = 0x09
    VIDSTD_720P60       = 0x0A
    VIDSTD_1080I50      = 0x0B
    VIDSTD_1080I59_94   = 0x0C
    VIDSTD_1080I60      = 0x0D
    VIDSTD_1080P23_98   = 0x0E
    VIDSTD_1080P24      = 0x0F
    VIDSTD_1080P25      = 0x10
    VIDSTD_1080P29_97   = 0x11
    VIDSTD_1080P30      = 0x12
    VIDSTD_1080P50      = 0x13
    VIDSTD_1080P59_94   = 0x14
    VIDSTD_1080P60      = 0x15
    VIDSTD_1080PSF23_98 = 0x16
    VIDSTD_1080PSF24    = 0x17
    VIDSTD_1080PSF25    = 0x18
    VIDSTD_1080PSF29_97 = 0x19
    VIDSTD_1080PSF30    = 0x1A
    VIDSTD_1080P50B     = 0x1B
    VIDSTD_1080P59_94B  = 0x1C
    VIDSTD_1080P60B     = 0x1D
    VIDSTD_2160P23_98   = 0x1F
    VIDSTD_2160P24      = 0x20
    VIDSTD_2160P25      = 0x21
    VIDSTD_2160P29_97   = 0x22
    VIDSTD_2160P30      = 0x23
    VIDSTD_2160P50      = 0x24
    VIDSTD_2160P50B     = 0x25
    VIDSTD_2160P59_94   = 0x26
    VIDSTD_2160P59_94B  = 0x27
    VIDSTD_2160P60      = 0x28
    VIDSTD_2160P60B     = 0x29

    TSG_FLAG_SDI_FRM_CNT = 0x01

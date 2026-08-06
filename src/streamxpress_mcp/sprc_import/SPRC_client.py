# *#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#* SPRC_client.py *#*#*#*#*#*#*#*#*#*#* (C) 2024 DekTec
#

""" This file contains wrapper functions to use the SOAP-based SPRC interface, to control
    the StreamXpress. The functions have a similar signature as used in the C++ SpRcApi.
    See also the SpRcApi documentation.
    Based on SpRcApi v1.11.0.19.
    Requires zeep plug-in 4.2.1 (or higher).
"""

import zeep
import zeep.helpers
from pathlib import Path
import os
from dataclasses import dataclass, asdict
from collections import OrderedDict
import copy
from typing import Optional

from .SPRC_types import *

class SPRC_client:
    # Members
    _zeep_client: Optional[zeep.Client]
    _wsdl_file : str
    _wsdl_template: Optional[str]
    
    def __init__(self, wsdl_template: str | None = None):
        """ Constructor """
        self._zeep_client = None
        self._wsdl_file = ''
        self._wsdl_template = wsdl_template

    def cleanup(self) -> None:
        """ Cleans up zeep client and deletes temporary wsdl-file """
        if self._zeep_client :
            self.__zeep_client().service.CloseSession()
            self._zeep_client = None
        if os.path.isfile(self._wsdl_file):
            os.remove(Path(self._wsdl_file))
        self._wsdl_file = ''
    
    def open_session(self,  ip_port : int,  ip_host : str ='') -> None:
        """ Wrapper for OpenSession() """
        if self._zeep_client:
             raise SpRcException(SPRC_RESULT.E_SESSION_OPEN,'A session is already open')
        self._wsdl_file = self.__create_wsdl_file_for_service( ip_port, ip_host)
        self._zeep_client = zeep.Client(self._wsdl_file, port_name='SpRc')
        r = self.__zeep_client().service.OpenSession()
        sprc_result = self.__get_sprc_result(r)
        if sprc_result != SPRC_RESULT.OK:
            # Open failed, delete wsdl file
            if os.path.isfile(self._wsdl_file):
                os.remove(Path(self._wsdl_file))
            self._wsdl_file = ''
            # and destroy zeep client
            self._zeep_client = None
            raise SpRcException(sprc_result, 'Could not open session')

    def close_session(self) -> None:
        """ Wrapper for CloseSession() """
        # Cleanup zeep client
        sprc_result = SPRC_RESULT.OK
        if self._zeep_client:
            r = self.__zeep_client().service.CloseSession()
            sprc_result = self.__get_sprc_result(r)
            self._zeep_client = None
        # Delete temporary wsdl file
        if os.path.isfile(self._wsdl_file):
            os.remove(Path(self._wsdl_file))
        self._wsdl_file = ''
        # Check result
        if sprc_result != SPRC_RESULT.OK:
            raise SpRcException(sprc_result)

    def clear_errors(self) -> None:
        """ Wrapper for ClearErrors() """
        r = self.__zeep_client().service.ClearErrors()
        self.__check_sprc_result(r)

    def get_app_info(self) -> tuple[str, SpRcVersion]:
        """ Wrapper for GetAppInfo() 
            returns a tuple consisting of application name and version """
        r = self.__zeep_client().service.GetAppInfo()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r)
        rd.pop('SpRcResult')
        app_name = rd.pop('AppName')
        return (str(app_name), SpRcVersion(**rd))

    def get_remote_version(self) -> SpRcVersion:
        """ Wrapper for GetRemoteVersion() """
        r = self.__zeep_client().service.GetRemoteVersion()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r)
        rd.pop('SpRcResult')
        return SpRcVersion(**rd)
    
    def get_remote_dtapi_version(self) -> SpRcVersion:
        """ Wrapper for GetRemoteDtapiVersion() """
        r = self.__zeep_client().service.GetRemoteDtapiVersion()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r)
        rd.pop('SpRcResult')
        return SpRcVersion(**rd)
    
    def scan_ports(self) -> list[SpRcPortDesc]:
        """ Wrapper for ScanPorts() """
        r = self.__zeep_client().service.ScanPorts()
        self.__check_sprc_result(r)
        out = []
        rd = zeep.helpers.serialize_object(r)
        port_descs = rd['PortDescs']
        if port_descs:
           for element in port_descs['item']:
                out.append(SpRcPortDesc(**element))
        return out
    
    def select_port(self, serial:int, port:int, modulation=0) -> None:
        """ Wrapper for SelectPort() """
        r = self.__zeep_client().service.SelectPort(serial, port, modulation)
        self.__check_sprc_result(r)

    def select_dta_plus(self, use_dta_plus, serial) -> None:
        """ Wrapper for SelectDtaPlus() """
        r = self.__zeep_client().service.SelectDtaPlus(use_dta_plus, serial)
        self.__check_sprc_result(r)

    def get_asi_pars(self) ->  SpRcAsiPars:
        """ Wrapper for GetAsiPars() """
        r = self.__zeep_client().service.GetAsiPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['AsiPars'])
        return SpRcAsiPars(**rd)
    
    def get_channel_modelling_pars(self) -> SpRcCmPars:
        """ Wrapper for GetChannelModellingPars() """
        r = self.__zeep_client().service.GetChannelModellingPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['CmPars'])
        paths = rd.pop('Paths')
        cm_pars = SpRcCmPars(**rd, Paths=[])
        if paths:
           for element in paths['item']:
                cm_pars.Paths.append(SpRcCmPath(**element))
        return cm_pars

    def get_cmmb_pars(self) -> SpRcCmmbPars:
        """ Wrapper for GetCmmbPars() """
        r = self.__zeep_client().service.GetCmmbPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['CmmbPars'])
        return SpRcCmmbPars(**rd)
    
    def get_dvb_t2_group(self) -> SpRcDvbT2Group:
        """ Wrapper for GetDvbT2Group() """
        r = self.__zeep_client().service.GetDvbT2Group()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['DvbT2Group'])
        return SpRcDvbT2Group(**rd)
    
    def get_dvb_t2_pars(self) -> SpRcDvbT2Pars:
        """ Wrapper for GetDvbT2Pars() """
        r = self.__zeep_client().service.GetDvbT2Pars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['DvbT2Pars'])
        return SpRcDvbT2Pars(**rd)

    def get_hw_noise_pars(self) -> SpRcHwNoisePars:
        """ Wrapper for GetHwNoisePars() """
        r = self.__zeep_client().service.GetHwNoisePars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['HwNoisePars'])
        return SpRcHwNoisePars(**rd)

    def get_iq_gain(self) -> int:
        """ Wrapper for GetIqGain() """
        r = self.__zeep_client().service.GetIqGain()
        self.__check_sprc_result(r)
        return int(r['IqGain'])

    def get_isdb_t_pars(self) -> SpRcIsdbtPars:
        """ Wrapper for GetIsdbtPars() """
        r = self.__zeep_client().service.GetIsdbtPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['IsdbtPars'])
        layer_pars = rd.pop('LayerPars')
        pid_mapping = rd.pop('Pid2Layer')
        isdbt_pars = SpRcIsdbtPars(**rd, LayerPars=[], Pid2Layer={})
        if layer_pars:
            for element in layer_pars['item']:
                isdbt_pars.LayerPars.append(SpRcIsdbtLayerPars(**element))
        if pid_mapping:
            for element in pid_mapping['item']:
                isdbt_pars.Pid2Layer[element['Pid']] = element['Layer']
        return isdbt_pars
    
    def get_mod_pars(self) -> SpRcModPars:
        """ Wrapper for GetModPars() """
        r = self.__zeep_client().service.GetModPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['ModPars'])
        return SpRcModPars(**rd)

    def get_playout_info(self) -> SpRcPlayoutInfo:
        """ Wrapper for GetPlayoutInfo() """
        r = self.__zeep_client().service.GetPlayoutInfo()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['PlayoutInfo'])
        return SpRcPlayoutInfo(**rd)
    
    def get_playout_status(self) -> SpRcPlayoutStatus:
        """ Wrapper for GetPlayoutStatus() """
        r = self.__zeep_client().service.GetPlayoutStatus()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['PlayoutStatus'])
        return SpRcPlayoutStatus(**rd)

    def get_rf_pars(self) -> SpRcRfPars:
        """ Wrapper for GetRfPars() """
        r = self.__zeep_client().service.GetRfPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['RfPars'])
        return SpRcRfPars(**rd)
    
    def get_sfn_status(self) -> SpRcSfnStatus:
        """ Wrapper for GetSfnStatus() """
        r = self.__zeep_client().service.GetSfnStatus()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['SfnStatus'])
        return SpRcSfnStatus(**rd)
        
    def get_signal_source(self) -> int:
        """ Wrapper for GetSignalSource() """
        r = self.__zeep_client().service.GetSignalSource()
        self.__check_sprc_result(r)
        return int(r['SignalSource'])
    
    def get_spi_pars(self) -> SpRcSpiPars:
        """ Wrapper for GetSpiPars() """
        r = self.__zeep_client().service.GetSpiPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['SpiPars'])
        return SpRcSpiPars(**rd)
    
    def get_tdt_adapt_pars(self) -> SpRcTdtAdaptPars:
        """ Wrapper for GetTdtAdaptPars() """
        r = self.__zeep_client().service.GetTdtAdaptPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['TdtAdaptPars'])
        mode = int(rd['TdtAdaptMode'])
        date_time = SpRcDateTime(**(rd['TdtDateTime']))
        return SpRcTdtAdaptPars(TdtAdaptMode=mode, TdtDateTime=date_time)
    
    def get_tsg_pars(self) -> SpRcTsgPars:
        """ Wrapper for GetTsgPars() """
        r = self.__zeep_client().service.GetTsgPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['TsgPars'])
        return SpRcTsgPars(**rd)
    
    def get_tsoip_pars(self) -> SpRcTsoipPars:
        """ Wrapper for GetTsoipPars() """
        r = self.__zeep_client().service.GetTsoipPars()
        self.__check_sprc_result(r)
        rd = zeep.helpers.serialize_object(r['TsoipPars'])
        return SpRcTsoipPars(**rd)
    
    def get_use_nit(self) -> bool:
        """ Wrapper for GetUseNit() """
        r = self.__zeep_client().service.GetUseNit()
        self.__check_sprc_result(r)
        return bool(r['UseNit'])

    def normalise(self) -> None:
        """ Wrapper for Normalise() """
        r = self.__zeep_client().service.Normalise()
        self.__check_sprc_result(r)

    def open_channel_modelling_file(self, file : str) -> None:
        """ Wrapper for OpenChannelModellingFile() """
        r = self.__zeep_client().service.OpenChannelModellingFile(file)
        self.__check_sprc_result(r)

    def open_file(self, file : str) -> None:
        """ Wrapper for OpenFile() """
        r = self.__zeep_client().service.OpenFile(file)
        self.__check_sprc_result(r)

    def save_channel_modelling_settings(self, file : str) -> None:
        """ Wrapper for GetRemoteDtapiVersion() """
        r = self.__zeep_client().service.SaveChannelModellingSettings(file)
        self.__check_sprc_result(r)

    def save_settings(self, file : str) -> None:
        """ Wrapper for SaveSettings() """
        r = self.__zeep_client().service.SaveSettings(file)
        self.__check_sprc_result(r)

    def set_asi_pars(self, asi_pars : SpRcAsiPars) -> None:
        """ Wrapper for SetAsiPars() """
        r = self.__zeep_client().service.SetAsiPars(asdict(asi_pars))
        self.__check_sprc_result(r)

    def set_channel_modelling_pars(self, cm_pars : SpRcCmPars) -> None:
        """ Wrapper for SetChannelModellingPars() """
        zeep_cm_pars = self.__SpRcCmPars(
            CmEnable=cm_pars.CmEnable,
            AwgnEnable=cm_pars.AwgnEnable,
            PathsEnable = cm_pars.PathsEnable,
            Snr = cm_pars.Snr,
            Paths = OrderedDict([("item",copy.deepcopy(cm_pars.Paths))]))
        r = self.__zeep_client().service.SetChannelModellingPars(asdict(zeep_cm_pars))
        self.__check_sprc_result(r)

    def set_cmmb_pars(self, cmmb_pars : SpRcCmmbPars) -> None:
        """ Wrapper for SetCmmbPars() """
        r = self.__zeep_client().service.SetCmmbPars(asdict(cmmb_pars))
        self.__check_sprc_result(r)

    def set_dvb_t2_group(self, group : SpRcDvbT2Group) -> None:
        """ Wrapper for SetDvbT2Group() """
        r = self.__zeep_client().service.SetDvbT2Group(asdict(group))
        self.__check_sprc_result(r)

    def set_dvb_t2_pars(self, t2_pars : SpRcDvbT2Pars) -> None:
        """ Wrapper for SetDvbT2Pars() """
        r = self.__zeep_client().service.SetDvbT2Pars(asdict(t2_pars))
        self.__check_sprc_result(r)

    def set_hw_noise_pars(self, noise_pars : SpRcHwNoisePars) -> None:
        """ Wrapper for SetHwNoisePars() """
        r = self.__zeep_client().service.SetHwNoisePars(asdict(noise_pars))
        self.__check_sprc_result(r)
    
    def set_isdb_t_pars(self, isdb_t_pars : SpRcIsdbtPars) -> None:
        """ Wrapper for SetIsdbtPars() """
        # Convert dictionary into list
        pid_2_layer_list = []
        for key, value in isdb_t_pars.Pid2Layer.items():
            pid_2_layer_list.append(self.__SpRcPid2Layer(Pid=key, Layer=value))
        # Create 
        zeep_isdb_t_pars = self.__SpRcIsdbtPars(
            DoMux=isdb_t_pars.DoMux,
            BType=isdb_t_pars.BType,
            Mode=isdb_t_pars.Mode,
            Guard=isdb_t_pars.Guard,
            PartialRx=isdb_t_pars.PartialRx,
            Emergency=isdb_t_pars.Emergency,
            IipPid=isdb_t_pars.IipPid,
            LayerPars=OrderedDict([("item",copy.deepcopy(isdb_t_pars.LayerPars))]),
            Pid2Layer=OrderedDict([("item",pid_2_layer_list)]),
            LayerOther=isdb_t_pars.LayerOther,
            ParXtra0=isdb_t_pars.ParXtra0,
            Virtual13Segm=isdb_t_pars.Virtual13Segm)
        r = self.__zeep_client().service.SetIsdbtPars(asdict(zeep_isdb_t_pars))
        self.__check_sprc_result(r)

    def set_iq_gain(self, gain : int) -> None:
        """ Wrapper for SetIqGain() """
        r = self.__zeep_client().service.SetIqGain(gain)
        self.__check_sprc_result(r)
        
    def set_loop_flags(self, flags : int) -> None:
        """ Wrapper for SetLoopFlags() """
        r = self.__zeep_client().service.SetLoopFlags(flags)
        self.__check_sprc_result(r)
        
    def set_mod_pars(self, mod_pars : SpRcModPars) -> None:
        """ Wrapper for SetModPars() """
        r = self.__zeep_client().service.SetModPars(asdict(mod_pars))
        self.__check_sprc_result(r)
    
    def set_playout_state(self, state : int) -> None:
        """ Wrapper for SetPlayoutState() """
        r = self.__zeep_client().service.SetPlayoutState(state)
        self.__check_sprc_result(r)

    def set_playout_state_sfn(self, state : SpRcPlayoutSfnPars) -> None:
        """ Wrapper for SetPlayoutStateSfn() """
        r = self.__zeep_client().service.SetPlayoutStateSfn(asdict(state))
        self.__check_sprc_result(r)

    def set_remux(self, remux : bool) -> None:
        """ Wrapper for SetRemux() """
        remux_pars = SpRcRemuxPars(Remux = remux)
        r = self.__zeep_client().service.SetRemux(asdict(remux_pars))
        self.__check_sprc_result(r)

    def set_rf_pars(self, rf_pars : SpRcRfPars) -> None:
        """ Wrapper for SetRfPars() """
        r = self.__zeep_client().service.SetRfPars(asdict(rf_pars))
        self.__check_sprc_result(r)
    
    def set_sfn_mode(self, sfn_mode : int) -> None:
        """ Wrapper for SetSfnMode() """
        r = self.__zeep_client().service.SetSfnMode(sfn_mode)
        self.__check_sprc_result(r)
    
    def set_signal_source(self, source : int) -> None:
        """ Wrapper for SetSignalSource() """
        r = self.__zeep_client().service.SetSignalSource(source)
        self.__check_sprc_result(r)
        
    def set_spi_pars(self, rf_pars : SpRcSpiPars) -> None:
        """ Wrapper for SetSpiPars() """
        r = self.__zeep_client().service.SetSpiPars(asdict(rf_pars))
        self.__check_sprc_result(r)

    def set_sub_loop_pars(self, sub_loop_pars : SpRcSubLoopPars) -> None:
        """ Wrapper for SetSubLoopPars() """
        r = self.__zeep_client().service.SetSubLoopPars(asdict(sub_loop_pars))
        self.__check_sprc_result(r)
    
    def set_tdt_adapt_pars(self, tdt_adapt_pars : SpRcTdtAdaptPars) -> None:
        """ Wrapper for SetTdtAdaptPars() """
        r = self.__zeep_client().service.SetTdtAdaptPars(asdict(tdt_adapt_pars))
        self.__check_sprc_result(r)
    
    def set_tsg_pars(self, tsg_pars : SpRcTsgPars) -> None:
        """ Wrapper for SetTsgPars() """
        r = self.__zeep_client().service.SetTsgPars(asdict(tsg_pars))
        self.__check_sprc_result(r)

    def set_tsiop_pars(self, tsoip_pars : SpRcTsoipPars) -> None:
        """ Wrapper for SetTsoipPars() """
        r = self.__zeep_client().service.SetTsoipPars(asdict(tsoip_pars))
        self.__check_sprc_result(r)

    def set_ts_rate(self, ts_rate : int) -> None:
        """ Wrapper for SetTsRate() """
        r = self.__zeep_client().service.SetTsRate(ts_rate)
        self.__check_sprc_result(r)

    def set_use_nit(self, use_nit : bool) -> None:
        """ Wrapper for SetUseNit() """
        r = self.__zeep_client().service.SetUseNit(use_nit)
        self.__check_sprc_result(r)

    def show_window(self, show : bool) -> None:
        """ Wrapper for ShowWindow() """
        r = self.__zeep_client().service.ShowWindow(show)
        self.__check_sprc_result(r)

    def wait_for_condition(self, condition : int, timeout : int) -> None:
        """ Wrapper for WaitForCondition() """
        r = self.__zeep_client().service.WaitForCondition(condition, timeout)
        self.__check_sprc_result(r)

    # Private helper functions
        
    def __zeep_client(self) -> zeep.Client :
        """ Returns the zeep client, raises an exception if it is None"""
        if self._zeep_client:
            return self._zeep_client
        else :
            raise SpRcException(SPRC_RESULT.E_SESSION_NOT_OPEN)
        
    def __check_sprc_result(self, result) -> None:
        """ Checks the SPRC result, if not OK raises an exception"""
        sprc_result = self.__get_sprc_result(result)
        if sprc_result != SPRC_RESULT.OK :
            raise SpRcException(sprc_result)

    def __get_sprc_result(self, result) -> SPRC_RESULT:
        """ Retrieves the SPRC result"""
        if isinstance(result, int):
            if result == 0: return SPRC_RESULT.OK
            else: return SPRC_RESULT(result)
        else: return SPRC_RESULT(result['SpRcResult'])

    def __create_wsdl_file_for_service(self, ip_port: int, ip_host : str) -> str :
        """ Creates a temporary SPRC wsdl file containing the server location"""
        # If necessary set defaults
        if ip_host == '' :
            ip_host = 'http://localhost'

        # Must start with http://
        if not (ip_host.startswith('http://') or ip_host.startswith('https://')):
            raise SpRcException(SPRC_RESULT. E_SERVER_NOT_FOUND, 'Invalid host name')
        # Create filename from host name and port e.g. http://192.168.2.1 port 5000
        # gives filename SpRc_http_192_168_2_1_5000.wsdl
        name = ip_host.replace(':', '_').replace('/', '')
        name = name.replace('.', '_')
        # Remove any remaining special characters
        name = ''.join([char for char in name if char.isalnum() or char == '_'])
        name += '_' + str(ip_port)
        wsdl_file_name = f'SpRc_{name}.wsdl'
        # Create a new wsdl file derived from the original wsdl
        if self._wsdl_template:
            orig_wsdl = Path(self._wsdl_template)
        else:
            orig_wsdl = Path(__file__).parent.joinpath('SpRc.wsdl')
        if not os.path.isfile(orig_wsdl):
            raise SpRcException(SPRC_RESULT.E_FILE_CANT_FIND, 'SpRc.wsdl file not found')
        orig_wsdl_txt = orig_wsdl.read_text()
        # Set the address of the server
        new_wsdl_txt = orig_wsdl_txt.replace(
                '<SOAP:address location=\"http://localhost:80\"/>',
                f'<SOAP:address location=\"{ip_host}:{str(ip_port)}\"/>'
            )
        new_wsdl = Path(__file__).parent.joinpath(wsdl_file_name)
        new_wsdl.write_text(new_wsdl_txt)
        return str(new_wsdl)

    # Private types used for conversion to SOAP interface
    @dataclass 
    class __SpRcPid2Layer:
        Pid: int                        # Pid to map
        Layer: int                      # ISDBT_LAYER_X

    @dataclass 
    class __SpRcIsdbtLayerPars:
        NumSegments: int                # Number of segments
        Modulation: int                 # Modulation type
        CodeRate: int                   # Code rate
        TimeInterleave: int             # Time interleaving

    @dataclass 
    class __SpRcIsdbtPars:
        DoMux: bool                     # Hierarchical multiplexing, True or False
        BType: int                      # Broadcast type
        Mode: int                       # Transmission mode
        Guard: int                      # Guard interval
        PartialRx: int                  # Partial reception, 0 or 1
        Emergency: int                  # Switch-on control for emergency broadcast, 0 or 1
        IipPid: int                     # PID used for multiplexing IIP packet
        LayerPars: OrderedDict          # Layer-A/B/C parameters
        Pid2Layer: OrderedDict          # PID-to-layer mapping
        LayerOther: int                 # Other PIDs are mapped to this layer
        ParXtra0: int                   # Extra parameters encoded like ParXtra0 in
                                        # SetModControl for DTAPI.MOD_ISDBT
        Virtual13Segm: int              # Virtual 13-segment mode
    
    @dataclass 
    class __SpRcCmPars:
        CmEnable: bool                  # Enable Channel Modelling
        AwgnEnable: bool                # Enable noise injection
        PathsEnable: bool               # Enable transmission paths simulation
        Snr: float                      # Signal-to-noise ratio in dB
        Paths: OrderedDict              # List of transmission paths
from __future__ import annotations
import sys
import os
import shutil
import pathlib
from typing import Any, Union, Optional, Dict, Protocol, Sequence
from KKT_Library.LibLog import lib_logger as log
import numpy as np
from pathlib import Path
from KKT_Library.Integration.wrapper import IKSOCIntegration


def setupDLL(dst:Optional[str]=None):
    if dst is None:
        dst = pathlib.Path.cwd()
    dst_dir = pathlib.Path(dst).joinpath('KSOC_Libs')
    if not dst_dir.is_dir:
        pathlib.Path.mkdir(dst, exist_ok=True)
    src_dir = pathlib.Path(__file__).parent.joinpath('KSOC_Libs')
    shutil.copytree(src=src_dir, dst=dst_dir, dirs_exist_ok=True)
    
class KsocLib:
    def __init__(self, integration:str='CSharp'):
        log.info("__init__...")
        if integration.upper() == 'WIFI':
            from KKT_Library.Integration.WifiWrapper import WIFIIntegration
            self._integration:IKSOCIntegration = WIFIIntegration()
        elif integration.upper() == 'CSHARP':
            from KKT_Library.Integration.CSharpWrapper import KSOCIntegration
            self._integration:IKSOCIntegration = KSOCIntegration()
        else:
            raise ValueError(f'Integration type {integration} not support')
        self.lib_ver = self.getLibVersion()
        log.info('KKT lib was instanced')

    def __del__(self):
        log.info("Running cleanup...")
        try:
            log.info("Device Disconnecting...")
            self.closeDevice()
            log.info("Device Disconnected")
        except:
            pass

    def getAutoPowerStateMachine(self)->int:
        return self._integration.getAutoPowerStateMachine()

    def setAutoPowerStateMachine(self, state:int):
        self._integration.setAutoPowerStateMachine(state)

    def switchAutoPowerStateMachine(self, IsStop: bool):
        self._integration.switchAutoPowerStateMachine(IsStop)

    # <editor-fold desc="Origin Integration">
    def getFWVersion(self)->str:
        return self._integration.getFWVersion()

    def switchLogMode(self, is_print=False, debug_view=False, output_to_File=False):
        self._integration.switchLogMode(is_print, debug_view, output_to_File)

    def getChipID(self)->str:
        return self._integration.getChipID()
    
    def getDeviceInfo(self, type:int=2) -> str:
        return self._integration.getDeviceInfo(type)

    def getSN(self)->str:
        return self._integration.getSN()

    def closeDevice(self):
        self._integration.closeDevice()

    def connectDevice(self, device_num=-1)->str:
        '''
        if device_num is default (-1),
        this function will try to connect all type of device and return connected device name.

        device_num :

        0: 'Unknow'
        1: 'Cypress'
        2: 'VComPort'
        3: 'I2C'

        '''

        device_dict = {0: 'Unknow',
                       1: 'Cypress',
                       2: 'VComPort',
                       3: 'I2C'}

        if device_dict.get(device_num):
            self._integration.connectDevice(device_num)
            return device_dict[device_num]

        for device_num in device_dict.keys():
            try:
                self._integration.connectDevice(device_num)
                return device_dict[device_num]
            except:
                continue
        raise ValueError('No device detected !')

    def outputDebugview(self, msg:str="", is_log:bool=False)->None:
        self._integration.outputDebugview(msg, is_log)

    def resetDevice(self):
        self._integration.resetDevice()

    def readEFuseCmd(self, addr:int)->int:
        return self._integration.readEFuseCmd(addr)

    def readHWRegister(self, addr, num_of_reg=1):
        log.debug('Read HW register addr=0x{:08X}'.format(addr))
        return self._integration.readHWRegister(addr, num_of_reg)

    def writeHWRegister(self, addr, val_ary):
        log.debug('Write HW register addr=0x{:08X}, write=0x{:08X}'.format(addr, val_ary[0]))
        return self._integration.writeHWRegister(addr, val_ary)

    def readRFICRegister(self, addr):
        log.debug("Read RF register addr=0x{:04X}".format(addr))
        return self._integration.readRFICRegister(addr)

    def writeRFICRegister(self, addr=None, val=None, RB_check=False):
        log.debug('Write RF register addr=0x{:04X}, write=0x{:04X}'.format(addr, val))
        self._integration.writeRFICRegister(addr, val)
        if RB_check:
            res = self._integration.readRFICRegister(addr)
            log.info('Write RF register(0x{:04X}) read back compare match :{}, write={}, read={}'.format(addr, res == val, val, res))

    def setAIWeightScript(self, filename, compare=True):
        self._integration.setAIWeightScript(filename, compare)

    def getLibVersion(self)->str:
        lib_ver = self._integration.getLibVersion()
        log.info('lib version : {}'.format(lib_ver))
        return lib_ver

    def getGestureResult(self)->tuple:
        return self._integration.getGestureResult()

    def writeRawDataToSRAM(self, channel , rawdata):
        rawdata_arr = np.asarray(rawdata, dtype='int8')
        rawdata_arr2 = bytearray(rawdata_arr)
        self._integration.writeRawDataToSRAM(channel , rawdata_arr2)

    def readRangeRegisters(self, first_addr, last_addr):
        addr_list = []
        for addr in range(first_addr, last_addr+1, 4):
            addr_list.append(addr)
        addr_arry = np.asarray(addr_list)
        val_arry = self._integration.readRangeRegisters(first_addr, last_addr)
        if len(addr_arry) == len(val_arry):
            # assert len(addr_arry) == len(val_arry), 'Number of address not match with results'
            return val_arry, addr_arry
        return None

    def switchSoftMaxInterrupt(self, enable, read_interupt=0, clear_interupt=0, size=4096, ch_of_RBank=0, reg_addrs=np.zeros(0,dtype='uint32'), frame_setting=120):
        self._integration.switchSoftmaxInterrupt(enable, read_interupt, clear_interupt, size, ch_of_RBank, reg_addrs, frame_setting)
        log.info('SwitchSoftMaxInterrupt success')

    def getSoftMaxInterruptAsserted(self, take_first_frame):
        res = self._integration.getSoftmaxInterruptAsserted(take_first_frame)
        if res is None:
            return None
        dtype = '>i2'
        for k, v in res.items():
            if k == 0:
                dtype = '>i2'
            if k == 1:
                dtype = '>i2'
            if k == 2:
                dtype = '>u4'
            if k == 3:
                dtype = '>i2'
            res[k] = np.frombuffer(v, dtype=dtype)
        return res

    def switchDiagnosisInterrupt(self, enable, gemmini_res=0, data_size=0, reg_addrs=np.zeros(0,dtype='uint32')):# Old function name
        assert (enable < 128), 'Argument enable is not valid !'
        gemmini_res = int(gemmini_res).to_bytes(4, 'big')
        self._integration.switchDiagnosisInterrupt(enable, gemmini_res, data_size, reg_addrs)
        log.info('SwitchSoftMaxInterrupt success')

    def getDiagnosisInterruptRegValues(self, take_first_frame=False):
        res = self._integration.getDiagnosisInterruptAsserted(take_first_frame)
        return res

    def getAllResults(self):
        return self._integration.getAllResults()

    def setAIWeightBinFile(self, filepath):
        self._integration.setAIWeight_bin(filepath)

    def switchSPIChannel(self, mode=None):
        return self._integration.switchSPIChannel(mode)

    def receiveAllData_list(self):
        return self._integration.receiveAllData_list()

    def startMassDataBuf_RAW(self, buf_size, delay_ms, chirps):
        self._integration.startMassDataBuf_RAW(buf_size, delay_ms, chirps)

    def startMassDataBuf_RDI(self, buf_size, delay_ms):
        self._integration.startMassDataBuf_RDI(buf_size, delay_ms)

    def stopMassDataBuf(self):
        self._integration.stopMassDataBuf()

    def getMassDataBuf(self):
        return self._integration.getMassDataBuf()

    def getMassDataBuf_RDI(self):
        return self._integration.getMassDataBuf_RDI()

    def initSIC(self):
        self._integration.initSIC()

    def getRXPhaseOffset(self):
        return self._integration.getRXPhaseOffset()

    def setUserTable_bin(self, filepath: str):
        self._integration.setUserTable_bin(filepath)

    # </editor-fold>

    # <editor-fold desc="extend function">

    def getSoftMaxInterruptRegValues(self, take_first_frame=False):
        return self.getSoftMaxInterruptAsserted(take_first_frame)

    def getRFSICEnableStatus(self):
        mode0_addrs = (0x0189, 0x018A, 0x018B)
        mode0_compare_val = self._integration.readRFICRegister(0x018A)
        l = list(bin(mode0_compare_val)[2:].zfill(16))
        l.reverse()
        return int(l[1])

    def readHWRegister_bit(self, addr, bitH, bitL):
        log.debug("Read HW register addr=0x{:08X} [{}:{}]".format(addr, bitH, bitL))
        assert 31 >= bitH >= bitL >= 0
        bitLen = (bitH - bitL) + 1
        data = self.readHWRegister(addr, 1)
        mask = ((1 << bitLen) - 1) << bitL
        return (data[0] & mask) >> bitL

    def writeHWRegister_bit(self, decvalue, addr, bitH, bitL, RBCheck=False):
        log.debug("Write HW register addr=0x{:08X} [{}:{}] to {}".format(addr, bitH, bitL, decvalue))
        bitLen = bitH - bitL + 1
        if decvalue < 0:
            decvalue = decvalue + 2 ** (bitLen)

        r_data = self.readHWRegister(addr, 1)

        temp = r_data[0] >> (bitH + 1)
        temp = temp << bitLen
        temp = temp | decvalue
        temp = temp << bitL
        temp = temp | (r_data[0] & ~(~(1 << bitL) + 1))
        w_data = [temp]

        log.debug("Write HW register val from 0x{:08X} to 0x{:08X}".format(r_data[0], temp))
        self.writeHWRegister(addr, w_data)

        if RBCheck == True:
            CmpData = self.readHWRegister_bit(addr, bitH, bitL)
            log.info("Write HW register(0x{:08X} [{}:{}]) read back compare match :{} write={}, read={}"
                     .format(addr, bitH, bitL, CmpData == decvalue, decvalue, CmpData))

    def setRFICScript(self, filename:str, compare=False , ignoreAddrList=None):
        suffix =  Path(filename).suffix
        if suffix == '.txt':
            self._integration.setRFICScript(filename, compare , ignoreAddrList)
        elif suffix == '.bin':
            self._integration.setUserTable_bin(filename)
            self._integration.runRFICInit()
        else:
            log.warning('[setScriptRfic] file suffix not exist')

    def getModulationOnStatus(self):
        result = self.readRFICRegister(0x0029)
        return (result == 0x40FE)

    def switchModulationOn(self, turn_on=True):
        if turn_on:
            value = 0x40FE
        else:
            value = 0x407E
        self.writeRFICRegister(0x0029, value)

    def pullUpRawDataWriteInterrupt(self):
        self._integration.controlGemmini(1)

    def resetMGUState(self):
        self._integration.controlGemmini(2)

    def setDigiParam0(self):
        self._integration.setDigiParam0()

    # </editor-fold>

    # <editor-fold desc="Old version function name">

    def closeCyDevice(self):
        self.closeDevice()

    def regRead(self, addr, num_of_reg=1):
        '''
            # For old version
        '''
        return self.readHWRegister(addr, num_of_reg)

    def regWrite(self, addr, val_ary):
        self.writeHWRegister(addr, val_ary)

    def SwitchSPIChannel(self, mode=None):
        return self.switchSPIChannel(mode)

    def rficRegRead(self, addr):  # Old function name
        '''
        # For old version
        '''
        return self.readRFICRegister(addr)

    def rficRegWrite(self, addr=None, val=None, Print=True, Compare=False):
        '''
        # For old version
        '''
        self.writeRFICRegister(addr, val, Compare)

    def readReg(self, addr, bitH, bitL):
        '''
        # For old version
        '''
        return self.readHWRegister_bit(addr, bitH, bitL)

    def writeReg(self, decvalue, addr, bitH, bitL, RBCheck=True, IsPrint=False, Compare=True):
        '''
        # For old version
        '''
        self.writeHWRegister_bit(decvalue, addr, bitH, bitL, RBCheck)

    def setScriptRfic(self, filename: str, compare=False, ignoreAddrList=None):
        self.setRFICScript(filename, compare, ignoreAddrList)

    def setScriptAIWeight(self, filename, compare=True):
        self.setAIWeightScript(filename, compare)

    def massdatabufStart_RAW(self, buf_size, delay_ms, chirps):  # Old function name
        self.startMassDataBuf_RAW(buf_size, delay_ms, chirps)

    def massdatabufStart_RDI(self, buf_size, delay_ms):  # Old function name
        self.startMassDataBuf_RDI(buf_size, delay_ms)

    def massdatabufStop(self):  # Old function name
        self.stopMassDataBuf()

    def massdatabufGet(self):  # Old function name
        return self.getMassDataBuf()

    def massdatabufGet_RDI(self):  # Old function name
        return self.getMassDataBuf_RDI()

    def writeRawDatatoSRAM(self, channel, rawdata):
        self.writeRawDataToSRAM(channel, rawdata)

    def getAllResultsAsList(self):
        return self.receiveAllData_list()

    def readFromFlash(self, read_start_address, read_size, read_align):
        return self._integration.readFromFlash(read_start_address, read_size, read_align)

    def readFromMemery(self, read_start_address, read_size, read_align):
        return self._integration.readFromMemery(read_start_address, read_size, read_align)
    # </editor-fold>
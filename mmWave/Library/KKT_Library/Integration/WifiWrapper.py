from KKT_Library.Integration.wrapper import IKSOCIntegration
from KKT_Library.LibLog import lib_logger as log
from typing import Any, Union, Optional, Sequence, Tuple, Protocol
import inspect
from ksoc_wifi_connection import ConnectionOfWebsocket

class KKTLibException(Exception):
    def __init__(self, function_name, kres, *args, **kwargs):
        msg = "[ {} ] Failure, kres = {}".format(function_name, kres)
        super(KKTLibException, self).__init__(msg, *args, **kwargs)
    pass

class WIFIIntegration():
    def __init__(self):
        self._connection = ConnectionOfWebsocket()

    def getLibVersion(self)->str:
        '''
        Get C# Lib version.

        :return: [Customer ID (00000 ~ 65535)]-[model ID (001 ~ 255)]-v[major version].[patches]
        '''
        return '0-0-v0.0.0'

    def getDeviceInfo(self, comport_type=2)->str:
        '''
        Get ComPort informations.

        0: 'Unknow' ,
        1: 'Cypress' ,
        2: 'VComPort' ,
        3: 'I2C'

        :param comport_type: Comport type number.
        :return: ComPort informations
        '''
        return 'WIFI'

    def getSN(self):
        '''
        Get series number.
        '''
        # kres, SN = self.GetSN(None)
        # if kres != 0:
        #     raise KKTLibException(function_name=inspect.stack()[0][3], kres=kres)
        return ''

    def outputDebugview(self, msg="", isWriteLog=False):
        '''
        Output message to debug view.

        :param msg: Message to ouput on debug view.
        :param isWriteLog: Save to log file.
        :return:
        '''
        # self.OutputMsgToDebugView(msg, isWriteLog)
        raise KKTLibException(function_name=inspect.stack()[0][3], kres=0)

    def switchLogMode(self, Isprint=False, DebugView=False, OutputToFile=False):
        # self.SwitchLogMode(Isprint, DebugView, OutputToFile)
        raise KKTLibException(function_name=inspect.stack()[0][3], kres=0)

    def connectDevice(self, device:int)->None:
        kres = self._connection.connectDevice()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def closeDevice(self):
        kres = self._connection.disconnectDevice()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def readHWRegister(self, addr, num_of_reg=1):
        kres, val = self._connection.readHWRegister(addr)
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)
        return val

    def writeHWRegister(self, addr, val_ary):
        kres = self._connection.writeHWRegister(addr, val_ary)
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def switchSPIChannel(self, mode):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def readRFICRegister(self, addr):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def writeRFICRegister(self, addr, val):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getAllResults(self):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getAutoPowerStateMachine(self)->int:
        kres, mode = self._connection.getPowerSavingMode()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)
        return mode

    def setAutoPowerStateMachine(self, PowerState: int):
        kres = self._connection.setPowerSavingMode(PowerState)
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def receiveAllData_list(self):
        '''
        Get HW results using FW cmd "0xA0".

        :return:
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getGestureResult(self):
        '''
        Read registers after softmax interrupt to get HW results and clear softmax interrupt.

        :return: ( gesture number, axis(x, y, z), probability )
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def setRFICScript(self, filename, compare=False, ignoreAddrList=None):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def setAIWeightScript(self,filename, compare=True):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def startMassDataBuf_RAW(self, buf_size, delay_ms, chirps=32):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def startMassDataBuf_RDI(self, buf_size, delay_ms):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def stopMassDataBuf(self):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getMassDataBuf(self):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getMassDataBuf_RDI(self):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def readEFuseCmd(self, addr):
        raise KKTLibException(inspect.stack()[0][3], 0)

    def getFWVersion(self):
        kres, version = self._connection.getFirmwareVersion()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)
        return version

    def resetDevice(self):
        '''
        Reset device.

        :return: kres
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def writeRawDataToSRAM(self, channel, rawdata:bytearray):
        '''
        Write raw data to SRAM.

        :param channel: address of RX.
        :param rawdata: array of rawdata in dtype='int16'.
        :return: kres
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def readRangeRegisters(self, first_addr: int, last_addr: int):
        '''
        Give range of registers and get array of values.

        :param first_addr: start address
        :param last_addr: end address
        :return: Array of values or None
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def switchSoftmaxInterrupt(self, enable, read_interrupt, clear_interrupt, size, ch_of_RBank, reg_addrs, frame_setting):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt to clean.
        :param ch_of_RBank: Bit to enable the channel of reference bank .
        :param reg_addrs: Array of address.
        :return: kres
        '''
        kres = self._connection.switchCollectionOfMultiResults(enable, read_interrupt, clear_interrupt, size, ch_of_RBank, reg_addrs, frame_setting)
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def switchDiagnosisInterrupt_payload(self, payload: bytearray):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt 20to clean.
        :param num_of_reg: Number of register.
        :param reg_addrs: Array of address.
        :return: kres
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)

    def switchDiagnosisInterrupt(self, enable, gemmini_res, data_size, reg_addrs):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt 20to clean.
        :param num_of_reg: Number of register.
        :param reg_addrs: Array of address.
        :return: kres
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.SwitchDiagnosisInterruptAsserted(enable, gemmini_res, data_size, reg_addrs)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def getSoftmaxInterruptAsserted(self)->Optional[dict]:
        '''
        Get array of register's values when interrupt go high.

        :return: None or array of register's values.
        '''
        kres, res_dict = self._connection.getMultiResults()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)
        return res_dict

    def getDiagnosisInterruptAsserted(self):
        '''
        Get array of register's values when interrupt go high.

        :return: None or array of register's values.
        '''
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres, raw, diagnosis, AGC, Motion = self.GetDiagnosisInterruptAssertedRegValues(None, None, None, None)
        # if kres != 0:
        #     return None
        # if raw is not None:
        #     raw = np.asarray(list(raw), dtype='int16')
        #
        # if diagnosis is not None:
        #     diagnosis = list(diagnosis)
        #
        # if AGC is not None:
        #     AGC = bytearray(AGC)
        #     AGC = np.asarray(AGC, dtype='int8')
        #
        # if Motion is not None:
        #     Motion = np.asarray(list(Motion), dtype='int16')
        #
        # return raw, diagnosis, AGC, Motion

    def updateRFICSetting(self, path):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.UpdateRFICSetting(path)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def runRFICInit(self):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.RunRFICInit()
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def switchAutoPowerStateMachine(self, is_stop: bool):
        kres = self._connection.stopPowerStateMachine(is_stop)
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)

    def getChipID(self):
        kres, chip_id = self._connection.getChipID()
        if kres.value != 0:
            raise KKTLibException(inspect.stack()[0][3], kres.value)
        return chip_id

    def getOldFWVersion(self):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres, old_ver = self.GetOldVersion(None)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)
        # return old_ver

    def setAIWeight_bin(self, filepath):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.Set_AIWeight_Bin(filepath)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def setUserTable_bin(self, filepath):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.Set_UserTable_Bin(filepath)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def controlGemmini(self, mode):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.Control_Gemmini(mode)
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)

    def initRFIC(self):
        raise KKTLibException(inspect.stack()[0][3], 0)
        # kres = self.InitRFIC()
        # if kres != 0:
        #     raise KKTLibException(inspect.stack()[0][3], kres)
        # return kres
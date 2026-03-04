from KKT_Module.ksoc_global import kgl, global_variables
import os
import glob
import numpy as np
import re
from typing import Optional, Tuple

from KKT_Module.SettingProcess.ExcelParsing import ParamSheet
from KKT_Module.SettingProcess.ProcessList import ProcessList


class ScriptDir:
    Script_path:Optional[str] = None
    Hardware_excel:Optional[str] = None
    Hardware_text:Optional[str] = None
    RF_setting:Optional[str] = None
    AIweight_h5:Optional[str] = None
    AIweight_coe:Optional[str] = None
    AIweight_bin:Optional[str] = None

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def keys(self):
        return [k for k in dir(self) if not k.startswith('__') and not callable(getattr(self, k))]

    def get(self, key, default=None):
        return getattr(self, key, default)

    def setScriptDir(self, script_name, ini_configs=None):
        '''
        Get all file's path in Hardware setting folder.

        :param script_path: Hardware setting folder name.
        '''
        for k in self.keys():
            self[k] = None

        script_path = os.path.join(kgl.KKTTempParam, script_name)
        print('Script Path : {}'.format(script_path))
        assert os.path.isdir(script_path), 'Script folder not found !'
        self['Script_path'] = script_path

        HW_excel_path = os.path.join(script_path)
        HW_excel = glob.glob(os.path.join(HW_excel_path, '*.xlsx'))
        if len(HW_excel) != 0:
            self['Hardware_excel'] = HW_excel[0]

        HW_text_path = os.path.join(script_path, 'param')
        HW_text = glob.glob(HW_text_path + '/*.txt')
        if len(HW_text) != 0:
            self['Hardware_text'] = HW_text[0]

        weight_h5_path = os.path.join(script_path, 'ai_acc_weight', 'sram_h5')
        weight_h5 = glob.glob(weight_h5_path + '/*.h5')
        if len(weight_h5) != 0:
            self['AIweight_h5'] = weight_h5[0]

        weight_coe_path = os.path.join(script_path, 'ai_acc_weight', 'sram_coe')
        weight_coe = glob.glob(weight_coe_path + '/*.coe')
        if len(weight_coe) != 0:
            self['AIweight_coe'] = weight_coe

        weight_bin_path = os.path.join(script_path, 'ai_acc_weight', 'sram_bin')
        weight_bin = glob.glob(weight_bin_path + '/*.bin')
        if len(weight_bin) != 0:
            self['AIweight_bin'] = weight_bin

        if ini_configs is not None:
            if hasattr(ini_configs, 'enable_rf_txt') and int(ini_configs.enable_rf_txt) == 1:
                RF_text_path = os.path.join(script_path, 'Integration_Test_script', 'SOCA')
                RF_text = glob.glob(RF_text_path + '/*.txt')
                if len(RF_text) != 0:
                    self['RF_setting'] = RF_text[0]

        RF_bin_path = os.path.join(script_path, 'Integration_Test_script', 'SOCA')
        RF_bin = glob.glob(RF_bin_path + '/*.bin')
        if len(RF_bin) != 0:
            self['RF_setting'] = RF_bin[0]
        # import pprint
        # pprint.pprint(cls.ScriptDir,)
        pass

    def getScriptInfo(self)->Tuple[str, str, str, str, str, str]:
        ScriptDir = self.get('Script_path')
        assert ScriptDir is not None, 'Empty Script path !'
        ScriptDir = os.path.basename(ScriptDir)
        IC = 'K60168'
        ReleaseStatus = None
        CustomerID = 'xxxxx'
        SubCustomerID = 'xxx'
        ProductVer = 'vx.x.x'
        Date = None

        ScriptDir_list = str(ScriptDir).split('-')
        if ScriptDir_list[0] != IC:
            return IC, ReleaseStatus, CustomerID, SubCustomerID, ProductVer, Date

        CustomerID_re = re.compile('-(\d{5})-')
        if CustomerID_re.search(ScriptDir) is not None:
            CustomerID = CustomerID_re.search(ScriptDir).group(1)

        ProductVer_re = re.compile('v\d+\.\d+\.\d+')
        if ProductVer_re.search(ScriptDir) is not None:
            ProductVer = ProductVer_re.search(ScriptDir).group()

        SubCustomerID_re = re.compile('-(\d{3})-')
        if SubCustomerID_re.search(ScriptDir) is not None:
            SubCustomerID = SubCustomerID_re.search(ScriptDir).group(1)

        Date_re = re.compile('-(\d{7}\d$)')
        if Date_re.search(ScriptDir) is not None:
            Date = Date_re.search(ScriptDir).group(1)

        IC = ScriptDir_list[0]
        ReleaseStatus = ScriptDir_list[1]

        return IC, ReleaseStatus, CustomerID, SubCustomerID, ProductVer, Date

    def getScriptInfo2(self)->dict:
        script_dir = self.get('Script_path')
        assert ScriptDir is not None, 'Empty Script path !'
        script_ver = os.path.basename(script_dir)

        # pattern = r'([A-Z\d]+)-(\d+)-(\d+)-v([\d.]+)-(\d+)'
        pattern = r'(K\d{5})-(\w+)-(\d{5})-(\d{3})-(v\d+\.\d+\.\d+)-(\d{8})'
        match = re.match(pattern, script_ver)
        if match:
            info = {}
            for k,v in zip(['IC', 'ReleaseStatus', 'CustomerID', 'SubCustomerID', 'ProductVer', 'Date'], match.groups()):
                info[k] = v
            return info
        else:
            return {}

class SettingConfigs:
    '''
    Configs generated or need for init in Script setting process .

    '''

    Processes = [
        'Reset Device',
        'Gen Process Script',
        'Gen Param Dict', 'Get Gesture Dict',
        'Set Script',
        'Phase Calibration',
        'Run SIC',
        'Modulation On'
    ]
    ScriptDir = ScriptDir()
    SheetParam:Optional[ParamSheet] = None
    ProcList:Optional[ProcessList] = []
    ParamDict:dict = {}
    CoreGestures = {}
    SiameseGestures = {}
    Firmware = ''
    Tool = ''
    PhaseKConfigs = {}
    Chip_ID = 'K60168'

    class SIC:
        isDebug = False
        SIC_from_DSP_dict = True
        SIC_open = False

    class AIWeight:
        Enable = True

    class Connect:
        ...

    class PhaseK:
        # Phase calibrate
        OpenRX = 'RX123'
        OpenRXByScript = True
        OpenRX1 = True
        OpenRX2 = True
        OpenRX3 = True

    class HardwareSetting:
        AI_MUX = None
        Tracking_MUX = None
        Ch_valid = None

    class RFSetting:
        Enable = True
        Enable_RX1 = False
        Enable_RX2 = False
        Enable_RX3 = False

    class ModulationOn:
        Enable = True
        Status = False

    class GenScript:
        SaveTextScript = True

    def __init__(self, **kwargs):
        self.SIC = self.SIC()
        self.AIWeight = self.AIWeight()
        self.Connect = self.Connect()
        self.PhaseK = self.PhaseK()
        self.HardwareSetting = self.HardwareSetting()
        self.RFSetting = self.RFSetting()
        self.ModulationOn = self.ModulationOn()
        self.GenScript = self.GenScript()
        self.ini_configs = None
        if kwargs.get('ini_configs'):
            self.ini_configs = kwargs.get('ini_configs')

    @classmethod
    def setDefaultParamDict(cls):
        txt_file_name = os.path.join(kgl.KKTConfig, 'Default_Param.txt')
        if not os.path.isfile(txt_file_name):
            print("No Default param")
            return
        from KKT_Module.SettingProcess.ProcessList import ProcessListGenerator
        from KKT_Module.SettingProcess.ExcelParsing import ParamDictGenerator

        PLG = ProcessListGenerator()
        PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_setting.json')
        ProcList = PLG.readProcListFromFile(txt_file_name)
        cls.ParamDict = PDG.writeRegVal(ProcList)
        pass

    def setScriptDir(self, script_name):
        '''
        Get all file's path in Hardware setting folder.

        :param script_path: Hardware setting folder name.
        '''
        self.ScriptDir.setScriptDir(script_name, self.ini_configs)

    def genDSPConfigs(self):
        assert self.ParamDict is not None, "DSP config hasn't been set !"
        d625k_u0_reg_AICctrl0_param0 = self.ParamDict['DSPRx625K_Unit_0']['0x400B0088']
        d625k_u0_reg_AICctrl1_param0 = self.ParamDict['DSPRx625K_Unit_0']['0x400B00A8']
        d625k_u1_reg_AICctrl0_param0 = self.ParamDict['DSPRx625K_Unit_1']['0x40090088']
        d625k_u1_reg_AICctrl1_param0 = self.ParamDict['DSPRx625K_Unit_1']['0x400900A8']

        # AIC_outputShiftNum
        DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum = d625k_u0_reg_AICctrl0_param0[3]['outputShiftNum']
        DSPRx625K_Uint_0_REG_AICctrl1_param0_outputShiftNum = d625k_u0_reg_AICctrl1_param0[3]["outputShiftNum"]
        DSPRx625K_Uint_1_REG_AICctrl0_param0_outputShiftNum = d625k_u1_reg_AICctrl0_param0[3]["outputShiftNum"]
        DSPRx625K_Uint_1_REG_AICctrl1_param0_outputShiftNum = d625k_u1_reg_AICctrl1_param0[3]["outputShiftNum"]
        arr = np.array(
            [DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum, DSPRx625K_Uint_0_REG_AICctrl1_param0_outputShiftNum,
             DSPRx625K_Uint_1_REG_AICctrl0_param0_outputShiftNum, DSPRx625K_Uint_1_REG_AICctrl1_param0_outputShiftNum])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_AICctrl0_param0_outputShiftNum ~= REG_AICctrl1_param0_outputShiftNum"
        AIC_outputShiftNum = DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum

        # chirp num
        DSPRx625K_Uint_0_REG_symbolPerFrm = d625k_u0_reg_AICctrl0_param0[3]["symbolPerFrm"]
        DSPRx625K_Uint_1_REG_symbolPerFrm = d625k_u1_reg_AICctrl0_param0[3]["symbolPerFrm"]
        DSPRx625K_Uint_0_REG_symbolPerFrm_user = d625k_u0_reg_AICctrl0_param0[3]["symbolPerFrm_user"]
        DSPRx625K_Uint_1_REG_symbolPerFrm_user = d625k_u1_reg_AICctrl0_param0[3]["symbolPerFrm_user"]
        assert DSPRx625K_Uint_0_REG_symbolPerFrm == DSPRx625K_Uint_1_REG_symbolPerFrm, \
            "Warning: Uint{0,1} REG_symbolPerFrm ~= REG_symbolPerFrm"
        assert DSPRx625K_Uint_0_REG_symbolPerFrm_user == DSPRx625K_Uint_1_REG_symbolPerFrm_user, \
            "Warning: Uint{0,1} REG_symbolPerFrm_user ~= REG_symbolPerFrm_user"
        chirp_num = 0
        if DSPRx625K_Uint_0_REG_symbolPerFrm == 0:
            chirp_num = 16
        elif DSPRx625K_Uint_0_REG_symbolPerFrm == 1:
            chirp_num = 32
        elif DSPRx625K_Uint_0_REG_symbolPerFrm == 2:
            chirp_num = 64
        elif DSPRx625K_Uint_0_REG_symbolPerFrm >= 3:
            chirp_num = DSPRx625K_Uint_0_REG_symbolPerFrm_user

        d20m_u0_REG_RDIGen0_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D2008']
        d20m_u0_REG_RDIGen1_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D6008']
        d20m_u1_REG_RDIGen0_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F2008']
        d20m_u1_REG_RDIGen1_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F6008']

        # Fast_time_sample
        DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample = d20m_u0_REG_RDIGen0_param0[3]["FT_sample"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_FT_sample = d20m_u0_REG_RDIGen1_param0[3]["FT_sample"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_FT_sample = d20m_u1_REG_RDIGen0_param0[3]["FT_sample"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_FT_sample = d20m_u1_REG_RDIGen1_param0[3]["FT_sample"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample, DSPRx20M_Uint_0_REG_RDIGen1_param0_FT_sample,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_FT_sample, DSPRx20M_Uint_1_REG_RDIGen1_param0_FT_sample])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_FT_sample ~= REG_RDIGen1_param0_FT_sample"
        Fast_time_sample = None
        if DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample == 0:
            Fast_time_sample = 64
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample == 1:
            Fast_time_sample = 128

        # up_down_combining
        DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb = d20m_u0_REG_RDIGen0_param0[3]["upDownComb"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_upDownComb = d20m_u0_REG_RDIGen1_param0[3]["upDownComb"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_upDownComb = d20m_u1_REG_RDIGen0_param0[3]["upDownComb"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_upDownComb = d20m_u1_REG_RDIGen1_param0[3]["upDownComb"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb, DSPRx20M_Uint_0_REG_RDIGen1_param0_upDownComb,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_upDownComb, DSPRx20M_Uint_1_REG_RDIGen1_param0_upDownComb])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_upDownComb ~= REG_RDIGen1_param0_upDownComb"
        upDownComb = DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb

        # Slow_time_symbols
        DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt = d20m_u0_REG_RDIGen0_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_ST_SymbolCnt = d20m_u0_REG_RDIGen1_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_ST_SymbolCnt = d20m_u1_REG_RDIGen0_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_ST_SymbolCnt = d20m_u1_REG_RDIGen1_param0[3]["ST_SymbolCnt"]
        arr = np.array(
            [DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt, DSPRx20M_Uint_0_REG_RDIGen1_param0_ST_SymbolCnt,
             DSPRx20M_Uint_1_REG_RDIGen0_param0_ST_SymbolCnt, DSPRx20M_Uint_1_REG_RDIGen1_param0_ST_SymbolCnt])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_ST_SymbolCnt ~= REG_RDIGen1_param0_ST_SymbolCnt"
        Slow_time_symbols = None
        if DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 0:
            Slow_time_symbols = 16
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 1:
            Slow_time_symbols = 32
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 2:
            Slow_time_symbols = 64

        # Slow_time_conv2polar_GainShift
        DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift = d20m_u0_REG_RDIGen0_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_con2PolarGainShift = d20m_u0_REG_RDIGen1_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_con2PolarGainShift = d20m_u1_REG_RDIGen0_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_con2PolarGainShift = d20m_u1_REG_RDIGen1_param0[3]["con2PolarGainShift"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift,
                        DSPRx20M_Uint_0_REG_RDIGen1_param0_con2PolarGainShift,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_con2PolarGainShift,
                        DSPRx20M_Uint_1_REG_RDIGen1_param0_con2PolarGainShift])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_con2PolarGainShift ~= REG_RDIGen1_param0_con2PolarGainShift"
        con2PolarGainShift = DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift

        d20m_u0_REG_phaseMap_ctrl0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D8018']
        d20m_u1_REG_phaseMap_ctrl0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F8018']
        # PHD
        # phasemap_ctrl_enable
        DSPRx20M_Uint_0_REG_phaseMap_ctrl0 = d20m_u0_REG_phaseMap_ctrl0[3]["Enable"]
        DSPRx20M_Uint_1_REG_phaseMap_ctrl0 = d20m_u1_REG_phaseMap_ctrl0[3]["Enable"]
        arr = np.array([DSPRx20M_Uint_0_REG_phaseMap_ctrl0, DSPRx20M_Uint_1_REG_phaseMap_ctrl0])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_phaseMap_ctrl0 ~= REG_phaseMap_ctrl0"
        phaseMap_enable = DSPRx20M_Uint_0_REG_phaseMap_ctrl0

        d20m_u0_REG_phaseMap_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D801C']
        d20m_u1_REG_phaseMap_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F801C']
        # conv2polar_gain_RDI
        DSPRx20M_Uint_0_REG_gainRDI = d20m_u0_REG_phaseMap_param0[3]["gainRDI"]
        DSPRx20M_Uint_1_REG_gainRDI = d20m_u1_REG_phaseMap_param0[3]["gainRDI"]
        arr = np.array([DSPRx20M_Uint_0_REG_gainRDI, DSPRx20M_Uint_1_REG_gainRDI])
        result = np.all(arr == arr[0])
        # assert result, "Warning: Uint{0,1} REG_gainRDI ~= REG_gainRDI"
        conv2polar_gain_RDI = DSPRx20M_Uint_0_REG_gainRDI

        # conv2polar_gain_PhaseFFT
        DSPRx20M_Uint_0_REG_gainPhaseFFT = d20m_u0_REG_phaseMap_param0[3]["gainPhaseFFT"]
        DSPRx20M_Uint_1_REG_gainPhaseFFT = d20m_u1_REG_phaseMap_param0[3]["gainPhaseFFT"]
        arr = np.array([DSPRx20M_Uint_0_REG_gainPhaseFFT, DSPRx20M_Uint_1_REG_gainPhaseFFT])
        result = np.all(arr == arr[0])
        # assert result,"Warning: Uint{0,1} REG_gainPhaseFFT ~= REG_gainPhaseFFT"
        conv2polar_gain_PhaseFFT = DSPRx20M_Uint_0_REG_gainPhaseFFT

        # n_c
        if phaseMap_enable == 0:
            RDI_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                    np.log2(Slow_time_symbols) + 1) - 1 + con2PolarGainShift
            kProcMap1_nc = RDI_nc
            kProcMap2_nc = RDI_nc
        elif phaseMap_enable == 1:
            RDI_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                    np.log2(Slow_time_symbols) + 1) - 1 + conv2polar_gain_RDI
            PHD_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                    np.log2(Slow_time_symbols) + 1) - np.log2(2) - 1 + conv2polar_gain_PhaseFFT
            kProcMap1_nc = RDI_nc
            kProcMap2_nc = PHD_nc

        # print('DSP Config = ', kProcMap1_nc, kProcMap2_nc, chirp_num)
        return kProcMap1_nc, kProcMap2_nc, chirp_num

    def getBackgroundID(self):
        for k, v in self.CoreGestures.items():
            if v == 'Background':
                return k
        return '-1'

    def getScriptInfo(self):
        return self.ScriptDir.getScriptInfo2()
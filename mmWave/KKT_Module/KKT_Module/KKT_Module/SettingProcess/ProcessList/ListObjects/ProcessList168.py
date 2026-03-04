from KKT_Module.SettingProcess.ProcessList.Core import ProcessList, ProcessListSymbol
import os
import typing
from datetime import datetime

class DigitalControls_168:
    def _getReg_RFIC_SPI_Regs_Div(self):
        bitsMap = [
            #  size, pos
            [0, 0],  # DIVIDER
            [0, 16],  # DIVIDER 2
        ]
        addr = getRegAddr('RFIC_SPI_Regs_Div', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [79, 0])
        return reg_adr, val
        # self._ProcList.append([pls.RegSymbol, reg_adr, val])

    def _getReg_RFIC_SPI_Regs_SSR(self):
        bitsMap = [
            #  size, pos
            [0, 0],  # SSR
            [0, 2],  # SS_LVL
            [0, 3],  # ASS
            [0, 4],  # SS_LTRIG
            [0, 5],  # LTRIG_FLAG
        ]
        addr = getRegAddr('RFIC_SPI_Regs_SSR', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [1, 0, 1, 0, 0])
        return reg_adr, val

    def _getReg_RFIC_SPI_Regs_CNTRL(self):
        bitsMap = [
            #  size, pos
            [0, 0],  # GO_BUSY
            [0, 1],  # RX_NEG
            [0, 2],  # TX_NEG
            [0, 3],  # TX_BIT_LEN
            [0, 8],  # TX_NUM
            [0, 10],  # LSB
            [0, 11],  # CLKP
            [0, 12],  # SLEEP
            [0, 16],  # IF
            [0, 17],  # IE
            [0, 18],  # SLAVE
            [0, 19],  # BYTE_SLEEP
            [0, 20],  # BYTE_ENDIAN
            [0, 21],  # FIFO
            [0, 22],  # TWOB
            [0, 23],  # VARCLK_EN
            [0, 24],  # RX_EMPTY
            [0, 25],  # RX_FULL
            [0, 26],  # TX_EMPTY
            [0, 27],  # TX_FULL
            [0, 28],  # %DMA_ASS_BURST
        ]
        bsize = 0  # 0 -> 32bit for 15bit address
        # bsize = 24;     #for 7bit address
        addr = getRegAddr('RFIC_SPI_Regs_CNTRL', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [0, 1, 1, bsize, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        return reg_adr, val

    def _getReg_APBCLK(self, val: typing.List[int]):
        if len(val) != 10:
            raise Exception("[ERROR] getRegAISYSCTL: array range error")

        bitsMap = [
            #  size, pos
            [0, 9],  # TRACK_EN
            [0, 17],  # AIACC_EN
            [0, 18],  # FFT_EN
            [0, 19],  # SPIGES_EN
            [0, 22],  # MOTION_EN
            [0, 28],  # SPI_FLASH_EN
            [0, 29],  # SPI_RFIC_EN
            [0, 30],  # ANA_EN
        ]
        addr = getRegAddr('APBCLK', None)
        reg_adr = addr[0] + addr[1]
        reg_val = bit2Val(bitsMap, val[:-2])
        reg_val = 0xffffffff & reg_val
        reg_val = 0xffffffff
        # self._ProcList.append([pls.RegSymbol, reg_adr, reg_val])
        return reg_adr, reg_val

    def _getReg_AIMTXEN(self, val: typing.List[int]):
        bitsMap = [
            #  size, pos
            [0, 0],  # AISRAM_REQ
            [0, 31],  # Force SRAM 625K
        ]
        # SysCtlPin(9)     0;     % AISRAM_REQ
        # SysCtlPin(10)     31];	% Force SRAM 625K
        addr = getRegAddr('AIMTXEN', None)
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val[-2:])

    def _getRegSysReset(self, val: typing.List[int]):
        bitsMap = [
            #  size, pos
            [1, 18],  # FFT_Rst
            [1, 19],  # TRACK_Rst
            [1, 21],  # SPIGES_Rst
            [1, 22],  # MOTION_Rst
            [1, 27],  # AIACC_Rst
            [1, 28],  # SPI_FLASH_Rst
            [1, 29],  # SPI_RFIC_Rst
            [1, 30],  # ANA_Rst
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getSysReset: array range error")

        addr = getRegAddr('IPRSTC2_SetReset', None)

        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_RDIGen0_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # startRDI_trig
            [0, 1],  # stopRDI_trig
            [0, 2],  # startPowerSave_trig
            [0, 3],  # stopPowerSave_trig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_RDIGen0_ctrl0: array range error")

        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen0_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen0_ctrl0', 'DSPRx20M_Unit_0')

        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_RDIGen1_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # startRDI_trig
            [0, 1],  # stopRDI_trig
            [0, 2],  # startPowerSave_trig
            [0, 3],  # stopPowerSave_trig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_RDIGen1_ctrl0: array range error")

        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen1_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen1_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625k_AICctrl_ctrl0(self, val: typing.List[int], dsp_unit: int):
        bitsMap = [
            #  size, pos
            [1, 0],  # opTrigger
            [1, 1],  # stopTrigger
            [1, 2],  # startPowerSave_trig
            [1, 3],  # stopPowerSave_trig
            [1, 4],  # resetWeightTrigger
            [1, 5],  # clearBufferTrigger
            [1, 6],  # enableWnCntUpTrig
            [1, 7],  # disableWnCntUpTrig
            [1, 8],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_AICctrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625k_AICctrl_ctrl1(self, val: typing.List[int], dsp_unit: int):
        bitsMap = [
            #  size, pos
            [1, 0],  # opTrigger
            [1, 1],  # stopTrigger
            [1, 2],  # startPowerSave_trig
            [1, 3],  # stopPowerSave_trig
            [1, 4],  # resetWeightTrigger
            [1, 5],  # clearBufferTrigger
            [1, 6],  # enableWnCntUpTrig
            [1, 7],  # disableWnCntUpTrig
            [1, 8],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_AICctrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl1', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl1', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_FX3InfCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # RDICh0En
            [0, 1],  # RDICh1En
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_FX3InfCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_AIInfCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # RDICh0En
            [0, 1],  # RDICh1En
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_AIInfCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_AIInfCtrl_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_AIInfCtrl_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625K_RFCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # oneFrmTrig
            [0, 1],  # extRFStartTrig
            [0, 2],  # extRFStopTrig
            [0, 3],  # regSettingTrig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625k_RFCctrl_ctrl2(self, val: typing.List[int], dsp_unit: int):
        bitsMap = [
            #  size, pos
            [0, 0],  # ch0En
            [0, 1],  # ch1En
            [0, 2],  # extRFSel
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_RFCctrl_ctrl2: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl2', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl2', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625K_RFCtrl_ctrl3(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # numOfFrm
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl3: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl3', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl3', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx625K_RFCtrl_ctrl4(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # frmStartPeriod
            [0, 20],  # frmSampleOffset
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl4: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl4', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl4', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_WinFuncCtrl0_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_WinFuncCtrl0_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl0_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl0_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSPRx20M_WinFuncCtrl1_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_WinFuncCtrl1_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl1_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl1_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSP_Motion_ctrl0(self, val):
        bitsMap = [
            #  size, pos
            [0, 0],  #
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSP_Motion_ctrl0: array range error")
        addr = getRegAddr('DSP_Motion_ctrl0', None)
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

    def _getReg_DSP_Motion_ctrl1(self, val):
        bitsMap = [
            #  size, pos
            [0, 0],  #
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSP_Motion_ctrl1: array range error")
        addr = getRegAddr('DSP_Motion_ctrl1', None)
        reg_adr = addr[0] + addr[1]
        return reg_adr, bit2Val(bitsMap, val)

class ProcessList168(ProcessList, DigitalControls_168):
    def __init__(self, list_symbol:ProcessListSymbol=ProcessListSymbol()):
        super().__init__(list_symbol)

    def fromSheetParam(self, sheet_param, rf_script_file:str=None, AI_weights:list=None):
        proc_list = self
        self.clear()
        Line = self.line
        # header
        proc_list.append(Line.Comment())
        proc_list.append(Line.Comment(f"Created Date : {datetime.now().strftime(r'%Y/%m/%d %H:%M:%S')}"))
        proc_list.append(Line.Comment(f"Config File : {os.path.basename(sheet_param['file_name'])}"))
        proc_list.append(Line.Comment())

        # proc_list.append(Line.Comment("Clear_AI_Enable"))
        # proc_list.append(Line.Reg(0x400608F8, 0x00000000))
        #
        # proc_list.append(Line.Comment("SIC_Disable"))
        # proc_list.append(Line.Reg(0x40060900, 0x00000000))
        # proc_list.append(Line.Reg(0x400601AC, 0x00000000))
        #
        # proc_list.append(Line.Reg(0x400B0084, 0x00000402))
        # proc_list.append(Line.Reg(0x400B00A4, 0x00000402))
        # proc_list.append(Line.Reg(0x40090084, 0x00000402))
        #
        # proc_list.append(Line.Comment("Dynamic_AIC_Operation"))
        # proc_list.append(Line.Reg(0x400B00E4, 0x00000030))
        # proc_list.append(Line.Reg(0x400900E4, 0x00000030))
        # proc_list.append(Line.Reg(0x4005C0E4, 0x00000004))
        #
        # proc_list.append(Line.Comment("AI_FFT_Tracking_Reset"))
        # dsp_unit_num = 0
        # reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        # reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        #
        # dsp_unit_num = 1
        # reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        # reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        #
        # reg = self._getRegSysReset([1, 1, 0, 0, 1, 0, 0, 0])
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        #
        # proc_list.append(Line.Comment("Clear AI_FFT_Tracking_Reset"))
        # reg = self._getRegSysReset([0, 0, 0, 0, 0, 0, 0, 0])
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        #
        # # SPI_master_Init
        # reg = self._getReg_RFIC_SPI_Regs_Div()
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        # reg = self._getReg_RFIC_SPI_Regs_SSR()
        # proc_list.append(Line.Reg(reg[0], reg[1]))
        # reg = self._getReg_RFIC_SPI_Regs_CNTRL()
        # proc_list.append(Line.Reg(reg[0], reg[1]))

        proc_list.append(Line.Comment("Pre-RFIC-Script Setting"))
        rf_script_file = os.path.join(sheet_param['workbook']['$RFIC_S2P']['FilePath'],
                                      sheet_param['workbook']['$RFIC_S2P']['FileName'][0])
        proc_list.append(Line.RFPath(rf_script_file))
        proc_list.append(Line.Comment("RFIC_Script Write from Excel Param."))

        proc_list.append(Line.Comment("Pre-AI_WeightData Setting"))
        reg = self._getRegSysReset([1, 1, 0, 0, 1, 0, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        reg = self._getReg_APBCLK([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_AIMTXEN([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        proc_list.append(Line.Comment("AI-WeightData-Script"))
        aiweightdatafolder = sheet_param['workbook']['$AI_WeightData']['FilePath']
        aiweightdatafiles = sheet_param['workbook']['$AI_WeightData']['FileName']
        proc_list.append(Line.AIPath(aiweightdatafolder))
        proc_list.append(Line.AIFile(aiweightdatafiles))

        proc_list.append(Line.Comment("select AI_WeightData Excel Param."))

        proc_list.append(Line.Comment("Post-AI_WeightData Setting"))
        reg = self._getRegSysReset([0, 0, 0, 0, 0, 0, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        reg = self._getReg_APBCLK([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_AIMTXEN([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        proc_list.append(Line.Comment("Init AI/FFT/SPI_GES/Track_3D Clock"))
        reg = self._getReg_APBCLK([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        reg = self._getReg_AIMTXEN([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])
        proc_list.append(Line.Reg(reg[0], reg[1]))

        proc_list.append(Line.Comment("RFIC S2P Set Process"))
        for reg in sheet_param['workbook']['$RFIC_S2P']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("Adc_Mux Parameters"))
        for reg in sheet_param['workbook']['$Adc_MUX']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("Tracking Parameters"))
        for reg in sheet_param['workbook']['$Tracking']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("AIACC_MEM Parameters"))
        for reg in sheet_param['workbook']['$AIACC_MEM']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("AIACC_Layer Parameters"))
        for reg in sheet_param['workbook']['$AIACC_Layer']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("AIACC_PARAM Parameters"))
        for reg in sheet_param['workbook']['$AIACC_PARAM']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("AIACC_Siamese Parameters"))
        for reg in sheet_param['workbook']['$AIACC_Siamese']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        # DPS UNIT 0
        proc_list.append(Line.Comment("DSPRx20M_Unit_0 Parameters"))
        for reg in sheet_param['workbook']['$DSPRx20M_Unit_0']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("DSPRx625K_Unit_0 Parameters"))
        for reg in sheet_param['workbook']['$DSPRx625K_Unit_0']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("DSP Control and Sync: DSP_UNIT_0"))
        dsp_unit_num = 0
        reg = self._getReg_DSPRx625k_RFCctrl_ctrl2([1, 1, 0], dsp_unit_num)
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen0_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch0 start RDI trig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen1_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch1 start RDI trig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen0_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch0 DIPowerSaveModeTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen1_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch1 DIPowerSaveModeTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 1, 0, 0, 0, 1, 0, 0],
                                                   dsp_unit_num)  # ch0 AICPowerSaveModTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 1, 0, 0, 0, 1, 0, 0],
                                                   dsp_unit_num)  # ch1 AICPowerSaveModTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_FX3InfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_AIInfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        proc_list.append(Line.Reg(reg[0], reg[1]))
        TestNumOfFrm = 0

        reg = self._getReg_DSPRx625K_RFCtrl_ctrl3([TestNumOfFrm], dsp_unit_num)  # TestNumOfFrm
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl4([0x2000, 0], dsp_unit_num)  # init RF Ctrl
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 1, 0, 0], dsp_unit_num)  # startExtRFTrig
        proc_list.append(Line.Reg(reg[0], reg[1]))

        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 0, 0, 0, 0, 0, 0, 1],
                                                   dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 0, 0, 0, 0, 0, 0, 1],
                                                   dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_WinFuncCtrl0_ctrl0([1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_WinFuncCtrl1_ctrl0([1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 0, 0, 1], dsp_unit_num)  # regSettingTrig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                   dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                   dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))

        # DPS UNIT 1
        proc_list.append(Line.Comment("DSPRx20M_Unit_1 Parameters"))
        for reg in sheet_param['workbook']['$DSPRx20M_Unit_1']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("DSPRx625K_Unit_1 Parameters"))
        for reg in sheet_param['workbook']['$DSPRx625K_Unit_1']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))

        proc_list.append(Line.Comment("DSP Control and Sync: DSP_UNIT_1"))
        dsp_unit_num = 1
        reg = self._getReg_DSPRx625k_RFCctrl_ctrl2([1, 1, 0], dsp_unit_num)
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen0_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch0 start RDI trig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen1_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch1 start RDI trig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen0_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch0 DIPowerSaveModeTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_RDIGen1_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch1 DIPowerSaveModeTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 1, 0, 0, 0, 1, 0, 0],
                                                   dsp_unit_num)  # ch0 AICPowerSaveModTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 1, 0, 0, 0, 1, 0, 0],
                                                   dsp_unit_num)  # ch1 AICPowerSaveModTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_FX3InfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_AIInfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        proc_list.append(Line.Reg(reg[0], reg[1]))

        TestNumOfFrm = 0
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl3([TestNumOfFrm], dsp_unit_num)  # TestNumOfFrm
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl4([0x2000, 0], dsp_unit_num)  # init RF Ctrl
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 1, 0, 0], dsp_unit_num)  # startExtRFTrig
        proc_list.append(Line.Reg(reg[0], reg[1]))

        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 0, 0, 0, 0, 0, 0, 1],
                                                   dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 0, 0, 0, 0, 0, 0, 1],
                                                   dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_WinFuncCtrl0_ctrl0([1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx20M_WinFuncCtrl1_ctrl0([1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 0, 0, 1], dsp_unit_num)  # regSettingTrig
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl0([1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                   dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSPRx625k_AICctrl_ctrl1([1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                   dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        proc_list.append(Line.Reg(reg[0], reg[1]))

        # DSP_Motion
        proc_list.append(Line.Comment("DSP_Motion Parameters"))
        for reg in sheet_param['workbook']['$DSP_Motion']['Registers']:
            proc_list.append(Line.Reg(reg[1], reg[2]))
        proc_list.append(Line.Comment("DSP_Motion Control"))

        reg = self._getReg_DSP_Motion_ctrl0([0x100])  #
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSP_Motion_ctrl1([4])  #
        proc_list.append(Line.Reg(reg[0], reg[1]))
        reg = self._getReg_DSP_Motion_ctrl0([1])  #
        proc_list.append(Line.Reg(reg[0], reg[1]))
        return proc_list

def getBaseAddr(addr):
    return{
        'TRK_BA'            :0x50000500,
        'DSPRx20M_Unit_0'   :0x400D0000,
        'DSPRx625K_Unit_0'  :0x400B0000,
        'DSPRx20M_Unit_1'   :0x400F0000,
        'DSPRx625K_Unit_1'  :0x40090000,
        'DSP_Motion'        :0x4005C000,
        'AIACC'             :0x40060000,
        'GCR_BA'            :0x50000000,
        'CLK_BA'            :0x50000200,
        'SPI_RFIC_BA'       :0x400A0000,
        'AI_WEIGHT_BA'      :0x20020000,
    }.get(addr,None)

def getRegAddr(reg, dsp_unit):
    return{
        'IPRSTC2_SetReset'              :[getBaseAddr('GCR_BA'), 0x0C],
        'RFIC_SPI_Regs_CNTRL'           :[getBaseAddr('SPI_RFIC_BA'), 0x00],  #RFIC_SPI_Regs_CNTRL
        'RFIC_SPI_Regs_Div'             :[getBaseAddr('SPI_RFIC_BA'), 0x04],  #RFIC_SPI_Regs_DIVIDER
        'RFIC_SPI_Regs_SSR'             :[getBaseAddr('SPI_RFIC_BA'), 0x08],  #RFIC_SPI_Regs_DIVIDER
        'APBCLK'                        :[getBaseAddr('CLK_BA'), 0x08],  #APBCLK
        'AIMTXEN'                       :[getBaseAddr('TRK_BA'), 0x00],  #AIMTXEN

        'DSPRx625k_WinFuncCtrl0_ctrl0'  :[getBaseAddr(dsp_unit), 0xC4],
        'DSPRx625k_WinFuncCtrl1_ctrl0'  :[getBaseAddr(dsp_unit), 0xD4],
        'DSPRx625k_AICctrl_ctrl0'       :[getBaseAddr(dsp_unit), 0x84],
        'DSPRx625k_AICctrl_ctrl1'       :[getBaseAddr(dsp_unit), 0xA4],
        'DSPRx625k_RFCtrl_ctrl0'        :[getBaseAddr(dsp_unit), 0x40],
        'DSPRx625k_RFCtrl_ctrl1'        :[getBaseAddr(dsp_unit), 0x44],
        'DSPRx625k_RFCtrl_ctrl2'        :[getBaseAddr(dsp_unit), 0x48],
        'DSPRx625k_RFCtrl_ctrl3'        :[getBaseAddr(dsp_unit), 0x4C],
        'DSPRx625k_RFCtrl_ctrl4'        :[getBaseAddr(dsp_unit), 0x50],

        'DSPRx20M_RDIGen0_ctrl0'        :[getBaseAddr(dsp_unit), 0x2000],
        'DSPRx20M_RDIGen1_ctrl0'        :[getBaseAddr(dsp_unit), 0x6000],
        'DSPRx20M_AIInfCtrl_ctrl0'      :[getBaseAddr(dsp_unit), 0x8008],
        'DSPRx20M_RDIGen_ctrl0'         :[getBaseAddr(dsp_unit), 0x8010],

        'DSP_Motion_ctrl0'              :[getBaseAddr('DSP_Motion'), 0x84],
        'DSP_Motion_ctrl1'              :[getBaseAddr('DSP_Motion'), 0x40],
    }.get(reg, None)

def bit2Val(bitsMap, val):
    if len(val) != len(bitsMap):
        raise Exception("[ERROR] bit2Val: array range error")
    new_val = 0
    for i in range(len(val)):
        if bitsMap[i][0] == 0:
            mask = 0xffffffff
        else:
            mask = 2 ** bitsMap[i][0] - 1
        v = val[i] & mask
        v <<= bitsMap[i][1]
        new_val |= v
    return new_val

def bitFieldToVal(fieldVal, field):
    if len(fieldVal) != len(field):
        raise Exception("[ERROR] bitFieldToVal: array range error")
    new_val = 0
    shift = 0
    for i, f in enumerate(field):
        mask = 2 ** f - 1
        v = fieldVal[i] & mask
        v <<= shift
        new_val |= v
        shift = shift + f
    return new_val
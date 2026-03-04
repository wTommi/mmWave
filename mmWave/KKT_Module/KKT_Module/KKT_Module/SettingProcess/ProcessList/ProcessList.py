import os
import pprint

from KKT_Module.SettingProcess.ProcessList.Core import ProcessList, ProcessListSymbol
from KKT_Module.SettingProcess.ProcessList.ListObjects import ProcessList168, ProcessList169
from KKT_Module.SettingProcess.ExcelParsing import KsocExcelParser


class ProcessListUtils:
    def __init__(self, chip_ID='K60168'):
        self.chip_ID = chip_ID
        self.list_symbol = ProcessListSymbol()
        if 'K60168' in chip_ID:
            self.process_list:ProcessList = ProcessList168(self.list_symbol)
        elif 'K60169' in chip_ID:
            self.process_list: ProcessList = ProcessList169(self.list_symbol)
        self.KKT_xlsx_parser = KsocExcelParser()
        pass
    def genProcListFromExcelFile(self, file_path)->ProcessList:
        sheet_param = self.KKT_xlsx_parser.parsing(file_path)
        self.process_list.fromSheetParam(sheet_param=sheet_param)
        return self.process_list

    def genProcListFromTextFile(self, file_path)->ProcessList:
        self.process_list.fromText(file_path=file_path)
        return self.process_list

    def saveProcListToText(self, file_path):
        self.process_list.genText(file_path=file_path)


class ProcessListGenerator(ProcessListUtils):
    '''
    舊版 module 介面
    '''
    def genProcessList(self, sheet_param):
        return self.process_list.fromSheetParam(sheet_param)

    def readProcListFromFile(self, file_path):
        return self.genProcListFromTextFile(file_path)

    def saveProcListToFile(self, filepath:str, proclist=None):
        self.saveProcListToText(filepath)



if __name__ == '__main__':
    # Testing
    from pathlib import Path
    from KKT_Module.ksoc_global import kgl

    def test_4_168B():
        PL_UT = ProcessListUtils(chip_ID='168')
        PL_UT.genProcListFromExcelFile(
            Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168B_Format\210628_KSOCB_SIAMESE_ON.xlsx'))
        PL_UT.saveProcListToText(Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168B_Format\param\param_210628_KSOCB_SIAMESE_ON_new.txt'))
        PL_UT.genProcListFromTextFile(Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168B_Format\param\param_210628_KSOCB_SIAMESE_ON_new.txt'))
        PL_UT.saveProcListToText(Path(kgl.KKTModule).joinpath(
            r'SettingProcess\Test_Param\168B_Format\param\param_210628_KSOCB_SIAMESE_ON_new_txt.txt'))


    def test_4_168A():
        PL_UT = ProcessListUtils(chip_ID='168')
        PL_UT.genProcListFromExcelFile(
            Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168A_Format\kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle.xlsx'))
        PL_UT.saveProcListToText(Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168A_Format\param\param_kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle_new.txt'))
        PL_UT.genProcListFromTextFile(Path(kgl.KKTModule).joinpath(r'SettingProcess\Test_Param\168A_Format\param\param_kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle_new.txt'))
        PL_UT.saveProcListToText(Path(kgl.KKTModule).joinpath(
            r'SettingProcess\Test_Param\168A_Format\param\param_kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle_new_txt.txt'))

    def test_4_169():
        PL_UT = ProcessListUtils(chip_ID='169')
        PL_UT.genProcListFromExcelFile(r'C:\work\Python\KSOC Tool in MVVM\TempParam\fpga_test_for_gen_1101_1T1R_RDI\param\Hardware_setting_1T1R_64upsample_total128sample_32chirps_RDIPHD_1D_Tracking20220810.xlsx')
        PL_UT.saveProcListToText(r'C:\work\Python\KSOC Tool in MVVM\TempParam\fpga_test_for_gen_1101_1T1R_RDI\param\testtttt.txt')
        PL_UT.genProcListFromTextFile(r'C:\work\Python\KSOC Tool in MVVM\TempParam\fpga_test_for_gen_1101_1T1R_RDI\param\testtttt.txt')
        PL_UT.saveProcListToText(r'C:\work\Python\KSOC Tool in MVVM\TempParam\fpga_test_for_gen_1101_1T1R_RDI\param\testtttt.txt')



    # test_4_168B()
    # test_4_168A()
    test_4_169()
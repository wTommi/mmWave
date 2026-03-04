from KKT_Module.SettingProcess.ProcessList.Core import ProcessList, ProcessListSymbol
import os
import typing
from datetime import datetime

class ProcessList169(ProcessList):
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

        proc_list.append(Line.Comment("Pre-RFIC-Script Setting"))
        rf_script_dir, rf_script_file = self.getRFFilePath(sheet_param, rf_script_file)
        proc_list.append(Line.RFPath(rf_script_file))
        # proc_list.append(Line.Comment("RFIC_Script Write from Excel Param."))

        # proc_list.append(Line.Comment("Pre-AI_WeightData Setting"))#

        proc_list.append(Line.Comment("AI-WeightData-Script"))
        ai_weight_dir, ai_weight_files = self.getAIWeightFilePath(sheet_param, AI_weights)
        proc_list.append(Line.AIPath(ai_weight_dir))
        proc_list.append(Line.AIFile(ai_weight_files))

        # proc_list.append(Line.Comment("select AI_WeightData Excel Param."))
        #
        # proc_list.append(Line.Comment("Post-AI_WeightData Setting"))#

        for sheet_name, sheet in sheet_param['workbook'].items():
            if sheet_name[0] != "$" or sheet_name in ('$RevisionHistory', '$AI_WeightData'):
                continue
            sheet_text = sheet_name[1:] + ' Parameters'
            proc_list.append(Line.Comment(sheet_text))
            for reg in sheet['Registers']:
                proc_list.append(Line.Reg(reg[1], reg[2]))

        return proc_list


import abc
import re
import typing
from pathlib import Path

class ProcessListSymbol:
    '''
    Mapping 文本 與 process list 每一行表頭字串的 Configs類別物件
    '''
    RegSymbol = "Register"
    CommentSymbol = "Remark"
    RFFileSymbol = "RFFile"
    AIWeightPathSymbol = "AIWeightPath"
    AIWeightFilesSymbol = "AIWeightFiles"
    def getScriptSymbol(self, symbol:str)->typing.Optional[str]:
        return { self.RegSymbol: 'reg_write',
                 self.CommentSymbol: '//',
                 # ProcessListSymbol.WeightFileSymbol: '// WeightFile',
                 self.RFFileSymbol: '// RFFile',
                 self.AIWeightPathSymbol: '// AIWeightPath',
                 self.AIWeightFilesSymbol: '// AIWeightFiles',
                 }.get(symbol, None)

class Line:
    '''
    返還 Process list 每行根據表頭會有不同的文字格式的物件。
    '''
    def __init__(self, list_symbol:ProcessListSymbol=ProcessListSymbol()):
        self.list_symbol = list_symbol

    def Comment(self, comment: str = '') -> tuple:
        return (self.list_symbol.CommentSymbol, str(comment))


    def Reg(self, addr: int, val: int) -> tuple:
        return (self.list_symbol.RegSymbol, addr, val)


    def RFPath(self, path:str) -> tuple:
        return (self.list_symbol.RFFileSymbol, str(path))


    def AIFile(self, path:list) -> tuple:
        return (self.list_symbol.AIWeightFilesSymbol, path)


    def AIPath(self, path:str) -> tuple:
        return (self.list_symbol.AIWeightPathSymbol, str(path))

class ProcessList(list):
    def __init__(self, list_symbol:ProcessListSymbol=ProcessListSymbol()):
        super().__init__([])
        self.list_symbol = list_symbol
        self.line = Line(self.list_symbol)

    @abc.abstractmethod
    def fromSheetParam(self, sheet_param, rf_script_file:str=None, AI_weights:list=None)->typing.Optional[list]:
        return

    def fromText(self, file_path:str)->list:
        assert Path(file_path).is_file()
        self.clear()
        regex = re.compile(r'0x[0-9A-Fa-f]+')
        pls = self.list_symbol
        Line = self.line
        with open(file_path) as in_file:
            for line in in_file:
                if line.find(pls.getScriptSymbol(pls.RegSymbol)) >= 0:
                    val = regex.findall(line)
                    if len(val) >= 2:
                        self.append(Line.Reg(int(val[0], 16), int(val[1], 16)))

                elif line.find(pls.getScriptSymbol(pls.CommentSymbol)) >= 0:

                    if line.find(pls.getScriptSymbol(pls.RFFileSymbol)) >= 0:
                        val = line.split(':')
                        self.append(Line.RFPath(val[1].strip()))

                    elif line.find(pls.getScriptSymbol(pls.AIWeightPathSymbol)) >= 0:
                        val = line.split(':')
                        self.append(Line.AIPath(val[1].strip()))

                    elif line.find(pls.getScriptSymbol(pls.AIWeightFilesSymbol)) >= 0:
                        val = line.split(':')
                        files = val[1].strip().split(' ')
                        self.append(Line.AIFile(files))
                    else:
                        val = line.replace(pls.getScriptSymbol(pls.CommentSymbol), "")
                        self.append(Line.Comment(val.strip()))
        return self

    def genText(self, file_path:str):
        assert len(self) != 0,'Empty process list!'
        if not Path(file_path).parent.is_dir():
            Path(file_path).parent.mkdir(exist_ok=True)
        proc_list = self
        pls = self.list_symbol
        with open(file_path, 'w') as script_list:
            for line in proc_list:
                if line[0] == pls.RegSymbol:
                    l = f"{pls.getScriptSymbol(pls.RegSymbol)} ( 0x{line[1]:08X}, 0x{line[2]:08X});"
                elif line[0] == pls.CommentSymbol:
                    l = f'{pls.getScriptSymbol(pls.CommentSymbol)} {line[1]}'
                elif line[0] == pls.RFFileSymbol:
                    l = f'{pls.getScriptSymbol(pls.RFFileSymbol)} : {line[1]}'
                elif line[0] == pls.AIWeightPathSymbol:
                    l = f'{pls.getScriptSymbol(pls.AIWeightPathSymbol)} : {line[1]}'
                elif line[0] == pls.AIWeightFilesSymbol:
                    l = f'{pls.getScriptSymbol(pls.AIWeightFilesSymbol)} : {" ".join(str(x) for x in line[1])}'
                else:
                    continue
                script_list.write(l + '\n')

    def setRegValue(self, addr, val, header:str=None):
        assert len(self) != 0, 'Empty process list!'
        pls = self.list_symbol
        read_line = False
        for line in self:
            if header is not None:
                if (line[0] == pls.CommentSymbol) and (line[1] == header):
                    read_line = True
            else:
                read_line = True

            if not read_line:
                continue

            if line[0] == pls.RegSymbol:
                if line[1] == addr:
                    line[2] = val

    def getRegValue(self, addr, field:tuple=None, header:str=None):
        assert len(self) != 0, 'Empty process list!'
        pls = self.list_symbol
        read_line = False
        for line in self:
            if header is not None:
                if (line[0] == pls.CommentSymbol) and (line[1] == header):
                    read_line = True
            else:
                read_line = True

            if not read_line:
                continue

            if (line[0] == pls.RegSymbol) and (line[1] != addr):
                val = int(line[2], 16)
                if field is not None:
                    vals = []
                    for f in field:
                        mask = 2 ** f - 1
                        vals.append(val & mask)
                        val = val >> f
                    return vals
                return val

        return None


    def getRFFilePath(self, sheet_param, rf_script_file):
        if rf_script_file is None:
            rf_script_dir = r'/Integration_Test_script/SOCA'
            rf_script_file = 'unset'
            RFIC_S2P_sheet = sheet_param['workbook'].get('$RFIC_S2P')
            if RFIC_S2P_sheet is not None:
                rf_script_dir = RFIC_S2P_sheet.get('FilePath')
                rf_script_file = RFIC_S2P_sheet.get('FileName')
        else:
            rf_script_dir = Path(rf_script_file).parent

        return rf_script_dir, rf_script_file

    def getAIWeightFilePath(self, sheet_param, AI_weights):
        if AI_weights is None:
            ai_weight_dir = sheet_param['workbook']['$AI_WeightData']['FilePath']
            ai_weight_files = sheet_param['workbook']['$AI_WeightData']['FileName']
        else:
            ai_weight_dir = 'unset'
            ai_weight_files = []
            for file in AI_weights:
                ai_weight_files.append(Path(file).stem)
                ai_weight_dir = Path(file).parent

        return ai_weight_dir, ai_weight_files
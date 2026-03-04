
import os.path
import time
import openpyxl as pxl
import re
import json
import copy
from KKT_Module.ksoc_global import kgl

class KsocExcelParser():
    @staticmethod
    def parsing(file_path):
        from  KKT_Module.SettingProcess.ExcelParsing.ParamSheet import ParamSheet
        print('Excel file path : {}'.format(file_path))
        param_sheet = ParamSheet(file_name=file_path)
        wb = pxl.load_workbook(file_path)
        param_sheet.parseKsocExcel(wb)
        wb.close()
        return param_sheet

class ParamDictGenerator():
    class K60168:
        Sheets_map={"RFIC S2P Set Process"       :'$RFIC_S2P',
                    "Adc_Mux Parameters"         :'$Adc_MUX',
                    "Tracking Parameters"        :'$Tracking',
                    "AIACC_MEM Parameters"       :'$AIACC_MEM',
                    "AIACC_Layer Parameters"     :'$AIACC_Layer',
                    "AIACC_PARAM Parameters"     :'$AIACC_PARAM',
                    "AIACC_Siamese Parameters"   :'$AIACC_Siamese',
                    "DSPRx20M_Unit_0 Parameters" :'$DSPRx20M_Unit_0',
                    "DSPRx625K_Unit_0 Parameters":'$DSPRx625K_Unit_0',
                    "DSPRx20M_Unit_1 Parameters" :'$DSPRx20M_Unit_1',
                    "DSPRx625K_Unit_1 Parameters":'$DSPRx625K_Unit_1',
                    "DSP_Motion Parameters"      :'$DSP_Motion',
                    }
    def __init__(self, std_param_dict_path=(kgl.KKTConfig + r'/HW_setting.json')):
        '''
        Generate hardware setting parameter dictionary
        '''
        assert os.path.isfile(std_param_dict_path)
        self._std_ParamDict_path = std_param_dict_path
        self._std_ParamDict = {}
        self._current_ParamDict = {}
        self._current_ParamDict_with_val = {}
        self._std_version = ''
        self._current_version = ''
        self.initGenerator(self._std_ParamDict_path)
        pass

    def initGenerator(self, std_ParamDict_path=None):
        if std_ParamDict_path is not None:
            assert os.path.isfile(std_ParamDict_path)
            self._std_ParamDict_path = std_ParamDict_path
        print(self._std_ParamDict_path)
        self._std_ParamDict = self.readJson(self._std_ParamDict_path)
        self._std_version = str(self._std_ParamDict['RevisionHistory']['Version'])
        self._current_ParamDict = self._std_ParamDict
        self._current_version = self._std_version

    def genParamDict(self, param_sheet):
        ''' Generate parameter dictionary from hardware excel. '''
        self._current_ParamDict = {}
        workbook = param_sheet.get('workbook')
        for k, v in workbook.items():
            if k == '$RevisionHistory':
                version = v.get('Version')
                if version is None:
                    print('version empty')
                self._current_ParamDict[k.split('$')[1]] = {'Version': version}
            elif k == '$AI_WeightData':
                continue
            else:
                self._current_ParamDict[k.split('$')[1]] = {}
                registers = workbook[k]['Registers']
                for register in registers:
                    names = workbook[k]['Registers_d'][register[0]]
                    Name = []
                    bitmap = []
                    Sign = []
                    val = {}
                    pos = 0
                    for name in names:
                        Name.append(name[4].strip())
                        Sign.append(name[0].strip())
                        if type(name[1]) == str:
                            # print(register)
                            # print(name)
                            pos = eval(name[1].replace(':', ','))[1]
                            size = eval(name[1].replace(':', ','))[0] - pos + 1
                            bitmap.append([size, pos])

                        elif (type(pos) and type(name[2])) == int:
                            bitmap.append([name[2], pos])
                            pos = pos + name[2]
                        # else:
                        #     print(register[0], name[4], pos, name[2])
                    self._current_ParamDict[k.split('$')[1]][str(register[4])] = [register[0], bitmap, Name, Sign, val]
        self._current_version = str(self._current_ParamDict['RevisionHistory']['Version'])
        return self._current_ParamDict

    def writeJson(self, dict=None, dictname=None):
        '''
           Write parameter dictionary to json file parse from hardware excel.
        '''
        if dictname is None:
            dictname = self._std_ParamDict_path
        if dict is None:
            assert self._current_ParamDict != {}, 'None cuurent param dict'
            dict = self._current_ParamDict
        with open(dictname , 'w') as outfile:
            json.dump(dict, outfile, ensure_ascii=False)
            outfile.write('\n')
        print('dict save')

    def readJson(self, path):
        ''' Write parameter dictionary to json file parse from hardware excel.'''
        with open(path, newline='') as json_file:
            param_dict = json.load(json_file)
        print('get dict')
        return param_dict

    def writeRegVal(self, read_procList, ParamDict=None):
        '''
           Write register value from process list to parameter dictionary.
        '''
        # sheets = list(ParamDict.keys())
        if ParamDict is None:
            ParamDict = copy.deepcopy(self._std_ParamDict)
        write = False
        sheet_name =''
        for l in read_procList:
            # print(l)
            if l[0] == 'Remark':
                sheet_name = self.K60168.Sheets_map.get(l[1])
                if sheet_name is None:
                    write = False
                    continue
                sheet_name = sheet_name.split('$')[1]
                write = True
            elif l[0] == "Register" and write:
                # if l[1]==1074462852:
                #     s=2
                addr = hex(l[1]).zfill(10).upper().replace('X', 'x')
                bitmap = ParamDict[sheet_name][addr][1]
                if type(ParamDict[sheet_name][addr][3]) is dict:
                    signlist = ParamDict[sheet_name][addr][4]
                else:
                    signlist = ParamDict[sheet_name][addr][3]
                val_list = val2vallist(bitmap, l[2], signlist)
                # print(addr, bitmap, signlist, val_list)
                if len(val_list) == len(ParamDict[sheet_name][addr][2]):
                    nameval = dict(zip(ParamDict[sheet_name][addr][2], val_list))
                    ParamDict[sheet_name][addr].insert(3, nameval)
                else:
                    print(ParamDict[sheet_name][addr], val_list, 'field not match')
            else:
                write = False
        self._current_ParamDict_with_val = ParamDict
        return ParamDict

def readProcListFromFile(filename):
    read_procList =[]
    regex = re.compile(r'0x[0-9A-Fa-f]+')
    with open(filename) as in_file:
        for line in in_file:
            if line.find(getSymbolString('RegSymbol')) >= 0:
                val = regex.findall(line)
                if len(val) >= 2:
                    read_procList.append(['RegSymbol', int(val[0], 16), int(val[1], 16)])
            elif line.find(getSymbolString('CommentSymbol')) >= 0:
                if line.find(getSymbolString('RFFileSymbol')) >= 0:
                    val = line.split(':')
                    read_procList.append(['RFFileSymbol', val[1].strip()])
                elif line.find(getSymbolString('AIWeightPathSymbol')) >= 0:
                    val = line.split(':')
                    read_procList.append(['AIWeightPathSymbol', val[1].strip()])
                elif line.find(getSymbolString('AIWeightFilesSymbol')) >= 0:
                    val = line.split(':')
                    files = val[1].strip().split(' ')
                    read_procList.append(['AIWeightFilesSymbol', files])
                else:
                    val = line.replace(getSymbolString('CommentSymbol'), "")
                    read_procList.append(['CommentSymbol', val.strip()])

    return read_procList

def getSymbolString(symbol):
    return{
        'RegSymbol'           : 'reg_write',
        'CommentSymbol'       : '//',
        # kgl.WeightFileSymbol    : '// WeightFile',
        'RFFileSymbol'        : '// RFFile',
        'AIWeightPathSymbol'  : '// AIWeightPath',
        'AIWeightFilesSymbol' : '// AIWeightFiles',
    }.get(symbol,None)

def val2vallist(bitsMap, val, signlist):
    val_list = []
    for i in range(len(bitsMap)):
        if signlist[i] in ['$UNSG32', '$UNSG33'] :
            mask = 2 ** bitsMap[i][0] - 1
            new_val =  val >> bitsMap[i][1]
            v = new_val & mask
            val_list.append(v)
        elif signlist[i] == '$SIGN32':
            mask = 2 ** (bitsMap[i][0]) - 1
            new_val =  val >> bitsMap[i][1]
            v = new_val & mask
            sign = bin(v)[2:].zfill(bitsMap[i][0])[0]
            v = int('0b'+bin(v)[2:].zfill(bitsMap[i][0])[1:], 2)
            if sign == '0':
                val_list.append(v)
            elif sign == '1':
                v = -((v ^ (2 ** (bitsMap[i][0]-1)) - 1) +1)
                val_list.append(v)
    return  val_list

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

def strToInt(s):
    try:
        return int(s)
    except ValueError:
        return None

def strToFloat(s):
    try:
        f = float(s)
        return f
    except :
        return None

if __name__ == '__main__':
    from KKT_Module.ksoc_global import kgl
    s = time.time()
    file_name = r'C:\Users\eric.li\Desktop\Python\0_Standard_Ksoc_Tool\KKT_Module\SettingProcess\Test_Param\1691T1R_Format\param\Hardware_setting_1T1R_64upsample_total128sample_32chirps_COMPLEX_1D_Tracking20220810.xlsx'
    p = KsocExcelParser.parsing(file_name)
    KsocHWSetting = ParamDictGenerator(os.path.join(kgl.KKTConfig, 'HW_setting.json'))
    KsocHWSetting.genParamDict(p)
    KsocHWSetting.writeJson()

    pd = KsocHWSetting.readJson(os.path.join(kgl.KKTConfig, 'HW_setting.json'))
    proc_list = readProcListFromFile(
        r'C:\Users\eric.li\Desktop\Python\KKT_Python_Module\TempParam\210906_SIAMESE_ON\param\param_210628_KSOCB_SIAMESE_ON.txt')

    pd_w = KsocHWSetting.writeRegVal(read_procList=proc_list)

    print(time.time() - s)
    input('any:')










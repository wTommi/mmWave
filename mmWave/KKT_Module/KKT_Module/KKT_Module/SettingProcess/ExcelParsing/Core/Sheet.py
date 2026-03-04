from KKT_Module.SettingProcess.ExcelParsing.Core import Register, SymbolChar, BitRow
from openpyxl.worksheet.worksheet import Worksheet
import typing
import abc
import re

base_dict = {
            'TRK_BA': 0x50000500,
            'DSPRx20M_Unit_0': 0x400D0000,
            'DSPRx625K_Unit_0': 0x400B0000,
            'DSPRx20M_Unit_1': 0x400F0000,
            'DSPRx625K_Unit_1': 0x40090000,
            'DSP_Motion': 0x4005C000,
            'AIACC': 0x40060000,
            'GCR_BA': 0x50000000,
            'CLK_BA': 0x50000200,
            'SPI_RFIC_BA': 0x400A0000,
            'AI_WEIGHT_BA': 0x20020000,
}
class Sheet:
    def __init__(self, name:str):
        # print(f'Gen sheet {name}')
        self.name = name
        self.column_idx = {}


    def __getitem__(self, item):
        if hasattr(self, item):
            return self.__getattribute__(item)
        return None

    def asDict(self)->dict:
        d={}
        for k,v in self.__dict__.items():
            d.setdefault(k,v)
        return d

    def get(self, item, ret=None):
        return self[item]

    def parseSheet(self, sheet:Worksheet):
        print(f'[Parsing Exel sheet ({sheet.title})]')
        self._getContent(sheet)

    def getColumns(self, sheet:Worksheet)->bool:
        idx = 0
        isKeySymbolFound = False
        for column in sheet.columns:
            if column[0].value == None:
                continue
            if column[0].value.find(SymbolChar.Detect + SymbolChar.Key) >= 0:
                self.column_idx[SymbolChar.Key] = idx
                isKeySymbolFound = True

            elif column[0].value.find(SymbolChar.Detect + SymbolChar.Offset) >= 0:
                self.column_idx[SymbolChar.Offset] = idx

            elif column[0].value.find(SymbolChar.Detect + SymbolChar.BitSize)>= 0:
                self.column_idx[SymbolChar.BitSize] = idx

            elif column[0].value.find(SymbolChar.Detect + SymbolChar.BitPos) >= 0:
                self.column_idx[SymbolChar.BitPos] = idx

            elif column[0].value.find(SymbolChar.Detect + SymbolChar.Name) >= 0:
                self.column_idx[SymbolChar.Name] = idx

            elif column[0].value.find(SymbolChar.Detect + SymbolChar.Value) >= 0:
                self.column_idx[SymbolChar.Value] = idx
            idx += 1
        if isKeySymbolFound:
            print(f'  Sheet({self.name}) columns = {self.column_idx.keys()}')
            return True
        print(f"[ERROR] Not find Key Symbol, sheet name = {sheet.title}")
        return False

    @abc.abstractmethod
    def _getContent(self, sheet:Worksheet):
        return

class RevisionSheet(Sheet):
    def __init__(self):
        super(RevisionSheet, self).__init__(name = "$RevisionHistory")
        self.Version:float = 0


    def _getContent(self, sheet:Worksheet):
        ver = 0
        for column in sheet.columns:
            if column[0].value.find(SymbolChar.Detect + SymbolChar.Version) >= 0:
                for cell in column:
                    v = RevisionSheet.strToFloat(cell.value)
                    if v != None and v > ver:
                        ver = v
                break
        self.Version = ver
        print(f'  latest Version: v{ver}')

    @staticmethod
    def strToFloat(s):
        try:
            f = float(s)
            return f
        except:
            return None

class FilePathSheet(Sheet):
    def __init__(self, name:str):
        super().__init__(name=name)
        self.FilePath = ''
        self.FileName = []

    def _getContent(self, sheet:Worksheet):
        if not self.getColumns(sheet):
            return
        for row in sheet.rows:
            if row[self.column_idx[SymbolChar.Key]].value == None:
                continue
            self.getFilePath(row)

    def getFilePath(self, row:tuple):
        if row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.FilePath) >= 0:
            ss = row[1].value.strip()
            self.FilePath = ss
            print(f'  File path :{ss}')
        elif row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.FileName) >= 0:
            ss = row[1].value.strip()
            if ss == None:
                raise Exception("[ERROR] No file name, sheetname = {0}".format(self.name))
            self.FileName.append(ss)
            print(f'  File name :{ss}')

class HWSettingSheet(FilePathSheet):
    @property
    def BaseAddressStr(self):
        return "0x{0:08X}".format(self.BaseAddress)
    @property
    def Registers(self):
        l = []
        for reg in self.registers:
            l.append(reg.attribute_list)
        return l
    @property
    def Registers_d(self):
        d = {}
        for reg in self.registers:
            d[reg.name] = [row.RowList for row in reg.bit_row]
        return d

    def __init__(self, name:str):
        super().__init__(name)
        self.registers:typing.List[Register] = []
        self.base_dict = base_dict
        self.BaseAddress = 0x00000000

    def __getitem__(self, item):
        if isinstance(item, str):
            chars = item.split("_")
            if chars[0] == 'ColIdx':
                return self.column_idx
            else:
                return super(HWSettingSheet, self).__getitem__(item)

    def asDict(self) ->dict:
        d = super().asDict()
        regs = []
        for reg in self.registers:
            regs.append(reg.asDict())
        d.update({'registers': regs})
        return d

    def _getContent(self, sheet:Worksheet):
        if not self.getColumns(sheet):
            return
        reg = None
        get_base = False
        for row in sheet.iter_rows(min_row=2):
            if row[self.column_idx[SymbolChar.Key]].value is None:
                continue

            self.getFilePath(row)

            if not get_base:
                get_base = self.getBaseAddress(row)

            if not get_base:
                continue

            is_reg_head, is_ignore = self.isRegisterHead(row)
            if is_reg_head:
                if reg is not None:
                    # last reg
                    reg.composeToValue()
                    if reg.value != None:
                        self.registers.append(reg)
                        print(f'  === Add reg "{reg.name}({reg.address_str})" to sheet "{self.name}" ===')
                reg = None
                if not is_ignore:
                    reg_addr_oft = int(row[self.column_idx[SymbolChar.Offset]].value.strip(), base=16)
                    reg_name = row[self.column_idx[SymbolChar.Name]].value.strip()
                    reg = Register(name=reg_name, base=self.BaseAddress, offset=reg_addr_oft)
                    print(f'  ==== Gen Register({reg.name}) base: {reg.base_str}, offset: {reg.offset_str}, address: {reg.address_str}====')
                continue

            if reg is not None:
                bit_row = self.getRegisterContent(row, reg)
                if bit_row is not None:
                    reg.bit_row.append(bit_row)

        if reg is not None:
            # last reg
            reg.composeToValue()
            if reg.value != None:
                self.registers.append(reg)
                print(f'  === Add reg "{reg.name}({reg.address_str})" to sheet "{self.name}" ===')


    def getBaseAddress(self, row:tuple):
        if row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.BaseAddr) >= 0:
            base = self.getBaseAddr(row[self.column_idx[SymbolChar.Offset]].value.strip())
            assert base != None, f'Base address in wrong format. Wrong format = {row[self.column_idx[SymbolChar.Offset]].value.strip()}'
            self.BaseAddress = base
            print(f'  Sheet({self.name}) base address = {self.BaseAddressStr}')
            return True
        return False

    def getBaseAddr(self, addr)->int:
        if re.match('^.*\s#0x[A-z0-9]{8}$', addr):
            print(f'Base name :{addr.split("#")[0]}')
            return int(addr.split('#')[-1], 16)
        return self.base_dict.get(addr, None)

    def isRegisterHead(self, row:tuple)->typing.Tuple[bool, bool]:
        get_head = True
        ignore = True
        if row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.Reg32) >= 0:
            # Is head row of register
            ignore = False
        elif row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.IgnoreReg) >= 0:
            # Is head row of register but is ignorable.
            ignore = True
        else:
            get_head = False
        return get_head, ignore

    def getRegisterContent(self,row:tuple, reg:Register)->typing.Optional[BitRow]:
        if row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.UnsignedInt) >= 0:
            ValueType = row[self.column_idx[SymbolChar.Key]].value.strip()


        elif row[self.column_idx[SymbolChar.Key]].value.find(SymbolChar.Detect + SymbolChar.SignedInt) >= 0:
            ValueType = row[self.column_idx[SymbolChar.Key]].value.strip()

        else:
            return None

        if row[self.column_idx[SymbolChar.Value]].value == None:
            print(f"Row's value empty sheet={self.name}, reg_name={reg.name}, "
                  f"bit={row[self.column_idx[SymbolChar.BitPos]].value}, "
                  f"name={row[self.column_idx[SymbolChar.Name]].value}")

        bit_row = BitRow(ValueType=ValueType,
                                 BitPos=row[self.column_idx[SymbolChar.BitPos]].value,
                                 BitSize=row[self.column_idx[SymbolChar.BitSize]].value,
                                 Value=row[self.column_idx[SymbolChar.Value]].value,
                                 Name=row[self.column_idx[SymbolChar.Name]].value.strip())
        # print(f'  {bit_row}')
        return bit_row
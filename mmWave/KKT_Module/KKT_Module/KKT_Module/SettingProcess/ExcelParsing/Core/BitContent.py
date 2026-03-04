from KKT_Module.SettingProcess.ExcelParsing.Core.SymbolChar import SymbolChar
from typing import Optional,Generic, Union
from dataclasses import dataclass, field, asdict
import re


@dataclass
class BitRow:
    ValueType:str
    Name:str
    BitSize:Optional[int]=None
    BitPos:Union[str, tuple]=None
    Value:Optional[int]=None
    @property
    def RowDict(self)->dict:
        return asdict(self)
    @property
    def RowList(self)->list:
        type = f'{self.ValueType}'
        if (self.BitPos is None):
            pos = None
        else:
            pos = f'[{self.BitPos[0]}:{self.BitPos[1]}]'
        size = self.BitSize
        name = self.Name
        value = self.Value
        return [type, pos, size,value, name]

    def __post_init__(self):
        assert self.Name is not None, f'Column {SymbolChar.Name} is empty.'
        # assert self.Value is not None, f'Column {SymbolChar.Value} is empty.'
        assert self.ValueType is not None, f'Column {SymbolChar.Key} is empty.'
        self._convertBit()
        self._convertBitPos()
        if self.BitPos != None and self.BitSize != None:
            assert ((self.BitPos[0] - self.BitPos[1]) + 1) == self.BitSize, \
                f'Bits name "{self.Name}" column {SymbolChar.BitSize}={self.BitSize} and {SymbolChar.BitSize}={self.BitPos} not match'
        assert self.BitSize is not None, 'Bit size could not be None.'

        self._checkValueType(self.Value)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def get(self, item, ret=None):
        return self[item]


    def _checkValueType(self, value):
        if value is None:
            return
        if self.ValueType.find(SymbolChar.Detect + SymbolChar.UnsignedInt) >= 0:
            # if unsigned
            assert value >= 0 and value < (2 ** self.BitSize)
        elif self.ValueType.find(SymbolChar.Detect + SymbolChar.SignedInt) >= 0:
            # if signed
            assert value != 2 ** (self.BitSize - 1)
            assert abs(value) <= (2 ** (self.BitSize - 1))


    def _convertBitPos(self):
        if self.BitPos is None:
            return
        if type(self.BitPos) == str:
            regex = re.compile(r'\d+')
            bit_match = regex.findall(self.BitPos)
            assert len(bit_match) == 2 ,f'Bit size format error bit size = {self.BitPos}.'
            self.BitPos = int(bit_match[0]), int(bit_match[1])
        self.BitPos = tuple(self.BitPos)
        assert self.BitPos[0] - self.BitPos[1] >= 0, f'Bit size format error bit size = {self.BitPos}.'
        if self.BitSize:
            assert self.BitSize == (self.BitPos[0] - self.BitPos[1] +1)
        self.BitSize = self.BitPos[0] - self.BitPos[1] +1
        assert self.BitSize != 0, 'Bit size could not be zero.'

    def _convertBit(self):
        if self.BitSize is None:
            return
        self.BitSize = int(self.BitSize)
        assert self.BitSize != 0, 'Bit size could not be zero.'

if __name__ == '__main__':
    br = BitRow(ValueType=SymbolChar.SignedInt, Name='123', BitPos=(5,0))
    print(br.RowDict)
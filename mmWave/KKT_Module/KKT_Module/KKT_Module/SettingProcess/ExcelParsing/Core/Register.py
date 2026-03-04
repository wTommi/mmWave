from typing import List
from KKT_Module.SettingProcess.ExcelParsing.Core import BitRow, SymbolChar

class Register:
    @property
    def attribute_list(self):
        return [self.name, self.address, self.value, self.offset, self.address_str, self.value_str]
    @property
    def address_str(self):
        if self.address is None:
            return self.address
        return "0x{0:08X}".format(self.address)
    @property
    def offset_str(self):
        return "0x{0:08X}".format(self.offset)
    @property
    def base_str(self):
        return "0x{0:08X}".format(self.base)
    @property
    def value_str(self):
        return "0x{0:08X}".format(self.value)
    def __init__(self, name, base, offset, address=None):
        self.name = name
        self.base = base
        self.offset = offset
        self.address = self.composeAddress(self.base, self.offset, address)
        self.value:int = 0
        self.bit_row:List[BitRow] = []

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, address={self.address_str}, value={self.value_str})'

    def asDict(self)->dict:
        d = {}
        bit_row = []
        for k, v in self.__dict__.items():
            if k not in ('name', 'address', 'value', 'bit_row'):
                continue
            if k == 'bit_row':
                for row in self.bit_row:
                    bit_row.append(row.RowDict)
                    v = bit_row
            d.update({k:v})
        return d

    def get(self, item, ret=None):
        return self[item]

    def composeAddress(self, base=None, offset=None, address=None):
        if address:
            return address
        return offset + base

    def composeToValue(self):
        cvt_by_bit_pos = False
        bit_offset = 0
        for bits in self.bit_row:
            if bits.Value is None:
                self.value = None
                break
            if bits.BitSize is None and bits.BitPos is None:
                raise Exception(
                    f"Register({self.name}) columns '{SymbolChar.BitPos}' and '{SymbolChar.BitSize}' empty in content name={bits.Name}")

            if (self.bit_row[0].BitPos is not None) or cvt_by_bit_pos == True:
                # convert value refer to bits position.
                cvt_by_bit_pos = True

            # FOR RDI VALUE FLAG
            #  if (cnt[4] == 'RAW_MODE_B') and (cnt[1] == '[5:5]'):
            #      if kgl.raw_flag == 'RawData':
            #          val = 0
            #      elif kgl.raw_flag == 'RDIData':
            #          val = 1
            #      print("val=",val)


            if cvt_by_bit_pos:
                self.value = Register.convertRegByBitPos(self.value, bits.BitPos, bits.Value)

                # reg_val = cls.__convertRegByBitpos(reg_name, reg_adr_oft, cnt_list)
            else:
                self.value = Register.convertRegByBitSize(self.value, bits.BitSize, bits.Value, bit_offset)
                bit_offset += bits.BitSize
                # reg_val = cls.__convertRegByBbitsize(reg_name, reg_adr_oft, cnt_list)


        # return [reg_name, reg_adr_oft + base_addr, reg_val, reg_adr_oft, "0x{0:08X}".format(reg_adr_oft + base_addr),
        #         "0x{0:08X}".format(reg_val)]

    @staticmethod
    def convertRegByBitSize(reg_val:int, bit_size:int, bit_val:int, bit_shift:int=0):
        mask = 2**bit_size - 1
        val = bit_val & mask
        val <<= bit_shift
        reg_val |= val
        return reg_val & 0xffffffff

    @staticmethod
    def convertRegByBitPos(reg_val:int, bit_pos:tuple, bit_val:int):
        mask = 2**(bit_pos[0]-bit_pos[1]+1) - 1
        val = bit_val & mask
        val <<= bit_pos[1]
        reg_val |= val
        return reg_val & 0xffffffff
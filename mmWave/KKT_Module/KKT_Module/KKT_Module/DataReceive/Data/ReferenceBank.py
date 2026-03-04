from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
from typing import Optional
class R_Bank(Data):
    '''
    Reference bank 為一個 shape=(ch, sample), dtype='int16'的 ndarray。
    '''
    def __init__(self, data, ch=3, sample=128):
        super().__init__(data)
        self.ch=ch
        self.sample = sample

    def fixData(self, data, **kwargs)->np.ndarray:
        return np.asarray(data, dtype='int16')

    @staticmethod
    def convert168BInt16Array(data, sample=128, ch=3, ch_enable=0b111)->np.ndarray:
        retention = np.zeros((ch, sample), dtype='int16')
        data = np.reshape(data, (-1, sample))
        enable_rx_num = 0
        for i in range(ch):
            if (ch_enable >> i) & 0b1:
                retention[i, :] = data[enable_rx_num, :]
                enable_rx_num += 1
        return retention

    @staticmethod
    def convert169Int16Array(data, sample=128, ch=2)->np.ndarray:
        # 將每個值右移10 bit
        arr_shifted = np.right_shift(data, 10)
        # 轉換為int16的陣列
        data = arr_shifted.astype(np.int16)

        retention = np.zeros((ch, sample), dtype='int16')
        data = np.reshape(data, (-1, sample))
        for i in range(ch):
            retention[i] = data[i]
        return retention

class IR_Bank(Results):
    # def __init__(self):
    #     super().__init__()
    #     self.R_bank = None

    @property
    def R_bank(self)->Optional[R_Bank]:
        return self['R_bank']

    @R_bank.setter
    def R_bank(self, data):
        if isinstance(data , R_Bank):
            self['R_bank']=data
        else:
            self['R_bank']=R_Bank(data)
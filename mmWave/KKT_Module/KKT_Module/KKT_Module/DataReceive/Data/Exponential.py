from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
from typing import Optional
class Exponential(Data):
    def __init__(self, data):
        super(Exponential, self).__init__(data)

    def fixData(self, data, **kwargs):
        return data

    @staticmethod
    def convertRegisterVal(data)->np.ndarray:
        val_line = ''
        for v in data:
            hex_val = hex(v).split('0x')[1].zfill(8)
            val_line = hex_val + val_line
        exponential = []
        for i in range(len(val_line), 0, -3):
            dec_val = int(val_line[i - 3:i], 16)
            dec_val = unsign2sign(dec_val, 12)
            exponential.append(dec_val)
        return np.asarray(exponential).astype('int16')

class SoftMax(Exponential):...

class Siamese(Exponential):...

class FcLast(Exponential):...

class ISoftMax(Results):
    @property
    def softmax_exp(self)->Optional[SoftMax]:
        return self['softmax_exp']

    @softmax_exp.setter
    def softmax_exp(self, data):
        if isinstance(data , Exponential):
            self['softmax_exp']=data
        else:
            self['softmax_exp']=SoftMax(data)

class ISiamese(Results):
    @property
    def siamese_exp(self)->Optional[Siamese]:
        return self['siamese_exp']

    @siamese_exp.setter
    def siamese_exp(self, data):
        if isinstance(data , Exponential):
            self['siamese_exp']=data
        else:
            self['siamese_exp']=Siamese(data)

class IFcLast(Results):
    @property
    def fc_last_exp(self)->Optional[FcLast]:
        return self['fc_last_exp']

    @fc_last_exp.setter
    def fc_last_exp(self, data):
        if isinstance(data , Exponential):
            self['fc_last_exp']=data
        else:
            self['fc_last_exp']=FcLast(data)

def unsign2sign(x, bit):
    '''
    return sign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x >= 0 and x < 2 ** (bit-1):
        y = x
    elif x >= 2 ** (bit-1) and x < 2**bit:
        y = x - 2**(bit)
    else:
        raise Exception('Value is out of bit range')
    return y

if __name__ == '__main__':
    import time
    class TestResults(ISoftMax, ISiamese):...
    res = TestResults()
    r = np.arange(16)
    r = r/r.sum()
    s = time.time_ns()
    for _ in range(100000):
        exp = SoftMax(r)
        res.softmax_exp = exp
    print(res.softmax_exp.data)
    print(f'{(time.time_ns() - s) / 100000 / (10 ** 6):.4f} ms')
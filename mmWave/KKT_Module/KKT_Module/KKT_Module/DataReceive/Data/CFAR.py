from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
from typing import Optional

class CFAR(Data):
    '''
    CFAR 為一個 shape=(32), dtype='uint16'的 ndarray。
    '''
    def __init__(self, data):
        super().__init__(data)

    def fixData(self, data, **kwargs)->np.ndarray:
        return np.asarray(data, dtype='uint16')

    @staticmethod
    def convertRegisterVal(data)->np.ndarray:
        data = np.asarray(data, dtype='uint32')
        dt = np.dtype('uint16')
        # dt = dt.newbyteorder('>')
        data = np.frombuffer(data, dtype=dt)
        return data

class IMax(Data):
    '''
    IMax 為一個 0~31的整數。
    '''
    def __init__(self, data:np.ndarray):
        super().__init__(data)

    def fixData(self, data, **kwargs):
        return data

    @staticmethod
    def convertRegisterVal(data)->int:
        data = np.asarray(data)
        data = np.frombuffer(data, dtype='uint16')
        return data[:1]

class ICFAR(Results):
    @property
    def CFAR(self)->Optional[CFAR]:
        return self['CFAR']

    @CFAR.setter
    def CFAR(self, data):
        if isinstance(data , CFAR):
            self['CFAR']=data
        else:
            self['CFAR']=CFAR(data)

class IIMax(Results):
    @property
    def IMax(self)->Optional[IMax]:
        return self['IMax']

    @IMax.setter
    def IMax(self, data):
        if isinstance(data , IMax):
            self['IMax']=data
        else:
            self['IMax']=IMax(data)

if __name__ == '__main__':
    r = IIMax()
    data = np.asarray([0xFFFF0001, 0xFFFF0002,0xFFFF0003,0xFFFF0004,0xFFFF0005,0xFFFF0006,0xFFFF0007,0xFFFF0008,
                       0xFFFF0001, 0xFFFF0002,0xFFFF0003,0xFFFF0004,0xFFFF0005,0xFFFF0006,0xFFFF0007,0xFFFF0008,],dtype='uint32')
    data = IMax.convertRegisterVal(data)
    r.IMax = IMax(data)
    print(r)
    print(r['IMax'])
    print(r.IMax.data)
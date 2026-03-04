from typing import Optional
from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
import time
class Tracking(Data):
    '''
    data 為一個 shape=3, dtype='int16'的 ndarray。
    '''
    def __init__(self, data:int, axis:tuple=('x','y','z')):
        self.axis = axis
        super(Tracking, self).__init__(data)

    def fixData(self, data, **kwargs)->np.ndarray:
        return np.asarray(data, dtype='int16')

    @staticmethod
    def convertRegisterVal(data):
        data[0], data[1] = data[1], data[0]
        data = np.asarray(data)
        data = np.frombuffer(data, dtype='>i2')
        return data[3:0:-1]

    @staticmethod
    def convert169Data(data):
        x = np.asarray([data[0]])
        if len(data) == 2:
            y = np.asarray([data[1]])
        else:
            y = np.asarray([10])
        rtn_data = np.array([int(x), int(y), 0])
        return rtn_data

class ITracking(Results):
    @property
    def tracking(self)->Optional[Tracking]:
        return self['tracking']

    @tracking.setter
    def tracking(self, data):
        if isinstance(data , (Tracking, Data)):
            self['tracking']=data
        else:
            self['tracking']=Tracking(data)


if __name__ == '__main__':
    class TestResults(ITracking):...
    res = TestResults()

    a = [0x00020001, 0x00000003]
    r = Tracking.convertRegisterVal(a)
    print(r)
    s = time.time_ns()
    for _ in range(100000):
        # r = np.random.randint(0, 10, (3))
        pos = Tracking(r)
        res.tracking = pos
    print(res.tracking.data)
    print(f'{(time.time_ns() - s) / 100000 / (10 ** 6):.4f} ms')
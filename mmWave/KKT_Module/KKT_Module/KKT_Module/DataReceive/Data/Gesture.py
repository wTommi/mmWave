from KKT_Module.DataReceive.Core import Results, Data
import time
import numpy as np

class Gesture(Data):
    def __init__(self, data:int, ges_dict:dict = None):
        self.ges_dict = {} if ges_dict is None else ges_dict
        self.gesture = ''
        super(Gesture, self).__init__(data)

    def fixData(self, data, **kwargs):
        self.gesture = Gesture.getGestureName(data[0], self.ges_dict)
        return data

    @staticmethod
    def getGestureName(data:int, ges_dict:dict):
        return ges_dict.get(str(data), str(data))

    @staticmethod
    def convertRegisterVal(data, start_bit=0, end_bit=4):
        data = np.right_shift(data,start_bit)
        mask = np.binary_repr(0xFFFFFFFF)[(start_bit-end_bit-1):]
        data = np.bitwise_and(data, int(mask,2))
        if type(data) == np.ndarray:
            data = data[0:1]
        return data


class IGesture(Results):
    # def __init__(self):
    #     super().__init__()
    #     self.gesture = None

    @property
    def gesture(self)->Gesture:
        return self['gesture']

    @gesture.setter
    def gesture(self, data):
        if isinstance(data , Gesture):
            self['gesture']=data
        else:
            self['gesture']=Gesture(data)


if __name__ == '__main__':
    class TestResults(IGesture):...
    res = TestResults()
    r = Gesture.convertRegisterVal([0x52140001])
    print(r)
    s = time.time_ns()
    for _ in range(100000):
        raw_data = Gesture(r)
        res.raw_data = raw_data
    print(res.raw_data.data)
    print(f'{(time.time_ns() - s) / 100000 / (10 ** 6):.4f} ms')
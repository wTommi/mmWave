from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
import time

class RawData(Data):
    def __init__(self, data, ch=2, chirp=32, sample=128):
        '''
        :param data:
        :param ch: RX number
        :param chirp: HW chirp
        :param sample: sample
        '''
        self.channel = ch
        self.chirp = chirp
        self.sample = sample
        super(RawData, self).__init__(data)

    # def fixData(self, data, **kwargs):
    #     return RawData.reshapeRaw(data, self.channel, self.chirp, self.sample)
    #
    # @staticmethod
    # def reshapeRaw(data, ch, chirp, sample):
    #     data = np.asarray(data)
    #     return np.reshape(data, (ch, chirp, sample))

    @staticmethod
    def convert168AInt16Array(data, ch=2, chirp=32, sample=128):
        # FrameCount1 = data[start]
        # FrameCount2 = data[start + 1]

        data = np.reshape(data, (ch, chirp, sample))
        # print(f'FrameCount 1={FrameCount1}, FrameCount 2={FrameCount2}')
        return data

    @staticmethod
    def convert168BInt16Array(data, size, start=2, ch=2, chirp=32, sample=128):
        # FrameCount1 = data[start]
        # FrameCount2 = data[start + 1]

        data = data[start:size]
        ch1 = data[1::2]
        ch2 = data[::2]
        data = np.vstack((ch1, ch2))
        data = np.reshape(data, (ch, chirp, sample))
        # print(f'FrameCount 1={FrameCount1}, FrameCount 2={FrameCount2}')
        return data

    @staticmethod
    def convert169Rawdata(res, start, size, ch, chirps=32, samples=128):

        if res is None:
            return

        if ch == 2:
            data = np.reshape(res[start + 2:], (2, int(chirps / 2), samples))
        else:
            data = np.reshape(res[start + 2:start + 2 + size], (1, chirps, samples))
        return data

    @staticmethod
    def convert169RawdataForVerify(res, start, size, ch, chirps=32, samples=128):
        if res is None:
            return

        data = np.zeros(size, dtype='int16')
        if ch == 2:
            data = np.reshape(data, (chirps, samples))
            res = np.reshape(res[start + 2:], (2, int(chirps / 2), samples))
            data[0::2] = res[0]
            data[1::2] = res[1]
            data = np.reshape(data, size)
        else:
            data = res[start + 2:start + 2 + size]

        return data


class IRawData(Results):
    # def __init__(self):
    #     super().__init__()
    #     self.raw_data = None
    @property
    def raw_data(self)->RawData:
        return self['raw_data']


    @raw_data.setter
    def raw_data(self, data):
        if isinstance(data , RawData):
            self['raw_data']=data
        else:
            self['raw_data']=RawData(data)

if __name__ == '__main__':
    class TestResults(IRawData):...
    res = TestResults()
    r = np.arange(8192)
    s = time.time_ns()
    times = 100000
    for _ in range(times):
        raw_data = RawData(r)
        res.raw_data = raw_data

    print(res.raw_data.data)
    print(f'average :{(time.time_ns() - s) / times / (10 ** 6):.4f} ms')
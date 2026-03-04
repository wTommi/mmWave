import time
from KKT_Module.DataReceive.Core import Results, Data
import numpy as np
from typing import Optional

class FeatureMap(Data):
    def __init__(self, data, num=2, chirp=32, sample=128):
        self.num = num
        self.chirp = chirp
        self.sample = sample
        super(FeatureMap, self).__init__(data)
    def fixData(self, data, **kwargs):
        return np.reshape(data, (-1, 32, int(self.sample/4)))

    @staticmethod
    def convertFeatureMap(rdi_raw, dual_mode=False):
        rdi_raw = np.asarray(rdi_raw)
        shape_pack = rdi_raw.reshape([15, 18, 16])
        spec_pack = np.transpose(shape_pack, (1, 2, 0))
        map = np.zeros((2, 33, 33), dtype='uint16')
        spec_pack_up = spec_pack[0:9, :, :]
        spec_pack_down = spec_pack[9:, :, :]

        for idx in range(15):
            row_start = 2 * idx
            row_end = row_start + 3

            map[0,row_start:row_end, 0:16:2] = spec_pack_up[::3, ::2, idx]
            map[1,row_start:row_end, 0:16:2] = spec_pack_up[::3, 1::2, idx]

            map[0,row_start:row_end, 1:17:2] = spec_pack_up[1::3, ::2, idx]
            map[1,row_start:row_end, 1:17:2] = spec_pack_up[1::3, 1::2, idx]

            map[0,row_start:row_end, 2:18:2] = spec_pack_up[2::3, ::2, idx]
            map[1,row_start:row_end, 2:18:2] = spec_pack_up[2::3, 1::2, idx]

            map[0,row_start:row_end, 16:32:2] = spec_pack_down[::3, ::2, idx]
            map[1,row_start:row_end, 16:32:2] = spec_pack_down[::3, 1::2, idx]

            map[0,row_start:row_end, 17:33:2] = spec_pack_down[1::3, ::2, idx]
            map[1,row_start:row_end, 17:33:2] = spec_pack_down[1::3, 1::2, idx]

            map[0,row_start:row_end, 18:34:2] = spec_pack_down[2::3, ::2, idx]
            map[1,row_start:row_end, 18:34:2] = spec_pack_down[2::3, 1::2, idx]

        return map[0,:32, :32], map[1,:32, :32]

    @staticmethod
    def convert168BInt16Array(res, start, size):
        FrameCount = res[start]
        data = res[start:start+size]
        data = np.frombuffer(data, dtype='>u4')
        # print(f'FrameCount 1={(FrameCount & 0xFFFF)}, FrameCount 2={(FrameCount >> 16) & 0xFFFF)}')
        raw_RDI = convertBitArray(data,32,12)
        data = FeatureMap.convertFeatureMap(rdi_raw=raw_RDI)
        return data

    @staticmethod
    def convert169Data(res, channel):
        rdi = np.zeros((32, 32), dtype='int16')
        phd = np.zeros((32, 32), dtype='int16')
        if channel == 1:
            rdi = np.reshape(res, (32, 32))
        elif channel == 2:
            rdi = np.reshape(res[:int(len(res)/2)], (32, 32))
            phd = np.reshape(res[int(len(res) / 2):], (32, 32))

        return rdi, phd

class IMap(Results):
    @property
    def feature_map(self)->Optional[FeatureMap]:
        return self['feature_map']

    @feature_map.setter
    def feature_map(self, data):
        if isinstance(data , FeatureMap):
            self['feature_map']=data
        else:
            self['feature_map']=FeatureMap(data)

def convertBitArray(arry, src_bit, dis_bit, dtype='uint16'):
    niddles = int(src_bit/4)
    new_niddle_num = int(dis_bit/4)
    Hex_line = ''
    for i in arry:
        Hex = hex(i).split('0x')[1].zfill(niddles)
        Hex_line =  Hex + Hex_line


    hexs = [int(Hex_line[3*k:3*k+new_niddle_num],16) for k in range(int(len(Hex_line)/new_niddle_num))]

    output = hexs

    output.reverse()

    return np.asarray(output,dtype=dtype)

if __name__ == '__main__':
    class TestResults(IMap):...
    res = TestResults()
    d = np.arange(15*16*18)
    s = time.time_ns()
    for _ in range(100000):
        map = FeatureMap(FeatureMap.convertFeatureMap(d))
        res.feature_map = map
    print(res.feature_map.data)
    print(f'{(time.time_ns()-s)/100000/(10**6):.4f} ms')
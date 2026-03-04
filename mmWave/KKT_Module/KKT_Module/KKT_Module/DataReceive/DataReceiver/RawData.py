import numpy as np
from KKT_Module.DataReceive.Core import Receiver, Data
from KKT_Module.DataReceive.Results import Result168
from KKT_Module.DataReceive.Data import RawData
from KKT_Module.ksoc_global import kgl
from KKT_Module.DataReceive.ReceiverLog import log


class RawDataReceiver(Receiver):
    def __init__(self, chirps:int=32, samples:int=128):
        '''
        Receive Raw data and frame count from hardware.

        :param chirps: chirps number.
        '''
        super(RawDataReceiver, self).__init__()
        self.__LastFrameCount = 0
        self.chirps = chirps
        self.samples = samples
        self.results = Result168()
        pass

    def trigger(self, **kwargs):
        self.setConfig(**kwargs)
        self.__LastFrameCount = 0
        self._ADC_Mux = kgl.ksoclib.readReg(0x50000544, 3, 0)
        rdi_enable = kwargs.get('rdi_enable')
        if rdi_enable is None:
            kgl.ksoclib.writeReg(0, 0x50000504, 5, 5, 0)
        # time.sleep(0.3)
        if self.chirps < 32:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 16)
        elif self.chirps < 64:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 32)
        else:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 64)
        log.info('switch Raw ')
        pass

    def getResults(self):
        '''
        :return: CH1 Raw data , CH2 Raw data
        '''
        result = kgl.ksoclib.massdatabufGet()
        if result is None:
            return None
        framecount1 = result[0]
        framecount2 = result[2]
        if self._ADC_Mux in [2, 4, 5]:
            result_ch1 = result[3]
            result_ch2 = result[1]
        else:
            result_ch1 = result[1]
            result_ch2 = result[3]

        log.debug(f'(framecount1/framecount2) = ("{framecount1} "/"{framecount2} ")')
        if framecount1 != framecount2:
            log.warning(f'(framecount1 != framecount2) = ("{framecount1} "/"{framecount2} ")')
        elif framecount1 == 0 and framecount2 ==0:
            pass
            # print("framcount1 = 0")
        elif framecount1 - 1 != self.__LastFrameCount and framecount1 != -1:
            log.warning("shift ", framecount1 - self.__LastFrameCount - 1)
        self.__LastFrameCount = framecount1
        # return result_ch1, result_ch2
        data = np.vstack((result_ch1, result_ch2))
        raw_data = RawData.convert168AInt16Array(data, 2, self.chirps)
        self.results.raw_data = RawData(raw_data, ch=2, chirp=self.chirps, sample=self.samples)

        # self.results.raw_data = RawData((result_ch1, result_ch2))
        self.results['frame_count'] = Data(data=np.asarray([framecount1, framecount2]))
        return self.results

    def stop(self):
        kgl.ksoclib.massdatabufStop()

if __name__ == '__main__':
    r = RawDataReceiver()
    res = r.getResults()







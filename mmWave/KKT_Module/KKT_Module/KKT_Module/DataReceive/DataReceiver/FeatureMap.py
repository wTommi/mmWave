import numpy as np
import time
from KKT_Module.DataReceive.Core import Receiver, Data
from KKT_Module.DataReceive.Results import Result168
from KKT_Module.DataReceive.Data import FeatureMap
from KKT_Module.ksoc_global import kgl
from KKT_Module.DataReceive.ReceiverLog import log



class FeatureMapReceiver(Receiver):
    def __init__(self, chirps:int=32):
        '''
        Receive RDI PHD map from hardware.

        :param chirps: chirps number.
        '''
        super(FeatureMapReceiver, self).__init__()
        self.__LastFrameCount = 0
        self.chirps = chirps
        self.results = Result168()
        pass

    def trigger(self, **kwargs):
        kgl.ksoclib.writeReg(1, 0x50000504, 5, 5, 0)
        log.info('switch RDI ')
        time.sleep(0.3)
        if self.chirps <= 35:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x0C)
        elif self.chirps <= 64:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x10)
        else:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x08)
        self._trigger = True
        pass

    def getResults(self):
        '''
        :return: RDI, PHD shape 32*32 array.
        '''
        result = kgl.ksoclib.massdatabufGet_RDI()

        if result is None:
            return None

        framecount1 = result[0]
        framecount2 = result[1]
        raw_RDI = result[2]

        log.debug(f'(framecount1/framecount2) = ({framecount1}/{framecount2})')

        if framecount1 != framecount2:
            log.warning(f"framecount1 != framecount2 ({framecount1}/{framecount2})")
        elif framecount1 == 0 and framecount2 ==0:
            pass
            # print("framcount1 = 0")
        elif framecount1 - 1 != self.__LastFrameCount and framecount1 != -1:
            log.warning(f"shift {framecount1 - self.__LastFrameCount - 1}" )
        self.__LastFrameCount = framecount1
        self.results.feature_map = FeatureMap(FeatureMap.convertFeatureMap(raw_RDI))
        self.results['frame_count'] = Data(data=np.asarray([result[0], result[1]]))
        return self.results

    def stop(self):
        kgl.ksoclib.massdatabufStop()
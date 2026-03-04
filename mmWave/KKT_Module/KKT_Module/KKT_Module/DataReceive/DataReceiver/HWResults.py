from KKT_Module.DataReceive.Core import Receiver
from KKT_Module.DataReceive.Results import Result168
from KKT_Module.DataReceive.Data import Gesture, Tracking, SoftMax
from KKT_Module.ksoc_global import kgl


class HWResultOpenPSMReceiver(Receiver):
    '''
    Rename from AllResultReceiver.

    Get all Hardware results without trigger receiver.
    '''
    def __init__(self):
        super(HWResultOpenPSMReceiver, self).__init__()
        self.results = Result168()
        pass

    def trigger(self):
        pass

    def getResults(self):
        return kgl.ksoclib.getAllResultsAsList()

    def stop(self):
        pass

class HWResultReceiver(Receiver):
    def __init__(self):
        '''
        Rename from GesturesReceiver.

        Read register and receive some hardware results.
        (Gesture, Axis and Exponential).
        '''
        super(HWResultReceiver, self).__init__()
        self.results = Result168()
        pass

    def trigger(self, **kwargs):
        pass

    def getResults(self):
        '''
        :return: Gesture, Axis and Exponential.
        '''
        res = kgl.ksoclib.getGestureResult()
        if res in None:
            return None
        self.results.gesture = Gesture(res[0])
        self.results.tracking = Tracking(res[1])
        self.results.softmax_exp = SoftMax(res[2])
        return self.results

    def stop(self):
        pass
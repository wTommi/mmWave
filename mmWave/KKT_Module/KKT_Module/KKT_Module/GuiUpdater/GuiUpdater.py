import time
import numpy as np
from collections import deque
from abc import ABCMeta, abstractmethod
from KKT_Module.DataReceive.Core import Results


class Updater(metaclass=ABCMeta):
    def __init__(self):
        self.Widgets = []
        self.win = None
        self.user_level = 1
        self.FPS_counter = FPSCounter()
        pass
    def __del__(self):
        self.deleteWidgets()

    def setup(self, wg):
        pass

    @abstractmethod
    def update(self, res:Results):
        pass

    def deleteWidgets(self):
        for widget in self.Widgets:
            try:
                widget.deleteLater()
            except Exception as error:
                print(error)
        pass

    def setChirp(self,chirp):
        pass

    def addWidgetToCanvas(self):
        pass

    def addWidgetToSublayout(self):
        pass

    def enableSublayoutWidget(self, enable):
        pass

    def setConfigs(self,**kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                print( 'Attribute "{}" not in updater.'.format(k))
                continue
            # assert hasattr(self, k), 'Attribute "{}" not in receiver.'.format(k)
            self.__setattr__(k,v)
            print('Attribute "{}", set "{}"'.format(k, v))
        pass

    def updateBufferData(self, res):
        return res

    def updateLoadData(self, load_data):
        return load_data

    def setWidgetParameters(self, settings):...

class FPSCounter:
    def __init__(self):
        self.s = None
        self.FPS = 0

    def reset(self):
        self.s = None
        self.FPS = 0
        pass

    def updateFPS(self):
        if self.s is None:
            self.s = time.time_ns()
        self.FPS = (10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)
        self.s = time.time_ns()
        return self.FPS

class DataBuffer:
    def __init__(self, buffer_len=None):
        '''
        Data buffer for received data, it will save latest frames data.

        :param buffer_len: numbers of frames to save temporary.
        '''
        self._buffer_len = buffer_len
        self._buffer = deque(maxlen=buffer_len)
        self.initBuffer(self._buffer_len)
        pass
    def __del__(self):
        self._buffer.clear()

    def getDataBuffer(self, as_array=False):
        '''
        Get the buffer.

        :return: latest frames data in List.
        '''
        if as_array:
            return np.asarray(self._buffer)
        else:
            return  self._buffer

    def updateBuffer(self, res):
        '''
        To update the buffer per frame.

        :param res: received data.
        '''
        self._buffer.append(res)
        # if self.buffer_number < self._buffer_len:
        #     self.buffer_number = self.buffer_number + 1

    def initBuffer(self, buffer_len=None):
        '''
        Init the buffer size.
        :param buffer_len: buffer size.
        '''
        if buffer_len:
            self._buffer_len = buffer_len
        self._buffer.clear()
        self._buffer = deque(maxlen=buffer_len)

    def setBuffer(self, buffer):
        self._buffer = deque(buffer, maxlen=self._buffer_len)

    def getBufferLength(self):
        return len(self._buffer)


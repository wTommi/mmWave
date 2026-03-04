from __future__ import annotations
import sys
import time
from typing import Optional, Any, Union, Callable, Dict
import threading
from KKT_Module.KKTModuleLogger import get_logger
from KKT_Module.GuiUpdater import Updater, FPSCounter
from KKT_Module.DataReceive import Receiver

log = get_logger(name='FRM')


def except_hook(args):
    sys.excepthook(*sys.exc_info())

threading.excepthook = except_hook

def singleton(cls):
    instances:Dict[object, FiniteReceiveMachine] = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            log.info('Create instance of {}'.format(cls.__name__))
        return instances[cls]
    return getinstance

class RepeatTimer():
    def __init__(self, interval:float, func):
        self.daemon = False
        self.interval = interval
        self.func = func
        self.thread = threading.Timer(interval=0, function=self.handle_function)
        self.thread.daemon = self.daemon

    def handle_function(self):
        self.func()
        self.thread = threading.Timer(self.interval, self.handle_function)
        self.thread.daemon = self.daemon
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class ReceiveThread(threading.Thread):
    @property
    def is_start(self)->bool:
        return self._is_start.is_set()

    def __init__(self, interval:float, func, *args, **kargs):
        super().__init__(*args, **kargs)
        self._is_start = threading.Event()   # Flag is True for pause the thread
        self._is_start.clear()
        self.__running = threading.Event()  # Flag is True for start the thread
        self.__running.clear()
        self._func = func
        self.interval = interval

    def run(self) -> None:
        if self.is_start:
            return
        self._is_start.set()
        while self.is_start:
            time.sleep(self.interval)
            self._func()

    def cancel(self):
        if not self.is_start:
            return
        self._is_start.clear()
@singleton
class FiniteReceiveMachine:
    '''
    Receive data from receiver and update to updater.
    '''
    _updater: Optional[Updater] = None
    _receiver: Optional[Receiver] = None
    _data_collect_handler: Optional[Callable] = None
    # _start_Thread: Union[RepeatTimer | ReceiveThread] = None
    _is_start = False
    def __init__(self, receiver:Optional[Receiver]=None):
        self.FPS_Counter = FPSCounter()
        self._receiver = receiver
        self._start_Thread: Union[None | ReceiveThread] = None

    def __del__(self):
        self.stop()
        log.info("Close Finite Receive Machine...")

    def __repr__(self):
        return f'Receiver={self._receiver}, Updater={self._updater}'

    def setFRM(self, receiver:Receiver, updater:Updater=None):
        self.setReceiver(receiver)
        self.setUpdater(updater)

    def setDataCollectHandler(self, handler:Callable):
        self._data_collect_handler = handler

    def setReceiver(self, receiver):
        if self._is_start:
            raise Exception(f'Disable to set Receiver when FRM is launching.')
        self._receiver = receiver

    def setReceiverConfigs(self, **kwargs):
        if self._is_start:
            raise Exception(f"Disable to set Receiver's configs when FRM is launching.")
        self._receiver.setConfigs(**kwargs)

    def setUpdater(self, updater):
        if self._is_start:
            raise Exception(f'Disable to set Updater when FRM is launching.')
        self._updater = updater

    def trigger(self, **trigger_arg):
        if self._receiver is None:
            raise Exception(f'Disable to trigger FRM without delegate the receiver.')
        # receiver_config = ReceiverConfigs(os.path.join(kgl.KKTConfig, 'Reciver_Configs.ini'))
        #
        # config = receiver_config.getConfig(self._receiver.__class__.__name__)
        # trigger_arg.update(config)
        self._receiver.trigger(**trigger_arg)

    def start(self, interval:float=0, buffer=False):
        if (self._start_Thread) and (self._start_Thread.is_start):
            log.info('Your machine is launching')
            return
        if self._receiver is None:
            raise Exception(f'Disable to launch FRM without delegate the receiver.')
        self._start_Thread = ReceiveThread(interval, self.get)
        self._start_Thread.daemon = True
        self._start_Thread.interval = interval
        self._start_Thread.start()
        log.info('start FSM')


    def stop(self):
        if (self._start_Thread is None) or (not self._start_Thread.is_start):
            log.info("You can't stop the machine if it's not launching")
            return
        if self._receiver is None:
            raise Exception(f'Disable to launch FRM without delegate the receiver.')
        self._start_Thread.cancel()
        self._start_Thread.join(timeout=3)
        log.info('stop FRM')
        if self._receiver is not None:
            self._receiver.stop()

    def pause(self):
        if (self._start_Thread is None) or (not self._start_Thread.is_start):
            log.info("You can't stop the machine if it's not launching")
            return
        log.info('pause FRM')
        self._start_Thread.cancel()

    def get(self):
        log.debug('getting results')
        res = self._receiver.getResults()
        if res is None:
            return
        # print(res)
        if self._data_collect_handler is not None:
            self._data_collect_handler(res)
        if self._updater is not None:
            self._updater.update(res)
        self.FPS_Counter.updateFPS()

    def setUpdaterParameters(self, settings):
        if self._updater is not None:
            self._updater.setWidgetParameters(settings)
        pass

FRM:FiniteReceiveMachine = FiniteReceiveMachine()










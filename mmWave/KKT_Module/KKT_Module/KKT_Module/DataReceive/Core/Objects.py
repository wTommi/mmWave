from abc import ABCMeta, abstractmethod
from typing import Optional,Dict
from KKT_Module.DataReceive.ReceiverLog import log
from functools import wraps

class Data:
    _data = None
    def __init__(self, data):
        self.data = data

    def __repr__(cls):
        attrs = [f'{attr}={val}' for attr, val in cls.__dict__.items() if not attr.startswith("_")]
        display_name = cls.__class__.__name__ if not cls.__class__.__name__.startswith("_") else ""
        return "{}({})".format(display_name, (", ").join(attrs))

    @property
    def data(self):
        '''
        提取資料
        '''
        # if self._data is not None:
        #     data = self.fixData(self._data)
        return self._data

    @data.setter
    def data(self, data):
        '''
        存入資料並作統一化
        '''
        if data is not None:
            data = self.fixData(data)
        self._data = data

    def fixData(self, data, **kwargs):
        '''
        實作資料格式整合的抽象方法。
        '''
        return data

class Results:
    def __init__(self):
        self._data_dict :Dict[str, Data] = {}

    def __repr__(cls):
        attrs = [f'{attr}={val}' for attr, val in cls._data_dict.items() if not attr.startswith("_")]
        display_name = cls.__class__.__name__ if not cls.__class__.__name__.startswith("_") else ""
        return "{}({})".format(display_name, (", ").join(attrs))

    def items(self):
        return self._data_dict.items()

    @classmethod
    def new(cls, *args, **kwargs):
        return cls()

    def __setitem__(self, key, value):
        self.setData(key, value)

    def __getitem__(self, item):
        return self.getData(item)

    def get(self, key:str, default=None):
        return self._data_dict.get(key, default)

    def setData(self, name:str, data:Data):
        self._data_dict.update({name: data})

    def getData(self, name:str)->Optional[Data]:
        return self._data_dict.get(name)

def wrap_trigger():
    def decorator(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            log.info(f'Starting receiver : {self.__class__.__name__}')
            func(self, *args, **kwargs)
            self._trigger = True
            log.info('Started receiver')
            return func
        return wrap
    return decorator
def wrap_getResults():
    def decorator(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if not self._trigger:
                return
            log.debug('get Results')
            self.results = self.results.new()
            return func(self, *args, **kwargs)
        return wrap
    return decorator
def wrap_stop():
    def decorator(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            log.info(f'Stopping receiver : {self.__class__.__name__}')
            func(self, *args, **kwargs)
            self._trigger = False
            return func
        return wrap
    return decorator

class Receiver(metaclass=ABCMeta):
    '''
    Data receiver.
    '''
    def __init__(self):
        self._trigger = False
        self.results:Optional[Results] = None
        pass
    @wrap_trigger()
    @abstractmethod
    def trigger(self, **kwargs)->None:
        '''
        Before start to get the data which receivedH5 from the receiver,
        you have to init some configs and trigger it.
        '''
        ...
    @wrap_getResults()
    @abstractmethod
    def getResults(self)->Results:
        ...

    @wrap_stop()
    @abstractmethod
    def stop(self):
        ...

    def setConfig(self, **kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                log.info( 'Attribute "{}" not in receiver.'.format(k))
                continue
            # assert hasattr(self, k), 'Attribute "{}" not in receiver.'.format(k)
            self.__setattr__(k,v)
            log.info('Attribute "{}", set "{}"'.format(k, v))

    # @abstractmethod
    # def _triggerProc(self, **kwargs)->bool:...
    #
    # @abstractmethod
    # def _getResultsProc(self)->Results:...
    #
    # @abstractmethod
    # def _stopProc(self):...



if __name__ == '__main__':
    r= Results()
    r['AAA'] = Data(133)
    print(r)
    print(r['AAA'])





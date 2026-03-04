from __future__ import annotations
import sys, os
from pathlib import Path
from KKT_Library.KSOCLib import KsocLib
from KKT_Library.LibLog import lib_logger as log
from typing import Any, Union, Dict, Protocol,Optional, Sequence, Tuple
import numpy as np


def singleton(cls):
    instances:Dict[object, Lib] = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            log.info('Create instance of {}'.format(cls.__name__))
        return instances[cls]
    return getinstance


@singleton
class Lib:
    '''
    Singleton for KSOC lib.
    '''
    ksoclib:Optional[KsocLib] = None

    def __init__(self, lib_type:str='CSharp'):
        log.info('# ======== Set KKT Lib ===========')
        self.ksoclib = KsocLib(lib_type)




if __name__ == '__main__':
    lib = Lib()
    print('')
    input('any:')
    print(lib.ksoclib.connectDevice())
    print(lib.ksoclib.regRead(0x50000544, 1))



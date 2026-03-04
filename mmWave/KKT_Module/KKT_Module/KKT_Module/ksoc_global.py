from typing import Dict, Optional

class kgl:
    ksoclib = None
    KKTLibDll = ''
    KKTModule = ''
    KKTConfig = ''
    KKTImage = ''
    KKTSound = ''
    KKTTempParam = ''
    KKTRecord= ''
    @classmethod
    def setLib(cls):
        from KKT_Library import Lib
        kgl.ksoclib = Lib().ksoclib
        return kgl.ksoclib

class global_variable:
    chip_id = ''

global_variables = global_variable()


if __name__ == '__main__':
    input('any:')

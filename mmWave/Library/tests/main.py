import time

import numpy as np
import sys
from KKT_Library.KKTLib import Lib

def test_SoftMaxInterrupt():

    # print(Lib.ksoclib.connectDevice())
    # print(hex(Lib.ksoclib.readHWRegister(0x50000544, 1)))
    time.sleep(5)
    frm= 60
    Lib.ksoclib.switchSoftMaxInterrupt(0b1, 0, 0, (8192 + 2) * 2, 1, [])
    i = 0
    while i <= frm:
        res = Lib.ksoclib.getSoftMaxInterruptAsserted()
        if res is None:
            continue
        for k , v in res.items():
            if k == 3:
                v = np.reshape(v, (-1,130))
            if k == 0:
                print(f"raw frame cnt = {np.asarray(v[0], dtype='uint16')}")
            if k ==2:
                v = hex(v[0])
            print(f'action {k} {v}')

        # print(f'action 3 {np.asarray(res.get(3))}')
        # for j in range( len(list(res)) ):
        #     print('data size: {0}'.format(sys.getsizeof(list(res[j]))) )
        #     print(np.asarray(list(res[j])))
        i += 1
        print(f'loop index = {i}')

    Lib.ksoclib.switchSoftmaxInterrupt(0)
    Lib.ksoclib.closeDevice()

def test_EFuse_Read():
    print(Lib.ksoclib.connectDevice())
    print(hex(Lib.ksoclib.readHWRegister(0x50000544, 1)[0]))

    for i in range(16):
        res = Lib.ksoclib.readEFuseCmd(i)
        print(str(i) + ':' + str(res))

def test_SIC_Init():
    print(Lib.ksoclib.connectDevice())
    print(Lib.ksoclib.initSIC())


def test_read_register():
    print(hex(Lib.ksoclib.readHWRegister(0x50000544, 1)))


def test_set_param0():
    Lib.ksoclib.setDigiParam0()

def test_get_RX_phase_offset():
    print(Lib.ksoclib.getRXPhaseOffset())




if __name__ == '__main__':
    Lib = Lib()
    # Lib.ksoclib.switchLogMode(True)
    print('====')
    print(Lib.ksoclib.connectDevice())
    # test_EFuse_Read()

    # test_SoftMaxInterrupt()

    # test_SIC_Init()

    # test_read_register()
    # test_SoftMaxInterrupt()
    test_set_param0()
    test_get_RX_phase_offset()
    sys.exit(Lib.ksoclib.closeDevice())


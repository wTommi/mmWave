from KKT_Module.ksoc_global import kgl
import time
import numpy as np

class DigiController:
    @classmethod
    def clearSoftMaxInterrupt(cls):
        kgl.ksoclib.writeHWRegister_bit(1, 0x50000580, 8, 8, 0)
        kgl.ksoclib.writeReg(1, 0x50000580, 10, 10, 1)
        val = kgl.ksoclib.readReg(0x50000544, 12, 12)
        if val == 1:
            kgl.ksoclib.writeReg(0, 0x50000544, 12, 12, 0)
            kgl.ksoclib.writeReg(1, 0x50000544, 12, 12, 0)

    @classmethod
    def enableRDI(cls, enable: bool) -> bool:
        if enable:
            print('switch RDI ')
            kgl.ksoclib.writeReg(1, 0x50000504, 5, 5, 1)
        else:
            print('switch Raw')
            kgl.ksoclib.writeReg(0, 0x50000504, 5, 5, 1)
        return True

    @classmethod
    def getChirpNumber(cls):
        """
        For KSOC Tool use
        """
        chirp = kgl.ksoclib.readReg(0x50000530, 21, 16) + 1
        print('get chirp = {}'.format(chirp))
        return chirp

    @classmethod
    def getSampleNumber(cls):
        """
        For KSOC Tool use
        """
        sample = kgl.ksoclib.readReg(0x50000530, 26, 24)
        sample = sample * 64
        print('get sample = {}'.format(sample))
        return sample

    @classmethod
    def triggerRegSettingDoneAll(cls):
        RBCheck = False
        # triggerRegSettingDoneAll
        kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x40090084, 8, 8, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 8, 8, RBCheck)


    @classmethod
    def triggerSIC(cls):
        RBCheck = False
        kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 9, 9, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 9, 9, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x40090084, 9, 9, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 9, 9, RBCheck)

    @classmethod
    def triggerAIC(cls):
        RBCheck = False
        kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 0, 0, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 0, 0, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x40090084, 0, 0, RBCheck)
        kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 0, 0, RBCheck)

    @classmethod
    def stopSIC(cls):
        # stop SIC
        RBCheck = False
        kgl.ksoclib.writeReg(1, 0x400B0084, 10, 10, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400B00A4, 10, 10, RBCheck)
        kgl.ksoclib.writeReg(1, 0x40090084, 10, 10, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400900A4, 10, 10, RBCheck)

    @classmethod
    def unfreezeAIC(cls):
        RBCheck = False
        kgl.ksoclib.writeReg(0, 0x400B0098, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(0, 0x40090098, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(0, 0x400B00B8, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(0, 0x400900B8, 25, 25, RBCheck)

    @classmethod
    def freezeAIC(cls):
        RBCheck = False
        kgl.ksoclib.writeReg(1, 0x400B0098, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(1, 0x40090098, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400B00B8, 25, 25, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400900B8, 25, 25, RBCheck)

    @classmethod
    def stopAIC(cls):
        # stop SIC
        RBCheck = False
        kgl.ksoclib.writeReg(1, 0x400B0084, 1, 1, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400B00A4, 1, 1, RBCheck)
        kgl.ksoclib.writeReg(1, 0x40090084, 1, 1, RBCheck)
        kgl.ksoclib.writeReg(1, 0x400900A4, 1, 1, RBCheck)

    @classmethod
    def resetDSP(cls):
        kgl.ksoclib.writeReg(1, 0x5000000C, 18, 18)
        time.sleep(0.01)
        kgl.ksoclib.writeReg(0, 0x5000000C, 18, 18)

    @classmethod
    def updateSICMuxValue(cls):
        # from KKT_Module.SettingProcess.sic_func import muxcfg, UpdateMUXValue, find
        zdx = cls._UpdateMUXValue()
        u0c0, u0c1, u1c0, u1c1 = cls._UpdateMUXValue()
        idx1 = find(zdx, 1)
        if len(idx1) != 0:
            feedback1 = idx1[0]
        else:
            feedback1 = 2

        idx2 = find(zdx, 2)
        if len(idx2) != 0:
            feedback2 = idx2[0][0]
        else:
            feedback2 = 2

        idx3 = find(zdx, 3)
        if len(idx3) != 0:
            feedback3 = idx3[0][0]
        else:
            feedback3 = 2
        cls._muxcfg(u0c0, u0c1, u1c0, u1c1, feedback1, feedback2, feedback3)
        print("Overwrite SIC MUX: u0c0:", str(u0c0), " u0c1:", str(u0c1), " u1c0:", str(u1c0), " u1c1:", str(u1c1),
              " feedback1:", str(feedback1), " feedback2:", str(feedback2), " feedback3:", str(feedback3))

    @classmethod
    def _UpdateMUXValue(cls):
        global MUXValue
        data = kgl.ksoclib.regRead(0x50000544, 1)
        MUXValue = data[0]

        u0 = MUXValue & 0xF
        # u0 = 5
        print('u0: {}'.format(MUXValue & 0xF))
        u0c0, u0c1 = getCh(u0)
        u1 = (MUXValue >> 4) & 0xF
        # u1 = 5
        print('u1: {}'.format((MUXValue >> 4) & 0xF))
        u1c0, u1c1 = getCh(u1)
        return u0c0, u0c1, u1c0, u1c1

    @classmethod
    def _muxcfg(cls, u0c0_frmstartSel, u0c1_frmstartSel, u1c0_frmstartSel, u1c1_frmstartSel, rf1_sic_in_sel, rf2_sic_in_sel,
                rf3_sic_in_sel):
        print("--> [Func] muxcfg")
        RBCheck = True

        # %-------------------Basic:SIC input mux----------------
        kResult = kgl.ksoclib.writeReg(u0c0_frmstartSel, 0x400B0200, 1, 0, RBCheck)
        kResult = kgl.ksoclib.writeReg(u0c1_frmstartSel, 0x400B0200, 3, 2, RBCheck)
        kResult = kgl.ksoclib.writeReg(u1c0_frmstartSel, 0x400B0200, 5, 4, RBCheck)
        kResult = kgl.ksoclib.writeReg(u1c1_frmstartSel, 0x400B0200, 7, 6, RBCheck)

        kResult = kgl.ksoclib.writeReg(u0c0_frmstartSel, 0x40090200, 1, 0, RBCheck)
        kResult = kgl.ksoclib.writeReg(u0c1_frmstartSel, 0x40090200, 3, 2, RBCheck)
        kResult = kgl.ksoclib.writeReg(u1c0_frmstartSel, 0x40090200, 5, 4, RBCheck)
        kResult = kgl.ksoclib.writeReg(u1c1_frmstartSel, 0x40090200, 7, 6, RBCheck)

        kResult = kgl.ksoclib.writeReg(rf1_sic_in_sel, 0x400B0200, 10, 8, RBCheck)
        kResult = kgl.ksoclib.writeReg(rf2_sic_in_sel, 0x400B0200, 13, 11, RBCheck)
        kResult = kgl.ksoclib.writeReg(rf3_sic_in_sel, 0x400B0200, 16, 14, RBCheck)

        kResult = kgl.ksoclib.writeReg(rf1_sic_in_sel, 0x40090200, 10, 8, RBCheck)
        kResult = kgl.ksoclib.writeReg(rf2_sic_in_sel, 0x40090200, 13, 11, RBCheck)
        kResult = kgl.ksoclib.writeReg(rf3_sic_in_sel, 0x40090200, 16, 14, RBCheck)
        # %-----------------------------------------------------------

    @classmethod
    def setMUXParam(cls, AIMux, TrackingMux, Dim_sel, CH_valid):
        """
        For KSOC Tool use
        """
        # AIMUX
        kgl.ksoclib.writeReg(AIMux, 0x50000544, 3, 0, 1)
        # TrackingMux
        kgl.ksoclib.writeReg(TrackingMux, 0x50000544, 7, 4, 1)
        # Dim_sel
        kgl.ksoclib.writeReg(Dim_sel, 0x50000544, 9, 8, 1)
        # ch-valid
        kgl.ksoclib.writeReg(CH_valid, 0x50000504, 10, 8, 1)
        print(AIMux, TrackingMux, Dim_sel, CH_valid)
        pass

    @classmethod
    def getMuxParam(cls):
        """
        For KSOC Tool Gesture recording use
        """
        # AIMUX
        AIMux = kgl.ksoclib.readReg(0x50000544, 3, 0)
        # TrackingMux
        TrackingMux = kgl.ksoclib.readReg(0x50000544, 7, 4)
        # Dim_sel
        Dim_sel = kgl.ksoclib.readReg(0x50000544, 9, 8)
        # ch-valid
        CH_valid = kgl.ksoclib.readReg(0x50000504, 10, 8)
        param = (AIMux, TrackingMux, Dim_sel, CH_valid)
        print('Get Mux parameter: AIMUX={}, TrackingMux={}, Dim_sel={}, ch_valid={}'.format(*param))
        return param

    @classmethod
    def setFT_startPoint(cls, start_point):
        kgl.ksoclib.writeReg(start_point, 0x400D2008, 9, 2, 0)
        kgl.ksoclib.writeReg(start_point, 0x400D6008, 9, 2, 0)
        kgl.ksoclib.writeReg(start_point, 0x400F2008, 9, 2, 0)
        kgl.ksoclib.writeReg(start_point, 0x400F6008, 9, 2, 0)

class Digi168BController(DigiController):

    @classmethod
    def getFPGAResult(cls, first_addr, last_addr):
        val = kgl.ksoclib.readReg(0x50000580, 8, 8)
        if val == 1:
            # printMessage('Got FPGA result !')
            val_arry, addr_arry = kgl.ksoclib.readRangeRegisters(first_addr, last_addr)
            # printMessage(val_arry)
            return val_arry, addr_arry
        else:
            print('SoftMax is not 1')

    @classmethod
    def enableTDD(cls, enable: bool = 1):
        print('Enable TDD => {}'.format(enable))
        kgl.ksoclib.writeReg(enable, 0x5000004C, 0, 0, RBCheck=1)
        return

    @classmethod
    def checkDualMode(cls):
        return kgl.ksoclib.readReg(0x40000A1C, 17, 17)

    @classmethod
    def checkCh2MapType(cls):
        val = kgl.ksoclib.readReg(0x50000598, 0, 0)
        if val == 0:
            return 'PHD'
        elif val == 1:
            val2 = kgl.ksoclib.readReg(0x50000598, 1, 1)
            if val2 == 0:
                return 'MPL'
            elif val2 == 1:
                return 'OTT'

    @classmethod
    def checkExpType(cls):

        if kgl.ksoclib.readReg(0x4006053C, 22, 22):  # en_softmax_irq
            return 'exp_fx'
        if kgl.ksoclib.readReg(0x400604F8, 12, 12):  # en_sigmoid
            return 'sig_fx'
        elif kgl.ksoclib.readReg(0x400604F8, 13, 13):  # en_tanh
            return 'tanh_fx'
        elif kgl.ksoclib.readReg(0x400604F8, 14, 14):  # en_softmax
            return 'exp_fx'
        else:
            return 'fc_fx'

    @classmethod
    def readAGC(cls, frame=0):
        base_addr_dict = {'Unit0': 0x400D0000, 'Unit1': 0x400F0000}
        para_dict0 = {'AGC_ByPass': [0x00008040, 1, 1, False],
                      'samples_per_acc': [0x00008048, 15, 0, False],
                      'log_p_targ': [0x00008048, 31, 16, True],
                      'alpha': [0x0000804C, 12, 0, True],
                      'agc_gain_init': [0x0000804C, 24, 13, False],
                      'zValue': [0x0000805C, 15, 0, True],
                      'agc_gain': [0x00008060, 11, 0, False],
                      'i_part': [0x00008060, 19, 12, True],
                      }
        para_dict1 = {'AGC_ByPass': [0x00008080, 1, 1, False],
                      'samples_per_acc': [0x00008088, 15, 0, False],
                      'log_p_targ': [0x00008088, 31, 16, True],
                      'alpha': [0x0000808C, 12, 0, True],
                      'agc_gain_init': [0x0000808C, 24, 13, False],
                      'zValue': [0x0000809C, 15, 0, True],
                      'agc_gain': [0x000080A0, 11, 0, False],
                      'i_part': [0x000080A0, 19, 12, True],
                      }
        ch_list = {'CH0': para_dict0, 'CH1': para_dict1}
        AGC_list = []
        AGC_list.append(' ============  AGC param in frame = {} =========='.format(frame))
        # print(' ============  AGC param in frame = {} =========='.format(frame))
        for base_name, base_addr in base_addr_dict.items():
            for ch, para_dict in ch_list.items():
                AGC_list.append('[{}_{}]'.format(base_name, ch))
                # print('[{}_{}]'.format(base_name, ch))
                for name, addr_info in para_dict.items():
                    addr = base_addr_dict[base_name] + addr_info[0]
                    val = kgl.ksoclib.readReg(addr, addr_info[1], addr_info[2])
                    val = wrapValue(val, (addr_info[1] - addr_info[2] + 1), addr_info[3])
                    AGC_list.append('\t{}:　{}'.format(name, val))
                    # print('{}:　{}'.format(name, val))

        return AGC_list

    @classmethod
    def getTotalNNLayer(cls):
        return kgl.ksoclib.readReg(0x40060004, 5, 0)

    @classmethod
    def getGestureNumber(cls):
        return kgl.ksoclib.readReg(0x40060004, 16, 12)

    @classmethod
    def checkSiameseEnable(cls):
        return kgl.ksoclib.readReg(0x40060900, 1, 0)

class Digi169Controller(DigiController):
    @classmethod
    def getChirpNumber(cls):
        """
        For KSOC Tool use
        """
        chirps = int(kgl.ksoclib.readReg(0x60000530, 7, 0)) + 1
        samples = int(kgl.ksoclib.readReg(0x60000530, 28, 16))
        drop_chirp_en = int(kgl.ksoclib.readReg(0x60000594, 12, 12))
        drop_chirp_num = int(kgl.ksoclib.readReg(0x60000594, 11, 0) / samples)
        if drop_chirp_en == 1:
            chirps = int(chirps - drop_chirp_num)

        return chirps

    @classmethod
    def getSampleNumber(cls):
        """
        For KSOC Tool use
        """
        samples = int(kgl.ksoclib.readReg(0x60000530, 28, 16))
        upsample_en = int(kgl.ksoclib.readReg(0x600005BC, 31, 31))
        upsample_num = int(kgl.ksoclib.readReg(0x600005BC, 7, 0)) + 1
        if upsample_en == 1:
            samples = upsample_num

        return samples

    @classmethod
    def getSwitchMode(cls):
        """
        For KSOC Tool use
        """
        return kgl.ksoclib.readReg(0x680B00E4, 10, 8)

    @classmethod
    def setFT_startPoint(cls, start_point):
        ...

class Digi169A2Controller(DigiController):
    @classmethod
    def getChirpNumber(cls):
        """
        For KSOC Tool use
        """
        chirps = int(kgl.ksoclib.readReg(0x60000530, 7, 0)) + 1
        samples = int(kgl.ksoclib.readReg(0x60000530, 28, 16))
        drop_chirp_en = int(kgl.ksoclib.readReg(0x60000594, 12, 12))
        drop_chirp_num = int(kgl.ksoclib.readReg(0x60000594, 11, 0) / samples)
        if drop_chirp_en == 1:
            chirps = int(chirps - drop_chirp_num)

        return chirps

    @classmethod
    def getSampleNumber(cls):
        """
        For KSOC Tool use
        """
        samples = int(kgl.ksoclib.readReg(0x60000530, 28, 16))
        upsample_en = int(kgl.ksoclib.readReg(0x600005BC, 31, 31))
        upsample_num = int(kgl.ksoclib.readReg(0x600005BC, 11, 0)) + 1
        if upsample_en == 1:
            samples = upsample_num

        return samples

    @classmethod
    def getSwitchMode(cls):
        """
        For KSOC Tool use
        """
        return kgl.ksoclib.readReg(0x680B00E4, 10, 8)



class DigiControllerFactory:
    """
    Simple factory for digital controller.
    Those
    """
    @classmethod
    def createController(cls, chirp_id: str) -> DigiController:
        if chirp_id == 'K60168':
            return Digi168BController()
        elif chirp_id == 'K60169':
            return cls.select169Controller()
        else:
            raise ValueError(f'Invalid chip ID: {chirp_id}')

    @classmethod
    def select169Controller(cls) -> DigiController:
        """
        Read register address 0x6000_0000 to select 169 A0/A1  or A2

        If value get:
        0x0169_0000 -> A0/A1
        0x0169_0002 -> A2
        """
        reg_val = kgl.ksoclib.readHWRegister(0x6000_0000)
        if reg_val[0] == 0x0169_0000:
            return Digi169Controller()
        elif reg_val[0] == 0x0169_0002:
            return Digi169A2Controller()
        else:
            raise ValueError(f'Get the HW register Fail')

#####==========================
def find(source, target):
    zdx = np.array(source)
    return np.argwhere(zdx == target)


def getCh(u):
    o1 = 0
    o2 = 0

    if u == 0:
        o1 = 1
        o2 = 2
    elif u == 1:
        o1 = 2
        o2 = 3
    elif u == 2:
        o1 = 3
        o2 = 1
    elif u == 3:
        o1 = 1
        o2 = 1
    elif u == 4:
        o1 = 2
        o2 = 1
    elif u == 5:
        o1 = 3
        o2 = 2
    elif u == 6:
        o1 = 1
        o2 = 3
    elif u == 7:
        o1 = 2
        o2 = 2
    elif u == 8:
        o1 = 3
        o2 = 3
    return o1, o2

def wrapValue(val, bits=16, signed=True):
    if signed:
        if val < 2 ** (bits - 1) and val >= 0:
            return val
        else:
            return (2 ** (bits - 1)) - val
        return
    else:
        return val


if __name__ == '__main__':
    kgl.setLib()
    kgl.ksoclib.connectDevice()
    # print(Digi168BController.checkExpType())
    reg_val = kgl.ksoclib.readHWRegister(0x6000_0000)
    print(f'0x{reg_val[0]:X}')
    digi_control = DigiControllerFactory.createController("K60169")
    print(digi_control.getChirpNumber())
    # print(digi_control.checkDualMode())



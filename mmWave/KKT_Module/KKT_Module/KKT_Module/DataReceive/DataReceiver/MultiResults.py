from KKT_Module.DataReceive.Core import Receiver, wrap_stop, wrap_trigger, wrap_getResults, Data
from KKT_Module.DataReceive.Results import Result168, Result169
from KKT_Module.DataReceive.Data import RawData, FeatureMap, R_Bank, CFAR, Gesture, Exponential, Tracking, IMax, DiagnosisDict, Motion
from KKT_Module.KKTUtility.DigiControl import Digi168BController, DigiControllerFactory
from KKT_Module.KKTUtility.RFControl import RFController
from KKT_Module.ksoc_global import kgl
import time
import numpy as np

class MultiResult4168BReceiver(Receiver):
    '''
    Rename from AIResultReceiver.

    Instance with interrupts and get hardware results when "read_interrupt"
    was detected ,clear the results when "clear_interrupt was detected."'''
    _res_addrs_dict = {
        'SoftmaxExponential': [addr for addr in range(0x50000508, 0x5000051C + 1, 4)],
        'Axis': [addr for addr in range(0x50000578, 0x5000057C + 1, 4)],
        'Gestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)],
        'SiameseGestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)],
        'SiameseExponential': [addr for addr in range(0x50000604, 0x50000618 + 1, 4)],
        'IMax': [addr for addr in range(0x500005A4, 0x500005A4 + 1, 4)],
        'CFAR': [addr for addr in range(0x500005A8, 0x500005E4 + 1, 4)],
        'RSSI': [addr for addr in range(0x4005C10C, 0x4005C10C + 1, 4)],
        'Motion': [addr for addr in range(0x4005C140, 0x4005C15C + 1, 4)],
        'Motion EABS': [addr for addr in range(0x4005C190, 0x4005C1AC + 1, 4)],
        'AGC_Ch1': [addr for addr in range(0x400D8060, 0x400D8060 + 1, 4)],
        'AGC_Ch2': [addr for addr in range(0x400D80A0, 0x400D80A0 + 1, 4)],
        'AGC_Ch3': [addr for addr in range(0x400F8060, 0x400F8060 + 1, 4)],

        'AI Sram': [0x20020C04, 0x20022404, 0x20023C04, 0x20025404, 0x20026C04, 0x20028404,
                    0x20029C04,
                    0x2002B404, 0x2002CC04, 0x2002E404, 0x2002FC04, 0x20031404, 0x20020C08,
                    0x20022408,
                    0x20023C08, 0x20025408, 0x20026C08, 0x20028408, 0x20029C08, 0x2002B408,
                    0x2002CC08,
                    0x2002E408, 0x2002FC08, 0x20031408],
                            }
    def __init__(self, actions=0b1, read_interrupt:int=0, clear_interrupt:int=0, rbank_ch_enable=0b111, chirps=32, samples=128, channel=2, **kwargs):
        super(MultiResult4168BReceiver, self).__init__()
        self._result_list = []
        self._result_dict = {'SoftmaxExponential': [],
                            'Axis': [],
                            'Gestures': [],
                            'SiameseGestures': [],
                            'SiameseExponential': [],
                            'IMax': [],
                            'CFAR': [],
                            'RSSI': [],
                            'Motion': [],
                            'Motion EABS': [],
                            'AGC Ch1': [],
                            'AGC Ch2': [],
                            'AGC Ch3': [],
                            'AI Sram':[],
                             }

        self._trigger = False
        self.read_interrupt = read_interrupt
        self.clear_interrupt = clear_interrupt
        self.rbank_ch_enable = rbank_ch_enable
        self.actions = actions
        self.RDI_enable = True
        self.results = Result168()
        self.chirps = chirps
        self.samples = samples
        self.channel = channel
    @wrap_trigger()
    def trigger(self, **kwargs):
        '''
        :param kwargs:

        read_interrupt = read interrupt\n
        clear_interrupt = clear interrupt\n
            interrupt types are 0: softmax, 1: cfar, 2: amplitude, 3: md, 4: tracking, 5: raw_data, 6: c1_done

        enable:
            2 - Enable to read registgers and RAW/RDI\n
            1 - Enable to read registgers\n
            0 - Disable\n

        RDI_enable: Switch RDI/Raw.

        :return:
        '''
        self.setConfig(**kwargs)
        total_res = []
        self.actions = int(self.actions)
        self.read_interrupt = int(self.read_interrupt)
        self.clear_interrupt = int(self.clear_interrupt)
        self.rbank_ch_enable = int(self.rbank_ch_enable)
        self.chirps = Digi168BController.getChirpNumber()
        self.samples = Digi168BController.getSampleNumber()
        self._result_list=[]
        if (self.actions & 0b100):
            if self.read_interrupt == 0:
                self._result_list = list(self._res_addrs_dict.keys())
                # self._result_list = ['Axis']
            elif self.read_interrupt == 3:
                self._result_list = ['RSSI', 'Motion', 'Motion EABS']
            elif self.read_interrupt == 2:
                self._result_list = ['CFAR', 'RSSI', 'Motion', 'Motion EABS']
            elif self.read_interrupt == 1:
                self._result_list = ['CFAR', 'IMax', 'RSSI', 'Motion', 'Motion EABS']
            elif self.read_interrupt == 4:
                self._result_list = ['Axis', 'CFAR', 'IMax', 'RSSI', 'Motion', 'Motion EABS']
            # instance paring machine
            for res_name in self._result_list:
                total_res = total_res + self._res_addrs_dict[res_name]
        reg_addrs = np.asarray(total_res).astype('uint32')
        self.size = 1
        if (self.actions & 0b1):
            self.RDI_enable = kgl.ksoclib.readReg(0x50000504, 5, 5)
            if self.RDI_enable:
                self.size = 1620 + self.size
            else:
                self.size = self.chirps*self.samples + self.size
        kgl.ksoclib.switchSoftMaxInterrupt(self.actions, self.read_interrupt, self.clear_interrupt, self.size*4, self.rbank_ch_enable, reg_addrs)
        # self._trigger = True
        # print('SwitchSoftMaxInterrupt success')
        time.sleep(0.5)

    @wrap_getResults()
    def getResults(self):
        '''

        Returns: result dictionary or None

        '''
        res = kgl.ksoclib.getSoftMaxInterruptRegValues()

        if res is None:
            return None
        self.results = Result168()
        if (int(self.actions) & 0b1):
            data = res[0]
            self.results['frame_count'] = Data(data[0:2])
            if self.RDI_enable:
                self.results['feature_map'] = FeatureMap(FeatureMap.convert168BInt16Array(data, 2, self.size*2), num=2, chirp=self.chirps, sample=self.samples)
                # self.results['frame_count'] = Data(data[0:2])
            else:
                raw_data = RawData.convert168BInt16Array(data, self.size*2, ch=self.channel, chirp=self.chirps, sample=self.samples)
                self.results['raw_data'] = RawData(raw_data, ch=self.channel, chirp=self.chirps, sample=self.samples)
                # self.results['frame_count'] = Data(data[0:2])

        if (int(self.actions) & 0b10):
            data = res[1]
            self.results['R_bank'] = R_Bank(R_Bank.convert168BInt16Array(data, ch_enable=self.rbank_ch_enable, sample=self.samples))

        if (int(self.actions) & 0b100):
            data = res[2]
            start = 0
            result_dict ={}
            for res_name in self._result_list:
                result_dict.setdefault(res_name, data[start:start + len(self._res_addrs_dict[res_name])])
                start = start + len(self._res_addrs_dict[res_name])
            self._parsing(result_dict)
        return self.results
    @wrap_stop()
    def stop(self):
        kres = kgl.ksoclib.switchSoftMaxInterrupt(enable=0)

    def _parsing(self, result_dict: dict):
        for result in self._result_list:
            data = result_dict.get(result)
            if data is None:
                continue
            if result in ['CFAR']:
                self.results['CFAR'] = CFAR(CFAR.convertRegisterVal(data))
            elif result in ['SoftmaxExponential']:
                self.results['softmax_exp'] = Exponential(Exponential.convertRegisterVal(data))
            elif result in ['SiameseExponential']:
                self.results['siamese_exp'] = Exponential(Exponential.convertRegisterVal(data))
            elif result in ['Axis']:
                self.results['tracking'] = Tracking(Tracking.convertRegisterVal(data))
            elif result in ['Gestures']:
                self.results['gesture'] = Gesture(Gesture.convertRegisterVal(data, 16, 20))
            elif result in ['SiameseGestures']:
                self.results['sia_gesture'] = Gesture(Gesture.convertRegisterVal(data))
            elif result in ['IMax']:
                self.results['IMax'] = IMax(IMax.convertRegisterVal(data))
            # elif result in ['AI Sram']:
            #     arry = self.__parseAISram(arry)

class MultiResult4169CReceiver(Receiver):
    def __init__(self, chirps: int = 32, samples: int = 128, channel: int = 2, enable: str = '0x0F', binary_array: str = '0'):
        '''
        Receive some hardware results
        (Gesture, Axis and Exponential).
        '''
        super(MultiResult4169CReceiver, self).__init__()
        self._result_list = []
        self.interrupt_list = []
        self.dec = None
        self.data_size = 4096
        self.RFController = RFController()
        self.DigiController = DigiControllerFactory.select169Controller()
        self.results = Result169()
        self.chirps = chirps
        self.samples = samples
        self.channel = channel
        self.enable = enable
        self.binary_array = binary_array
        self.take_first_frame = False
        pass

    def setDec(self, dec):
        self.dec = dec
    @wrap_trigger()
    def trigger(self, **kwargs):
        super(MultiResult4169CReceiver, self).trigger()
        # self.RFController.turnOnModulation(True)
        self.setConfig(**kwargs)
        self._ResultParser = ResultParsing(self._result_list)
        enable = int(self.enable, 16)
        dec = int(self.binary_array, 16)
        chirps = kwargs.get('chirps')
        if chirps is not None:
            self.chirps = chirps
        else:
            self.chirps = self.DigiController.getChirpNumber()
        samples = kwargs.get('samples')
        if samples is not None:
            self.samples = samples
        else:
            self.samples = self.DigiController.getSampleNumber()
        self.data_size = self.chirps * self.samples
        # size = kwargs.get('raw_size')
        # if size is not None:
        #     self.data_size = size
        switch_mode = kwargs.get('switch_mode')
        if switch_mode is None:
            switch_mode = self.DigiController.getSwitchMode()
        if switch_mode == 1:
            self.channel = 2
        elif switch_mode == 2:
            self.channel = 1
        elif switch_mode == 4:
            self.channel = 1
        else:
            raise ValueError('Switch mode is wrong !')

        self.interrupt_list = self.__genFPGAAnswerDict(dec)

        kgl.ksoclib.switchDiagnosisInterrupt(enable, gemmini_res=dec, reg_addrs=[], data_size=self.data_size * 2)
        pass
    @wrap_getResults()
    def getResults(self):
        '''

        :return: Gesture, Axis and Exponential.
        '''
        res = kgl.ksoclib.getDiagnosisInterruptRegValues()
        start = 0
        if res is None:
            return None
        raw = res[0]
        diagnosis = res[1]
        AGC = res[2]
        Motion_data = res[3]
        InterferenceBank = res[4]
        raw_data = RawData.convert169Rawdata(raw, start, self.data_size, self.channel, self.chirps, self.samples)
        if raw is not None:
            self.results['frame_count'] = Data(data=np.frombuffer(raw[1:2], dtype='>u2'))
            self.results.raw_data = RawData(raw_data, ch=self.channel, chirp=self.chirps, sample=self.samples)
        if Motion_data is not None:
            self.results.motion = Motion(Motion_data)
        if AGC is not None:
            self.results['AGC'] = Data(AGC)
        if InterferenceBank is not None:
            self.results['R_bank'] = R_Bank(R_Bank.convert169Int16Array(InterferenceBank, ch=self.channel, sample=self.samples))

        diagnosis_dict = {}
        diagnosis_dict = DiagnosisDict.convertDiagnosisDictData(diagnosis_dict, diagnosis, self.interrupt_list)
        diagnosis_dict_keys_list = list(diagnosis_dict.keys())
        for i in range(len(diagnosis_dict_keys_list)):
            if diagnosis_dict_keys_list[i] == 'DFT_CORDIC':
                self.results.feature_map = FeatureMap(FeatureMap.convert169Data(diagnosis_dict.get('DFT_CORDIC').data, channel=self.channel))
            elif diagnosis_dict_keys_list[i] == 'TRACKING':
                self.results.tracking = Tracking(Tracking.convert169Data(diagnosis_dict.get('TRACKING').data))
            elif diagnosis_dict_keys_list[i] == 'SF_SOFTMAX':
                self.results.softmax_exp = Exponential(diagnosis_dict.get('SF_SOFTMAX').data)
            elif diagnosis_dict_keys_list[i] == 'SF_FC_LAST':
                self.results.fc_last_exp = Exponential(np.asarray(diagnosis_dict.get('SF_FC_LAST').data, dtype='int16'))
            else:
                self.results[diagnosis_dict_keys_list[i]] = diagnosis_dict.get(diagnosis_dict_keys_list[i])
        if self.results['DFT_SLOW_RESULT_REAL'] is not None and self.results['DFT_SLOW_RESULT_IMAG'] is not None:
            self.results['DFT_SLOW_RESULT'] = Data(np.vstack((self.results['DFT_SLOW_RESULT_REAL'].data, self.results['DFT_SLOW_RESULT_IMAG'].data)))
        return self.results
    @wrap_stop()
    def stop(self):
        kgl.ksoclib.switchDiagnosisInterrupt(0)
        pass

    def __genFPGAAnswerDict(self, binary: int):
        binarys = list(bin(binary)[2:].zfill(32))
        binarys.reverse()
        interrupt_list = []
        diagnosis = [
            'SCID_ITS_DIAG_MIN',  # 0
            'SCID_ITS_DIAG_ROWDATA_LOOPBACK',
            'SCID_ITS_DIAG_DFT_FAST_REAL',
            'SCID_ITS_DIAG_DFT_FAST_IMAG',
            'SCID_ITS_DIAG_DFT_CORDIC',
            'SCID_ITS_DIAG_DFT_SLOW_RESULT_REAL',  # 5
            'SCID_ITS_DIAG_DFT_SLOW_RESULT_IMAG',
            'SCID_ITS_DIAG_CONVD_1',
            'SCID_ITS_DIAG_CONVP_1',
            'SCID_ITS_DIAG_CONVD_2',
            'SCID_ITS_DIAG_CONVP_2',  # 10
            'SCID_ITS_DIAG_GLOBAL_AVERAGE',
            'SCID_ITS_DIAG_BATCH_NORMALIZATION',
            'SCID_ITS_DIAG_CONV_REV1',
            'SCID_ITS_DIAG_CONV_REV2',
            'SCID_ITS_DIAG_MGU_CONCAT_STATE',  # 15
            'SCID_ITS_DIAG_MGU_TILED_MATMUL_G',
            'SCID_ITS_DIAG_MGU_SIGMOID',
            'SCID_ITS_DIAG_MGU_SUB',
            'SCID_ITS_DIAG_MGU_MUL1',
            'SCID_ITS_DIAG_MGU_CONCAT_MUL1',  # 20
            'SCID_ITS_DIAG_MGU_TILED_MATMUL_C',
            'SCID_ITS_DIAG_MGU_TANH',
            'SCID_ITS_DIAG_MGU_MUL3',
            'SCID_ITS_DIAG_MGU_ADD',
            'SCID_ITS_DIAG_MGU_REV1',  # 25
            'SCID_ITS_DIAG_MGU_REV2',
            'SCID_ITS_DIAG_NEXT_MGU_STATE',
            'SCID_ITS_DIAG_SF_FC_LAST',
            'SCID_ITS_DIAG_SF_SOFTMAX',
            'SCID_ITS_DIAG_TRACKING'  # 30
        ]
        for i in range(len(binarys)):
            if binarys[i] == '1':
                interrupt_list.append(diagnosis[i].replace('SCID_ITS_DIAG_', ''))
        return interrupt_list

    def initDataBuffer(self, enable, interrupt_list):
        pass




class ResultParsing():
    '''
        Import a list for the hardware results want to be parsed.

    '''
    def __init__(self, result_list:list):
        self._result_list = result_list
        self._parsed_result_dict = {}
        pass

    def parsing(self, result_dict:dict):
        parsed_result_dict = {}
        for result in self._result_list:
            arry = result_dict.get(result)
            if arry is None:
                continue
            if result in ['CFAR']:
                arry = self.__parseCFAR(arry)
            elif result in ['SoftmaxExponential']:
                arry = self.__parseSoftMaxExponential(arry)
            elif result in ['SiameseExponential']:
                arry = self.__parseSiameseExponential(arry)
            elif result in ['Axis']:
                arry = self.__parseAxis(arry)
            elif result in ['Gestures']:
                arry = self.__parseGesture(arry, 0, 4)
            elif result in ['SiameseGestures']:
                arry = self.__parseGesture(arry, 16, 20)
            elif result in ['IMax']:
                arry = self.__parseIMax(arry)
            elif result in ['AI Sram']:
                arry = self.__parseAISram (arry)
            else:
                pass
            parsed_result_dict[result] = arry
        self._parsed_result_dict = parsed_result_dict

    def getParsedResults(self):
        return self._parsed_result_dict

    def __parseAISram(self, arry):
        ai_sram = []
        binvals=''
        for i in range(len(arry)):
            binval = bin(arry[i]).split('0b')[1].zfill(32)
            binvals = binval+binvals

        ai_sram_list = [binvals[i: i + 12] for i in range(0, len(binvals), 12)]

        for i in range(len(ai_sram_list)):
            ai_sram.insert(0,  unsign2sign(int(ai_sram_list[i],2),12))


        return ai_sram

    def __parseCFAR(self, arry):
        CFAR = []
        for i in range(len(arry)):
            binval = bin(arry[i]).split('0b')[1].zfill(32)
            CFAR_amp_odd = int(binval[0:16], 2)
            CFAR.append(CFAR_amp_odd)
            CFAR_amp_even = int(binval[16:32], 2)
            CFAR.append(CFAR_amp_even)
        return np.asarray(CFAR).astype('int16')

    def __parseIMax(self, arry):
        IMax = []
        binval = bin(arry[0]).split('0b')[1].zfill(32)
        imax = int(binval[0:16], 2)
        IMax.append(imax)
        return np.asarray(IMax).astype('int16')

    def __parseSoftMaxExponential(self, arry):
        val_line = ''
        for v in arry:
            hex_val = hex(v).split('0x')[1].zfill(8)
            val_line = hex_val + val_line
        exponential = []
        for i in range(len(val_line), 0, -3):
            dec_val = int(val_line[i - 3:i], 16)
            dec_val = unsign2sign(dec_val, 12)
            exponential.append(dec_val)
        return np.asarray(exponential).astype('int16')

    def __parseSiameseExponential(self, arry):
        val_line = ''
        for v in arry:
            hex_val = hex(v).split('0x')[1].zfill(8)
            val_line = hex_val + val_line
        exponential = []
        for i in range(len(val_line), 0, -3):
            dec_val = int(val_line[i - 3:i], 16)
            exponential.append(dec_val)
        return np.asarray(exponential).astype('int16')

    def __parseGesture(self, arry, start_bit=0, end_bit=4):
        gesture = []
        bin_val = bin(arry[0]).split('0b')[1].zfill(32)
        bin_val_rev = bin_val[::-1]
        val_rev = bin_val_rev[start_bit:end_bit + 1]
        val = val_rev[::-1]
        if val[-5] == '0':
            gesture.append(int(val[-4:], 2))
        elif val[-5] == '1':
            gesture.append(int(val[-4:], 2) - 16)
        else:
            print('gesture not save')
            return
        return np.asarray(gesture).astype('int16')

    def __parseAxis(self, arry):
        # tracking_axis = []
        hex_val_0 = hex(arry[0]).split('0x')[1].zfill(8)
        hex_val_1 = hex(arry[1]).split('0x')[1].zfill(8)
        tracking_axis = [int(hex_val_0[4:8], 16),
                         int(hex_val_0[0:4], 16),
                         int(hex_val_1[4:8], 16)]
        return np.asarray(tracking_axis).astype('int16')

    def parseRawData(self, res, start, end):
        FrameCount1 = res[start]
        FrameCount2 = res[start+1]

        data = res[start + 2:end]
        ch1 = data[::2]
        ch2 = data[1::2]
        data = np.vstack((ch1, ch2))

        # print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount & 0xFFFF), (FrameCount >> 16) & 0xFFFF))
        return data

    def parseRDI(self, res, start, end):

        FrameCount = res[start]
        data = res[start + 1:start+end]
        # print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount & 0xFFFF), (FrameCount >> 16) & 0xFFFF))
        raw_RDI = convertBitArray(data,16,12)
        return raw_RDI
        # return np.frombuffer(data.tobytes(), dtype='int16')

    def parseRawData2(self, res, start, size, switch_mode, chirps=32, samples=128):
        '''
        For 0xAF command raw data
        Args:
            res:
            start:
            size:

        Returns:

        '''
        if res is None:
            return
        FrameCount1 = res[start]
        FrameCount2 = res[start+1]
        data = np.zeros(size, dtype='int16')


        if switch_mode == 1:
            data = np.reshape(data, (chirps, samples))
            res = np.reshape(res[start + 2:], (2, int(chirps / 2), samples))
            data[0::2] = res[0]
            data[1::2] = res[1]
            data = np.reshape(data, size)
        else:
            data = res[start + 2:start + 2 + size]

        print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount1 & 0xFFFF), (FrameCount2) & 0xFF))
        return data


def unsign2sign(x, bit):
    '''
    return sign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x >= 0 and x < 2 ** (bit-1):
        y = x
    elif x >= 2 ** (bit-1) and x < 2**bit:
        y = x - 2**(bit)
    else:
        raise Exception('Value is out of bit range')
    return y


def convertBitArray(arry, src_bit, dis_bit):
    niddles = int(src_bit/4)
    new_niddle_num = int(dis_bit/4)
    Hex_line = ''
    for i in arry:
        Hex = hex(i).split('0x')[1].zfill(niddles)
        Hex_line =  Hex + Hex_line


    hexs = [int(Hex_line[3*k:3*k+new_niddle_num],16) for k in range(int(len(Hex_line)/new_niddle_num))]

    output = hexs

    output.reverse()

    return np.asarray(output,dtype='uint16')





if __name__ == '__main__':
    # result_dict = {}
    # result_dict['SoftmaxExponential'] = np.random.randint(2 ** 32, size=6, dtype='uint32')
    # result_dict['SiameseExponential'] = np.random.randint(2 ** 32, size=6, dtype='uint32')
    # result_dict['Axis'] = np.random.randint(2 ** 32, size=2, dtype='uint32')
    # result_dict['Gestures'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['SiameseGestures'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['IMax'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['CFAR'] = np.random.randint(2 ** 32, size=16, dtype='uint32')
    # result_list = list(result_dict.keys())
    # s = time.time_ns()
    # result_parser = ResultParsing(result_list)
    # result_parser.parsing(result_dict)
    # results = result_parser.getParsedResults()
    # e = time.time_ns()
    # print(results)
    arry = np.asarray([i for i in range(1620)])
    a =  convertBitArray(arry, 32, 12)
    print(a)

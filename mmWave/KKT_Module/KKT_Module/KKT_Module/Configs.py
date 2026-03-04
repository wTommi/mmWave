from KKT_Module.ksoc_global import kgl
import os
import platform
import sys
import configparser
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs

class INIConfigs:
    '''
    For parsing ini file.
    '''
    BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True, 'y': True,
                      '0': False, 'no': False, 'false': False, 'off': False, 'n': False,}
    class MyConfigParser(configparser.ConfigParser):
        def optionxform(self, option:str) -> str:
            return option
    def __init__(self, filename):
        self.config = self.MyConfigParser()
        self.config.read(filename, encoding="utf-8")
        self.section = self.config.sections()
        pass
    def setConfigs(self):
        for k,v in self.config['CONFIGS'].items():
                self.__setattr__(k.lower(), v)

class RecordingConfigs:
    '''
    For h5 file data recording.
    '''
    DataConfigs = {'Record_frames': 100,
                    'Datatime': '',
                    'Description': 'Open->Close->Open',
                    'Diversity': 'Random',
                    'Minimum_gap':10,
                    'Duration':[20],
                    'Gesture_name': [],
                    'Hand_type': 'Left hand',
                    'Mode': 'Manual',
                    'Attr_file_name': 'General_model_record_attribute_manual.xlsx',
                    'Owner': 'Eric',
                    'Device': 'K60SOCA1',
                    'Data_format' : 'RawData',
                    }
    RFConfigs = {'RFIC':None,
                 'Chirps':None,
                 'SIC_opened':None,
                 'MUX':None,
                 }
    DSP_Configs={}
    AIC_Configs = {}
    AGC_Configs = {}
    PHD_Configs = {}
    RDI_Configs = {}
    Record_Folder = 'temp'
    DataType = 'RawData'

    def __init__(self,**kwargs):
        '''
        kwargs:
        'Record_frames', 'Datatime', 'Description',
        'Diversity', 'Duration', 'Gesture_name',
        'Hand_type', 'Mode', 'Attr_file_name',
        'Owner', 'Device', 'Data_format'
        '''
        self.setDataConfig(**kwargs)
        pass


    def setDataConfig(self, **kwargs):
        '''
        Update KProcFSM configs.

        :param kwargs: 'Record_frames','Datatime','Description',
                       'Diversity','Duration','Gesture_name',
                       'Hand_type','Mode','Attr_file_name',
                       'Owner','Device','Data_format'
        '''
        for k, v in kwargs.items():
            assert self.DataConfigs.get(k) is not None, 'No attribute "{}" in DataConfigs.'.format(k)
            self.DataConfigs[k] = v


    def initDataConfigs(self, setting_configs):
        visualize_configs = ''
        if setting_configs is not None:
            Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
            Hardware_text = setting_configs.ScriptDir.get('Hardware_text')
            if Hardware_excel is None:
                assert Hardware_text is not None,'Empty hardware setting !'
                visualize_configs = os.path.basename(Hardware_text)
            else:
                visualize_configs = os.path.basename(Hardware_excel)

        self.DataConfigs['Visualize_config'] = visualize_configs

        self.DataConfigs['Version'] = 'Python ' + '.'.join([str(x) for x in [sys.version_info.major,
                                                                             sys.version_info.minor,
                                                                             sys.version_info.micro]])
        self.DataConfigs['Platform'] = platform.system() + ' ' + platform.release()
        self.DataConfigs['FW_version'] = kgl.ksoclib.getFWVersion()
        self.DataConfigs['Device'] = kgl.ksoclib.getChipID()
        if self.DataConfigs['Device'].split(' ')[0] != 'K60169A':
            self.DataConfigs['SN'] = kgl.ksoclib.getSN()
        else:
            self.DataConfigs['SN'] = ''


    def initDSPConfigs(self, setting_configs):
        if setting_configs is None:
            return
        Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
        Hardware_text = setting_configs.ScriptDir.get('Hardware_text')

        if Hardware_excel is None:
            assert Hardware_text is not None,'Empty hardware setting! '
            visualize_configs = os.path.split(Hardware_text)[1]
            visualize_configs = visualize_configs.split('.')[0].split('param_')[1]
        else:
            visualize_configs = os.path.split(Hardware_excel)[1]
            visualize_configs = visualize_configs.split('.')[0]

        DSP_cfg = setting_configs.genDSPConfigs()
        self.DSP_Configs['Map1_nc'] =DSP_cfg[0]
        self.DSP_Configs['Map2_nc'] =DSP_cfg[1]
        self.DSP_Configs['Gen_Mode'] = 'BT'
        self.DSP_Configs['Hardware_excel'] = visualize_configs


    def initAGCConfigs(self, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        self.AGC_Configs = {
            'alpha':DSPRx20M_Unit_0['0x400D804C'][3]['alpha'],
            'log_P_targ':DSPRx20M_Unit_0['0x400D8048'][3]['log_P_targ'],
            'AGC_bypass':DSPRx20M_Unit_0['0x400D8040'][3]['AGC_ByPass'],
            'AGC_fix_pt':0,
            'samples_per_ACC':DSPRx20M_Unit_0['0x400D8048'][3]['samples_per_acc'],
        }


    def initAICConfigs(self, setting_configs):
        if setting_configs is None:
            return
        chirp_period_dict = {0: 64, 1: 128}
        symbol_per_frame_dict = {0: 16, 1: 32, 2: 64, 3: 'user_define'}
        DSPRx625K_Unit_0 = setting_configs.ParamDict['DSPRx625K_Unit_0']
        DSP_Motion = setting_configs.ParamDict['DSP_Motion']

        AIC_symbol_per_frame = symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']]
        if symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']] == 'user_define':
            AIC_symbol_per_frame = DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm_user']

        self.AIC_Configs = {
            'AIC_chirp_periodicity':chirp_period_dict[DSPRx625K_Unit_0['0x400B0088'][3]['chirp_period']],
            'AIC_chirp_log_num':DSPRx625K_Unit_0['0x400B0088'][3]['chirp_log_num'],
            'AIC_sync_delay':DSPRx625K_Unit_0['0x400B0088'][3]['syncOffset'],
            'AIC_Wstart':DSPRx625K_Unit_0['0x400B008C'][3]['W_starting'],
            'AIC_Wend':DSPRx625K_Unit_0['0x400B008C'][3]['W_end'],
            'AIC_symbol_per_frame':AIC_symbol_per_frame,
            'AIC_right_shift_num':DSPRx625K_Unit_0['0x400B0088'][3]['outputShiftNum'],
            'En_first_velocity_est':DSP_Motion['0x4005C08C'][3]['En_first_velocity_est'],
            'Vel_right_shift_num':DSP_Motion['0x4005C08C'][3]['Vel_right_shift_num'],
            'AIC_fix_pt':0
        }


    def initPHDConfigs(self, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        self.PHD_Configs={
            'enable' : DSPRx20M_Unit_0['0x400D8018'][3]['Enable'],
            'Mode' : DSPRx20M_Unit_0['0x400D801C'][3]['mode'],
            'column' : DSPRx20M_Unit_0['0x400D801C'][3]['column'] + 1,
            'twiddle_table' : 0,
            'conv2polar_gain_RDI' : DSPRx20M_Unit_0['0x400D801C'][3]['gainRDI'],
            'conv2polar_gain_phaseFFT' : DSPRx20M_Unit_0['0x400D801C'][3]['gainPhaseFFT'],
            'PHD_fix_pt' : 0
        }


    def initRDIConfigs(self, setting_configs):
        if setting_configs is None:
            return
        Fast_time_sample_dict = {0: 64, 1: 128}
        Fast_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_symbols_dict = {0: 16, 1: 32, 2: 64}
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']
        self.RDI_Configs = {
            'Fast_time_sample' : Fast_time_sample_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_sample']],
            'up_down_combining' : DSPRx20M_Unit_0['0x400D2008'][3]['upDownComb'],
            'Fast_time_start_point' : DSPRx20M_Unit_0['0x400D2008'][3]['FT_startPoint'],
            'Fast_downsample_ratio' : Fast_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_downSampleRatio']],
            'Fast_time_conv2polar' : DSPRx20M_Unit_0['0x400D2008'][3]['FT_Con2Polar'],
            'Fast_time_post_FFT_comb_enable' : 0,
            'Slow_time_512FFT_ext' : DSPRx20M_Unit_0['0x400D2008'][3]['ST_512FFT_ext'],
            'Slow_time_symbols' : Slow_time_symbols_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_SymbolCnt']],
            'Slow_time_downsample_ratio' : Slow_time_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_downSampleRatio']],
            'Slow_time_conv2polar' : DSPRx20M_Unit_0['0x400D2008'][3]['ST_Con2Polar'],
            'Slow_time_conv2polar_gainshift' : DSPRx20M_Unit_0['0x400D2008'][3]['con2PolarGainShift'],
            'RDI_fix_pt' : 0,
            'Fast_time_rotate_vector_im_ch1': DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_im'],
            'Fast_time_rotate_vector_re_ch1': DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_re'],
            'Fast_time_rotate_vector_im_ch2': DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_im'],
            'Fast_time_rotate_vector_re_ch2': DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_re'],
        }


    def initRFConfigs(self, setting_configs:SettingConfigs):
        chirps = (kgl.ksoclib.rficRegRead(0x0026) & 0xFF) + 1
        mux = kgl.ksoclib.readReg(0x50000544, 3, 0, )
        if setting_configs is not None:
            RF_setting = setting_configs.ScriptDir.get('RF_setting')
            assert RF_setting is not None, 'Empty RF setting!'
            RF_setting = os.path.basename(RF_setting)
            SIC_opened = setting_configs.SIC.SIC_open
            self.RFConfigs.update(setting_configs.PhaseKConfigs)
        else:
            RF_setting = ''
            SIC_opened = kgl.ksoclib.getRFSICEnableStatus()


        self.RFConfigs['RFIC'] = RF_setting
        self.RFConfigs['Chirps'] = int(chirps)
        self.RFConfigs['SIC_opened'] = SIC_opened
        self.RFConfigs['MUX'] = int(mux)

def testSetting_configs():
    print('[Entry testSetting_configs]')
    print('[print main class]',SettingConfigs.SIC.SIC_open)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SC1.SIC.SIC_open = True
    print('[print main class]',SettingConfigs.SIC.SIC_open)
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SC2 = SettingConfigs()
    print('[print sub class SC2]',SC2.SIC.SIC_open)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SettingConfigs.SIC.SIC_open = True
    SC3 = SettingConfigs()
    print('[print sub class SC3]',SC3.SIC.SIC_open)
    # SC3.SIC.SIC_open = False
    print('[print main class]', SettingConfigs.SIC.SIC_open)
    print('[print sub class SC1]', SC1.SIC.SIC_open)
    print('[print sub class SC2]', SC2.SIC.SIC_open)
    print('[print sub class SC3]', SC3.SIC.SIC_open)

def testSetting_configs2():
    print('[Entry testSetting_configs]')
    print('[print main class]',SettingConfigs.Debounce)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.Debounce)
    SC1.Debounce = True
    print('[print main class]',SettingConfigs.Debounce)
    print('[print sub class SC1]',SC1.Debounce)
    SC2 = SettingConfigs()
    print('[print sub class SC2]',SC2.Debounce)
    print('[print sub class SC1]', SC1.Debounce)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.Debounce)
    SettingConfigs.Debounce = True
    SC3 = SettingConfigs()
    print('[print sub class SC3]',SC3.Debounce)
    # SC3.Debounce = False
    print('[print main class]', SettingConfigs.Debounce)
    print('[print sub class SC1]', SC1.Debounce)
    print('[print sub class SC2]', SC2.Debounce)
    print('[print sub class SC3]', SC3.Debounce)

if __name__ == '__main__':
    testSetting_configs()
    testSetting_configs2()
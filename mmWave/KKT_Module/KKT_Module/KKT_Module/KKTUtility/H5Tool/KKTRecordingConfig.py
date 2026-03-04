from __future__ import annotations
import os
import sys
import platform
from KKT_Module.KKTUtility.H5Tool.Core import H5DataSet, H5Group, DataConfig, DSPConfig, RFConfig, VideoConfig, RDIConfig, PHDConfig, AGCConfig, AICConfig
from KKT_Module.KKTUtility.DigiControl import Digi168BController, DigiControllerFactory
from KKT_Module.ksoc_global import kgl
from abc import abstractmethod ,ABC


class _ISetRecordAttribute(ABC):

    @abstractmethod
    def initDataConfigs(cls, Data_Configs:DataConfig, setting_configs):
        pass

    @abstractmethod
    def initDSPConfigs(cls, DSP_Configs:DSPConfig, setting_configs):
        pass

    @abstractmethod
    def initAGCConfigs(cls, AGC_Configs:AGCConfig, setting_configs):
        pass


    @abstractmethod
    def initAICConfigs(cls,AIC_Configs:AICConfig, setting_configs):
        pass

    @abstractmethod
    def initPHDConfigs(cls,PHD_Configs:PHDConfig, setting_configs):
        pass


    @abstractmethod
    def initRDIConfigs(cls,RDI_Configs:RDIConfig, setting_configs):
        pass

    @abstractmethod
    def initRFConfigs(cls, RF_Configs:RFConfig, setting_configs):
        pass

    @abstractmethod
    def initConfigs(self, record_config:KKTRecordConfig, setting_config):
        pass

class Set168Attribute(_ISetRecordAttribute):
    def initDataConfigs(self, Data_Configs:DataConfig, setting_configs):
        visualize_configs = ''
        if setting_configs is not None:
            Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
            Hardware_text = setting_configs.ScriptDir.get('Hardware_text')
            if Hardware_excel is None:
                assert Hardware_text is not None,'Empty hardware setting !'
                visualize_configs = os.path.basename(Hardware_text)
            else:
                visualize_configs = os.path.basename(Hardware_excel)

        Data_Configs.Visualize_config = visualize_configs

        Data_Configs.Version = 'Python ' + '.'.join([str(x) for x in [sys.version_info.major,
                                                                             sys.version_info.minor,
                                                                             sys.version_info.micro]])
        Data_Configs.Platform = platform.system() + ' ' + platform.release()
        if kgl.ksoclib:
            Data_Configs.FW_version = kgl.ksoclib.getFWVersion()
            Data_Configs.SN = kgl.ksoclib.getSN()
            Data_Configs.Device = kgl.ksoclib.getChipID()

    def initDSPConfigs(self, DSP_Configs:DSPConfig, setting_configs):
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

        # DSP_cfg = setting_configs.genDSPConfigs()
        # DSP_Configs.Map1_nc = DSP_cfg[0]
        # DSP_Configs.Map2_nc = DSP_cfg[1]
        DSP_Configs.Map1_nc = 1
        DSP_Configs.Map2_nc = 1
        DSP_Configs.Gen_Mode = 'BT'
        DSP_Configs.Hardware_excel = visualize_configs


    def initAGCConfigs(self, AGC_Configs:AGCConfig, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        AGC_Configs.alpha = DSPRx20M_Unit_0['0x400D804C'][3]['alpha']
        AGC_Configs.log_P_targ = DSPRx20M_Unit_0['0x400D8048'][3]['log_P_targ']
        AGC_Configs.AGC_bypass = DSPRx20M_Unit_0['0x400D8040'][3]['AGC_ByPass']
        AGC_Configs.AGC_fix_pt = 0
        AGC_Configs.samples_per_ACC = DSPRx20M_Unit_0['0x400D8048'][3]['samples_per_acc']


    def initAICConfigs(self,AIC_Configs:AICConfig, setting_configs):
        if setting_configs is None:
            return
        chirp_period_dict = {0: 64, 1: 128}
        symbol_per_frame_dict = {0: 16, 1: 32, 2: 64, 3: 'user_define'}
        DSPRx625K_Unit_0 = setting_configs.ParamDict['DSPRx625K_Unit_0']
        DSP_Motion = setting_configs.ParamDict['DSP_Motion']

        AIC_symbol_per_frame = symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']]
        if symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']] == 'user_define':
            AIC_symbol_per_frame = DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm_user']

        AIC_Configs.AIC_chirp_periodicity=chirp_period_dict[DSPRx625K_Unit_0['0x400B0088'][3]['chirp_period']]
        AIC_Configs.AIC_chirp_log_num=DSPRx625K_Unit_0['0x400B0088'][3]['chirp_log_num']
        AIC_Configs.AIC_sync_delay=DSPRx625K_Unit_0['0x400B0088'][3]['syncOffset']
        AIC_Configs.AIC_Wstart=DSPRx625K_Unit_0['0x400B008C'][3]['W_starting']
        AIC_Configs.AIC_Wend=DSPRx625K_Unit_0['0x400B008C'][3]['W_end']
        AIC_Configs.AIC_symbol_per_frame=AIC_symbol_per_frame
        AIC_Configs.AIC_right_shift_num=DSPRx625K_Unit_0['0x400B0088'][3]['outputShiftNum']
        AIC_Configs.En_first_velocity_est=DSP_Motion['0x4005C08C'][3]['En_first_velocity_est']
        AIC_Configs.Vel_right_shift_num=DSP_Motion['0x4005C08C'][3]['Vel_right_shift_num']
        AIC_Configs.AIC_fix_pt=0


    def initPHDConfigs(self,PHD_Configs:PHDConfig, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        PHD_Configs.enable= DSPRx20M_Unit_0['0x400D8018'][3]['Enable']
        PHD_Configs.Mode= DSPRx20M_Unit_0['0x400D801C'][3]['mode']
        PHD_Configs.column= DSPRx20M_Unit_0['0x400D801C'][3]['column'] + 1
        PHD_Configs.twiddle_table= 0
        PHD_Configs.conv2polar_gain_RDI= DSPRx20M_Unit_0['0x400D801C'][3]['gainRDI']
        PHD_Configs.conv2polar_gain_phaseFFT= DSPRx20M_Unit_0['0x400D801C'][3]['gainPhaseFFT']
        PHD_Configs.PHD_fix_pt= 0


    def initRDIConfigs(self,RDI_Configs:RDIConfig, setting_configs):
        if setting_configs is None:
            return
        Fast_time_sample_dict = {0: 64, 1: 128}
        Fast_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_symbols_dict = {0: 16, 1: 32, 2: 64}
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']
        RDI_Configs.Fast_time_sample= Fast_time_sample_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_sample']]
        RDI_Configs.up_down_combining= DSPRx20M_Unit_0['0x400D2008'][3]['upDownComb']
        RDI_Configs.Fast_time_start_point= DSPRx20M_Unit_0['0x400D2008'][3]['FT_startPoint']
        RDI_Configs.Fast_downsample_ratio= Fast_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_downSampleRatio']]
        RDI_Configs.Fast_time_conv2polar= DSPRx20M_Unit_0['0x400D2008'][3]['FT_Con2Polar']
        RDI_Configs.Fast_time_post_FFT_comb_enable= 0
        RDI_Configs.Slow_time_512FFT_ext= DSPRx20M_Unit_0['0x400D2008'][3]['ST_512FFT_ext']
        RDI_Configs.Slow_time_symbols= Slow_time_symbols_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_SymbolCnt']]
        RDI_Configs.Slow_time_downsample_ratio= Slow_time_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_downSampleRatio']]
        RDI_Configs.Slow_time_conv2polar= DSPRx20M_Unit_0['0x400D2008'][3]['ST_Con2Polar']
        RDI_Configs.Slow_time_conv2polar_gainshift= DSPRx20M_Unit_0['0x400D2008'][3]['con2PolarGainShift']
        RDI_Configs.RDI_fix_pt= 0
        RDI_Configs.Fast_time_rotate_vector_im_ch1= DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_im']
        RDI_Configs.Fast_time_rotate_vector_re_ch1= DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_re']
        RDI_Configs.Fast_time_rotate_vector_im_ch2= DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_im']
        RDI_Configs.Fast_time_rotate_vector_re_ch2= DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_re']


    def initRFConfigs(self, RF_Configs:RFConfig, setting_configs):
        chirps = (kgl.ksoclib.rficRegRead(0x0026) & 0xFF) + 1
        chirps = Digi168BController.getChirpNumber()
        mux = kgl.ksoclib.readReg(0x50000544, 3, 0, )

        if setting_configs is not None:
            RF_setting = setting_configs.ScriptDir.get('RF_setting')
            assert RF_setting is not None, 'Empty RF setting!'
            RF_setting = os.path.basename(RF_setting)
            SIC_opened = setting_configs.SIC.SIC_open
            for k, v in setting_configs.PhaseKConfigs.items():
                RF_Configs.__setattr__(k ,v)
        else:
            RF_setting = ''
            SIC_opened = kgl.ksoclib.getRFSICEnableStatus()

        RF_Configs.RFIC = RF_setting
        RF_Configs.Chirps = int(chirps)
        RF_Configs.SIC_opened = SIC_opened
        RF_Configs.MUX = str(mux)

    def initConfigs(self, record_config, setting_config):
        self.initDSPConfigs(record_config.DSP_Configs, setting_config)
        self.initDataConfigs(record_config.Data_Configs, setting_config)
        self.initRFConfigs(record_config.RF_Configs, setting_config)
        if record_config.Data_Configs.Data_format == 'RDIPHD':
            self.initAGCConfigs(record_config.AGC_Configs, setting_config)
            self.initRDIConfigs(record_config.RDI_Configs, setting_config)
            self.initAICConfigs(record_config.AIC_Configs, setting_config)
            self.initPHDConfigs(record_config.PHD_Configs, setting_config)
        pass
class Set169Attribute(_ISetRecordAttribute):
    def initDataConfigs(self, Data_Configs:DataConfig, setting_configs):
        visualize_configs = ''
        if setting_configs is not None:
            Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
            Hardware_text = setting_configs.ScriptDir.get('Hardware_text')
            if Hardware_excel is None:
                assert Hardware_text is not None,'Empty hardware setting !'
                visualize_configs = os.path.basename(Hardware_text)
            else:
                visualize_configs = os.path.basename(Hardware_excel)

        Data_Configs.Visualize_config = visualize_configs

        Data_Configs.Version = 'Python ' + '.'.join([str(x) for x in [sys.version_info.major,
                                                                             sys.version_info.minor,
                                                                             sys.version_info.micro]])
        Data_Configs.Platform = platform.system() + ' ' + platform.release()
        if kgl.ksoclib:
            Data_Configs.FW_version = kgl.ksoclib.getFWVersion()
            Data_Configs.SN = kgl.ksoclib.getSN()
            Data_Configs.Device = kgl.ksoclib.getChipID()

    def initDSPConfigs(self, DSP_Configs:DSPConfig, setting_configs):
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

        # DSP_cfg = setting_configs.genDSPConfigs()
        # DSP_Configs.Map1_nc = DSP_cfg[0]
        # DSP_Configs.Map2_nc = DSP_cfg[1]
        DSP_Configs.Map1_nc = 1
        DSP_Configs.Map2_nc = 1
        DSP_Configs.Gen_Mode = 'BT'
        DSP_Configs.Hardware_excel = visualize_configs

    def initAGCConfigs(self, AGC_Configs:AGCConfig, setting_configs):
        if setting_configs is None:
            return


    def initAICConfigs(self,AIC_Configs:AICConfig, setting_configs):
        if setting_configs is None:
            return

    def initPHDConfigs(self,PHD_Configs:PHDConfig, setting_configs):
        if setting_configs is None:
            return


    def initRDIConfigs(self,RDI_Configs:RDIConfig, setting_configs):
        if setting_configs is None:
            return

    def initRFConfigs(self, RF_Configs:RFConfig, setting_configs):
        # chirps = (kgl.ksoclib.rficRegRead(0x0026) & 0xFF) + 1
        chirps = DigiControllerFactory.createController('K60169').getChirpNumber()
        # mux = kgl.ksoclib.readReg(0x50000544, 3, 0, )

        if setting_configs is not None:
            RF_setting = setting_configs.ScriptDir.get('RF_setting')
            assert RF_setting is not None, 'Empty RF setting!'
            RF_setting = os.path.basename(RF_setting)
            SIC_opened = setting_configs.SIC.SIC_open
            for k, v in setting_configs.PhaseKConfigs.items():
                RF_Configs.__setattr__(k ,v)
        else:
            RF_setting = ''
            SIC_opened = kgl.ksoclib.getRFSICEnableStatus()

        RF_Configs.RFIC = RF_setting
        RF_Configs.Chirps = int(chirps)
        RF_Configs.SIC_opened = SIC_opened
        # RF_Configs.MUX = int(mux)

    def initConfigs(self, record_config:KKTRecordConfig, setting_config):
        self.initDSPConfigs(record_config.DSP_Configs, setting_config)
        self.initDataConfigs(record_config.Data_Configs, setting_config)
        self.initRFConfigs(record_config.RF_Configs, setting_config)


class KKTRecordConfig():
    @property
    def Data_Configs(self):
        return self._Data_Configs

    @Data_Configs.setter
    def Data_Configs(self, data_class:DataConfig):
        self._Data_Configs = data_class
        self.Root.getSubGroup(name='DATA_CONFIG').h5_data_class=self._Data_Configs
        if self._Data_Configs.Data_format == 'RDIPHD':
            self.RDI_Configs = RDIConfig()
            self.PHD_Configs = PHDConfig()
            self.AGC_Configs = AGCConfig()
            self.AIC_Configs = AICConfig()
            DSP_group = self.Root.getSubGroup('DSP_CONFIG')
            DSP_group.addSubGroup(H5Group(name='RDI_CONFIG', h5_data_class=self.RDI_Configs))
            DSP_group.addSubGroup(H5Group(name='PHD_CONFIG', h5_data_class=self.PHD_Configs))
            DSP_group.addSubGroup(H5Group(name='AGC_CONFIG', h5_data_class=self.AGC_Configs))
            DSP_group.addSubGroup(H5Group(name='AIC_CONFIG', h5_data_class=self.AIC_Configs))
        else:
            DSP_group = self.Root.getSubGroup('DSP_CONFIG')
            DSP_group.popSubGroup(name='RDI_CONFIG')
            DSP_group.popSubGroup(name='PHD_CONFIG')
            DSP_group.popSubGroup(name='AGC_CONFIG')
            DSP_group.popSubGroup(name='AIC_CONFIG')

    def __init__(self, chip_id:str='K60168'):
        if 'K60168' in chip_id.upper():
            self.set_record_attr = Set168Attribute()
        elif 'K60169' in chip_id.upper():
            self.set_record_attr = Set169Attribute()
        else:
            raise ValueError('Unknown chip id: %s'%chip_id)

        self.Root = H5Group()

        self._Data_Configs = DataConfig()
        self.RF_Configs = RFConfig()
        self.DSP_Configs = DSPConfig()
        self.Video_Configs = VideoConfig()

        DSP_group = H5Group(name='DSP_CONFIG', h5_data_class=self.DSP_Configs)

        self.Root.addSubGroup(H5Group(name='DATA_CONFIG', h5_data_class=self._Data_Configs))
        self.Root.addSubGroup(H5Group(name='RF_CONFIG', h5_data_class=self.RF_Configs))
        self.Root.addSubGroup(DSP_group)
        self.Root.addSubGroup(H5Group(name='VIDEO_CONFIG', h5_data_class=self.Video_Configs))



    def addDataSet(self, dataset:H5DataSet, group:H5Group=None):
        '''
        Add dataset to group, if group is None will add to main group.
        '''
        if group:
            group.addDataSet(dataset)
            return
        self.Root.addDataSet(dataset)


    def initConfigs(self, setting_config):
        self.set_record_attr.initConfigs(self, setting_config)
        pass

    def setDataConfig(self, Data_Configs:DataConfig, **kwargs):
        '''
        Update KProcFSM configs.

        :param kwargs: 'Record_frames','Datatime','Description',
                       'Diversity','Duration','Gesture_name',
                       'Hand_type','Mode','Attr_file_name',
                       'Owner','Device','Data_format'
        '''
        for k, v in kwargs.items():
            assert hasattr(Data_Configs, k), 'No attribute "{}" in DataConfigs.'.format(k)
            Data_Configs.__setattr__(k, v)


if __name__ == '__main__':
    data_config = DataConfig(Data_format='RDIPHD')
    RF_config = RFConfig()
    RDI_config = RDIConfig()
    PHD_config = PHDConfig()
    AGC_config = AGCConfig()
    AIC_config = AICConfig()
    DSP_config = DSPConfig()
    Video_config = VideoConfig()

    RC = KKTRecordConfig(Data_Configs=data_config,
                      RF_Configs = RF_config,
                      RDI_Configs = RDI_config,
                      PHD_Configs = PHD_config,
                      AGC_Configs = AGC_config,
                      AIC_Configs = AIC_config,
                      DSP_Configs = DSP_config,
                      Video_Configs=Video_config,
                      )
    RC.Root.showGroup()
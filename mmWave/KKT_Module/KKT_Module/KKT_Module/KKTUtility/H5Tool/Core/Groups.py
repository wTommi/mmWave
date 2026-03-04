from ..Core.DataH5 import H5Group, H5DataSet, DataH5
from dataclasses import dataclass, field
from h5py import File

@dataclass
class DataConfig(DataH5):
    name:str = 'DATA_CONFIG'
    Record_frames:int = field(default=None, metadata={'min': 100})
    Datatime: str = ''
    Description: str = 'Open->Close->Open'
    Diversity: str = 'Random'
    Minimum_gap :int =  field(default=10, metadata={'min': 10})
    Duration: list =  field(default_factory=list)
    Gesture_name: list = field(default_factory=list)
    Hand_type: str = field(default=None, metadata={'choices': ['Right Hand', 'Left Hand']})
    Mode: str = field(default=None, metadata={'choices': ['Manual', 'Pre-define', 'Impulse-like']})
    Attr_file_name: str = 'General_model_record_attribute_manual.xlsx'
    Owner: str = 'Eric'
    Device: str = None
    Data_format: str = field(default='RawData', metadata={'choices': ['RawData', 'RDIPHD']})
    Visualize_config:str = None
    Version:str = None
    Platform:str = None
    FW_version:str = None
    SN:str = None
    Hardware_ID:str = None

@dataclass
class RFConfig(DataH5):
    name:str = 'RF_CONFIG'
    RFIC: str = None
    Chirps: int = None
    SIC_opened: str = None
    MUX: int = None
    RX1_real_compansate: str = None
    RX1_image_compansate: str = None
    RX2_real_compansate: str = None
    RX2_image_compansate: str = None

@dataclass
class DSPConfig(DataH5):
    name:str = 'DSP_CONFIG'
    Map1_nc:int = None
    Map2_nc:int = None
    Gen_Mode: str = None
    Hardware_excel: str = None

@dataclass
class AGCConfig(DataH5):
    name:str = 'AGC_CONFIG'
    alpha:int = None
    log_P_targ:int = None
    AGC_bypass:int = None
    AGC_fix_pt:int = None
    samples_per_ACC:int=None

@dataclass
class AICConfig(DataH5):
    name:str = 'AIC_CONFIG'
    AIC_chirp_periodicity:int = None
    AIC_chirp_log_num:int = None
    AIC_sync_delay:int = None
    AIC_Wstart:int = None
    AIC_Wend:int = None
    AIC_symbol_per_frame:int = None
    AIC_right_shift_num:int = None
    En_first_velocity_est:int = None
    Vel_right_shift_num:int = None
    AIC_fix_pt:int = 0

@dataclass
class PHDConfig(DataH5):
    name:str = 'PHD_CONFIG'
    enable:int = None
    Mode:int = None
    column:int = None
    twiddle_table:int = 0
    conv2polar_gain_RDI:int =None
    conv2polar_gain_phaseFFT:int =None
    PHD_fix_pt:int = 0

@dataclass
class RDIConfig(DataH5):
    name:str = 'RDI_CONFIG'
    Fast_time_sample:int =None
    up_down_combining:int =None
    Fast_time_start_point:int =None
    Fast_downsample_ratio:int =None
    Fast_time_conv2polar:int =None
    Fast_time_post_FFT_comb_enable:int = 0
    Slow_time_512FFT_ext:int =None
    Slow_time_symbols:int =None
    Slow_time_downsample_ratio:int =None
    Slow_time_conv2polar:int =None
    Slow_time_conv2polar_gainshift:int =None
    RDI_fix_pt:int = 0
    Fast_time_rotate_vector_im_ch1:int =None
    Fast_time_rotate_vector_re_ch1:int =None
    Fast_time_rotate_vector_im_ch2:int =None
    Fast_time_rotate_vector_re_ch2:int =None

@dataclass
class VideoConfig(DataH5):
    name: str = 'VIDEO_CONFIG'
    Videos: list = field(default_factory=list)

if __name__ == '__main__':
    f = File('test.h5', 'w')
    file = H5Group(h5_file=f, name='/')
    data_config = H5Group(name='DATA_CONFIG',h5_data_class=DataConfig())
    RF_config = H5Group(name='RF_CONFIG',h5_data_class=RFConfig())
    RDI_config = H5Group(name='RDI_CONFIG',h5_data_class=RDIConfig())
    PHD_config = H5Group(name='PHD_CONFIG',h5_data_class=PHDConfig())
    AGC_config = H5Group(name='AGC_CONFIG',h5_data_class=AGCConfig())
    AIC_config = H5Group(name='AIC_CONFIG',h5_data_class=AICConfig())
    DSP_config = H5Group(name='DSP_CONFIG',h5_data_class=DSPConfig())
    Video_config = H5Group(name='VIDEO_CONFIG',h5_data_class=VideoConfig())

    file.addSubGroup(data_config)
    file.addSubGroup(RF_config)
    file.addSubGroup(DSP_config)
    file.addSubGroup(Video_config)
    DSP_config.addSubGroup(AGC_config)
    DSP_config.addSubGroup(AIC_config)
    DSP_config.addSubGroup(RDI_config)
    DSP_config.addSubGroup(PHD_config)
    ds1 = H5DataSet(name='DS1', shape=(2, 2, 32, 128), h5_file=f)
    file.addDataSet(ds1)

    file.createGroup()
    file.showGroup()
    file.showH5Attributes()
    f.close()



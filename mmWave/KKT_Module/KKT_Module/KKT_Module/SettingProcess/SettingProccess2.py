from __future__ import annotations
import atexit
import time
from threading import Thread
from abc import abstractmethod
from KKT_Module.ksoc_global import kgl
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs
from KKT_Module.SettingProcess.ExcelParsing import ParamDictGenerator , KsocExcelParser
from KKT_Module.SettingProcess.ProcessList import ProcessListGenerator
from KKT_Module.SettingProcess.ScriptSetting import ScriptSetter
from KKT_Module.KKTUtility.H5Tool import KKTH5Tool
from KKT_Module.SettingProcess import log
import os
from typing import Optional,Dict

class Process():
    def __init__(self, next_process:Optional[Process]=None):
        self.next_process = next_process

    def startupProcess(self, config:Optional[SettingConfigs]=None):
        log.info(f"# ======= Run {self.__class__.__name__} process =======")
        s = time.time()
        self._startUp(config)
        log.info(f'{self.__class__.__name__} {time.time() - s}s')
        if self.next_process is not None:
            self.next_process.startupProcess(config)

    def setNext(self, next_process:Process):
        self.next_process = next_process
        return self.next_process

    @abstractmethod
    def _startUp(self, config:Optional[SettingConfigs]):
        pass

    @abstractmethod
    def showInfo(self):
        pass



# Setting process class

class SettingProc():
    def __init__(self, process:Optional[Process]=None):
        atexit.register(self.__closeDevice)
        self.process = process
        self.processes_dict:Dict[str, Process]={'Connect Device' : ConnectDevice(),
                             'Reset Device' : ResetDevice(),
                             'Phase Calibration' : CompensatePhase(),
                             'Script Setting' : SetScript(),
                             'Gen Process Script': GenProcessScript(),
                             'Gen Param Dict' : GetParamDict(),
                             'Set Script' : SetScript(),
                             'Run SIC' : RunSIC(),
                             'Modulation On' : ModulationOn(),
                             'Get Gesture Dict' : GenGestureDict(),
                             }
    def startUp(self, config):
        assert config.ScriptDir.get('Script_path') is not None, 'Please set the script path'
        if self.process is None:
            start_process = None
            process = None
            for process_name in config.Processes:
                next_process = self.processes_dict[process_name]
                next_process.next_process = None
                if start_process is None:
                    start_process = next_process
                    process = start_process
                    continue
                process.next_process = next_process
                process = process.next_process
        else:
            start_process = self.process
        start_process.startupProcess(config)

    def __closeDevice(self):
        if kgl.ksoclib != None:
            kgl.ksoclib.closeCyDevice()
            # kgl.ksoclib = None
            log.info("Stop ksoc lib...")

    def startSetting(self,config):
        '''Start setting process in a subthread.'''
        arg = (config ,)
        T = Thread(target=self.startUp, args=arg)
        T.start()



# Process Class
class ConnectDevice(Process):
    '''
    Connect to the Device.
    '''
    def __init__(self, next_process:Optional[Process]=None):
        super(ConnectDevice, self).__init__(next_process=next_process)
        self.device = ''
        self.FW_ver = ''
        self.IC_info = ''

    def _startUp(self, config=None):
        super(ConnectDevice, self)._startUp(config)
        self.progress = [0,1]
        self.device = kgl.ksoclib.connectDevice()
        log.info('# -Device was connected')
        try:
            self.FW_ver = kgl.ksoclib.getFWVersion()
        except Exception as e:
            log.info('Cannot get FW version')
            log.debug(e)
            pass

        try:
            self.IC_info = kgl.ksoclib.getChipID().strip().split(' ')
        except Exception as e:
            log.info('Cannot get IC info')
            log.debug(e)
        self.progress[0] = 1
        # return self.device, FW_ver, IC_info

    def showInfo(self):
        log.info('Connect to {}'.format(self.device))

class ResetDevice(Process):
    '''
    Reset hardware register.
    '''
    def __init__(self, next_process:Optional[Process]=None):
        super(ResetDevice, self).__init__(next_process=next_process)
        self.progress = None

    def _startUp(self, config=None):
        super(ResetDevice, self)._startUp(config)
        self.progress = [0, 1]
        if kgl.ksoclib.rficRegRead(0x0029) == 0x40FE:
            kgl.ksoclib.switchModulationOn(False)
            log.info('Modulation off')
        kgl.ksoclib.resetDevice()
        kgl.ksoclib.connectDevice()
        # kgl.ksoclib.regWrite(0x50000030, [0x80010000])
        self.progress[0] = 1
        log.info('# -Device was reseted')

    def showInfo(self):
        log.info('Device Reseted')

class CompensatePhase(Process):
    '''
    Do the phase calibration.


    '''
    def __init__(self):
        super().__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(CompensatePhase, self)._startUp(config)
        s = time.time()
        from KKT_Module.kkt_module.KKTUtility.RFControl import RFController
        from KKT_Module.SettingProcess.PhaseCalibration import PhaseCalibration
        RFController = RFController()
        self.progress = [0, 1]
        PhaseK = PhaseCalibration(config)
        # if config.PhaseK.OpenRXByScript:
        # RX_enable = RFController.getOpenedRX()
        # open_RX = RXControl.enableRFRX(open_RX1=RX_enable['RX1'],
        #                                open_RX2=RX_enable['RX2'],
        #                                open_RX3=RX_enable['RX3']
        #                                )
        # else:
        #     open_RX = RXControl.enableRFRX(open_RX1=config.PhaseK.OpenRX1,
        #                                    open_RX2=config.PhaseK.OpenRX2,
        #                                    open_RX3=config.PhaseK.OpenRX3,
        #                                    )

        # RXControl.rewriteMuxConfig(open_RX, AI_mux=config.HardwareSetting.AI_MUX, tracking_mux=config.HardwareSetting.Tracking_MUX)
        PhaseK.calibrate()
        PhaseK.updateRFConfig(config.PhaseKConfigs)
        self.progress[0] = 1
        log.info('phase calibration {}s'.format(time.time() - s))

    def showInfo(self):
        ...

class ModulationOn(Process):
    '''
    Modulation on.
    '''
    def __init__(self):
        super(ModulationOn, self).__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(ModulationOn, self)._startUp(config)
        self.progress = [0, 1]
        if config.ModulationOn.Enable:
            config.ModulationOn.Status = False
            kgl.ksoclib.rficRegWrite(addr=0x0029, val=0x40FE)
            time.sleep(0.3)
            result = kgl.ksoclib.rficRegRead(0x0029)
            config.ModulationOn.Status = False
            assert result == 0x40FE, 'Modulation on failed !'
            config.ModulationOn.Status = True
        self.progress[0] = 1
        log.info('# -Modulation on : {}'.format(config.ModulationOn.Status))

    def showInfo(self):
        ...

class SetScript(Process):
    '''
    Set RF, AI and hardware setting by setting script.
    '''
    def __init__(self):
        super(SetScript, self).__init__()
        self.progress = None
        from KKT_Module.kkt_module.KKTUtility.RFControl import RFController
        self.RFController = RFController()


    def _startUp(self, config=None):
        super(SetScript, self)._startUp(config)

        SS = ScriptSetter()
        self.progress = SS.process
        # if config.RFSetting.Enable:
        #     self.RFController.enableRX('RX1', True)
        #     self.RFController.enableRX('RX2', True)
        #     self.RFController.enableRX('RX3', True)
        SS.configByDevice(script_dir=config.ScriptDir,
                          procList=config.ProcList,
                          write_AI=config.AIWeight.Enable,
                          write_RF=config.RFSetting.Enable)

    def showInfo(self):...

class GenProcessScript(Process):
    '''
    Generate setting process script.
    '''
    def __init__(self):
        super(GenProcessScript, self).__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(GenProcessScript, self)._startUp(config)
        self.progress = [0, 1]
        exl_file_name = config.ScriptDir.get('Hardware_excel')
        txt_file_name = config.ScriptDir.get('Hardware_text')
        PLG = ProcessListGenerator(config.Chip_ID)
        if exl_file_name is None:
            assert txt_file_name is not None, 'Empty script file !'
            txt_file_name = txt_file_name
            assert os.path.isfile(txt_file_name), 'File not found !'
            config.ProcList = PLG.readProcListFromFile(txt_file_name)
        else:
            exl_file_name = exl_file_name
            assert os.path.isfile(exl_file_name), 'File not found !'
            config.Sheet_param = KsocExcelParser.parsing(exl_file_name)
            config.ProcList = PLG.genProcessList(config.Sheet_param)
            if config.GenScript.SaveTextScript:
                paramname = os.path.basename(exl_file_name)
                paramname = paramname.split(".")
                paramname.pop(-1)
                paramname.insert(0, 'param_')
                paramname.append('.txt')
                paramname = ''.join(paramname)
                paramdir = os.path.join(kgl.KKTTempParam, config.ScriptDir['Script_path'], 'param')
                paramfile = os.path.join(paramdir, paramname)
                if not os.path.isdir(paramdir):
                    os.makedirs(paramdir)
                PLG.saveProcListToFile(filepath=paramfile, proclist=config.ProcList)
        self.progress[0] = 1

    def showInfo(self):...

class GenGestureDict(Process):
    '''
    Get gesture mapping dictionary for Ai weight H5 file.
    '''
    def __init__(self):
        super(GenGestureDict, self).__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(GenGestureDict, self)._startUp(config)
        self.progress = [0, 1]
        assert config.ScriptDir.get('AIweight_h5') is not None, 'Empty AIweight H5 file !'
        mapping_dicts = KKTH5Tool.getGestureDict(config.ScriptDir['AIweight_h5'])

        if mapping_dicts.get('Mapping_dict_Core') is None:
            assert mapping_dicts.get('Mapping_dict') is not None,'Empty Core Gestures !'
            config.CoreGestures = mapping_dicts.get('Mapping_dict')
        else:
            config.CoreGestures = mapping_dicts.get('Mapping_dict_core')
        config.SiameseGestures = mapping_dicts.get('Mapping_dict_siamese')
        log.info(f'Core Gestures dictionary : {config.CoreGestures}' )
        log.info(f'Siamese Gestures dictionary :{config.SiameseGestures}' )
        self.progress[0] = 1


    def showInfo(self):...

class GetParamDict(Process):
    '''
    Generate hardware setting parameter dictionary from excel or text file.
    '''
    def __init__(self):
        super(GetParamDict, self).__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(GetParamDict, self)._startUp(config)

        self.progress = [0, 1]
        if 'K60168' in config.Chip_ID:
            PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_168B_setting.json')
        elif 'K60169' in config.Chip_ID:
            PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_169_setting.json')
        else:
            raise ValueError('Unknown Chip ID !')
        # PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_setting.json')
        config.ParamDict = PDG.writeRegVal(config.ProcList)
        self.progress[0] = 1


    def showInfo(self):...

class RunSIC(Process):
    '''
    Set SIC setting and trigger.
    '''
    def __init__(self):
        super(RunSIC, self).__init__()
        self.progress = None

    def _startUp(self, config=None):
        super(RunSIC, self)._startUp(config)
        s = time.time()
        self.progress = [0, 1]
        SIC_trigger = kgl.ksoclib.getRFSICEnableStatus()
        log.info("RF SIC Open : {}".format(SIC_trigger))
        config.SIC.SIC_open = SIC_trigger
        # SIC_trigger = False
        #runSIC(SIC_trigger, config)
        kgl.ksoclib.initSIC()
        self.progress[0] = 1
        log.info('SIC trigger {}s'.format(time.time() - s))

    def showInfo(self):...


if __name__ == '__main__':
    from typing import Union


    def get_settings() -> list:
        dirs = os.listdir(kgl.KKTTempParam)
        for dir in dirs:
            if not os.path.isdir(os.path.join(kgl.KKTTempParam, dir)):
                dirs.remove(dir)
        return dirs

    def set_setting(setting: Union[int, str]):
        if type(setting) == int:
            setting = get_settings()[setting]
        log.info(f"Setting: {setting}")
        reset_porc = ResetDevice()
        gen_script_proc = GenProcessScript()
        gen_param_proc = GetParamDict()
        get_gesture_proc = GenGestureDict()
        set_script_proc = SetScript()
        run_sic_proc = RunSIC()
        compensate_phase_proc = CompensatePhase()
        modulation_on_proc = ModulationOn()
        start_proc = reset_porc
        proc = start_proc.setNext(gen_script_proc)
        proc = proc.setNext(gen_param_proc)
        proc = proc.setNext(get_gesture_proc)
        proc = proc.setNext(set_script_proc)
        proc = proc.setNext(run_sic_proc)
        proc = proc.setNext(compensate_phase_proc)
        proc = proc.setNext(modulation_on_proc)

        ksp = SettingProc(start_proc)
        setting_config = SettingConfigs()
        setting_config.Chip_ID = 'K60169'
        # setting_config.Processes = [
        # 'Reset Device',
        # 'Gen Process Script',
        # 'Gen Param Dict',
        # 'Get Gesture Dict',
        # 'Set Script',
        # 'Run SIC',
        # 'Phase Calibration',
        # 'Modulation On',
        # ]
        setting_config.setScriptDir(setting)
        ksp.startUp(setting_config)
        log.info("Setting Done!")
        log.info("Setting UserTable Done!")

    kgl.setLib()
    # kgl.ksoclib.switchLogMode(is_print=True)
    log.info(kgl.ksoclib.connectDevice())
    settings = get_settings()
    for i in range(len(settings)):
        print(f"{i}: {settings[i]}")
    setting = eval(input('select setting: '))

    set_setting(setting)
    pass

















import os
from typing import Union
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs
from KKT_Module.ksoc_global import kgl

if __name__ == '__main__':
    def get_settings() -> list:
        dirs = os.listdir(kgl.KKTTempParam)
        for dir in dirs:
            if not os.path.isdir(os.path.join(kgl.KKTTempParam, dir)):
                dirs.remove(dir)
        return dirs

    def set_setting(setting: Union[int, str]):
        if type(setting) == int:
            setting = get_settings()[setting]
        print(f"Setting: {setting}")
        ksp = SettingProc()
        c = ConnectDevice()
        c.startUp()
        setting_config = SettingConfigs()
        setting_config.Chip_ID = 'K60169'
        setting_config.Processes = [
        'Reset Device',
        'Gen Process Script',
        'Gen Param Dict',
        'Get Gesture Dict',
        'Set Script',
        'Run SIC',
        'Phase Calibration',
        'Modulation On',
        ]
        setting_config.setScriptDir(setting)
        ksp.startUp(setting_config)
        print("Setting Done!")
        # kgl.ksoclib.setUserTable_bin(r'C:\work\Python\KSOC Tool in MVVM\TempParam\fpga_test_for_gen_1101_1T1R_RDI\userTable\UserTable_Loopback.bin')
        print("Setting UserTable Done!")

    kgl.setLib()
    # kgl.ksoclib.switchLogMode(is_print=True)
    print(kgl.ksoclib.connectDevice())
    settings = get_settings()
    for i in range(len(settings)):
        print(f"{i}: {settings[i]}")
    setting = eval(input('select setting: '))

    set_setting(setting)
import os
from typing import Union
from PySide2 import QtWidgets, QtGui, QtCore
from KKT_Module.SettingProcess.SettingProccess import SettingProc
from KKT_Module.SettingProcess.Utilitys import getConfigList
from KKT_Module.SettingProcess.SettingConfig import SettingConfigs
from KKT_Module.SettingProcess.UI.SetScriptWidget import SetScriptWidget
from KKT_Module.ksoc_global import kgl


ksp = SettingProc()


def set_setting(setting: Union[int, str]):
    setting_config = SettingConfigs()
    setting_config.Chip_ID = kgl.ksoclib.getChipID()
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
    ksp.startSetting(setting_config)


if __name__ == '__main__':
    kgl.setLib()
    print(kgl.ksoclib.connectDevice())

    app = QtWidgets.QApplication([])
    widget = SetScriptWidget(setting_list=getConfigList(kgl.KKTTempParam))
    widget.SetScript_Signal.connect(set_setting)

    def update_proc():
        widget.updateProcess(ksp.getProgress())
        pass

    widget.update_timer.timeout.connect(update_proc)
    ksp.end_callback_func = widget.sig_stop_process.emit

    widget.show()

    app.exec_()


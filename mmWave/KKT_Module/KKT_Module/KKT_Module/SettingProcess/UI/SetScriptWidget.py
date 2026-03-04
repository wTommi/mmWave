from PySide2 import QtWidgets, QtGui, QtCore
from KKT_Module.ksoc_global import kgl
from KKT_Module.SettingProcess.Utilitys import getConfigList
from pathlib import Path
from typing import List, Tuple
class SubWidgetQFrame(QtWidgets.QFrame):
    def __init__(self, border=True):
        super(SubWidgetQFrame, self).__init__()
        self.setObjectName("frame")
        if border:
            self.default_css = "#frame {border: 1px solid lightgrey; border-radius: 3px;}"
            self.setStyleSheet(self.default_css)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 6, 0, 6)

        self.grid_widget = QtWidgets.QWidget()
        self.layout.addWidget(self.grid_widget)

        self.grid = QtWidgets.QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(6, 0, 6, 0)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.setup()

    def setup(self):
        pass

class SetScriptProgressBar(QtWidgets.QProgressBar):
    DEFAULT_STYLE = """ 
            QProgressBar{ 
                border: 1px solid lightgrey; 
                text-align: center 
            } 

            QProgressBar::chunk { 
                background-color: lightgreen; 

            } 
            """
    COMPLETED_STYLE = """ 
     QProgressBar{ 
         border: 1px solid lightgrey; 
         text-align: center 
     } 

     QProgressBar::chunk { 
         background-color: limegreen; 
     } 
     """
class SetScriptWidget(SubWidgetQFrame):
    SetScript_Signal = QtCore.Signal(object)
    sig_stop_process = QtCore.Signal()
    def  __init__(self, setting_list ,label:str='Set Script :', progress_bar=True,  border=True):
        super().__init__(border=border)
        self._setting_list = setting_list
        self._progress_bar = progress_bar
        self._label_text = label
        self._script_set = False
        self.setupGUI()
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(5)
        self.sig_stop_process.connect(self.processDone)
    def mousePressComboBox(self, event:QtGui.QMouseEvent) -> None:
        self._setting_list = getConfigList(kgl.KKTTempParam)
        self.ccb_setting.clear()
        self.ccb_setting.addItems(self._setting_list)
        self.ccb_setting.showPopup()
        event.accept()


    def setupGUI(self):
        self.grid.setColumnStretch(2, 1)
        self.ccb_setting = QtWidgets.QComboBox()
        self.ccb_setting.setFont(QtGui.QFont('Yu Gothic UI', 10))
        self.ccb_setting.addItems(self._setting_list)
        self.ccb_setting.mousePressEvent = self.mousePressComboBox

        self._title = QtWidgets.QLabel(self._label_text)
        self._title.setFont(QtGui.QFont('Yu Gothic UI', 10))

        self._pb_start = QtWidgets.QPushButton('Set Script')
        self._pb_start.setFont(QtGui.QFont('Yu Gothic UI', 10))
        self._pb_start.clicked.connect(self._setScript)

        ly_select = QtWidgets.QHBoxLayout()
        if self._label_text is not None:
            ly_select.addWidget(self._title, 1)
        ly_select.addWidget(self.ccb_setting, 6)
        ly_select.addWidget(self._pb_start, 1)

        self._lb_progress = QtWidgets.QLabel(' [ Progress ]')
        self._lb_progress.setFont(QtGui.QFont('Yu Gothic UI', 10))

        self._pgb = SetScriptProgressBar()
        self._pgb.setRange(0, 100)
        self._pgb.setValue(0)
        self._pgb.setFormat('%v%')
        self._pgb.setFont(QtGui.QFont('Yu Gothic UI', 10))
        self._pgb.setTextVisible(True)

        ly_progress = QtWidgets.QGridLayout()
        ly_progress.addWidget(self._pgb, 0, 0)
        ly_progress.addWidget(self._lb_progress, 0, 0)


        # self.openRX = HComboBoxWidget('Open RX :',['RX23'])
        # self.RXCheckBox = CheckBoxListWidget({'RX1':{'enable':True, 'check':False},
        #                                        'RX2':{'enable':True, 'check':True},
        #                                        'RX3':{'enable':False, 'check':True}},label='Open RX :',cols=3)

        self.grid.addLayout(ly_select, 0, 0, 1, 4)
        if self._progress_bar:
            self.grid.addLayout(ly_progress, 1, 0, 1, 4)
        pass

    def _setScript(self):
        self.initStatus()
        self.enableWidget(False)
        self.update_timer.start()
        self.SetScript_Signal.emit(self.ccb_setting.currentText())

    def getItemCheck(self, item):
        return self.RXCheckBox.getItemCheck(item)

    def getItemStatus(self):
        return self.RXCheckBox.getItemsStatus()

    def getSetting(self):
        return self.ccb_setting.currentText()

    def initStatus(self):
        if self.update_timer.isActive():
            self.update_timer.stop()
        self._script_set = False
        self._pgb.setValue(0)
        self._lb_progress.setText(' [ Progress ]')
        self.enableWidget(True)

    def updateProcess(self, process:Tuple[str, Tuple[int, int], int]):
        if not self._progress_bar:
            return
        # process = self._setting_proc.getProgress()
        if process is None:
            return
        process_name = process[0]
        current_process = process[1][0]
        total_process = process[1][1]
        progress_value = process[2]
        self._lb_progress.setText(f' [ {process_name} ] ({current_process}/{total_process})')
        self._pgb.setValue(progress_value)

    def processDone(self):
        while self.update_timer.isActive():
            self.update_timer.stop()
        self._lb_progress.setText(' [ Done ]')
        self._pgb.setValue(100)
        self.enableWidget(True)
        self._script_set = True
        pass

    def enableWidget(self, enable:bool):
        self._pb_start.setEnabled(enable)
        # self.RXCheckBox.setEnabled(enable)
        self.ccb_setting.setEnabled(enable)
        pass

class SetScriptWidgetAIoT(SetScriptWidget):
    def __init__(self, setting_list ,label='Hardware Setting:', progress_bar=True,  border=True):
        super().__init__(setting_list, label=label, progress_bar=progress_bar, border=border)

    def setupGUI(self):
        super().setupGUI()
        self._pgb.setStyleSheet(SetScriptProgressBar.DEFAULT_STYLE)
        ly_set = QtWidgets.QHBoxLayout()
        if self._label_text is not None:
            ly_set.addWidget(self._title, 1)
        # ly_set.addWidget(self.ccb_setting, 6)
        ly_set.addWidget(self._pb_start, 1)

        ly_select = QtWidgets.QHBoxLayout()
        ly_select.addWidget(self.ccb_setting, 6)

        ly_progress = QtWidgets.QGridLayout()
        ly_progress.addWidget(self._pgb, 0, 0)
        ly_progress.addWidget(self._lb_progress, 0, 0)

        self.grid.addLayout(ly_set, 0, 0, 1, 4)
        self.grid.addLayout(ly_select, 1, 0, 1, 4)
        if self._progress_bar:
            self.grid.addLayout(ly_progress, 2, 0, 1, 4)


    def initStatus(self):
        super().initStatus()
        self._pgb.setStyleSheet(SetScriptProgressBar.DEFAULT_STYLE)
    def setProgressBarColor(self, color):

        self._pgb.setStyleSheet("QProgressBar:chunk{background-color: b;}"
                                )
    def setRXSection(self, visible, RX1, RX2, RX3):
        self._RXCheckBox.setVisible(visible)
        item_dict = self.getItemStatus()
        item_dict.get('RX1')['check'] = RX1
        item_dict.get('RX2')['check'] = RX2
        item_dict.get('RX3')['check'] = RX3
        self._RXCheckBox.setItemsConfigs(item_dict)

    def processDone(self):
        super().processDone()
        self._pgb.setStyleSheet(SetScriptProgressBar.COMPLETED_STYLE)

if __name__ == '__main__':
    import sys
    i = 0
    p = 0
    def update_func():
        global i, p
        i = i + 1
        wg.updateProcess((f'process {p}', (i, 20), p))
        if i == 20:
            p = p + 1
            i = 0
        if p == 100:
            wg.processDone()
            i = 0
            p = 0


    app = QtWidgets.QApplication([])
    wg = SetScriptWidgetAIoT(['a', 'b', 'c', 'd'])
    wg.update_timer.timeout.connect(update_func)
    wg.show()
    sys.exit(app.exec_())

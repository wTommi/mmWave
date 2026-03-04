import pyqtgraph as pg
from PySide2 import QtCore, QtWidgets, QtGui
from typing import Literal, overload, Optional,List, Dict
from KKT_UI.KKTGraph.Base.StemPlot import StemPlotWidget
from KKT_UI.QTWidget.qt_obj import InputThreshold


class GestureLabel(QtWidgets.QLabel):
    time_out = 700
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setText(self._genText())
        self.setFont(QtGui.QFont("Yu Gothic UI",14))
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.detectGesTimeout)

    def _genText(self, ges:str='')->str:
        return f'Gesture : {ges:20s}'

    def setGesture(self, ges:str):
        if self.timer.isActive():
            self.timer.stop()
        self.setText(self._genText(ges))
        self.timer.start(self.time_out)
    def detectGesTimeout(self):
        self.timer.stop()
        self.setText(self._genText())

class GestureStemWidget(QtWidgets.QFrame):
    @property
    def axis_range(self) -> list:
        ''' The number of chirp.'''

        return self._axis_range

    @axis_range.setter
    def axis_range(self, value: list):
        if value is not None:
            self._axis_range = value
            self.ges_stem_plot.setAxisRange(value[0], value[1])

    def __init__(self, title='Gesture vs. Probability', ges_dict:Dict[int, str]=None):
        super().__init__()
        self.stem_plot_title = title
        self.ges_dict = {0: 'ges 0', 1: 'ges 1', 2: 'ges 2', 3: 'ges 3', 4: 'ges 4', 5: 'ges 5'} if ges_dict is None else ges_dict

        self._lastTime = None
        self._axis_range = None
        self.setupGUI()


    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

    def setGestureDict(self, ges_dict:Dict[int, str]):
        self.ges_dict = ges_dict
        self.ges_stem_plot.getAxisItem('bottom').setTicks([[(int(k),str(v)) for k, v in self.ges_dict.items()]])

    def addThresholdWidget(self, threshold:List[float]=[0.2, 0.4], layout:QtWidgets.QVBoxLayout=None):
        self.threshold = InputThreshold(threshold=threshold)
        line_1 = pg.InfiniteLine(pos=threshold[0], angle=0, pen=pg.mkPen('r', width=1, dash=[3]), movable=False)
        line_1.setToolTip('Lower Threshold')
        line_2 = pg.InfiniteLine(pos=threshold[1], angle=0, pen=pg.mkPen('g', width=1, dash=[3]), movable=False)
        line_2.setToolTip('Upper Threshold')
        self.ges_stem_plot.addItem(line_1)
        self.ges_stem_plot.addItem(line_2)
        self.threshold._sb_lower.valueChanged.connect(line_1.setValue)
        self.threshold._sb_upper.valueChanged.connect(line_2.setValue)

        if layout:
            layout.addWidget(self.threshold, alignment=QtCore.Qt.AlignLeft)
        return self.threshold

    def setupGUI(self):

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        self.lb_gesture = GestureLabel()
        layout.addWidget(self.lb_gesture, alignment=QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)

        self.ges_stem_plot = StemPlotWidget(title=self.stem_plot_title)
        self.ges_stem_plot.has_point = True
        self.ges_stem_plot.view_box.setLimits(yMin=0, yMax=1.1, minYRange=1.1)
        self.ges_stem_plot.getAxisItem('bottom').setTicks([[(k,v) for k, v in self.ges_dict.items()]])
        self.ges_stem_plot.getAxisItem('left').setLabel('Probability')
        self.ges_stem_plot.view_box.setDefaultPadding(padding=0.25)

        layout.addWidget(self.ges_stem_plot)



    def setGestureLabel(self, ges:str):
        self.lb_gesture.setGesture(str(ges))
        pass

    def getThresholdList(self):
        return self.threshold.getThreshold()


    def setData(self, data):
        self.ges_stem_plot.setData(data)

    def clearData(self):
        self.ges_stem_plot.clearData()

    def setThreshold(self, threshold):
        self.threshold.setThreshold(threshold)


if __name__ == '__main__':
    import sys
    import numpy as np
    count = 0
    def data_update():
        global wg
        global count
        y = np.random.random(size=(5))
        ges_idx = np.argmax(y)
        count += 1
        wg.setGestureLabel(wg.ges_dict.get(ges_idx))

        if count % 2 == 0:
            wg.clearData()
        else:
            wg.setData(y)

    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    wg = GestureStemWidget()
    win.setCentralWidget(wg)
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(500)

    # display_plot_image_with_minimal_setup()
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
    qtimer.stop()

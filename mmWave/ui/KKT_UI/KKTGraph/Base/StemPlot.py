import numpy as np
import pyqtgraph as pg
from typing import Any, Optional, Tuple
from PySide2 import QtGui, QtCore, QtWidgets
from KKT_UI.KKTGraph.Base.KKTGraph import DataPlotWidget, KKTGraph


class StemPlotWidget(DataPlotWidget, KKTGraph):
    _point_symbol_size = 8
    @property
    def has_point(self)->bool:
        return self._has_point
    @has_point.setter
    def has_point(self, value:bool):
        self._has_point = value
        self._setPointCurve()

    def __init__(self, parent: QtWidgets.QWidget = None, title="Stem Plot", enable_menu=False):
        super().__init__(parent=parent, enable_menu=enable_menu, title=title)
        self.stem_curve:Optional[pg.PlotDataItem] = None
        self.point_curve:Optional[pg.PlotDataItem] = None
        self.has_point = False
        self._setStemCurve()
        self._setPointCurve()
        self.scale(3, 4)

    def _setPointCurve(self):
        if self.has_point:
            if self.point_curve in self.plot_item.items:
                return
            self.point_curve = self.plot(pen=None, symbol='o', symbolPen='b',
                                         symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)),
                                         symbolSize=self._point_symbol_size,
                                         name='Points')
        else:
            self.plot_item.removeItem(self.point_curve)
            self.point_curve = None

    def _setStemCurve(self):
        if self.stem_curve in self.plot_item.items:
            return
        self.stem_curve = self.plot(pen=pg.mkPen('b', width=0.5), connect='pairs', name='Stems')

    def setAxisRange(self, x_range:Tuple[float, float], y_range:Tuple[float, float]):
        self.view_box.setXRange(x_range[0], x_range[1], padding=.01)
        self.view_box.setYRange(y_range[0], y_range[1], padding=0)

    def setData(self, data:np.ndarray):
        '''Set data to plot
        Args:
            data (np.ndarray): 1D array of data
            '''
        if self.stem_curve is None:
            self._setStemCurve()
            self._setPointCurve()

        x = np.arange(0, len(data))

        if self.has_point :
            self.point_curve.setData(x, data)

        new_x = np.insert(x.reshape(-1, 1), 1, x, axis=1).flatten()
        new_y = np.insert(data.reshape(-1, 1), 0, 0, axis=1).flatten()
        self.stem_curve.setData(new_x, new_y)

    def clearData(self):
        if self.stem_curve != None:
            self.removeItem(self.stem_curve)
            self.stem_curve = None

        if self.point_curve != None:
            self.removeItem(self.point_curve)
            self.point_curve = None

if __name__ == '__main__':
    def data_update():
        global wg
        global count

        y = np.random.randint(100, size=(16))
        count += 1
        if count % 2 == 0:
            wg.clearData()
        else:
            wg.setData(y)
    count = 0
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    wg = StemPlotWidget()
    wg.setAxisLabel(left='probability', bottom='gestures')
    wg.has_point = True
    win.setCentralWidget(wg)

    wg.setAxisRange([-1, 16], [0, 100])
    qtimer = QtCore.QTimer()

    qtimer.timeout.connect(data_update)
    qtimer.start(1000)
    # data_update()
    win.show()

    app.exec_()

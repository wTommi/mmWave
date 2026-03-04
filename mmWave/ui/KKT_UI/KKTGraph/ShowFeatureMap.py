from __future__ import annotations
from typing import Tuple, List, Iterator, Sequence, Literal
import numpy as np
import pyqtgraph as pg
from PySide2 import QtWidgets, QtCore, QtGui
from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget
from KKT_UI.QTWidget.qt_obj import DoubleSpinBoxListWidget
from dataclasses import dataclass

@dataclass
class FeatureMapPlotState():
    chirp:int
    sample:int
    max_distance:float
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]
    def renderWidget(self, widget:FeatureMapPlotWidget)->FeatureMapPlotWidget:
        widget.plot_item.setTitle(self.title)
        widget.setAxis(x_len=(self.x_range[1]-self.x_range[0]),
                       x_start=self.x_range[0],
                       y_start=self.y_range[0],
                       y_len=self.max_distance/2)
        widget.setAxisLabel(**self.axis_label)
        return widget

##=====================================================================================
class FeatureMapPlotWidget(DataPlotWidget, KKTGraph):
    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, value):
        self._axis = value
        self.setAxisRange(x_range=self._axis[0], y_range=self._axis[1])

    @property
    def max_distance(self):
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        self._max_distance = value

    @property
    def chirp(self):
        return self._chirp

    @chirp.setter
    def chirp(self, value):
        self._chirp = value
        self.map_shape = (self._sample//4, self._chirp)
        self.feature_map.setImage(np.zeros(self.map_shape).T, autoLevels=False)
        self.setAxis(x_len=(self._axis[0][1]-self._axis[0][0]),
                       x_start=self._axis[0][0],
                       y_start=self._axis[1][0],
                       y_len=self.max_distance/2)

    @property
    def sample(self):
        return self._sample

    @sample.setter
    def sample(self, value):
        self._sample = value
        self.map_shape = (self._sample//4, self._chirp)
        self.feature_map.setImage(np.zeros(self.map_shape).T, autoLevels=False)
        self.setAxis(x_len=(self._axis[0][1] - self._axis[0][0]),
                     x_start=self._axis[0][0],
                     y_start=self._axis[1][0],
                     y_len=self.max_distance / 2)


    def __init__(self, parent=None, title='Feature Map', enable_menu=True, chirp=32, sample=128, max_distance:float=68, whole_map=False, **kwargs):
        super().__init__(parent=parent, title=title, enable_menu=enable_menu)
        # plot config
        self._chirp = chirp
        self._sample = sample
        if whole_map:
            self.map_shape = (sample//2, chirp)
        else:
            self.map_shape=(sample//4, chirp)
        self._max_distance = max_distance
        self._axis = [(-0.15, 0.15), (0, self.max_distance/2)]

        self.setupUI()

        self.feature_map.setImage(np.zeros(self.map_shape).T, autoLevels=False)
        self.feature_map.setLevels(levels=(0, 1500))
        self.bar.setLevels(low=0, high=1500)
        self.default_state = FeatureMapPlotState(chirp=self.chirp,
                                                 sample=self.sample,
                                                 max_distance=self.max_distance,
                                                 x_range=self._axis[0],
                                                 y_range=self._axis[1],
                                                 title=title,
                                                 axis_label={'left':'Distance (cm)', 'bottom':'Velocity (cm/s)'}
                                                 )
        self.default_state.renderWidget(self)


    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

    def setupMenu(self):
        super().setupMenu()
        for action in self.view_box_menu.actions():
            if action.text() in ('View All', 'X axis', 'Y axis', 'Mouse Mode'):
                action.setVisible(False)

        map_option = self.plot_option_menu.addMenu('Map Options')
        act_map_option = QtWidgets.QWidgetAction(map_option)
        self.cb_Map_configs = DoubleSpinBoxListWidget(items={
            'FT_downSample': {'Enable': True,
                              'Label': 'Fast Down Sample Ratio',
                              'Check': True,
                              'Range': [1, 2, 1],
                              'Value': 2,
                              },
            'ST_downSample': {'Enable': True,
                              'Label': 'Slow Down Sample Ratio',
                              'Check': True,
                              'Range': [1, 2, 1],
                              'Value': 2,
                              },
            'FT_startPoint': {'Enable': True,
                              'Label': 'RDI Map Start Range (cm)',
                              'Check': True,
                              'Range': [0, 34, 34 / 64],
                              'Value': 0,
                              },
        })
        act_map_option.setDefaultWidget(self.cb_Map_configs)
        map_option.addAction(act_map_option)

        self.cb_Map_configs.change_Signal.connect(self.changeMapConfigs)

    def changeMapConfigs(self, items:dict):
        self.setAxis(x_len=0.3, x_start=-0.15, y_start=0 + items['FT_startPoint']['Value'],
                                y_len=self.max_distance / 2, x_ratio=items['ST_downSample']['Value'],
                                y_ratio=items['FT_downSample']['Value'])
        pass

    def setAxis(self, x_len=0.3, y_len=34, x_start:float=-0.15, y_start:float=0, x_ratio=2, y_ratio=2):
        '''

        Parameters
        ----------
        x_len :X軸刻度長度
        y_len :Y軸刻度長度
        x_start :X軸刻度起始點
        y_start :Y軸刻度起始點
        x_ratio :X軸刻度比例
        y_ratio :Y軸刻度比例

        Returns
        -------

        '''

        if y_len is not None:
            self.max_distance = y_len * 2

        y_len = self.max_distance / 2 * (y_ratio / 2)
        x_len = x_len * (x_ratio / 2)
        x_start = x_start * (x_ratio /2)

        tr = QtGui.QTransform()
        tr.scale(x_len / self.map_shape[1], y_len / self.map_shape[0])
        tr.translate(x_start/(x_len /self.map_shape[1]), y_start/(y_len/ self.map_shape[0]))
        self.feature_map.setTransform(tr)
        self.setAxisRange(x_range=(x_start, x_start + x_len), y_range=(y_start, y_start + y_len), padding=0)

    def setupUI(self):
        self.feature_map = pg.ImageItem()
        # self.feature_map.setBorder(b={'color': 'transparent', 'width': 10})

        colors = [
            (25, 25, 112, 255),
            (0, 0, 255, 255),  # blue
            (0, 255, 255, 255),  # Aqua
            (0, 255, 0, 255),  # lime
            (255, 255, 0, 255),  # yellow
            (255, 0, 0, 255)  # Red
        ]
        pos = [0.0, 0.1, 0.25, 0.45, 0.7, 1.0]
        color_map = pg.ColorMap(pos=pos, color=colors)
        self.feature_map.setColorMap(color_map)
        self.plot_item.addItem(self.feature_map)
        self.bar = pg.ColorBarItem(interactive=False, colorMap=color_map, label='Level scale color bar')
        for axe in ('left', 'bottom', 'right', 'top'):
            self.bar.getAxis(axe).label.setFont(QtGui.QFont('Yu Gothic UI', 10))
            self.bar.getAxis(axe).setStyle(tickFont=QtGui.QFont('Yu Gothic UI', 10))
        self.bar.setImageItem(self.feature_map, insert_in=self.plot_item)
        self.bar.setZValue(99)


        self.line = pg.InfiniteLine(pos=255,# 用色度值表示
                                    bounds=[0, 255],# 用色度值表示
                                    angle=0,
                                    movable=True,
                                    pen=pg.mkPen((100, 100, 100, 255), width=5),
                                    hoverPen=(150, 150, 150, 200),)
        self.line.setZValue(100)
        self.line.addMarker('o', position=1, size=10)

        self.mark = pg.InfLineLabel(self.line, position=0.5, color=(100, 100, 100))
        self.mark.setText(f'{self.line.value() / 255 * 1500:.0f}')
        self.bar.addItem(self.line)
        self.line.sigPositionChanged.connect(self.updateLevel)

        self.view_box.invertY(True)
        self.view_box.setMouseEnabled(x=False, y=False)

    def setData(self, data:np.ndarray):
        self.feature_map.setImage(data.T, autoLevels=False)

    def updateLevel(self, line:pg.InfiniteLine):
        self.bar.setLevels(low=0, high=line.value()/255*1500)
        self.mark.setText(f'{line.value()/255*1500:.0f}')

class MultiFeatureMapPlotsWidget(QtWidgets.QWidget, KKTGraph):
    @property
    def axis(self):
        return self._axis

    @axis.setter
    def axis(self, value):
        self._axis = value
        for plots in self._plots:
            plots.axis = value

    def __init__(self, parent=None, chart_shape=[1, 2]):
        super().__init__(parent=parent,)
        self._plots:List[FeatureMapPlotWidget] = []
        self._axis = [(-16, 16), (0, 32)]
        self.chart_shape = chart_shape
        self.setupUI()

    def setParam(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k, v)
                print(f"set param {k} to {v}.")

    def resizeEvent(self, event:QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.height() <= self.width()//2:
            height = self.height()
        else:
            height = self.width()//2
        # self.setMaximumHeight(height)
        self.resize(self.width(), height)
        # self.map1.plot_item.setFixedHeight(height*0.9)
        # self.map2.plot_item.setFixedHeight(height*0.9)
        for item in self._plots:
            item.plot_item.setFixedHeight(height*0.9)

    def setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignVCenter)

        # self.map1 = FeatureMapPlotWidget(self, title='RDI')
        #
        # self._plots.append(self.map1)
        # layout.addWidget(self.map1)
        # self.map2 = FeatureMapPlotWidget(self, title='PHD')

        # self._plots.append(self.map2)
        # layout.addWidget(self.map2)

        for i in range(self.chart_shape[0]):
            ly_map = QtWidgets.QHBoxLayout()
            for j in range(self.chart_shape[1]):
                feature_map = FeatureMapPlotWidget()
                ly_map.addWidget(feature_map)
                self._plots.append(feature_map)
                layout.addLayout(ly_map, 2)

    def setData(self, data: np.ndarray):
        # for i in range(data.shape[0]):
        #     self._plots[i].setData(data[i])

        plot_index = 0
        for i in range(self.chart_shape[0]):
            for j in range(self.chart_shape[1]):
                if plot_index < len(self._plots):
                    if data.ndim == 3:
                        self._plots[plot_index].setData(data[j, :, :])
                    elif data.ndim == 4:
                        self._plots[plot_index].setData(data[j, :, :, i])
                    plot_index += 1


##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    def data_update():
        global map_wg
        # time.sleep(0.05)
        m = np.random.randint(0, 70, size=(32,32))
        map_wg.setData(m)
        # l = random.randint(0,1)
        # map_wg.setBorder(l,l)
        # m = random.randint(200,1000)
        # g_map.setLevel(m,m)

    # g_map = None
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(800,600)

    map_wg = FeatureMapPlotWidget()
    # map_wg.setAxisRange(x_range=(-1.5,1.5), y_range=(0,34))

    win.setCentralWidget(map_wg)
    win.setWindowTitle('Unit test')
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(40)
    app.exec_()
    qtimer.stop()
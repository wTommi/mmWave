from __future__ import annotations
import sys
from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget, DataPlotState
from KKT_UI.KKTGraph.Base.OverlapLinePlot import OverLapLinePlotWidget, OverlapLinePlotState
from KKT_UI.KKTGraph.Base.MeanLinePlot import MeanLinePlotState, MeanLinePlotWidget
from KKT_UI.KKTGraph.Base.StemPlot import StemPlotWidget
import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
import abc
from dataclasses import dataclass
from typing import Literal, Protocol, Any, Dict, Union, Optional


@dataclass
class OverlapRawDataLinePlotState():
    chirp:int
    sample:int
    item_range:tuple[int, int]
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:OverlapRawDataLinePlotWidget)->OverlapRawDataLinePlotWidget:
        widget.chirp = self.chirp
        widget.sample = self.sample
        widget.item_range = self.item_range
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return widget
class OverlapRawDataLinePlotWidget(OverLapLinePlotWidget, KKTGraph):
    sig_state_changed = QtCore.Signal(DataPlotState)

    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        self.overlap_num = self._chirp # Set the overlap number to the number of chirp.
        if value < 4:
            self.item_range = (0, value)

    @property
    def sample(self)->int:
        ''' The number of sample.'''
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        self.setAxisRange(x_range=(0, self._sample-1), y_range=(-2**15, 2**15))


    def __init__(self,parent=None, title='Raw Data Line Plot', chirp=32, sample=128, item_range=(0, 4)):
        ''' The raw data line plot.

        Args:
            parent: The parent widget.
            title: The title of the plot.
            chirp: The number of chirp.
            sample: The number of sample.
            item_range: The range of the overlap items.
            '''
        super().__init__(parent=parent, title=title, overlap_num=chirp, item_range=item_range)
        self.plot_dict: dict[int, pg.PlotDataItem] = {}
        self.chirp = chirp
        self.sample = sample
        self.item_range = item_range
        self.setAxisLabel(bottom='Sample Number', left='Amplitude')
        self.default_state = OverlapRawDataLinePlotState(chirp=self.chirp,
                                                         sample=self.sample,
                                                         item_range=self.item_range,
                                                         x_range=self.view_box.viewRange()[0],
                                                         y_range=self.view_box.viewRange()[1],
                                                         title=self.plot_item.titleLabel.text,
                                                         axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})

        self.setAxisLabel(bottom='sample number')
        self.default_state.renderWidget(self)



    def setDefaultAxis(self):
        self.chirp = self.default_state.chirp
        self.sample = self.default_state.sample
        self.setAxisLabel(**self.default_state.axis_label)
        self.setAxisRange(self.default_state.x_range, self.default_state.y_range)

    def setAxisRange(self, x_range:tuple[float, float], y_range:tuple[float, float]):
        ''' Set the range for the given axis.

        Args:
            x_range: The range of the x axis.
            y_range: The range of the y axis.

        '''
        self.view_box.setLimits(xMin=x_range[0] - 5, xMax=x_range[1] + 5, yMin=y_range[0] - 10, yMax=y_range[1] + 10)
        super().setAxisRange(x_range, y_range)
        self.plot_item.getAxis('bottom').setTicks([[(i, str(i)) for i in range(int(x_range[0]), int(x_range[1])+1, 16)]])

    def getState(self)->OverlapRawDataLinePlotState:
        ''' Get the state of the widget.

        Returns:
            The state of the widget.

        '''
        return OverlapRawDataLinePlotState(chirp=self.chirp,
                                           sample=self.sample,
                                           item_range=self.item_range,
                                           x_range=self.view_box.viewRange()[0],
                                           y_range=self.view_box.viewRange()[1],
                                           title=self.plot_item.titleLabel.text,
                                           axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})

@dataclass
class MeanRawDataLinePlotState():
    chirp:int
    sample:int
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:OverlapRawDataLinePlotWidget)->OverlapRawDataLinePlotWidget:
        widget.chirp = self.chirp
        widget.sample = self.sample
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return widget

class MeanRawDataLinePlotWidget(MeanLinePlotWidget, KKTGraph):
    @property
    def sample(self)->int:
        return self._sample
    @sample.setter
    def sample(self, value:int):
        self._sample = value
        self.setAxisRange(x_range=(0, self._sample-1), y_range=(-2**15, 2**15))

    def __init__(self, parent=None, title='Raw Data Mean Plot', chirp=32, sample=128):
        super().__init__(parent=parent, title=title)
        self.setupGUI()
        self.chirp = chirp
        self.sample = sample
        self.setAxisLabel(bottom='Sample Number', left='Amplitude')
        self.default_state = MeanRawDataLinePlotState(chirp=self.chirp,
                                                      sample=self.sample,
                                                      x_range=self.view_box.viewRange()[0],
                                                      y_range=self.view_box.viewRange()[1],
                                                      title=self.plot_item.titleLabel.text,
                                                      axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})
        self.setAxisLabel(bottom='sample number')
        self.default_state.renderWidget(self)
        pass

    def setDefaultAxis(self):
        self.default_state.renderWidget(self)

    def setAxisRange(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        ''' Set the range for the given axis.'''
        self.view_box.setLimits(xMin=x_range[0] - 5, xMax=x_range[1] + 5, yMin=y_range[0] - 10, yMax=y_range[1] + 10)
        super().setAxisRange(x_range, y_range)
        self.plot_item.getAxis('bottom').setTicks([[(i, str(i)) for i in range(int(x_range[0]), int(x_range[1]) + 1, 16)]])

    def getState(self) -> MeanRawDataLinePlotState:
        return MeanRawDataLinePlotState(chirp=self.chirp,
                                        sample=self.sample,
                                        x_range=self.view_box.viewRange()[0],
                                        y_range=self.view_box.viewRange()[1],
                                        title=self.plot_item.titleLabel.text,
                                        axis_label={'bottom': self.getAxis('bottom').labelText,
                                                    'left': self.getAxis('left').labelText})

@dataclass
class RawDataStemPlotState():
    chirp:int
    sample:int
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:RawDataStemPlotWidget)->RawDataStemPlotWidget:
        widget.chirp = self.chirp
        widget.sample = self.sample
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return widget


class RawDataStemPlotWidget(StemPlotWidget, KKTGraph):
    _chirp=32
    _sample=128
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        self.setAxisRange(x_range=(0, self.chirp*self.sample), y_range=(-(2 ** 15), 2 ** 15))

    @property
    def sample(self)->int:
        return self._sample
    @sample.setter
    def sample(self, value:int):
        self._sample = value
        self.setAxisRange(x_range=(0, self.chirp*self.sample), y_range=(-(2**15), 2**15))

    def __init__(self, parent=None, title='Raw Data Stem Plot', chirp=32, sample=128,enable_menu=True):
        super().__init__(parent=parent, title=title,enable_menu=enable_menu)
        self.chirp = chirp
        self.sample = sample
        self.getAxisItem('bottom').setLabel(text='Sample Number')
        self.getAxisItem('left').setLabel(text='Amplitude')
        self.default_state = RawDataStemPlotState(chirp=self.chirp,
                                                  sample=self.sample,
                                                  x_range=self.view_box.viewRange()[0],
                                                  y_range=self.view_box.viewRange()[1],
                                                  title=self.plot_item.titleLabel.text,
                                                  axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})
        self.setAxisLabel(bottom='sample number')
        self.default_state.renderWidget(self)
        pass
    def setDefaultAxis(self):
        self.default_state.renderWidget(self)

    def setData(self, data:np.ndarray):
        data = np.reshape(data, (data.shape[0]*data.shape[1]))
        super().setData(data)

    def setAxisRange(self, x_range: tuple[float, float], y_range: tuple[float, float]):
        ''' Set the range for the given axis.'''
        self.view_box.setLimits(xMin=x_range[0] - 5, xMax=x_range[1] + 5, yMin=y_range[0] - 10, yMax=y_range[1] + 10)
        self.view_box.setXRange(x_range[0], x_range[1], padding=.02)
        self.view_box.setYRange(y_range[0], y_range[1], padding=0)


    def getState(self) -> RawDataStemPlotState:
        return RawDataStemPlotState(chirp=self.chirp,
                                    sample=self.sample,
                                    x_range=self.view_box.viewRange()[0],
                                    y_range=self.view_box.viewRange()[1],
                                    title=self.plot_item.titleLabel.text,
                                    axis_label={'bottom': self.getAxis('bottom').labelText,
                                                'left': self.getAxis('left').labelText})


class RawDataPlotsWidget(QtWidgets.QWidget, KKTGraph):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''

        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        for wg in self.wg.values():
            if hasattr(wg, 'chirp'):
                setattr(wg, 'chirp', value)
    @property
    def sample(self)->int:
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        for wg in self.wg.values():
            if hasattr(wg, 'sample'):
                setattr(wg, 'sample', value)

    def __init__(self, parent=None, widgets:Optional[Dict[str, Union[KKTGraph,DataPlotWidget]]]=None, chirp=32, sample=128, **kwargs):
        super().__init__(parent=parent)
        self._chirp = chirp
        self._sample = sample
        self.wg = widgets
        self.setupGUI()
        pass


    def setupGUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.cb_raw_data_plot = QtWidgets.QComboBox(self)
        self.cb_raw_data_plot.setFont(QtGui.QFont('Yu Gothic UI'))
        # self.cb_raw_data_plot.setMaximumWidth(100)
        self.layout.addWidget(self.cb_raw_data_plot, alignment=QtCore.Qt.AlignLeft)

        self.stack = QtWidgets.QStackedWidget(self)
        self.layout.addWidget(self.stack)

        for name, wg in self.wg.items():
            self.addStackPlotWidget(name, wg)

        self.cb_raw_data_plot.currentIndexChanged.connect(self.stack.setCurrentIndex)
        pass

    def addStackPlotWidget(self, name:str, widget:QtWidgets, **obj_args):
        if (name in self.wg.keys()) and (widget is not self.wg[name]):
            idx = self.stack.indexOf(self.wg[name])
            self.stack.removeWidget(self.wg[name])
            # self.cb_raw_data_plot.removeItem(idx)
            self.wg[name].deleteLater()
            self.stack.insertWidget(idx, widget)
        else:
            self.stack.addWidget(widget)
            self.cb_raw_data_plot.addItem(name, name)
        self.wg[name] = widget



    def setData(self, data:np.ndarray):
        wg:KKTGraph = self.stack.currentWidget()
        wg.setData(data)
        pass

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

class MultiRawDataPLotsWidget(QtWidgets.QWidget, KKTGraph):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp

    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        for plots in self._plots:
            plots.chirp = value

    @property
    def sample(self)->int:
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        for plots in self._plots:
            plots.sample = value

    def __init__(self, parent=None, chart_count=2):
        super().__init__(parent=parent)
        self._chirp = 32
        self._sample = 128
        self._chart_count = chart_count
        self._plots:list[RawDataPlotsWidget] = []
        self.setupGUI()
        pass

    def setupGUI(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        for i in range(self._chart_count):
            raw_plots = RawDataPlotsWidget(self, chirp=self.chirp, sample=self.sample,
                                                widgets={
                                                    'Stem': RawDataStemPlotWidget(chirp=self.chirp,
                                                                                  sample=self.sample),
                                                    'Line': OverlapRawDataLinePlotWidget(chirp=self.chirp,
                                                                                         sample=self.sample),
                                                    'Mean': MeanRawDataLinePlotWidget(chirp=self.chirp,
                                                                                      sample=self.sample),
                                                    })
            self.layout.addWidget(raw_plots)
            self._plots.append(raw_plots)

        # self.CH2_raw_plots = RawDataPlotsWidget(self, chirp=self.chirp, sample=self.sample,
        #                                         widgets={
        #                                             'Stem': RawDataStemPlotWidget(chirp=self.chirp,
        #                                                                           sample=self.sample),
        #                                             'Line': OverlapRawDataLinePlotWidget(chirp=self.chirp,
        #                                                                                  sample=self.sample),
        #                                             'Mean': MeanRawDataLinePlotWidget(chirp=self.chirp,
        #                                                                               sample=self.sample),
        #                                             }
        #                                         )
        # self.layout.addWidget(self.CH2_raw_plots)
        # self._plots.append(self.CH2_raw_plots)

        pass


    def setData(self, data:np.ndarray):
        for i in range(data.shape[0]):
            self._plots[i].setData(data[i])
        pass

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

if __name__ == '__main__':
    import time
    s = time.time()
    def updatePlot():
        global s
        res = np.random.randint(-2 ** 11, 2 ** 11 - 1, (32,128), dtype='int16')
        p.setData(res)
        print('fps : {}'.format(1 / (time.time() - s)))
        s = time.time()

    app = QtWidgets.QApplication(sys.argv)
    p = RawDataPlotsWidget()
    p.resize(800,600)
    T = QtCore.QTimer()
    T.timeout.connect(updatePlot)
    T.start(50)
    p.show()
    app.exec()





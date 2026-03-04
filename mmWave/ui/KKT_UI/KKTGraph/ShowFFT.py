import typing
from typing import Optional, Dict, Union
from PySide2 import QtWidgets, QtCore, QtGui
from KKT_UI.KKTGraph.Base import KKTGraph, MeanLinePlot, OverlapLinePlot
from KKT_UI.KKTGraph.Base.KKTGraph import DataPlotWidget, DataPlotState, KKTGraph
import numpy as np

class OverlapFFTLinePlotWidget(OverlapLinePlot.OverLapLinePlotWidget):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        self.overlap_num = self._chirp # Set the overlap number to the number of chirp.
        self.default_state = self.getDefaultState()

    @property
    def sample(self)->int:
        ''' The number of sample.'''
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample / 4))
        self._up_chirp_num = int(self._sample / 2)
        self.default_state = self.getDefaultState()

    @property
    def max_distance(self)->int:
        ''' The max distance of the data.'''
        return self._max_distance

    @max_distance.setter
    def max_distance(self, value:int):
        self._max_distance = value
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample/4))
        self.default_state = self.getDefaultState()
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
    @property
    def max_amplitude(self)->int:
        ''' The max amplitude of the data.'''
        return self._max_amplitude
    @max_amplitude.setter
    def max_amplitude(self, value:int):
        self._max_amplitude = value
        self.default_state = self.getDefaultState()
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
    @property
    def up_chirp_num(self)->int:
        return self._up_chirp_num

    @property
    def xrange_label(self)->np.ndarray:
        return self._xrange_label

    def __init__(self, parent=None, title='FFT Line Plot', chirp=32, sample=128, item_range=(0, 4), max_distance=68, max_amplitude=200000):
        self._chirp = chirp
        self._sample = sample
        self._max_distance = max_distance
        self._max_amplitude = max_amplitude
        super().__init__(parent=parent, title=title, overlap_num=chirp, item_range=item_range)
        self._up_chirp_num = int(self._sample / 2)
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample/4))
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
        self.setAxisLabel(bottom='Distance (m)', left='Amplitude')
        self.default_state = self.getDefaultState()
        self.setDefaultAxis()

    def setDefaultAxis(self):
        ''' Set the default axis.'''
        self.setAxisRange(x_range=(0, self.default_state['max_distance']), y_range=(0, self.default_state['max_amplitude']))

    def setAxisRange(self, x_range:typing.Tuple[float, float], y_range:typing.Tuple[float, float]):
        ''' Set the range for the given axis.

        Args:
            x_range: The range of the x axis.
            y_range: The range of the y axis.

        '''
        x_span = (x_range[1] - x_range[0])*0.01
        y_span = (y_range[1] - y_range[0])*0.01
        self.view_box.setLimits(xMin=x_range[0] - x_span, xMax=x_range[1] + x_span, yMin=y_range[0] - y_span, yMax=y_range[1] + y_span)
        super().setAxisRange(x_range, y_range)
        self.getAxisItem('bottom').setTickSpacing(8,1)##.setTickSpacing(2, 1)

    def setData(self, data:np.ndarray):
        ''' Set the data to the plot.'''
        data = data[:,:self._up_chirp_num]
        for i in range(self.item_range[0],self.item_range[1]):
            self.plot_dict[i].setData(self._xrange_label, data[i])

class MeanFFTLinePlotWidget(MeanLinePlot.MeanLinePlotWidget):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        self.overlap_num = self._chirp # Set the overlap number to the number of chirp.
        self.default_state = self.getDefaultState()

    @property
    def sample(self)->int:
        ''' The number of sample.'''
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample / 4))
        self._up_chirp_num = int(self._sample / 2)
        self.default_state = self.getDefaultState()

    @property
    def max_distance(self)->int:
        ''' The max distance of the data.'''
        return self._max_distance
    @max_distance.setter
    def max_distance(self, value:int):
        self._max_distance = value
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample/4))
        self.default_state = self.getDefaultState()
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
    @property
    def max_amplitude(self)->int:
        ''' The max amplitude of the data.'''
        return self._max_amplitude
    @max_amplitude.setter
    def max_amplitude(self, value:int):
        self._max_amplitude = value
        self.default_state = self.getDefaultState()
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
    @property
    def up_chirp_num(self)->int:
        return self._up_chirp_num
    @property
    def xrange_label(self)->np.ndarray:
        return self._xrange_label

    def __init__(self, parent=None, title='FFT Mean Plot', chirp=32, sample=128, item_range=(0, 4), max_distance=68, max_amplitude=200000):
        self._chirp = chirp
        self._sample = sample
        self._max_distance = max_distance
        self._max_amplitude = max_amplitude
        super().__init__(parent=parent, title=title)
        self._up_chirp_num = int(self._sample / 2)
        self._xrange_label = np.linspace(0, self._max_distance, int(self._sample/4))
        self.setAxisRange(x_range=(0, self._max_distance), y_range=(0, self._max_amplitude))
        self.setAxisLabel(bottom='Distance (m)', left='Amplitude')
        self.default_state = self.getDefaultState()
        self.setDefaultAxis()
    def setDefaultAxis(self):
        ''' Set the default axis.'''
        self.setAxisRange(x_range=(0, self.default_state['max_distance']), y_range=(0, self.default_state['max_amplitude']))

    def setAxisRange(self, x_range:typing.Tuple[float, float], y_range:typing.Tuple[float, float]):
        ''' Set the range for the given axis.

        Args:
            x_range: The range of the x axis.
            y_range: The range of the y axis.

        '''
        x_span = (x_range[1] - x_range[0])*0.01
        y_span = (y_range[1] - y_range[0])*0.01
        self.view_box.setLimits(xMin=x_range[0] - x_span, xMax=x_range[1] + x_span, yMin=y_range[0] - y_span, yMax=y_range[1] + y_span)
        super().setAxisRange(x_range, y_range)
        self.getAxisItem('bottom').setTickSpacing(8, 1)  ##.setTickSpacing(2, 1)

    def setData(self, data:np.ndarray):
        ''' Set the data to the plot.'''
        data = data[:,:self._up_chirp_num]
        mean_data = np.mean(data, axis=0)
        self.mean_plot.setData(self._xrange_label, mean_data)

class FFTPlotsWidget(QtWidgets.QWidget):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        for name, wg in self.wg.items():
            if hasattr(wg, 'chirp'):
                wg.chirp = self._chirp

    @property
    def sample(self)->int:
        ''' The number of sample.'''
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        for name, wg in self.wg.items():
            if hasattr(wg, 'sample'):
                wg.sample = self._sample


    def __init__(self, parent=None, widgets:Optional[Dict[str, Union[KKTGraph,DataPlotWidget]]]=None, chirp=32, sample=128):
        super().__init__(parent=parent)
        self._chirp = chirp
        self._sample = sample
        self.wg = widgets if widgets is not None else {}
        self.setupGUI()

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")
                continue
            for name, wg in self.wg.items():
                if hasattr(wg, k):
                    wg.__setattr__(k, v)
                    print(f"set param {k} to {v} in {name}.")
                    break


    def setupGUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.cb_raw_data_plot = QtWidgets.QComboBox(self)
        self.cb_raw_data_plot.setFont(QtGui.QFont('Yu Gothic UI'))
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

    def setData(self, data: np.ndarray):
        wg = self.stack.currentWidget()
        wg.setData(data)
        pass

class MultiFFTPlotsWidget(QtWidgets.QWidget):
    @property
    def chirp(self)->int:
        ''' The number of chirp.'''
        return self._chirp
    @chirp.setter
    def chirp(self, value:int):
        self._chirp = value
        for plots in self._plots:
            plots._chirp = value

    @property
    def sample(self)->int:
        ''' The number of sample.'''
        return self._sample

    @sample.setter
    def sample(self, value:int):
        self._sample = value
        for plots in self._plots:
            plots._sample = value

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._chirp = 32
        self._sample = 128
        self._plots: list[FFTPlotsWidget] = []
        self.setupGUI()

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

    def setupGUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.CH1_fft_plots = FFTPlotsWidget(self, chirp=self.chirp, sample=self.sample,
                                            widgets={'Line':OverlapFFTLinePlotWidget(chirp=self.chirp, sample=self.sample),
                                                     'Mean':MeanFFTLinePlotWidget(chirp=self.chirp, sample=self.sample),
                                                     }
                                            )
        self.layout.addWidget(self.CH1_fft_plots)
        self._plots.append(self.CH1_fft_plots)

        self.CH2_fft_plots = FFTPlotsWidget(self, chirp=self.chirp, sample=self.sample,
                                            widgets={'Line': OverlapFFTLinePlotWidget(chirp=self.chirp, sample=self.sample),
                                                     'Mean': MeanFFTLinePlotWidget(chirp=self.chirp, sample=self.sample)}
                                            )
        self.layout.addWidget(self.CH2_fft_plots)
        self._plots.append(self.CH2_fft_plots)

        pass

    def setData(self, data: np.ndarray):
        for i in range(data.shape[0]):
            self._plots[i].setData(data[i])
        pass


if __name__ == '__main__':
    import time
    import sys
    s = time.time()
    def updatePlot():
        global s
        res = np.random.randint(-2 ** 11, 2 ** 13 - 1, (32,32), dtype='int16')
        p.setData(res)
        print('fps : {}'.format(1 / (time.time() - s)))
        s = time.time()

    app = QtWidgets.QApplication(sys.argv)
    p = FFTPlotsWidget(widgets={'Line':OverlapFFTLinePlotWidget(chirp=32, sample=128),
                                'Mean':MeanFFTLinePlotWidget(chirp=32, sample=128)})
    p.resize(800,600)
    T = QtCore.QTimer()
    T.timeout.connect(updatePlot)
    T.start(50)
    p.show()
    app.exec_()

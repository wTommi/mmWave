import sys
from abc import ABC

import numpy as np
from PySide2 import QtWidgets, QtCore

from KKT_UI.KKTGraph.Base.StemPlot import StemPlotWidget
from KKT_Module.KKTUtility.FFT import getFFT
from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph
from KKT_UI.KKTGraph.ShowFFT import FFTPlotsWidget, MeanFFTLinePlotWidget, OverlapFFTLinePlotWidget


class MultiRetentionPlots(QtWidgets.QWidget, KKTGraph):
    @property
    def chirp(self) -> int:
        ''' The number of chirp.'''

        return self._chirp

    @chirp.setter
    def chirp(self, value: int):
        self._chirp = value
        self.ch1_FFT.chirp = value
        self.ch2_FFT.chirp = value
        self.ch3_FFT.chirp = value

    @property
    def sample(self) -> int:
        return self._sample

    @sample.setter
    def sample(self, value: int):
        self._sample = value
        self.ch1_FFT.sample = value
        self.ch2_FFT.sample = value
        self.ch3_FFT.sample = value

    def __init__(self):
        super().__init__()
        self._chirp = 32
        self._sample = 128
        self.setupGUI()
        pass

    def setParam(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k, v)
                print(f"set param {k} to {v}.")

    def setupGUI(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.ch1_stem = StemPlotWidget(title='ch1', enable_menu=True)
        # self.ch1_stem.has_point = False
        self.ch1_stem.setAxisRange([0, 130], [-2 ** 15, 2 ** 15])
        self.ch2_stem = StemPlotWidget(title='ch2', enable_menu=True)
        # self.ch2_stem.setCurvepointSymbolVisible(False)
        self.ch2_stem.setAxisRange([0, 130], [-2 ** 15, 2 ** 15])
        self.ch3_stem = StemPlotWidget(title='ch3', enable_menu=True)
        # self.ch3_stem.setCurvepointSymbolVisible(False)
        self.ch3_stem.setAxisRange([0, 130], [-2 ** 15, 2 ** 15])

        self.ch1_FFT = MeanFFTLinePlotWidget(chirp=self.chirp, sample=self.sample)
        self.ch2_FFT = MeanFFTLinePlotWidget(chirp=self.chirp, sample=self.sample)
        self.ch3_FFT = MeanFFTLinePlotWidget(chirp=self.chirp, sample=self.sample)

        self.layout.addWidget(self.ch1_stem, 0, 0, 1, 1)
        self.layout.addWidget(self.ch2_stem, 0, 1, 1, 1)
        self.layout.addWidget(self.ch3_stem, 0, 2, 1, 1)
        self.layout.addWidget(self.ch1_FFT, 1, 0, 1, 1)
        self.layout.addWidget(self.ch2_FFT, 1, 1, 1, 1)
        self.layout.addWidget(self.ch3_FFT, 1, 2, 1, 1)

    def setData(self, data: np.ndarray):
        self.ch1_stem.setData(data[0])
        self.ch2_stem.setData(data[1])
        self.ch3_stem.setData(data[2])
        retention = np.reshape(data, (3, 1, 128))
        retention_FFT = np.zeros((3, 1, 32))
        retention_FFT[0] = getFFT(retention[0], 32)
        retention_FFT[1] = getFFT(retention[1], 32)
        retention_FFT[2] = getFFT(retention[2], 32)
        self.ch1_FFT.setData(retention_FFT[0])
        self.ch2_FFT.setData(retention_FFT[1])
        self.ch3_FFT.setData(retention_FFT[2])




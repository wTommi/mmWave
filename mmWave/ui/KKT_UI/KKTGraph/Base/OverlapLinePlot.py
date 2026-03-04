from __future__ import annotations

from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget, DataPlotState
import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui

from dataclasses import dataclass
from typing import Literal, Protocol, Any, Optional

@dataclass
class OverlapLinePlotState():
    item_range:tuple[int, int]
    overlap_num:int
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:OverLapLinePlotWidget)->OverLapLinePlotWidget:
        widget.chirpRange = self.item_range
        widget.overlap_num = self.overlap_num
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return widget

class OverLapLinePlotWidget(DataPlotWidget, KKTGraph):
    ''' The widget for the overlap line plot.'''
    sig_state_changed = QtCore.Signal(DataPlotState)

    class OverLapSpinBox(QtWidgets.QFrame):
        sig_Changed_Spin = QtCore.Signal(object)

        def __init__(self, start: int = 1, end: int = 5, range: Optional[iter] = None, items: Optional[dict] = None):
            super().__init__()
            self.start = start
            self.end = end
            self.range = range if items is not None else [1, 32]
            self.items = items if items is not None else {'Start Line': {'Value': self.start,
                                                                         'Range': self.range},
                                                          'End Line': {'Value': self.end,
                                                                       'Range': self.range},
                                                          }
            self.setupGUI()

        def setupGUI(self):
            from KKT_UI.QTWidget.qt_obj import SpinBoxListWidget
            self.grid = QtWidgets.QGridLayout(self)
            self.setLayout(self.grid)
            self.spin_chirps = SpinBoxListWidget(items=self.items, cols=1)
            self.spin_chirps.change_Signal.connect(lambda: self._changeSpinBox())
            self.grid.addWidget(self.spin_chirps, 1, 0, 1, 2)

        def _changeSpinBox(self):
            status = self.spin_chirps.getItemsStatus()
            start = status.get('Start Line')['Spin'].value()
            end = status.get('End Line')['Spin'].value()
            if start > end:
                self.spin_chirps.setValue('Start Line', self.start)
                self.spin_chirps.setValue('End Line', self.end)
                QtWidgets.QMessageBox.warning(self, 'Disable Operate',
                                              'End Chirp Number must be greater than Start Chirp Number !')
            else:
                self.start = start
                self.end = end
                self.sig_Changed_Spin.emit(status)
    @property
    def overlap_num(self)->int:
        ''' The number of the overlap. '''
        return self._overlap_num
    @overlap_num.setter
    def overlap_num(self, num:int):
        self._overlap_num = num
        self._setPlotDict(self._overlap_num)
        if self._item_range[1] > num:
            self._item_range = (self._item_range[0], num)
        self._setOverlapItems(start=self._item_range[0], end=self._item_range[1])

    @property
    def item_range(self)->tuple[int, int]:
        ''' The range of the items to be shown. '''
        return self._item_range

    @item_range.setter
    def item_range(self, item_range:tuple[int, int]):
        assert item_range[0] < item_range[1], 'The start value must be smaller than the end value.'
        assert item_range[0] >= 0, 'The start value must be larger than 0.'
        assert item_range[1] <= self.overlap_num, 'The end value must be smaller than the overlap number.'
        self._item_range = item_range
        self._setOverlapItems(start=self._item_range[0], end=self._item_range[1])


    def __init__(self, parent=None, title='Overlap Line Plot', overlap_num=32, item_range=(0, 4)):
        ''' The widget for the overlap line plot.
        Args:
            parent: The parent widget.
            title: The title of the plot.
            overlap_num: The number of the overlap.
            item_range: The range of the items to be shown.
        '''
        self._overlap_num = overlap_num
        self._item_range = item_range
        super().__init__(parent=parent, title=title)
        self.plot_dict: dict[int, pg.PlotDataItem] = {}
        self._setPlotDict(self._overlap_num)
        self._setOverlapItems(start=self._item_range[0], end=self._item_range[1])
        self.default_state = OverlapLinePlotState(item_range=self.item_range,
                                                  overlap_num=self.overlap_num,
                                                  x_range=self.view_box.viewRange()[0],
                                                  y_range=self.view_box.viewRange()[1],
                                                  title=self.plot_item.titleLabel.text,
                                                  axis_label={'bottom': self.getAxis('bottom').labelText,
                                                              'left': self.getAxis('left').labelText})


        self.overlap_widget = OverLapLinePlotWidget.OverLapSpinBox(start=self.item_range[0]+1,
                                                                   end=self.item_range[1]+1,
                                                                   range=[1, self.overlap_num],)
        self.overlap_widget.sig_Changed_Spin.connect(lambda x: self._setOverlapItems(start=x.get('Start Line')['Spin'].value()-1,
                                                                                      end=x.get('End Line')['Spin'].value()))
        display_line = self.plot_option_menu.addMenu('Display Line')
        act_display_line = QtWidgets.QWidgetAction(display_line)
        act_display_line.setDefaultWidget(self.overlap_widget)
        display_line.addAction(act_display_line)


        pass


    def _setPlotDict(self, chirp:int):
        ''' Set the plot dict.'''
        self.plot_dict = {} # clear the plot dict
        for i in range(chirp):
            item = pg.PlotDataItem(pen=(i, 3))
            self.plot_dict.update({i:item})

    # def setupGUI(self):
    #     self._setPlotDict(self.overlap_num)

    # def initPlots(self):
    #     self._setOverlapItems(start=self.item_range[0], end=self.item_range[1])
    #
    def _setOverlapItems(self, start, end):
        self.plot_item.clear() # clear the plot item
        for i in range(start, end):
            self.addItem(self.plot_dict[i])
            pass

    def setData(self, data:np.ndarray):
        ''' Set the data to the plot.'''
        for i in range(self.item_range[0],self.item_range[1]):
            self.plot_dict[i].setData(data[i])

    def setDefaultState(self):
        ''' Set the default state of the widget.'''
        self.default_state.renderWidget(self)

    def getState(self)->OverlapLinePlotState:
        return OverlapLinePlotState(item_range=self.item_range,
                                    overlap_num=self.overlap_num,
                                    x_range=self.view_box.viewRange()[0],
                                    y_range=self.view_box.viewRange()[1],
                                    title=self.plot_item.titleLabel.text,
                                    axis_label={'bottom': self.getAxis('bottom').labelText,
                                                'left': self.getAxis('left').labelText})
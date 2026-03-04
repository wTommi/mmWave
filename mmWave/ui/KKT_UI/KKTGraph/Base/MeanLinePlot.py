from __future__ import annotations

from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget, DataPlotState
import pyqtgraph as pg
import numpy as np

from dataclasses import dataclass
from typing import Literal, Protocol, Any

@dataclass
class MeanLinePlotState():
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:MeanLinePlotWidget)->MeanLinePlotWidget:
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return widget

class MeanLinePlotWidget(DataPlotWidget, KKTGraph):
    def __init__(self, parent=None, title='Mean Plot'):

        super().__init__(parent=parent, title=title)
        self.setupGUI()
        self.default_state = MeanLinePlotState(x_range=self.view_box.viewRange()[0],
                                               y_range=self.view_box.viewRange()[1],
                                               title=self.plot_item.titleLabel.text,
                                               axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})
        pass

    def setupGUI(self):
        self.mean_plot = self.plot(pen=6)


    def setData(self, data: np.ndarray):
        ''' Set the data to the plot.
        Args:
            data: The data to be shown. The shape of the data should be (N, N).
            '''
        res = np.mean(data, axis=0)
        self.mean_plot.setData(res)

    def setDefaultState(self):
        self.default_state.renderWidget(self)

    def getState(self) -> MeanLinePlotState:
        return MeanLinePlotState(x_range=self.view_box.viewRange()[0],
                                 y_range=self.view_box.viewRange()[1],
                                 title=self.plot_item.titleLabel.text,
                                 axis_label={'bottom': self.getAxis('bottom').labelText,
                                                    'left': self.getAxis('left').labelText})
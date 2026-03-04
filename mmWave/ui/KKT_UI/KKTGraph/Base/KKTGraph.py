from __future__ import annotations
from pyqtgraph.graphicsItems.ViewBox import ViewBoxMenu
import pyqtgraph as pg
import abc
from PySide2 import QtWidgets, QtCore, QtGui
from dataclasses import dataclass
from typing import Literal, Any, Optional, Union, Tuple

AXES = Literal['top', 'bottom', 'left', 'right']
class KKTGraph():
    ''' KKTGraph is interface for which need to be implemented setData() method. '''
    @abc.abstractmethod
    def setData(self, data:Any)->None:...

    def getDefaultState(self)->dict:
        state = {}
        for attr in dir(self.__class__):
            if attr.startswith("__") and attr.endswith('__'):
                continue
            obj = getattr(self.__class__, attr)
            if isinstance(obj, property):
               val = obj.__get__(self, self.__class__)
               state[attr] = val
        return state

@dataclass
class DataPlotState():
    x_range:tuple[float, float]
    y_range:tuple[float, float]
    title:str
    axis_label:dict[Literal['top', 'bottom', 'left', 'right'], str]

    def renderWidget(self, widget:DataPlotWidget)->DataPlotWidget:
        widget.setAxisLabel(**self.axis_label)
        widget.setAxisRange(self.x_range, self.y_range)
        widget.plot_item.setTitle(self.title)
        return  widget

class DataPlotWidget(pg.PlotWidget):
    ''' PlotData2 is a wrapper for pyqtgraph.PlotWidget '''
    @property
    def plot_item(self)->pg.PlotItem:
        ''' Get the plot item.'''
        return self.getPlotItem()

    @property
    def view_box(self)->pg.ViewBox:
        ''' Get the view box.'''
        return self.plot_item.getViewBox()
    @property
    def title(self):
        return self.plot_item.titleLabel
    @property
    def plot_option_menu(self)->QtWidgets.QMenu:
        return self.plot_item.ctrlMenu
    @property
    def view_box_menu(self)->Union[ViewBoxMenu.ViewBoxMenu, QtWidgets.QMenu]:
        return self.view_box.menu



    def __init__(self, parent=None, title='test plot', enable_menu=True, **kwargs):
        super().__init__(parent=parent, title=title, enableMenu=enable_menu, background='transparent', **kwargs)
        self.scale(2,3) # scale the plot
        style = {'font-size': '10pt', 'color': 'k'}
        self.title.setText(title, size='12pt', **style)
        self.title.item.setFont(QtGui.QFont('Yu Gothic UI'))

        for axe in ('left', 'bottom', 'right', 'top'):
            item = self.getAxisItem(axe)
            item.setTextPen(pg.mkPen('k', width=1))
            item.label.setFont(QtGui.QFont('Yu Gothic UI'))
            item.setPen(pg.mkPen('k', width=1))
            item.setStyle(tickFont=QtGui.QFont('Yu Gothic UI', 10))
            item.setLabel(**style)

        self.setupMenu()


    def setupMenu(self):
        self.plot_item.setContextMenuActionVisible('Transforms', False)
        self.plot_item.setContextMenuActionVisible('Downsample', False)
        self.plot_item.setContextMenuActionVisible('Average', False)
        self.plot_item.setContextMenuActionVisible('Alpha', False)
        self.plot_item.setContextMenuActionVisible('Points', False)


        self.default_axis_action = QtWidgets.QAction(parent=self.view_box, text='Default Axis')
        self.default_axis_action.triggered.connect(self.setDefaultAxis)
        if self.view_box_menu :
            self.view_box_menu.insertAction(self.view_box_menu.viewAll, self.default_axis_action)

    def setDefaultAxis(self):
        pass


    def setAxisLabel(self, top:str=None, bottom:str=None, left:str=None, right:str=None):
        ''' Set the label for the given axis.

        Args:
            top: The label for the top axis.
            bottom: The label for the bottom axis.
            left: The label for the left axis.
            right: The label for the right axis.
            '''
        if top is not None:
            self.getAxisItem('top').setLabel(top)
        if bottom is not None:
            self.getAxisItem('bottom').setLabel(bottom)
        if left is not None:
            self.getAxisItem('left').setLabel(left)
        if right is not None:
            self.getAxisItem('right').setLabel(right)

    def getAxisItem(self, axis:AXES)->pg.AxisItem:
        ''' Get the axis item.

        Args:
            axis: The axis to get.

        Returns:
            The axis item.
        '''
        return self.plot_item.getAxis(axis)

    def setAxisRange(self,x_range:Tuple[float, float], y_range:Tuple[float, float], padding:int=0):
        ''' Set the range for the given axis.

        Args:
            x_range: The range of the x axis.
            y_range: The range of the y axis.

        '''
        self.view_box.setXRange(min =x_range[0], max=x_range[1], padding=0)
        self.view_box.setYRange(min =y_range[0], max=y_range[1], padding=0)

    def getState(self)->DataPlotState:
        ''' Get the state of the plot.'''
        return DataPlotState(x_range=tuple(self.view_box.viewRange()[0]),
                             y_range=tuple(self.view_box.viewRange()[1]),
                             title=self.plot_item.titleLabel.text,
                             axis_label={'bottom': self.getAxis('bottom').labelText, 'left': self.getAxis('left').labelText})

    def plot(self, *args, **kwargs)->pg.PlotDataItem:
        ''' Wrapper for pyqtgraph.PlotWidget.plot()'''
        return self.plot_item.plot(*args, **kwargs)


if __name__ == '__main__':
    count = 0

    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600, 400)
    wg = DataPlotWidget()
    win.setCentralWidget(wg)
    wg.setAxisRange([-1, 16], [0, 100])
    win.show()

    app.exec_()
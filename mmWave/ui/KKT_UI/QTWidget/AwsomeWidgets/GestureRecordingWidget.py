import time
from typing import Literal, Sequence, List, Tuple
from PySide2 import QtGui, QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
from collections import deque
from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget, DataPlotState


class StemPlotForLabeling(DataPlotWidget, KKTGraph):
    sig_increase_frame = QtCore.Signal(object)
    Colors = ((255, 255, 0),  # yellow # (255, 204, 0),
              (255, 0, 0),    # red
              (0, 255, 0),    # lime , green
              (255, 0, 255),  # Fuchsia
              (204, 255, 51),
              (255, 102, 0),
              (51, 204, 51),
              (204, 51, 255),
              (255, 153, 0),
              (255, 80, 80),
              (0, 204, 102),
              (204, 0, 153),
              (153, 51, 51),
              (0, 204, 153),
              (102, 0, 255),)
    def __init__(self,title='StemPlotForLabeling', x_range=(0,100), show_frames=100, frame_level=0.4, label_level=0.9):
        super().__init__(title=title, enable_menu=False)
        self.__XRange = x_range
        self.__show_frames = show_frames
        self.__showXRange = (x_range[0],self.__show_frames)
        self.__frame_level = frame_level
        self.__label_level = label_level
        self.fixed_curves = deque()
        self.setup()
        self.sig_increase_frame.connect(lambda x:self.incDynamicStem(x))

    def setConfigs(self, **kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                print( 'Attribute "{}" not in the class.'.format(k))
                continue
            self.__setattr__(k,v)
            print('Attribute "{}", set "{}"'.format(k, v))

    def setData(self, data:int):
        assert data in [0, 1]
        self.sig_increase_frame.emit(data)

    def setup(self):
        self.setupFrameStems()
        self.setupLabelStems(c=1)
        self.setPlotXRange()
        self.axis_bottom = self.plot_item.getAxis('bottom')
        self.axis_bottom.setLabel('Frames')
        self.axis_left = self.plot_item.getAxis('left')
        self.axis_left.hide()
        pass

    def setPlotXRange(self):
        arg = {'xMin':self.__showXRange[0]-int(self.__show_frames*0.05),
               'xMax':self.__showXRange[1]+int(self.__show_frames*0.05),
               'yMin':0,
               'yMax':1.2,
               'minXRange':self.__show_frames+int(self.__show_frames*0.05)*2,
                'maxXRange':self.__show_frames+int(self.__show_frames*0.05)*2,
              'minYRange':1,
              'maxYRange':1}
        self.view_box.setLimits(**arg)
        self.view_box.setRange(xRange=self.__showXRange, yRange=(0, 1))

    def _removeCurve(self, curve):
        if curve is not None:
            self.removeItem(curve)

    def addFixedStemGroup(self, x_range:Sequence[int], y_level:float, color:int=None, label_string:str=None):
        x = np.arange(x_range[0],x_range[1])
        y = np.linspace(y_level, y_level, x_range[1] - x_range[0])
        text = None
        cor, cor1 = self._selectColor(color)
        color_stem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen(cor, width=3), connect='pairs', name='Stems')
        color_point = self.plot(x, y, pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1, symbolSize=8, name='Points')

        if label_string is not None:
            text = pg.TextItem(label_string, border='w', fill=(0, 0, 255, 150))
            text.setPos(x[0], y[-1])
            text.setFont(QtGui.QFont('Yu Gothic UI', 15))
            self.addItem(text)
        self.fixed_curves.append([color_stem, color_point, text])

    def removeLastFixedStemGroup(self):
        if len(self.fixed_curves) == 0:
            return
        remove = self.fixed_curves[-1]
        for item in remove:
            if item is not None:
                self._removeCurve(item)
        self.fixed_curves.remove(remove)

    def removeFirstFixedStemGroup(self):
        if len(self.fixed_curves) == 0:
            return
        remove = self.fixed_curves[0]
        for item in remove:
            if item is not None:
                self._removeCurve(item)
        self.fixed_curves.remove(remove)

    def removeAllFixedStemGroup(self):
        for curve in self.fixed_curves:
            for item in curve:
                if item is not None:
                    self._removeCurve(item)
        self.fixed_curves.clear()

    def setDynamicStem(self, x_range, ylevel, show_frames=None):
        '''
         Setup the recording timing graph axis.

        :param xrange: list(start frames:0, number of record frames)
        :param ylevel: list()
        '''
        self.__XRange = x_range
        self.__frame_level = ylevel[0]
        self.__label_level = ylevel[1]
        if show_frames is not None:
            self.__show_frames = show_frames
        self.__showXRange = (x_range[0],self.__show_frames)
        self.clearDynamicStem()
        self.setPlotXRange()
        self.__curveXCount = 0

    def clearDynamicStem(self):
        self.x_frame = np.zeros(0, dtype='uint32')
        self.y_frame = np.zeros(0)
        self.x_label = np.zeros(0, dtype='uint32')
        self.y_label = np.zeros(0)
        self.stem_x_frame = np.zeros(0, dtype='uint32')
        self.stem_y_frame = np.zeros(0)
        self.stem_x_label = np.zeros(0, dtype='uint32')
        self.stem_y_label = np.zeros(0)
        self.__setStemData(0, label_level=1)

    def incDynamicStem(self, labeled=0):
        s = time.time_ns()
        if self.__curveXCount >= self.__showXRange[1]:
            self.__showXRange = (self.__showXRange[0]+self.__show_frames, self.__showXRange[1]+self.__show_frames)
            self.setPlotXRange()
            self.clearDynamicStem()
        self.__curveXCount += 1
        self.__setStemData(count=self.__curveXCount+1, label_level=labeled)
        # print('Update label plot time = {} ms'.format((time.time_ns() - s)/1000000))

    def decDynamicStem(self):
        if self.__curveXCount <= 0:
            return
        self.__curveXCount -= 1
        self.__setStemData(self.__curveXRange, self.__curveYLevel, self.__curveXCount+1)

    def __setStemData(self, count, frame_level=0.8, label_level=1):
        length= len(self.x_frame)
        if count !=0 :
            self.stem_x_frame = np.append(self.stem_x_frame, [count-1, count-1])
            self.stem_y_frame = np.append(self.stem_y_frame , [0, frame_level])
        #
        self.frame_stem.setData(self.stem_x_frame, self.stem_y_frame)
        if not label_level:
            return
        length= len(self.y_label)
        if count != 0:

            self.stem_x_label = np.append(self.stem_x_label, [count - 1, count - 1])
            self.stem_y_label = np.append(self.stem_y_label, [0, label_level])
        self.label_stem.setData(self.stem_x_label, self.stem_y_label)

    def setupFrameStems(self):
        self.frame_stem = pg.PlotDataItem(pen=pg.mkPen('b', width=1), connect='pairs', name='Stems')
        self.frame_point = pg.PlotDataItem(pen=None, symbol='o', symbolPen='b',
                                           symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)), symbolSize=8, name='Points')
        self.plot_item.addItem(self.frame_stem)
        self.plot_item.addItem(self.frame_point)

    def setupLabelStems(self, c):
        cor, cor1 = self._selectColor(c)
        self.label_stem = pg.PlotDataItem(pen=pg.mkPen(cor, width=2), connect='pairs', name='Stems')
        self.label_point = pg.PlotDataItem(pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1, symbolSize=8,
                                           name='Points')
        self.plot_item.addItem(self.label_stem)
        self.plot_item.addItem(self.label_point)

    def _selectColor(self, c):
        if c is None:
            cor = 'r'
            cor1 = (20, 20, 200)
        else:
            if c >= len(self.Colors):
                c = c % len(self.Colors)
            c1 = c + 1
            if c1 >= len(self.Colors):
                c1 = c1 % len(self.Colors)
            cor = self.Colors[c]
            cor1 = self.Colors[c1]
        return cor, cor1

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        super().contextMenuEvent(event)
        menu = QtWidgets.QMenu()
        range = menu.addAction('Set Range')
        selected_action = menu.exec_(QtGui.QCursor.pos())
        if selected_action == range:
            num , ok = QtWidgets.QInputDialog.getInt(None, 'X axis range', 'Input X axis range:', self.__show_frames, minValue=10)
            if ok:
                self.__show_frames = num
                self.__showXRange = (self.__showXRange[0], self.__showXRange[0]+self.__show_frames)
                self.setPlotXRange()
            print("You have selected the first option")
        return super().eventFilter(selected_action, event)

    def setFixLabel(self, label_info_list=None, label_string_list=None):
        '''
         Set gesture's labels name on plot

        :param label_info_list: Gesture information list, list(label start frame, label end frame, label y position)
        :param label_string_list: Gesture name list.
        '''
        if label_info_list is None:
            return
        count = 1
        for label_info in label_info_list:
            if label_string_list is not None:
                self.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    color=count,
                    label_string=str(label_string_list[count - 1]))
            else:
                self.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    color=count)
            count += 1

class GestureLabelingWidget(QtWidgets.QFrame):
    sig_press_label = QtCore.Signal(object)
    sig_press_ESC = QtCore.Signal(object)
    key_num_list = (QtCore.Qt.Key_1,
                    QtCore.Qt.Key_2,
                    QtCore.Qt.Key_3,
                    QtCore.Qt.Key_4,
                    QtCore.Qt.Key_5,
                    QtCore.Qt.Key_6,
                    QtCore.Qt.Key_7,
                    QtCore.Qt.Key_8,
                    QtCore.Qt.Key_9)
    def __init__(self, title='Gesture Recording'):
        super().__init__()
        self.title = title
        self.key = QtCore.Qt.Key_0
        self.labeling = False
        self.label_len = 0
        self.current_frame = 0
        self.label_region:List[Tuple[int,int]] = []
        self.setupUI()

    def keyPressEvent(self, event:QtGui.QKeyEvent):
        # print('enter press')
        super().keyPressEvent(event)
        if event.key() in self.key_num_list:
            self.sig_press_label.emit(event.key())
            self.labeling = True
            self.key = event.key()
            # print(event.text())

        if event.key() == QtCore.Qt.Key_Escape:
            self.sig_press_ESC.emit(True)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        # print('enter release')
        super().keyPressEvent(event)
        if not hasattr(self, 'key'):
            print('no key')
            return

        if self.key != event.key():
            return

        if event.isAutoRepeat():
            # print('release return')
            return

        if event.key() in self.key_num_list:
            self.sig_press_label.emit(0)
            self.key = QtCore.Qt.Key_0
            # print(event.text())

    def setupUI(self):
        ly = QtWidgets.QVBoxLayout()
        self.setLayout(ly)
        self.lb_frame = QtWidgets.QLabel('Collected Frames : ')
        self.lb_frame.setFont(QtGui.QFont('Yu Gothic UI', 15))
        ly.addWidget(self.lb_frame)
        self.label_wg = StemPlotForLabeling(title=self.title)
        ly.addWidget(self.label_wg)


    def setCurrentFrame(self, frame:int):
        self.current_frame = frame
        self.lb_frame.setText(f'Collected Frames : {frame}')

    def setData(self, data:int):
        self.label_wg.setData(data=data)
        if data:
            self.label_len += 1
        if (self.key == QtCore.Qt.Key_0) and self.labeling:
            self.label_region.append(((self.current_frame - self.label_len), self.current_frame))
            self.label_len = 0
            self.labeling = False

    def chkLastFrameLabel(self):
        if self.labeling:
            self.label_region.append(((self.current_frame - self.label_len), self.current_frame))
            self.label_len = 0
            self.labeling = False

    def addFixedStemGroup(self, x_range:Sequence[int], y_level:float, color:int=None, label_string:str=None):
        self.label_wg.addFixedStemGroup(x_range, y_level, color, label_string)

    def removeFirstFixedStemGroup(self):
        self.label_wg.removeFirstFixedStemGroup()

    def setDynamicStem(self, x_range, ylevel, show_frames=None):
        self.label_wg.setDynamicStem(x_range, ylevel, show_frames)

    def setFixLabel(self, label_info_list=None, label_string_list=None):
        for info in label_info_list:
            self.label_region.append((info[0]-1, info[1]+1))
        self.label_wg.setFixLabel(label_info_list, label_string_list)

    def initPlot(self):
        self.label_wg.clearDynamicStem()
        self.label_wg.removeAllFixedStemGroup()
        self.label_wg.setDynamicStem([0, 100], [0.8, 1])
        self.label_region = []


if __name__ == '__main__':
    count = 0
    def __data_update():
        global wg
        global count
        # print(count)
        if count == 0:
            wg.addFixedStemGroup([4,15], 0.8, 1, label_string='2')
            wg.addFixedStemGroup([20,35], 0.7, 2, label_string='3')
            wg.addFixedStemGroup([40,55], 0.6, 3, label_string='5')
            wg.addFixedStemGroup([60,75], 0.5, 4, label_string='f')
            count += 1
        elif count == 1:
            # pass
            wg.setDynamicStem([0, 1000], [0.4, 0.9])
            wg.removeFirstFixedStemGroup()
            # stempw.removeLastFixedStemGroup()
            count += 1
        elif count >= 2:
            label = 0
            # stempw.removeAllFixedStemGroup()
            # if count >= 20 and count < 60:
            #     label = 1
            wg.setData(data=wg.labeling)
            wg.setCurrentFrame(count-2)
            count += 1
            if count==1200:
                count=1



    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    wg = GestureLabelingWidget()
    win.setCentralWidget(wg)
    win.show()
    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(__data_update)
    qtimer.start(40)
    app.exec_()

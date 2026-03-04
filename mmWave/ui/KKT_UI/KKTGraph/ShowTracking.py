import typing

import numpy as np
import time
import pyqtgraph as pg
from PySide2 import  QtCore, QtWidgets
from collections import deque
from KKT_UI.KKTGraph.Base.KKTGraph import KKTGraph, DataPlotWidget, DataPlotState
##=====================================================================================

class TrackingPlotWidget(DataPlotWidget, KKTGraph):
    _layback_frames = 40
    _pos_pen = 'w'
    _pattern_pen = pg.mkPen(color='k', width=3)
    _sector_pen = pg.mkPen(color='gray', width=2)
    @property
    def has_position_record(self)->bool:
        return self._has_position_record
    @has_position_record.setter
    def has_position_record(self, has_position_record:bool):
        self._has_position_record = has_position_record
        if has_position_record:
            self.plot_item.addItem(self.pattern)
            self.plot_item.addItem(self.last_position)
        else:
            self.plot_item.removeItem(self.pattern)
            self.plot_item.removeItem(self.last_position)
    @property
    def has_sector_range(self)->bool:
        return self._has_sector_range
    @has_sector_range.setter
    def has_sector_range(self, has_sector_range:bool):
        self._has_sector_range = has_sector_range
        if has_sector_range:
            self.addItem(self.sector_left)
            self.addItem(self.sector_right)
            self.addItem(self.sector_top)
            self.addItem(self.sector_bottom)
            self.setSectorRegion()

        else:
            self.removeItem(self.sector_left)
            self.removeItem(self.sector_right)
            self.removeItem(self.sector_top)
            self.removeItem(self.sector_bottom)

    @property
    def tracking_point_size(self) -> int:
        return self._tracking_point_size

    @tracking_point_size.setter
    def tracking_point_size(self, tracking_point_size: int):
        self._tracking_point_size = tracking_point_size
        if self.tracking_position is not None:
            self.tracking_position.setSize(tracking_point_size)

    def __init__(self, parent=None, title='Tracking Plot', has_pos_record=False, has_sector_range=False, tracking_point_size = 25):
        super().__init__(parent=parent, title=title)
        self.tracking_position = None
        self.tracking_point_size = tracking_point_size
        self._setupUI()
        self.pos1_buffer = deque(maxlen=self._layback_frames)
        self.pos2_buffer = deque(maxlen=self._layback_frames)
        self.has_position_record = has_pos_record
        self.has_sector_range = has_sector_range


    def _setupUI(self):
        self.tracking_position = pg.ScatterPlotItem(pen=self._pos_pen, size=self.tracking_point_size)
        self.tracking_position.setZValue(100)
        self.plot_item.addItem(self.tracking_position)
        self.pattern = pg.PlotCurveItem(pen=self._pattern_pen)
        self.pattern.setZValue(1)
        self.last_position = pg.ScatterPlotItem(pen=self._pos_pen, size=10)
        self.last_position.setZValue(99)


        self.sector_left = pg.PlotCurveItem(pen=self._sector_pen)
        self.sector_left.setZValue(0)
        self.sector_right = pg.PlotCurveItem(pen=self._sector_pen)
        self.sector_right.setZValue(0)
        self.sector_top = pg.PlotCurveItem(pen=self._sector_pen)
        self.sector_top.setZValue(0)
        self.sector_bottom = pg.PlotCurveItem(pen=self._sector_pen)
        self.sector_bottom.setZValue(0)


    def setSectorRegion(self, R=17, r=4, angle=60, pts=100):
        self.R = R
        self.r = r
        self.elevation = 90-angle/2

        elevation = 90-angle/2
        down_x = r*np.cos(elevation*np.pi/180)
        up_x = R*np.cos(elevation*np.pi/180)

        left_x = np.linspace(-up_x, -down_x, pts)
        left_y = left_x * np.tan(-elevation*np.pi/180)
        self.sector_left.setData(x=left_x, y=left_y)

        right_x = np.linspace(down_x, up_x, pts)
        right_y = right_x * np.tan(elevation*np.pi/180)
        self.sector_right.setData(x=right_x, y=right_y)

        down_x = np.linspace(-down_x, down_x, pts)
        down_y = np.absolute(np.sqrt((r**2)-(down_x)**2))
        self.sector_bottom.setData(x=down_x, y=down_y)

        top_x = np.linspace(-up_x, up_x, pts)
        top_y = np.absolute(np.sqrt((R**2)-(top_x)**2))
        self.sector_top.setData(x=top_x, y=top_y)



    def setData(self, data:typing.Sequence) ->None:
        ''' Set the data to the plot.
        Args:
            data: The data to be shown. The shape of the data must be (2,).
            '''
        self.pos1_buffer.append(data[0])
        self.pos2_buffer.append(data[1])

        self.tracking_position.setData(x=[self.pos1_buffer[-1]], y=[self.pos2_buffer[-1]])

        if self.has_position_record:
            self.pattern.setData(x=np.asarray(self.pos1_buffer), y=np.asarray(self.pos2_buffer))
            self.last_position.setData(x=[self.pos1_buffer[0]], y=[self.pos2_buffer[0]])


class MultiPointTrackingPlotWidget(TrackingPlotWidget):

    def __init__(self, parent=None, title='Tracking Plot', has_pos_record=False, has_sector_range=False, **kwargs):
        super().__init__(parent=parent, title=title, has_pos_record=has_pos_record, has_sector_range=has_sector_range, **kwargs)
        self.pos1_buffer_dict = {}
        self.pos2_buffer_dict = {}
        self.pattern_dict = {}
        self.color_dict = {}

    def setData(self, data: typing.Dict) -> None:
        ''' Set the data to the plot.
        Args:
            data: The data to be shown. The data must be dict.
            '''
        # self.pos1_buffer.append(data[0])
        # self.pos2_buffer.append(data[1])
        self.updatebuffer(self.pos1_buffer_dict, data, 0)
        self.updatebuffer(self.pos2_buffer_dict, data, 1)
        colors_ary = self.genColorArray(data)

        pos1_ary = []
        pos2_ary = []
        for k, que in self.pos1_buffer_dict.items():
            pos1_ary.append(self.pos1_buffer_dict[k][-1])
            pos2_ary.append(self.pos2_buffer_dict[k][-1])
            if k not in self.pattern_dict:
                pattern = pg.PlotCurveItem(pen=self._pattern_pen)
                pattern.setZValue(1)
                self.plot_item.addItem(pattern)
                self.pattern_dict[k] = pattern

        self.pos1_buffer.append(pos1_ary)
        self.pos2_buffer.append(pos2_ary)
        self.tracking_position.setData(x=self.pos1_buffer[-1], y=self.pos2_buffer[-1], brush=colors_ary)

        if self.has_position_record:
            for k, ptn in self.pattern_dict.items():
                if k in self.pos1_buffer_dict.keys():
                    ptn.setData(x=np.asarray(self.pos1_buffer_dict[k]), y=np.asarray(self.pos2_buffer_dict[k]))
            self.last_position.setData(x=self.pos1_buffer[0], y=self.pos2_buffer[0])

    def updatebuffer(self, old_dict, new_dict, pos):
        for key, value_list in new_dict.items():
            if key not in old_dict:
                old_dict[key] = deque(maxlen=self._layback_frames)
            old_dict[key].append(value_list[pos])

        for key in list(old_dict.keys()):
            if key not in new_dict:
                old_dict[key].popleft()
                if len(old_dict[key]) == 0:
                    del old_dict[key]

        return old_dict

    def genColorArray(self, data_dict):
        for key in data_dict.keys():
            if key not in self.color_dict:
                color = "#{:06x}".format(np.random.randint(0, 0xFFFFFF))  # 產生隨機顏色
                self.color_dict[key] = color

        # 本次需要的顏色
        rtn_color_dict = {k: v for k, v in self.color_dict.items() if k in self.pos1_buffer_dict}

        # 刪除不需要的顏色
        # self.color_dict = {k: v for k, v in self.color_dict.items() if k in self.pos1_buffer_dict}

        return np.array(list(rtn_color_dict.values()))

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")
                continue


class MultiPointTrackingPlotsWidget(QtWidgets.QWidget, KKTGraph):
    @property
    def axis(self) -> list:
        return self._axis

    @axis.setter
    def axis(self, value: list):
        self._axis = value
        self.multi_point_tracking.setAxisRange(x_range=value[0], y_range=value[1])

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent)
        self._axis = [[-10, 10], [-10, 30]]
        self.setupUI(**kwargs)
        self.setParam(**kwargs)

    def setupUI(self, **kwargs):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.multi_point_tracking = MultiPointTrackingPlotWidget(title='XY Tracking', has_pos_record=True, **kwargs)
        layout.addWidget(self.multi_point_tracking)

    def setData(self, data: dict):
        self.multi_point_tracking.setData(data)

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")
                continue



class TrackingPlotsWidget(QtWidgets.QWidget, KKTGraph):
    @property
    def xy_axis(self) -> list:
        return self._xy_axis

    @xy_axis.setter
    def xy_axis(self, value: list):
        self._xy_axis = value
        self.tracking_XY.setAxisRange(x_range=value[0], y_range=value[1])
        self.tracking_XY_4_3D.setAxisRange(x_range=value[0], y_range=value[1])

    @property
    def xz_axis(self) -> list:
        return self._xz_axis

    @xz_axis.setter
    def xz_axis(self, value: list):
        self._xz_axis = value
        self.tracking_XZ.setAxisRange(x_range=value[0], y_range=value[1])
        self.tracking_XZ_4_3D.setAxisRange(x_range=value[0], y_range=value[1])

    @property
    def yz_axis(self) -> list:
        return self._yz_axis

    @yz_axis.setter
    def yz_axis(self, value: list):
        self._yz_axis = value
        self.tracking_YZ.setAxisRange(x_range=value[0], y_range=value[1])
        self.tracking_YZ_4_3D.setAxisRange(x_range=value[0], y_range=value[1])


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._xy_axis = [[-10, 10], [-10, 30]]
        self._xz_axis = [[-10, 10], [-1, 30]]
        self._yz_axis = [[-10, 10], [-1, 30]]
        self.setupUI()
        pass

    def setParam(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k,v)
                print(f"set param {k} to {v}.")

    def setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.cb_tracking = QtWidgets.QComboBox()
        layout.addWidget(self.cb_tracking)
        # self.cb_tracking.addItems(['3D Tracking'])
        self.cb_tracking.addItems(['3D Tracking', 'XY Tracking', 'XZ Tracking', 'YZ Tracking'])
        self.stack = QtWidgets.QStackedWidget(self)
        self.stack.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stack)

        self.tracking_XY = TrackingPlotWidget(self, title='XY Tracking', has_pos_record=True)
        self.tracking_XY.setAxisRange(x_range=self._xy_axis[0], y_range=self._xy_axis[1])
        self.tracking_XZ = TrackingPlotWidget(self, title='XZ Tracking',has_sector_range=True, has_pos_record=True)
        self.tracking_XZ.setAxisRange(x_range=self._xz_axis[0], y_range=self._xz_axis[1])
        self.tracking_YZ = TrackingPlotWidget(self, title='YZ Tracking',has_sector_range=True, has_pos_record=True)
        self.tracking_YZ.setAxisRange(x_range=self._yz_axis[0], y_range=self._yz_axis[1])

        self.tracking_3D = QtWidgets.QFrame(self)
        layout_3D = QtWidgets.QGridLayout(self.tracking_3D)
        layout_3D.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout_3D.setContentsMargins(0, 0, 0, 0)
        self.tracking_3D.setLayout(layout_3D)

        self.tracking_XY_4_3D = TrackingPlotWidget(self, title='XY Tracking', has_pos_record=True)
        self.tracking_XY_4_3D.setAxisRange(x_range=self._xy_axis[0], y_range=self._xy_axis[1])
        self.tracking_XZ_4_3D = TrackingPlotWidget(self, title='XZ Tracking',has_sector_range=True, has_pos_record=True)
        self.tracking_XZ_4_3D.setAxisRange(x_range=self._xz_axis[0], y_range=self._xz_axis[1])
        self.tracking_YZ_4_3D = TrackingPlotWidget(self, title='YZ Tracking',has_sector_range=True, has_pos_record=True)
        self.tracking_YZ_4_3D.setAxisRange(x_range=self._yz_axis[0], y_range=self._yz_axis[1])

        layout_3D.addWidget(self.tracking_XY_4_3D,0,0)
        layout_3D.addWidget(self.tracking_XZ_4_3D,0,1)
        layout_3D.addWidget(self.tracking_YZ_4_3D,1,0)



        self.stack.addWidget(self.tracking_3D)
        self.stack.addWidget(self.tracking_XY)
        self.stack.addWidget(self.tracking_XZ)
        self.stack.addWidget(self.tracking_YZ)

        self.cb_tracking.currentIndexChanged.connect(self.stack.setCurrentIndex)



    def setData(self, data:np.ndarray):
        # if self.cb_tracking.currentText() == '3D Tracking':
        self.tracking_XY_4_3D.setData(data[0:2])
        self.tracking_XZ_4_3D.setData(data[0:3:2])
        self.tracking_YZ_4_3D.setData(data[1:3])
        # else:
        self.tracking_XY.setData(data[0:2])
        self.tracking_XZ.setData(data[0:3:2])
        self.tracking_YZ.setData(data[1:3])


class MultiPointNebulaTrackingWidget(MultiPointTrackingPlotWidget):

    def __init__(self, parent=None, title='Tracking Plot', has_pos_record=False, has_sector_range=False, **kwargs):
        super().__init__(parent=parent, title=title, has_pos_record=has_pos_record, has_sector_range=has_sector_range, **kwargs)

    def _setupUI(self):
        super(MultiPointNebulaTrackingWidget, self)._setupUI()
        self.nebula_position = pg.ScatterPlotItem(pen=self._pos_pen, size=self.tracking_point_size/2)
        self.nebula_position.setZValue(100)
        self.plot_item.addItem(self.nebula_position)

    def setData(self, data: typing.Dict, nebula_data: list) -> None:
        super(MultiPointNebulaTrackingWidget, self).setData(data)

        if nebula_data is None:
            return
        nebula = np.array(nebula_data).T
        if len(nebula) > 0:
            self.nebula_position.setData(x=nebula[0], y=nebula[1])



##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    x=0
    y=0
    z=0

    x_inc = 0.2
    y_inc = 0.2
    z_inc = 0.2
    s = time.time()
    def data_update():
        global Tracking, y, x, y_inc, x_inc, z, z_inc,s
        if x >= 10:
            x_inc = -0.2
        if x <= -10:
            x_inc =0.2

        if y >= 10:
            y_inc = -0.3
        if y <= -10:
            y_inc = 0.3

        if z >= 20:
            z_inc = -0.2
        if z <= 0:
            z_inc = 0.2

        y = y + y_inc
        x = x + x_inc
        z = z + z_inc
        # Tracking.setData([x, y, z])
        if x < 1:
            Tracking.setData({'1': [x, y, z],
                              '2': [y, z, x]}, [[x-1, y], [y+1, z]])
        else:
            Tracking.setData({'1': [x, y, z],
                              '2': [y, z, x],
                              '3': [z, x, y]}, [[x-1, y], [y+1, z], [z, x+1]])
        # Tracking.setData([[x, y, z], [z, x, y]])
        # Tracking.setData({'1': [x, y, z],
        #                   '2': [y, z, x]})
        print(f'frame rate : {time.time()-s} s')
        s = time.time()

    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(800, 600)

    Tracking = MultiPointNebulaTrackingWidget(title='XY Tracking', has_pos_record=True)
    win.setCentralWidget(Tracking)
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(40)

    app.exec_()
    qtimer.stop()
import sys
from typing import Literal, overload, Optional,List, Dict
from pyqtgraph.dockarea import DockArea, Dock
from PySide2 import QtWidgets, QtCore, QtGui
from dataclasses import dataclass


class MultiPlots(DockArea):
    max_dock = 20
    def addDockWidget(self,
                      name: str,
                      label_text:str,
                      widget:QtWidgets.QWidget,
                      position:Literal['bottom','top', 'left', 'right', 'above','below']='right',
                      relativeTo=None)->Dock:
        row_element_num = 1

        if name in self.docks.keys():
            raise  Exception(f'dock name {name} is exist.')

        dock = Dock(name=str(name))
        dock.label.setText(label_text)
        dock.layout.setContentsMargins(3, 3, 3, 3)
        dock.addWidget(widget)
        self.addDock(dock=dock, position=position, relativeTo=relativeTo)
        dock.setOrientation(o='vertical', force=True)

        # dock append logic
        if len(dict(self.docks)) > self.max_dock:
            dock_name = tuple(self.docks.keys())[0]
            self.removeDockWidget(dock_name)

        if len(dict(self.docks)) > row_element_num:
            move_dock = dict(self.docks).get(tuple(self.docks.keys())[-row_element_num])
            self.moveDock(dock=move_dock, position='below', neighbor=dict(self.docks).get(tuple(self.docks.keys())[-2]))

        return dock

    def updateResults(self, results:dict):
        for name, dock in self.docks.items():
            if results.getData(name) is not None:
                dock.widgets[0].setData(results.getData(name).data)


    def removeDockWidget(self, dock_name:str):
        del_dock: Dock = self.docks.pop(dock_name)
        del_dock.close()
        del del_dock


@dataclass
class CheckBoxStatus:
    object_name:str
    text:str
    checked:bool
    enable:bool

    def renderWidget(self, check_box:QtWidgets.QCheckBox)->QtWidgets.QCheckBox:
        check_box.setText(self.text)
        check_box.setObjectName(self.object_name)
        check_box.setChecked(self.checked)
        check_box.setEnabled(self.enable)
        return check_box


class DynamicCheckBoxWidget(QtWidgets.QFrame):
    sig_check = QtCore.Signal(CheckBoxStatus)
    def __init__(self, parent=None, items:List[CheckBoxStatus]=None, cols_num=1):
        super().__init__(parent=parent)
        self.check_boxes: Dict[str, QtWidgets.QCheckBox] = {}
        self.setContentsMargins(0,0,0,0)
        self._cols_num = cols_num
        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setAlignment(QtGui.Qt.AlignmentFlag.AlignTop)
        self.setupCheckBox(items)


    def setupCheckBox(self, items:List[CheckBoxStatus]):
        if items is None:
            return
        for item in items:
            self.addCheckBox(item)
        self.updateLayout()


    def addCheckBox(self, item:CheckBoxStatus):
        check_box = QtWidgets.QCheckBox()
        check_box = item.renderWidget(check_box)
        self.check_boxes.setdefault(check_box.objectName(), check_box)
        check_box.toggled.connect(self._checkBox)

    def _checkBox(self):
        check_box = self.check_boxes.get(self.sender().objectName())
        check_box_item = CheckBoxStatus(object_name=check_box.objectName(),
                                        text=check_box.text(),
                                        checked=check_box.isChecked(),
                                        enable=check_box.isEnabled())
        self.sig_check.emit(check_box_item)

    def updateLayout(self):
        row=1
        col=0
        for obj_name, check_box in self.check_boxes.items():
            if check_box is None:
                continue
            self.grid.addWidget(check_box, row, col, 1, 1)
            col = col + 1
            if col == self._cols_num:
                row = row + 1
                col = 0
        self.update()


    def setCheckBoxStatus(self, item:CheckBoxStatus):
        if item.object_name not in self.check_boxes.keys():
            # self.addCheckBox(item)
            return

        check_box = self.check_boxes.get(item.object_name)
        item.renderWidget(check_box)


class ButtonCloseHandle(QtWidgets.QSplitterHandle):
    def __init__(self, orientation, closable_wg:QtWidgets.QWidget, parent=None,):
        super().__init__(orientation, parent)
        self.closable_wg = closable_wg
        self.handle_size = 10
        self.orientation = orientation
        if self.orientation == QtGui.Qt.Orientation.Horizontal:
            self.setFixedWidth(self.handle_size)
        else:
            self.setFixedHeight(self.handle_size)
        self.setStyleSheet("background-color: #ddd; border: 1px solid #aaa;")

        ly = QtWidgets.QVBoxLayout(self)
        ly.setAlignment(QtGui.Qt.AlignmentFlag.AlignTop)

        self.btn = QtWidgets.QPushButton("<>", self)
        ly.addWidget(self.btn)
        ly.setContentsMargins(0,0,0,0)

        if self.orientation == QtGui.Qt.Orientation.Horizontal:
            self.btn.setFixedWidth(self.handle_size)
            self.btn.setFixedHeight(60)
        else:
            self.btn.setFixedHeight(self.handle_size)
            self.btn.setFixedWidth(60)
        self.btn.clicked.connect(self.resizeClosableWidget)

    def setClosableWidget(self, wg:QtWidgets.QWidget):
        self.closable_wg = wg


    def resizeClosableWidget(self):
        splitter:QtWidgets.QSplitter = self.parent()
        sizes = splitter.sizes()

        if self.closable_wg.width() != self.closable_wg.minimumWidth():
            # self.btn.setText('<')
            self.closable_wg.resize(0, self.closable_wg.height())
            sizes[0] = 0
            splitter.setSizes(sizes)
        else:
            # self.btn.setText('>')
            self.closable_wg.resize(self.closable_wg.maximumWidth(), self.closable_wg.height())
            sizes = [self.closable_wg.width(), (sizes[1]-self.closable_wg.width())]
            splitter.setSizes(sizes)

class PlugInSplitter(QtWidgets.QSplitter):
    def __init__(self, parent:Optional[QtWidgets.QWidget]=None):
        super().__init__(parent=parent)
        # self.setStyleSheet("QSplitter::handle{background: lightgrey}")
        self.setFrameStyle(QtWidgets.QFrame.Shape.Panel | QtWidgets.QFrame.Shadow.Raised)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 4)
        self._initOptionArea()
        self._initCanvasArea()
        self.handle.setClosableWidget(self._scroll_area)



    def createHandle(self) -> ButtonCloseHandle:
        self.handle = ButtonCloseHandle(self.orientation(), QtWidgets.QWidget(), self)
        return self.handle


    def _initCanvasArea(self):
        self.canvas_widget = QtWidgets.QFrame()
        self.addWidget(self.canvas_widget)
        self.canvas_widget.setFrameShape(QtWidgets.QFrame.Shape.Box)
        layout = QtWidgets.QVBoxLayout(self.canvas_widget)
        self.canvas_widget.setLayout(layout)


    def _initOptionArea(self):
        self._scroll_area = QtWidgets.QScrollArea(self)
        self.addWidget(self._scroll_area)

        self._scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setMaximumWidth(350)
        self._scroll_area.resize(350, self._scroll_area.height())
        self._scroll_area.setWidgetResizable(True)
        # self._scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


        self.option_widget = QtWidgets.QFrame()
        self._scroll_area.setWidget(self.option_widget)
        self.option_area_layout = QtWidgets.QVBoxLayout(self.option_widget)
        self.option_area_layout.setContentsMargins(0, 3, 0, 3)
        self.option_area_layout.setSpacing(0)
        self.option_area_layout.setStretch(9, 1)

        self.option_widget.setLayout(self.option_area_layout)








if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    wg = QtWidgets.QWidget()
    ly = QtWidgets.QVBoxLayout(wg)
    wg.setLayout(ly)
    wg.resize(1200,600)
    dock = MultiPlots()
    btn = QtWidgets.QPushButton('666')
    ly.addWidget(btn)
    ly.addWidget(dock)
    btn.clicked.connect(lambda :dock.addDockWidget('dock.i','123',  QtWidgets.QLabel('12312313232132132132')))
    wg.show()
    app.exec_()

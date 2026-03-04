# -*- coding: utf-8 -*-
import numpy as np
from PySide2.QtCore import QSize
from PySide2.QtWidgets import QPushButton
from PySide2 import QtGui, QtCore

class LED(QPushButton):
    class Color:
        black = np.array([0x00, 0x00, 0x00], dtype=np.uint8)
        white = np.array([0xff, 0xff, 0xff], dtype=np.uint8)
        blue = np.array([0x73, 0xce, 0xf4], dtype=np.uint8)
        green = np.array([0x00, 0xff, 0x2f], dtype=np.uint8)
        orange = np.array([0xff, 0xa5, 0x00], dtype=np.uint8)
        purple = np.array([0xaf, 0x00, 0xff], dtype=np.uint8)
        red = np.array([0xf4, 0x37, 0x53], dtype=np.uint8)
        yellow = np.array([0xff, 0xff, 0x00], dtype=np.uint8)
    class Shape:
        capsule = 1
        circle = 2
        rectangle = 3

    def __init__(self, parent=None, on_color=Color.green, off_color=Color.black,
                 shape=Shape.rectangle, build='release', auto_off=0):
        super().__init__(parent=parent)
        self.auto_off = auto_off
        self.off_timer = QtCore.QTimer()
        self.off_timer.timeout.connect(self.turn_off)

        self.setFont(QtGui.QFont('Yu Gothic UI', 12))

        if build == 'release':
            self.setDisabled(True)
        else:
            self.setEnabled(True)

        self._qss = '''
        QPushButton {{
            border: 3px solid lightgray;
            border-radius: {}px;
            background-color: 
                QLinearGradient( 
                    y1: 0, y2: 1, 
                    stop: 0 white, 
                    stop: 0.2 #{}, 
                    stop: 0.8 #{}, 
                    stop: 1 #{} 
                    ); 
                    }}
        '''
        self._on_qss = ''
        self._off_qss = ''

        self._status = False
        self._end_radius = 0

        # Properties that will trigger changes on qss.
        self.__on_color = None
        self.__off_color = None
        self.__shape = None
        self.__height = 0

        self.on_color = on_color
        self.off_color = off_color
        self.shape = shape
        self._height = self.sizeHint().height()

        self.set_status(False)


    # =================================================== Reimplemented Methods
    def mousePressEvent(self, event):
        QPushButton.mousePressEvent(self, event)
        if self._status is False:
            self.set_status(True)
        else:
            self.set_status(False)

    def sizeHint(self):
        if self.shape == LED.Shape.capsule:
            base_w = 50
            base_h = 30
        elif self.shape == LED.Shape.circle:
            base_w = 30
            base_h = 30
        elif self.shape == LED.Shape.rectangle:
            base_w = 40
            base_h = 30
        else:
            base_w = 40
            base_h = 30
        width = int(base_w)
        height = int(base_h)
        return QSize(width, height)

    def resizeEvent(self, event):
        self._height = self.size().height()
        QPushButton.resizeEvent(self, event)

    def setFixedSize(self, width, height):
        self._height = height
        if self.shape == LED.Shape.circle:
            QPushButton.setFixedSize(self, height, height)
        else:
            QPushButton.setFixedSize(self, width, height)

    # ============================================================== Properties
    @property
    def on_color(self):
        return self.__on_color

    @on_color.setter
    def on_color(self, color):
        self.__on_color = color
        self._update_on_qss()

    @on_color.deleter
    def on_color(self):
        del self.__on_color

    @property
    def off_color(self):
        return self.__off_color

    @off_color.setter
    def off_color(self, color):
        self.__off_color = color
        self._update_off_qss()

    @off_color.deleter
    def off_color(self):
        del self.__off_color

    @property
    def shape(self):
        return self.__shape

    @shape.setter
    def shape(self, shape):
        self.__shape = shape
        self._update_end_radius()
        self._update_on_qss()
        self._update_off_qss()
        self.set_status(self._status)

    @shape.deleter
    def shape(self):
        del self.__shape

    @property
    def _height(self):
        return self.__height

    @_height.setter
    def _height(self, height):
        self.__height = height
        self._update_end_radius()
        self._update_on_qss()
        self._update_off_qss()
        self.set_status(self._status)

    @_height.deleter
    def _height(self):
        del self.__height

    # ================================================================= Methods
    def _update_on_qss(self):
        color, grad = self._get_gradient(self.__on_color)
        self._on_qss = self._qss.format(self._end_radius, grad, color, color)

    def _update_off_qss(self):
        color, grad = self._get_gradient(self.__off_color)
        self._off_qss = self._qss.format(self._end_radius, grad, color, color)

    def _get_gradient(self, color):
        grad = ((self.Color.white - color) / 2).astype(np.uint8) + color
        grad = '{:02X}{:02X}{:02X}'.format(grad[0], grad[1], grad[2])
        color = '{:02X}{:02X}{:02X}'.format(color[0], color[1], color[2])
        return color, grad

    def _update_end_radius(self):
        if self.__shape == LED.Shape.rectangle:
            self._end_radius = int(self.__height / 10)
        else:
            self._end_radius = int(self.__height / 2)

    def _toggle_on(self):
        self.setStyleSheet(self._on_qss)

    def _toggle_off(self):
        self.setStyleSheet(self._off_qss)

    def set_on_color(self, color):
        self.on_color = color

    def set_off_color(self, color):
        self.off_color = color

    def set_shape(self, shape):
        self.shape = shape

    def set_status(self, status):
        self._status = True if status else False
        if self._status is True:
            self._toggle_on()
            if self.auto_off != 0:
                self.off_timer.start(self.auto_off * 1000)
        else:
            self._toggle_off()
            if self.off_timer.isActive():
                self.off_timer.stop()


    def turn_on(self, status=True):
        self.set_status(status)


    def turn_off(self, status=False):
        self.set_status(status)



    def is_on(self):
        return True if self._status is True else False

    def is_off(self):
        return True if self._status is False else False


if __name__ == '__main__':
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QGridLayout
    from PySide2.QtWidgets import QWidget
    import sys

    class Demo(QWidget):
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            self._shape = ['capsule', 'circle', 'rectangle']
            self._color = ['blue', 'green', 'orange', 'purple', 'red', 'yellow']
            self._layout = QGridLayout(self)
            self._create_leds()
            self._arrange_leds()

        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                self.close()

        def _create_leds(self):
            for s in self._shape:
                for c in self._color:
                    exec('self._{}_{} = LED(self, on_color=LED.Color.{}, \
                          shape=LED.Shape.{}, build="debug", auto_off=1)'.format(s, c, c, s))
                    # exec(f'self._{s}_{c}.setText("{c}")')
                    exec('self._{}_{}.setFocusPolicy(Qt.NoFocus)'.format(s, c))

        def _arrange_leds(self):
            for r in range(len(self._shape)):
                for c in range(len(self._color)):
                    exec('self._layout.addWidget(self._{}_{}, {}, {}, 1, 1, \
                          Qt.AlignCenter)'
                         .format(self._shape[r], self._color[c], r, c))
                    c += 1
                r += 1

    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())

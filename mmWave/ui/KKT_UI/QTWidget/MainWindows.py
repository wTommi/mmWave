from PySide2 import QtWidgets, QtGui, QtCore


class KeyEventWidget(QtWidgets.QWidget):
    key_num_list = [QtCore.Qt.Key_0, QtCore.Qt.Key_1, QtCore.Qt.Key_2,
                    QtCore.Qt.Key_3, QtCore.Qt.Key_4, QtCore.Qt.Key_5,
                    QtCore.Qt.Key_6, QtCore.Qt.Key_7, QtCore.Qt.Key_8,
                    QtCore.Qt.Key_9]
    key_event = False
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if not self.key_event:
            return
        # print('enter press')

        key = a0.key()
        keytext = a0.text()
        self.key = key

        if key in self.key_num_list:
            self.press_num_Signal.emit(key)
            # print(keytext)

        if key == QtCore.Qt.Key_Escape:
            self.press_Esc_Signal.emit(True)
            # print(keytext)

    def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:
        if not self.key_event:
            return
        # print('enter release')
        key = a0.key()
        if not hasattr(self, 'key'):
            print('no key')
            return

        if self.key != key:
            return

        if a0.isAutoRepeat():
            # print('release return')
            return

        keytext = a0.text()
        if key in self.key_num_list:
            self.press_num_Signal.emit(False)
            # print(keytext)

    def enableKeyPressEvent(self, enable=True):
        self.key_event = enable
class KKTMainWindow(QtWidgets.QMainWindow):
    '''
    KKT QMainWidow, there's some signals and rewrite closeEvent, keyPressEvent and keyReleaseEvent.
    '''
    close_Signal = QtCore.Signal(bool)
    start_Signal = QtCore.Signal(bool)

    def __init__(self, title='test mode', enable_menu_bar=True):
        super().__init__()
        self.setStyleSheet("font-family: Yu Gothic UI;")
        self.setWindowTitle(title)

        self.lb_FPS = QtWidgets.QLabel('fps : ')
        self.lb_FPS.setFixedWidth(100)
        self.enable_menu_bar = enable_menu_bar
        # self.setup()
        # self._init_MenuBar()
        # self._init_StatusBar()
        pass

    def setup(self):
        self._init_MenuBar()
        self._init_StatusBar()
        pass


    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        reply = QtWidgets.QMessageBox.question(None, 'Quit', 'Are you sure to quit??', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.loop = False
            self.close_Signal.emit(True)
            # self.delete_Signal.emit()
            event.accept()
            print('Quit Mode Window')
        else:
            event.ignore()

    def _init_MenuBar(self):
        if not self.enable_menu_bar:
            return
        self.action_Connect = QtWidgets.QAction()
        self.action_Connect.setObjectName(u"action_Connect")
        self.actionDisconnect = QtWidgets.QAction()
        self.actionDisconnect.setObjectName(u"actionDisconnect")

        self.menuBar = QtWidgets.QMenuBar()
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 941, 21))
        self.menu_File = QtWidgets.QMenu(self.menuBar)
        self.menu_File.setObjectName(u"menu_File")
        self.setMenuBar(self.menuBar)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menu_File.addAction(self.action_Connect)
        self.menu_File.addAction(self.actionDisconnect)

        self.action_Connect.setText(QtCore.QCoreApplication.translate("MainWindow", u"&Connect", None))
        # if QT_CONFIG(tooltip)
        self.action_Connect.setToolTip(QtCore.QCoreApplication.translate("MainWindow", u"Connect to device", None))
        # endif // QT_CONFIG(tooltip)
        self.actionDisconnect.setText(QtCore.QCoreApplication.translate("MainWindow", u"Disconnect", None))
        self.menu_File.setTitle(QtCore.QCoreApplication.translate("MainWindow", u"&File", None))

    def _init_StatusBar(self):
        self.statusBar = QtWidgets.QStatusBar(self)
        self.statusBar.setObjectName(u"statusBar")
        self.setStatusBar(self.statusBar)

class ModeWindow(KKTMainWindow):
    '''
    Set QSplitter in the QMainWindow central and split to two area "canvas" and "scroll sublayout".
    '''
    def __init__(self, title='test mode', enable_menu_bar=False):
        super(ModeWindow, self).__init__(title, enable_menu_bar)

        # self.setup()
        pass

    def setup(self):
        super(ModeWindow, self).setup()
        splitter = self._init_splitter()
        self.setCentralWidget(splitter)
        scroll_wg = self._init_panel_scroll_area()
        self.main_widget.addWidget(scroll_wg)
        canvas_wg = self._init_canvas()
        self.main_widget.addWidget(canvas_wg)


        self.statusBar.addPermanentWidget(QtWidgets.QLabel())
        self.statusBar.addPermanentWidget(self.lb_FPS)

        pass

    def _init_splitter(self):
        self.main_widget = QtWidgets.QSplitter(self)
        self.main_widget.setStyleSheet("QSplitter::handle{background: lightgrey}")
        self.main_widget.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Sunken)
        self.main_widget.setStretchFactor(0, 1)
        self.main_widget.setStretchFactor(1, 4)
        return self.main_widget

    def _init_canvas(self):
        self.canvas_widget = QtWidgets.QFrame(self.main_widget)
        self.canvas_widget.setObjectName(u"canvas_widget")
        # self.canvas_widget.setContentsMargins(5,5,5,5)
        self.canvas_layout = QtWidgets.QVBoxLayout(self.canvas_widget)
        self.canvas_layout.setAlignment(QtCore.Qt.AlignCenter)
        self.canvas_widget.setLayout(self.canvas_layout)

        return self.canvas_widget

    def _init_panel_scroll_area(self):
        panel_scroll_area = QtWidgets.QScrollArea(self.main_widget)
        # scroll_ly = QtWidgets.QVBoxLayout(panel_scroll_area)
        # scroll_ly.setContentsMargins(0, 0, 0, 0)
        # scroll_ly.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        # panel_scroll_area.setLayout(scroll_ly)
        panel_scroll_area.setFocusPolicy(QtCore.Qt.StrongFocus)
        panel_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        panel_scroll_area.setMinimumWidth(350)
        panel_scroll_area.setMaximumWidth(500)
        # panel_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        panel_scroll_area.setWidgetResizable(True)
        # panel_scroll_area.horizontalScrollBar().setEnabled(False)

        self.panel_widget = QtWidgets.QFrame()
        # scroll_ly.addWidget(self.panel_widget, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        panel_scroll_area.setWidget(self.panel_widget)

        self.panel_layout = QtWidgets.QVBoxLayout(self.panel_widget)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_widget.setLayout(self.panel_layout)
        self.panel_layout.setAlignment(QtCore.Qt.AlignTop)
        self.panel_layout.setSpacing(0)
        return panel_scroll_area


    def addWidgetToCanvas(self):
        pass

    def enableSublayoutWidget(self, enable):
        pass

    def addSublayoutWidget(self):
        pass





if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication([])
    TestMode = ModeWindow(title='KKT Test Window')
    TestMode.setup()
    TestMode.resize(1000, 600)
    lb = QtWidgets.QLabel('Panel')
    lb2 = QtWidgets.QLabel('Canvas')
    TestMode.panel_layout.addWidget(lb)
    TestMode.canvas_layout.addWidget(lb2)
    TestMode.show()
    sys.exit(app.exec_())

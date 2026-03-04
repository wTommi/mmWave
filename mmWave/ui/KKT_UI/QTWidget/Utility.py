from PySide2 import QtCore


def quit_app(seconds):
    timer = QtCore.QTimer()
    timer.singleShot(seconds * 1000, QtCore.QCoreApplication.quit)
    QtCore.QCoreApplication.exec_()

def pause(seconds):
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(seconds * 1000, loop.quit)
    loop.exec_()
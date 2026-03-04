from PySide2 import QtWidgets, QtCore, QtGui

class CountDownQMessageBox(QtWidgets.QMessageBox):
    def __init__(self, icon:QtWidgets.QMessageBox.Icon, title:str, msg:str,  msg2:str='auto save', timeout:int=3, *args, **kwargs):
        super().__init__(icon, title, msg, *args, **kwargs)
        # self.setWindowTitle("message")
        self.addButton(QtWidgets.QMessageBox.Yes)
        self.addButton(QtWidgets.QMessageBox.No)
        self.timeout = timeout
        self.text1 = msg
        self.text2 = msg2
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.changeContent)
        if timeout > 0:
            self.setText(f"{self.text1}\n({self.text2} in {self.timeout} seconds.)")

    def closeEvent(self, event):
        if self.timer.isActive() :
            self.timer.stop()
        event.accept()

    def exec_(self) -> int:
        if self.timeout > 0:
            self.timer.start()
        return super().exec_()
    def changeContent(self, ):
        self.timeout -= 1
        self.setText(f"{self.text1}\n({self.text2} in {self.timeout} seconds.)")
        if self.timeout <= 0:
            self.timer.stop()
            self.button(QtWidgets.QMessageBox.Yes).click()



def AlternativeMessageBox(icon:QtWidgets.QMessageBox.Icon, msg:str, title:str='Question')->int:
    QMsgBox = QtWidgets.QMessageBox(icon, title, msg, QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
    if icon == QtWidgets.QMessageBox.Warning:
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    return QMsgBox.exec()


def OKMessageBox(icon:QtWidgets.QMessageBox.Icon, msg:str, title:str='Question'):
    QMsgBox = QtWidgets.QMessageBox(icon, title, msg, QtWidgets.QMessageBox.Ok)
    if icon == QtWidgets.QMessageBox.Warning:
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    return QMsgBox.exec()

def CountDownMessageBox(icon:QtWidgets.QMessageBox.Icon, msg:str, title:str='Question', msg2='auto save', timeout=3):
    QMsgBox = CountDownQMessageBox(icon=icon, title=title, msg=msg, msg2=msg2, timeout=timeout)
    if icon == QtWidgets.QMessageBox.Warning:
        QMsgBox.setStyleSheet("QLabel{ color: red}")
    return QMsgBox.exec()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ret = CountDownMessageBox(QtWidgets.QMessageBox.Warning, 'test', timeout=5)
    print(ret)
    app.exec_()
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi
from designer_wrapped import UI_Wrapped
import psutil
from PyQt5 import QtCore
app = QApplication(sys.argv)
ex = UI_Wrapped()
w = QMainWindow()
ex.setupUi(w)

w.show()


def handler_psutil():
    value = psutil.cpu_percent(interval=None, percpu=True)
    ex.textEdit.append(str(value))
    ex.update_cpu_perc(value)


timer = QtCore.QTimer()
timer.timeout.connect(handler_psutil)
timer.start(1000)


sys.exit(app.exec_())

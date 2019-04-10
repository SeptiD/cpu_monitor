import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from designer_wrapped import UI_Wrapped
import psutil
from PyQt5 import QtCore

app = QApplication(sys.argv)
ex = UI_Wrapped()
w = QMainWindow()
ex.setupUi(w)

w.show()


def handler_psutil():
    ex.update_cpu_perc()
    ex.update_cpu_extra_info()
    ex.update_memory_info()
    ex.update_net_info()
    ex.update_processes_info()
    ex.update_hpc_info()


timer = QtCore.QTimer()
timer.timeout.connect(handler_psutil)
timer.start(1000)

sys.exit(app.exec_())

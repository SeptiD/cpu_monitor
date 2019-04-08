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
    value2 = psutil.cpu_stats()
    value_temperature = psutil.sensors_temperatures()['coretemp']
    value_battery = psutil.sensors_battery()
    ex.update_cpu_extra_info(value2, value_temperature, value_battery)
    ex.update_memory_info()
    ex.update_net_info()
    ex.update_processes_info()


timer = QtCore.QTimer()
timer.timeout.connect(handler_psutil)
timer.start(1000)

sys.exit(app.exec_())

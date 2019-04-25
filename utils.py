from PyQt5 import QtCore, QtGui, QtWidgets
import json

class CustomProgressBar(QtWidgets.QProgressBar):
    th1 = 40
    th2 = 80

    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.customPallete = QtGui.QPalette(self.palette())

    def setValue(self, value):
        QtGui.QProgressBar.setValue(self, value)

        if value < CustomProgressBar.th1:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.blue))
        elif CustomProgressBar.th1 <= value < CustomProgressBar.th2:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.darkYellow))
        else:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.red))
        self.setPalette(self.customPallete)


class BatteryProgressBar(QtWidgets.QProgressBar):
    th1 = 20
    th2 = 70

    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.customPallete = QtGui.QPalette(self.palette())

    def setValue(self, value):
        QtGui.QProgressBar.setValue(self, value)

        if value < CustomProgressBar.th1:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.red))
        elif CustomProgressBar.th1 <= value < CustomProgressBar.th2:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.darkYellow))
        else:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                                        QtGui.QColor(QtCore.Qt.blue))
        self.setPalette(self.customPallete)


class GetHPCInfoThread(QtCore.QThread):
    HPC_FILE = 'hpc_info.txt'
    finished_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def get_info_from_hpc_file(self):
        out_dict = {}
        content = None
        with open(GetHPCInfoThread.HPC_FILE) as inf:
            content = json.load(inf)
        for elem in content:
            out_dict[elem['EventName']] = elem
        return out_dict

    def run(self):
        # your logic here
        result = self.get_info_from_hpc_file()
        self.finished_signal.emit(result)

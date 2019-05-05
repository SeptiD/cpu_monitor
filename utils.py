from PyQt5 import QtCore, QtGui, QtWidgets
import json
import matplotlib.pyplot as plt
import numpy as np


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


class PlotHPCThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(object)

    def __init__(self, log_file_name):
        QtCore.QThread.__init__(self)
        self.log_file_name = log_file_name
        self.data = {}

    def __del__(self):
        self.wait()

    def run(self):
        # your logic here
        bins = 100

        with open(self.log_file_name) as inf:
            for line in inf:
                temp_json = json.loads(line)
                for key, value in temp_json.items():
                    if key in self.data:
                        self.data[key].append(value)
                    else:
                        self.data[key] = [value]

        for key, value in self.data.items():
            f, axarr = plt.subplots(3)
            f.tight_layout()
            axarr[0].hist(value, bins)
            axarr[0].set_title(key + ' - histogram')

            axarr[1].boxplot(value)
            axarr[1].set_title(key + ' - boxplot')
            axarr[1].yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

            x = np.linspace(0, len(value) - 1, num=len(value))
            y = np.array(value)
            axarr[2].plot(x, y)
            axarr[2].set_title(key + ' - plot')

            plt.savefig(self.log_file_name + '-' + key + '.png')
            plt.close()

# re-implement the QTreeWidgetItem
class ProcessTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            return float(key1) < float(key2)
        except ValueError:
            return key1 < key2
from PyQt5 import QtCore, QtGui, QtWidgets
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import matplotlib.pyplot as plt
import numpy as np
import os


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
        result = self.get_info_from_hpc_file()
        self.finished_signal.emit(result)


class PlotHPCThread(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(object)

    def __init__(self, log_file_name, hpc_cnts):
        QtCore.QThread.__init__(self)
        self.log_file_name = log_file_name
        self.hpc_cnts = hpc_cnts
        self.data = {}

    def __del__(self):
        self.wait()

    def get_title(self, code):
        for key, value in self.hpc_cnts.items():
            if code[-4:-2] in value['UMask'] and code[-2:] in value['EventCode']:
                return key + '-' + code

    def run(self):
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
            seed_title = self.get_title(key)
            f, axarr = plt.subplots(3)
            f.tight_layout()
            axarr[0].hist(value, bins)
            axarr[0].set_title(seed_title + ' - histogram')

            axarr[1].boxplot(value)
            axarr[1].set_title(seed_title + ' - boxplot')
            axarr[1].yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

            x = np.linspace(0, len(value) - 1, num=len(value))
            y = np.array(value)
            axarr[2].plot(x, y)
            axarr[2].set_title(seed_title + ' - plot')

            plt.savefig(self.log_file_name + '-' + seed_title + '.png')
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


class Hpc_Dialog_Plots(QtWidgets.QDialog):

    def __init__(self, parent=None, plots_path=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.position = -1
        self.file_names = [x for x in os.listdir(plots_path) if str.endswith(x, '.png')]
        self.file_names.sort()
        self.hpc_plots_path = plots_path
        self.layout = QtWidgets.QVBoxLayout(self)
        self.pic_label = QtWidgets.QLabel()
        self.next_button = QtWidgets.QPushButton('Next Plot')
        self.next_button.clicked.connect(self.put_image)
        self.previous_button = QtWidgets.QPushButton('Previous Plot')
        self.previous_button.clicked.connect(self.put_previous_image)
        self.layout.addWidget(self.pic_label)
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_buttons.addWidget(self.previous_button)
        self.layout_buttons.addWidget(self.next_button)
        self.layout.addLayout(self.layout_buttons)
        self.put_image()

    def put_image(self):
        self.position = (self.position + 1) % len(self.file_names)
        self.pic_label.setPixmap(QtGui.QPixmap(self.hpc_plots_path + '/' + self.file_names[self.position]))

    def put_previous_image(self):
        self.position = (self.position - 1) % len(self.file_names)
        if self.position == -1:
            self.position = len(self.file_names) - 1
        self.pic_label.setPixmap(QtGui.QPixmap(self.hpc_plots_path + '/' + self.file_names[self.position]))

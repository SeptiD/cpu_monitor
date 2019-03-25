from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import multiprocessing


class UI_Wrapped(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        # plot1 = pg.PlotWidget()
        # self.verticalLayout_cpu_plots.addWidget(plot1)
        for cpu in range(multiprocessing.cpu_count()):
            self.verticalLayout_cpu_plots.addWidget(pg.PlotWidget())

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import multiprocessing
import psutil


class UI_Wrapped(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.frame_progress_bars.hide()

        for cpu in range(multiprocessing.cpu_count()):
            x = pg.PlotWidget()
            x.setYRange(0, 100)
            self.verticalLayout_cpu_plots.addWidget(x)
            self.verticalLayout_cpu_progress_bars.addWidget(QtWidgets.QProgressBar())

        # self.textEdit.append('start')
        self.button_cpu_views.clicked.connect(self.cpu_views_button_pushed)

    def cpu_views_button_pushed(self):
        if self.frame_cpu_plots.isHidden():
            self.frame_progress_bars.hide()
            self.frame_cpu_plots.show()
            self.button_cpu_views.setText('BARS')
        else:
            self.frame_progress_bars.show()
            self.frame_cpu_plots.hide()
            self.button_cpu_views.setText('PLOTS')



    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

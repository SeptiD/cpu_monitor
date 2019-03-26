from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import multiprocessing
import psutil


class UI_Wrapped(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.frame_progress_bars.hide()
        self.cpu_plots_list = []
        self.cpu_p_bars_list = []

        for cpu in range(multiprocessing.cpu_count()):
            temp_plot = pg.PlotWidget()
            temp_plot.setYRange(0, 100)
            self.cpu_plots_list.append(temp_plot)
            self.verticalLayout_cpu_plots.addWidget(temp_plot)

            temp_p_bar = QtWidgets.QProgressBar()
            self.cpu_p_bars_list.append(temp_p_bar)
            self.verticalLayout_cpu_progress_bars.addWidget(temp_p_bar)

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

    def update_cpu_perc(self, cpu_perc_list):
        if not self.frame_progress_bars.isHidden():
            self.textEdit.append(str(len(cpu_perc_list)))
            self.textEdit.append(str(len(self.cpu_p_bars_list)))

            for cpu_index in range(len(cpu_perc_list)):
                self.cpu_p_bars_list[cpu_index].setValue(cpu_perc_list[cpu_index])

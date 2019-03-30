from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import multiprocessing
import psutil
import utils


class UI_Wrapped(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.frame_progress_bars.hide()
        self.cpu_plots_list = []
        self.cpu_p_bars_list = []
        self.cpu_plots_data_lists = []
        self.cpu_plots_curves_list = []

        # setup cpu related
        for cpu in range(multiprocessing.cpu_count()):
            # setup real-time plots
            temp_plot = pg.PlotWidget()
            temp_plot.setYRange(0, 100)
            self.cpu_plots_list.append(temp_plot)
            self.cpu_plots_data_lists.append([])
            self.cpu_plots_curves_list.append(
                temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))
            self.verticalLayout_cpu_plots.addWidget(temp_plot)

            # setup progress bars
            temp_p_bar = utils.CustomProgressBar()
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

    def update_cpu_perc_p_bars(self, cpu_perc_list):
        if not self.frame_progress_bars.isHidden():
            self.textEdit.append(str(len(cpu_perc_list)))
            self.textEdit.append(str(len(self.cpu_p_bars_list)))

            for cpu_index in range(len(cpu_perc_list)):
                self.cpu_p_bars_list[cpu_index].setValue(cpu_perc_list[cpu_index])

    def update_cpu_perc_plots(self, cpu_perc_list):
        if not self.frame_cpu_plots.isHidden():
            for cpu_index in range(len(cpu_perc_list)):
                # curve = self.cpu_plots_list[cpu_index].plot(pen='y')
                self.cpu_plots_data_lists[cpu_index].insert(0, cpu_perc_list[cpu_index])
                self.cpu_plots_curves_list[cpu_index].setData(self.cpu_plots_data_lists[cpu_index])

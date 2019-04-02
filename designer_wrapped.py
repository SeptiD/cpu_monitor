from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import multiprocessing
import utils
from time import strftime, time, gmtime
from datetime import datetime


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [datetime.utcfromtimestamp(value).strftime('%M:%S') for value in values]


class UI_Wrapped(Ui_MainWindow):
    combobox_system_info_options = ['CPU PERCENTAGE', 'CPU INFO', 'MEMORY', 'NETWORK', 'PROCESSES']

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.cpu_plots_list = []
        self.cpu_p_bars_list = []
        self.cpu_plots_data_lists = []
        self.cpu_plots_curves_list = []
        self.cpu_plots_max_seconds = 10
        self.cpu_plots_X_values = []

        self.setup_combobox_system_info()
        self.setup_cpu_percentage()

    def setup_cpu_percentage(self):
        self.frame_progress_bars.hide()
        # setup cpu related
        for cpu in range(multiprocessing.cpu_count()):
            # setup real-time plots
            temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
            temp_plot.setYRange(0, 100)
            temp_plot.setXRange(0, 60)
            self.cpu_plots_list.append(temp_plot)
            self.cpu_plots_data_lists.append([])
            self.cpu_plots_curves_list.append(
                temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))
            self.verticalLayout_cpu_plots.addWidget(temp_plot)

            # setup progress bars
            temp_p_bar = utils.CustomProgressBar()
            self.cpu_p_bars_list.append(temp_p_bar)
            self.verticalLayout_cpu_progress_bars.addWidget(temp_p_bar)

        self.button_cpu_views.clicked.connect(self.cpu_views_button_pushed)

    def setup_combobox_system_info(self):
        self.comboBox_system_info.addItems(UI_Wrapped.combobox_system_info_options)
        self.comboBox_system_info.activated[str].connect(self.comboBox_system_info_selected)

    def comboBox_system_info_selected(self, combo_text):
        self.textEdit.append(combo_text)

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
        self.cpu_plots_X_values.insert(0, time())
        for cpu_index in range(len(cpu_perc_list)):
            self.cpu_plots_data_lists[cpu_index].insert(0, cpu_perc_list[cpu_index])

            self.cpu_plots_curves_list[cpu_index].setData(y=self.cpu_plots_data_lists[cpu_index])

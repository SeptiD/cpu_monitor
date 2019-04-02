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


class CPU_Extra_Info:
    def __init__(self):
        self.info_list = []
        self.label_ctx_switches = QtWidgets.QLabel("Context Switches:")
        self.info_list.append(self.label_ctx_switches)
        self.label_interrupts = QtWidgets.QLabel("Interrupts:")
        self.info_list.append(self.label_interrupts)
        self.label_soft_interrupts = QtWidgets.QLabel("Soft Interrupts:")
        self.info_list.append(self.label_soft_interrupts)

    def change_info(self, info_touple):
        self.label_ctx_switches.setText("Context Switches:" + str(info_touple.ctx_switches))
        self.label_interrupts.setText("Interrupts:" + str(info_touple.interrupts))
        self.label_soft_interrupts.setText("Software Interrupts:" + str(info_touple.soft_interrupts))


class UI_Wrapped(Ui_MainWindow):
    combobox_system_info_options = ['CPU PERCENTAGE', 'CPU INFO', 'MEMORY', 'NETWORK', 'PROCESSES']

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.gathered_frames = []
        self.cpu_plots_list = []
        self.cpu_p_bars_list = []
        self.cpu_plots_data_lists = []
        self.cpu_plots_curves_list = []
        self.cpu_plots_max_seconds = 10
        self.cpu_plots_X_values = []
        self.cpu_e_i = CPU_Extra_Info()

        self.gather_frames()
        self.setup_combobox_system_info()
        self.setup_cpu_percentage()
        self.setup_cpu_extra_percentages()

    def gather_frames(self):
        self.gathered_frames.append(self.frame_cpu_plots)
        self.gathered_frames.append(self.frame_progress_bars)
        self.gathered_frames.append(self.frame_cpu_extra_info)

    def show_frame(self, frame_to_show):
        for temp_frame in self.gathered_frames:
            if temp_frame is not frame_to_show:
                temp_frame.hide()
        frame_to_show.show()

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

    def setup_cpu_extra_percentages(self):
        for elem in self.cpu_e_i.info_list:
            self.verticalLayout_cpu_extra_info.addWidget(elem)

    def setup_combobox_system_info(self):
        self.comboBox_system_info.addItems(UI_Wrapped.combobox_system_info_options)
        self.comboBox_system_info.activated[str].connect(self.combobox_system_info_selected)

    def combobox_system_info_selected(self, combo_text):
        self.textEdit.append(combo_text)
        if combo_text == 'CPU PERCENTAGE':
            self.show_frame(self.frame_cpu_plots)
        elif combo_text == 'CPU INFO':
            self.show_frame(self.frame_cpu_extra_info)

    def cpu_views_button_pushed(self):
        if self.button_cpu_views.text() == 'PLOTS':
            self.show_frame(self.frame_cpu_plots)
            self.button_cpu_views.setText('BARS')
        else:
            self.show_frame(self.frame_progress_bars)
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

    def update_cpu_extra_info(self, info_tuple):
        self.cpu_e_i.change_info(info_tuple)

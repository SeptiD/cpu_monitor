from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import utils
from time import time
from datetime import datetime, timedelta
import psutil
import shlex
import sys
from subprocess import PIPE
from threading import Thread
from queue import Queue, Empty
import json
import os
from PyQt5 import QtTest
import pwd
import platform
from keras.models import load_model
import numpy as np
import pickle
from toggle_button import QSlideSwitch

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        # print(line)
        queue.put(line)
    out.close()


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [datetime.utcfromtimestamp(value).strftime('%M:%S') for value in values]


class HPCDialog(QtWidgets.QDialog):
    out_folder = 'hpc_record_data'
    nr_of_registers = 4

    def __init__(self, parent=None, hpc_cnt=None):
        super(QtWidgets.QDialog, self).__init__(parent)

        self.hpc_dlg_cnt = hpc_cnt
        self.perf_handler = None
        self.closed_request = False

        self.hpc_dlg_cnt_keys = [''] + list(self.hpc_dlg_cnt)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.setup_layout = QtWidgets.QVBoxLayout()
        self.hpc_dlg_setup_comboboxes = []

        self.hpc_dlg_total_time_layout = QtWidgets.QHBoxLayout()
        self.hpc_dlg_time_label = QtWidgets.QLabel('Time to monitor :')
        self.hpc_dlg_time = QtWidgets.QTimeEdit()

        self.hpc_dlg_sample_time_layout = QtWidgets.QHBoxLayout()
        self.hpc_dlg_sample_label = QtWidgets.QLabel('Sample time(ms):')
        self.hpc_dlg_sample = QtWidgets.QSpinBox()

        self.hpc_dlg_details_text = QtWidgets.QTextEdit()

        self.checks_layout = QtWidgets.QHBoxLayout()
        self.hpc_dlg_check_per_cpu = QtWidgets.QCheckBox('Per CPU')
        self.hpc_dlg_check_create_plots = QtWidgets.QCheckBox('Create Plots')

        self.hpc_dlg_enter_button = QtWidgets.QPushButton('ENTER')
        self.hpc_dlg_start_button = QtWidgets.QPushButton('START')

        self.data_layout = QtWidgets.QVBoxLayout()
        self.hpc_dlg_header_labels = ['C0', 'C1', 'C2', 'C3', 'SECS', 'SAMPLE', 'PER CPU']
        self.hpc_dlg_tree = QtWidgets.QTreeWidget()
        self.hpc_dlg_bar = QtWidgets.QProgressBar()
        self.init()

    def closeEvent(self, event):
        self.closed_request = True
        if self.perf_handler:
            self.perf_handler.kill()
        super(HPCDialog, self).closeEvent(event)

    def init(self):

        self.hpc_dlg_tree.setHeaderLabels(self.hpc_dlg_header_labels)
        self.hpc_dlg_tree.setSortingEnabled(False)
        self.hpc_dlg_tree.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.hpc_dlg_tree_action = QtWidgets.QAction("Remove row", None)
        self.hpc_dlg_tree_action.triggered.connect(self.remove_row_from_tree)
        self.hpc_dlg_tree.addAction(self.hpc_dlg_tree_action)

        self.hpc_dlg_details_text.setReadOnly(True)

        self.hpc_dlg_time.setDisplayFormat('hh:mm:ss')
        self.hpc_dlg_time.setMinimumTime(QtCore.QTime(0, 0, 1))

        self.hpc_dlg_sample.setMinimum(10)
        self.hpc_dlg_sample.setMaximum(1000)
        self.hpc_dlg_sample.setValue(1000)

        self.hpc_dlg_check_per_cpu.setChecked(True)
        self.hpc_dlg_check_create_plots.setChecked(True)

        self.hpc_dlg_enter_button.clicked.connect(self.enter_clicked)
        self.hpc_dlg_start_button.clicked.connect(self.start_clicked)
        self.hpc_dlg_time.timeChanged.connect(self.time_changed)

        for idx in range(4):
            temp = QtWidgets.QComboBox()
            temp.addItems(self.hpc_dlg_cnt_keys)
            temp.currentTextChanged.connect(self.hpc_dlg_combo_change)
            self.hpc_dlg_setup_comboboxes.append(temp)
            self.setup_layout.addWidget(temp)

        self.hpc_dlg_total_time_layout.addWidget(self.hpc_dlg_time_label)
        self.hpc_dlg_total_time_layout.addWidget(self.hpc_dlg_time)
        self.hpc_dlg_total_time_layout.setStretch(1, 3)

        self.hpc_dlg_sample_time_layout.addWidget(self.hpc_dlg_sample_label)
        self.hpc_dlg_sample_time_layout.addWidget(self.hpc_dlg_sample)
        self.hpc_dlg_sample_time_layout.setStretch(1, 3)

        self.setup_layout.addLayout(self.hpc_dlg_total_time_layout)
        self.setup_layout.addLayout(self.hpc_dlg_sample_time_layout)

        self.setup_layout.addWidget(self.hpc_dlg_details_text)

        self.checks_layout.addWidget(self.hpc_dlg_check_per_cpu)
        self.checks_layout.addWidget(self.hpc_dlg_check_create_plots)
        self.setup_layout.addLayout(self.checks_layout)

        self.setup_layout.addWidget(self.hpc_dlg_enter_button)
        self.setup_layout.addWidget(self.hpc_dlg_start_button)

        self.data_layout.addWidget(self.hpc_dlg_tree)
        self.data_layout.addWidget(self.hpc_dlg_bar)

        self.layout.addLayout(self.setup_layout)
        self.layout.addLayout(self.data_layout)
        self.setWindowTitle('HPC Record')
        self.resize(1100, 200)

        self.q = Queue()

    def enter_clicked(self):
        monit_data = []
        no_hpc_selected = True
        for combo in self.hpc_dlg_setup_comboboxes:
            monit_data.append(combo.currentText())
            if combo.currentText():
                no_hpc_selected = False

        if not no_hpc_selected:
            monit_data.append(self.time_to_sec())
            monit_data.append(str(self.hpc_dlg_sample.value()))

            if self.hpc_dlg_check_per_cpu.isChecked():
                monit_data.append('True')
            else:
                monit_data.append('False')

            QtWidgets.QTreeWidgetItem(self.hpc_dlg_tree, monit_data)
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('No Hardware Performance Counters selected!')
            msg.setWindowTitle('Hardware Performance Counters Monitor')
            msg.exec()

    def time_to_sec(self):
        hours = self.hpc_dlg_time.time().hour()
        minutes = self.hpc_dlg_time.time().minute()
        seconds = self.hpc_dlg_time.time().second()
        return str((hours * 3600) + (minutes * 60) + seconds)

    def time_changed(self):
        miliseconds = int(self.time_to_sec()) * 1000
        self.hpc_dlg_sample.setMaximum(miliseconds)

    def start_clicked(self):
        if not os.path.exists(HPCDialog.out_folder):
            os.mkdir(HPCDialog.out_folder)
        this_record_folder = HPCDialog.out_folder + '/' + str(
            datetime.utcfromtimestamp(time()).strftime('%Y-%m-%d-%H-%M-%S')) + '-hpc_record'

        os.mkdir(this_record_folder)

        for combo in self.hpc_dlg_setup_comboboxes:
            combo.setEnabled(False)
        self.hpc_dlg_time.setEnabled(False)
        self.hpc_dlg_sample.setEnabled(False)
        self.hpc_dlg_check_per_cpu.setEnabled(False)
        self.hpc_dlg_check_create_plots.setEnabled(False)
        self.hpc_dlg_enter_button.setEnabled(False)
        self.hpc_dlg_start_button.setEnabled(False)
        total_time = self.calculate_total_time()
        secs_passed = 0

        iterator = QtGui.QTreeWidgetItemIterator(self.hpc_dlg_tree)  # pass your treewidget as arg
        no_values_in_tree = True
        while iterator.value():
            no_values_in_tree = False

            line = iterator.value()
            self.hpc_dlg_tree.setCurrentItem(line)
            self.hpc_dlg_tree.setFocus()
            secs_to_monitor = line.text(self.hpc_dlg_header_labels.index('SECS'))
            sample_to_monitor = line.text(self.hpc_dlg_header_labels.index('SAMPLE'))
            per_cpu = line.text(self.hpc_dlg_header_labels.index('PER CPU'))

            if 'True' in per_cpu:
                per_cpu = True
            else:
                per_cpu = False

            events_str = ''
            just_events = ''
            for idx in range(HPCDialog.nr_of_registers):
                temp_name = line.text(self.hpc_dlg_header_labels.index('C' + str(idx)))
                if temp_name:
                    events_str = events_str + '-e ' + self.get_code(temp_name) + ' '
                    just_events = just_events + self.get_code(temp_name)
            if events_str:
                if per_cpu:
                    events_str = 'perf stat ' + events_str + '-I ' + \
                                 sample_to_monitor + ' -a -A -x , sleep ' + secs_to_monitor + ' ; '
                    # print(events_str)
                else:
                    events_str = 'perf stat ' + events_str + '-I ' + \
                                 sample_to_monitor + ' -a -x , sleep ' + secs_to_monitor + ' ; '
                print(events_str)
                res = self.do_the_job(secs_to_monitor, events_str, per_cpu, this_record_folder, just_events,
                                      sample_to_monitor)
                if res == -1:
                    return
                self.hpc_dlg_bar.setValue(0)
            iterator += 1

        if no_values_in_tree:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText('You need to add at least one Hardware Performance Counters monitor record!')
            msg.setWindowTitle('Hardware Performance Counters Monitor')
            msg.exec()

        for combo in self.hpc_dlg_setup_comboboxes:
            combo.setEnabled(True)
        self.hpc_dlg_time.setEnabled(True)
        self.hpc_dlg_sample.setEnabled(True)
        self.hpc_dlg_check_per_cpu.setEnabled(True)
        self.hpc_dlg_check_create_plots.setEnabled(True)
        self.hpc_dlg_enter_button.setEnabled(True)
        self.hpc_dlg_start_button.setEnabled(True)
        self.hpc_dlg_tree.clear()
        self.hpc_dlg_bar.setValue(0)

        for combo in self.hpc_dlg_setup_comboboxes:
            combo.setCurrentIndex(0)

        plots_dialog = utils.Hpc_Dialog_Plots(plots_path=this_record_folder)
        plots_dialog.exec()

    def calculate_total_time(self):
        total_time = 0
        iterator = QtGui.QTreeWidgetItemIterator(self.hpc_dlg_tree)  # pass your treewidget as arg
        while iterator.value():
            item = iterator.value()
            total_time += int(item.text(self.hpc_dlg_header_labels.index('SECS')))
            iterator += 1

        return total_time

    def do_the_job(self, secs_to_monitor, events_str, per_cpu, this_record_folder, just_events, sample_to_monitor_ms):
        secs_to_monitor = int(secs_to_monitor)
        sample_to_monitor_ms = int(sample_to_monitor_ms)

        # total_time = 5
        # total_events = 'perf stat -e r203 -e r803 -e r105 -e r205 -I 1000 -a -A -x , sleep 5 ; perf stat -e r203 -e r803 -e r105 -e r205 -I 1000 -a -A -x , sleep 10 ;'
        # total_events = 'perf stat -e r203 -e r803 -e r105 -e r205 -I 1000 -a -A -x , sleep 5'
        # events_str = 'perf stat -e r0801 -I 1000 -a -A -x , sleep 10 ;'

        if events_str:
            # args = shlex.split(events_str)
            # self.perf_handler = psutil.Popen(args, stderr=PIPE)
            self.perf_handler = psutil.Popen(events_str, stderr=PIPE, shell=True)

            self.t = Thread(target=enqueue_output, args=(self.perf_handler.stderr, self.q))
            self.t.daemon = True  # thread dies with the program
            self.t.start()

            cnt = 0.0
            this_job_file = this_record_folder + '/' + just_events + '-' + str(
                datetime.utcfromtimestamp(time()).strftime('%Y-%m-%d-%H-%M-%S')) + '.log'
            # print(this_job_file)
            all_temp_jsons = []
            while self.perf_handler.is_running():
                if self.closed_request:
                    return -1
                temp_json = {}
                this_time_of_sample = None
                while True:
                    try:
                        if self.q:
                            line = self.q.get(timeout=.1)
                            if per_cpu:
                                cpu, value, hpc, time_of_sample = self.update_data(line, per_cpu)
                                # print(cnt, str(cpu), value, hpc, time_of_sample)
                                if this_time_of_sample:
                                    if this_time_of_sample in time_of_sample:
                                        temp_json[str(cpu) + '_' + hpc] = value
                                    else:
                                        if temp_json:
                                            all_temp_jsons.append(temp_json)
                                        temp_json = {}
                                        this_time_of_sample = time_of_sample
                                        temp_json[str(cpu) + '_' + hpc] = value
                                else:
                                    this_time_of_sample = time_of_sample
                                    temp_json[str(cpu) + '_' + hpc] = value
                            else:
                                value, hpc = self.update_data(line, per_cpu)
                                temp_json[hpc] = value
                                # print(cnt, 'all', value, hpc)
                                if temp_json:
                                    all_temp_jsons.append(temp_json)
                                temp_json = {}

                        else:
                            break
                    except Empty:
                        break

                perc = int((cnt * 100) / secs_to_monitor)
                self.hpc_dlg_bar.setValue(perc)
                if cnt >= secs_to_monitor:
                    self.perf_handler.kill()
                    self.write_job_to_file(this_job_file, all_temp_jsons)
                    if self.hpc_dlg_check_create_plots.isChecked():
                        create_plots = utils.PlotHPCThread(this_job_file, self.hpc_dlg_cnt, sample_to_monitor_ms)
                        create_plots.start()
                    return 0

                QtTest.QTest.qWait(sample_to_monitor_ms)
                # print(str(secs_to_monitor - cnt))
                if sample_to_monitor_ms / 1000 <= (secs_to_monitor - cnt):
                    cnt += sample_to_monitor_ms / 1000
                else:
                    # print("Closing..")
                    self.perf_handler.kill()
                    self.write_job_to_file(this_job_file, all_temp_jsons)
                    if self.hpc_dlg_check_create_plots.isChecked():
                        create_plots = utils.PlotHPCThread(this_job_file, self.hpc_dlg_cnt, sample_to_monitor_ms)
                        create_plots.start()
                    return 0

    def write_job_to_file(self, this_job_file, all_temp_jsons):
        to_write = ''
        for job in all_temp_jsons:
            to_write = to_write + json.dumps(job) + '\n'
        with open(this_job_file, 'w') as otf:
            otf.write(to_write)

    def get_code(self, txt):
        temp_json = self.hpc_dlg_cnt[txt]
        return 'r' + temp_json['UMask'][2:] + temp_json['EventCode'][2:]

    def update_data(self, input_line, per_cpu):
        #  1.000418172 CPU1                40.462      r205
        #  1.000472956,CPU5,25933,,r105,1000277655,100,00,,
        input_line = input_line.decode('utf-8').strip()
        # print(input_line)
        splitted = input_line.split(',')
        if per_cpu:
            time_of_sample = splitted[1]
            cpu = int(splitted[1][-1])
            value = int(splitted[2])
            hpc = splitted[4]
            return cpu, value, hpc, time_of_sample
        else:
            value = int(splitted[1])
            hpc = splitted[3]
            return value, hpc

    def remove_row_from_tree(self):
        my_item = self.hpc_dlg_tree.currentItem()
        idx = self.hpc_dlg_tree.indexOfTopLevelItem(my_item)
        self.hpc_dlg_tree.takeTopLevelItem(idx)

    def hpc_dlg_combo_change(self, text):
        self.hpc_dlg_details_text.clear()
        if text in self.hpc_dlg_cnt:
            self.hpc_dlg_details_text.append(self.hpc_dlg_cnt[text]['PublicDescription'])


class CryptoAnalysisDialog(QtWidgets.QDialog):
    scaler_file = './ai/scaler_pck.save'
    feat_file = './ai/sel_nn_features.txt'
    model_file = './ai/selected_nn_best.h5'
    secs_to_monitor = '1'
    nr_of_cpu = psutil.cpu_count()

    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.cr_anl_start_btn = QtWidgets.QPushButton('Start!')
        self.cr_anl_start_btn.clicked.connect(self.start_pushed)

        self.cr_anl_p_bar = QtWidgets.QProgressBar()

        self.cr_anl_txt = QtWidgets.QTextEdit()
        self.cr_anl_txt.setReadOnly(True)
        self.cr_anl_txt.append("Crypto Analysis")

        self.layout.addWidget(self.cr_anl_start_btn)
        self.layout.addWidget(self.cr_anl_p_bar)
        self.layout.addWidget(self.cr_anl_txt)

        self.q = Queue()
        self.perf_handler = None
        self.t = None
        self.data = {}

    def start_pushed(self):
        self.cr_anl_txt.clear()
        self.cr_anl_txt.append('Start Analysis...')
        self.cr_anl_txt.append('Getting features...')

        with open(CryptoAnalysisDialog.feat_file) as inf:
            temp_line = inf.readline().strip()

        feats = [x.strip() for x in temp_line.split()]
        feats_copy = list.copy(feats)

        for i in range(CryptoAnalysisDialog.nr_of_cpu):
            temp_feat_dict = {}
            for feat in feats:
                temp_feat_dict[feat] = []
            self.data[i] = temp_feat_dict

        if len(feats) % 4 == 1:
            total_secs_of_anl = len(feats) / 4
        else:
            total_secs_of_anl = len(feats) / 4 + 1

        counter = 0
        while feats:
            this_batch = feats[:4]
            del feats[:4]
            events_str = ''
            for one_feat in this_batch:
                events_str = events_str + '-e ' + one_feat + ' '
            events_str = 'perf stat ' + events_str + '-I 1000 -a -A -x , sleep ' + CryptoAnalysisDialog.secs_to_monitor + ' ; '

            self.perf_handler = psutil.Popen(events_str, stderr=PIPE, shell=True)
            self.t = Thread(target=enqueue_output, args=(self.perf_handler.stderr, self.q))
            self.t.daemon = True  # thread dies with the program
            self.t.start()

            cnt = 0
            while self.perf_handler.is_running():
                while True:
                    try:
                        if self.q:
                            line = self.q.get(timeout=.1)
                            cpu, value, hpc = self.update_data(line, True)
                            self.data[cpu][hpc].append(value)
                        else:
                            break
                    except Empty:
                        break

                if cnt >= int(CryptoAnalysisDialog.secs_to_monitor):
                    self.perf_handler.kill()
                    break
                cnt += 1
                QtTest.QTest.qWait(1000)

            counter += 1
            self.cr_anl_p_bar.setValue(int(counter * 100 / total_secs_of_anl))
        self.cr_anl_p_bar.setValue(100)

        with open(CryptoAnalysisDialog.scaler_file, 'rb') as inf:
            scaler_f = pickle.load(inf)

        found_thread = False
        model = load_model(CryptoAnalysisDialog.model_file)
        for i in range(CryptoAnalysisDialog.nr_of_cpu):
            for j in range(int(CryptoAnalysisDialog.secs_to_monitor)):
                model_input = []
                for feat in feats_copy:
                    model_input.append(self.data[i][feat][j])
                model_input = np.array(model_input).astype(float).reshape(1, -1)
                input_scaled = scaler_f.transform(model_input)
                res = model.predict_classes(input_scaled)
                if res:
                    found_thread = True

        if found_thread:
            self.cr_anl_txt.append('Possible threat found!')
            max_proc = None
            for proc in psutil.process_iter(attrs=['pid', 'exe', 'cpu_percent']):
                proc_dict = proc.info
                if max_proc:
                    if proc_dict['cpu_percent'] > max_proc['cpu_percent']:
                        max_proc = proc_dict
                else:
                    max_proc = proc_dict
            self.cr_anl_txt.append(str(max_proc['pid']) + ' ' + max_proc['exe'])
        else:
            self.cr_anl_txt.append('No threat found!')

    @staticmethod
    def update_data(input_line, per_cpu):
        #  1.000418172 CPU1                40.462      r205
        #  1.000472956,CPU5,25933,,r105,1000277655,100,00,,
        input_line = input_line.decode('utf-8').strip()
        splitted = input_line.split(',')
        if per_cpu:
            cpu = int(splitted[1][-1])
            value = int(splitted[2])
            hpc = splitted[4]
            return cpu, value, hpc
        else:
            value = int(splitted[1])
            hpc = splitted[3]
            return value, hpc


class TracePidDialog(QtWidgets.QDialog):
    command_bgn = 'perf stat -e branches -e branch-misses -e cache-misses -e cache-references -e instructions -e cycles -p '
    command_end = ' -I 1000 -x ,'

    def __init__(self, parent=None, pid=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.pid = pid
        self.perf_command = TracePidDialog.command_bgn + str(self.pid) + TracePidDialog.command_end
        self.perf_handler = None

        self.layout = QtWidgets.QGridLayout(self)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)

        self.data_dict = {'branches': [], 'branch-misses': [], 'cache-references': [], 'cache-misses': [],
                          'instructions': [], 'cycles': []}

        self.curves_dict = {}

        self.instr_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')},
                                        title='Instructions Info')
        self.instr_plot.setXRange(0, 60)
        self.instr_plot.addLegend()
        self.curves_dict['instructions'] = self.instr_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0),
                                                                symbolPen='w', name='instructions')
        self.curves_dict['cycles'] = self.instr_plot.plot(pen=(200, 200, 200), symbolBrush=(0, 0, 255),
                                                          symbolPen='w', name='cycles')

        self.ipc_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')},
                                      title='Instructions Info')
        self.ipc_plot.setXRange(0, 60)
        self.ipc_plot.setYRange(0, 100)
        self.ipc_plot.addLegend()
        self.ipc_curve = self.ipc_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0),
                                            symbolPen='w', name='IPC')

        self.branch_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title='Branch Info')
        self.branch_plot.setXRange(0, 60)
        self.branch_plot.addLegend()
        self.curves_dict['branches'] = self.branch_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0),
                                                             symbolPen='w', name='branches')
        self.curves_dict['branch-misses'] = self.branch_plot.plot(pen=(200, 200, 200), symbolBrush=(0, 0, 255),
                                                                  symbolPen='w', name='branch-misses')

        self.caches_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title='Caches Info')
        self.caches_plot.setXRange(0, 60)
        self.caches_plot.addLegend()
        self.curves_dict['cache-references'] = self.caches_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0),
                                                                     symbolPen='w', name='cache-references')
        self.curves_dict['cache-misses'] = self.caches_plot.plot(pen=(200, 200, 200), symbolBrush=(0, 0, 255),
                                                                 symbolPen='w', name='cache-misses')

        self.layout.addWidget(self.instr_plot, 0, 0)
        self.layout.addWidget(self.ipc_plot, 0, 1)
        self.layout.addWidget(self.branch_plot, 1, 0)
        self.layout.addWidget(self.caches_plot, 1, 1)

        self.q = Queue()
        self.t = None
        self.init_tracing()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_from_perf)
        self.timer.start(1000)

    def init_tracing(self):
        self.perf_handler = psutil.Popen(self.perf_command, stderr=PIPE, shell=True)
        self.t = Thread(target=enqueue_output, args=(self.perf_handler.stderr, self.q))
        self.t.daemon = True  # thread dies with the program
        self.t.start()

    def read_from_perf(self):
        while True:
            try:
                if self.q:
                    line = self.q.get(timeout=.1)
                    line = line.decode('utf-8').strip()
                    if 'Error' in line:
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText('This process cannot be monitored!')
                        msg.setWindowTitle('Process Information')
                        msg.exec()
                        self.reject()
                        return

                    splitted = line.split(',')
                    val = splitted[1]
                    name = splitted[3]
                    if '<not counted>' not in val:
                        # self.text_edit.append(val + ' ' + name + '\n')
                        self.data_dict[name].insert(0, int(val))
                else:
                    break
            except Empty:
                self.update_plots()
                break

    def update_plots(self):
        for key, value in self.curves_dict.items():
            value.setData(self.data_dict[key])

        if len(self.data_dict['cycles']) == len(self.data_dict['instructions']):
            ipcs = [x / y * 100 for x, y in zip(self.data_dict['instructions'], self.data_dict['cycles'])]
            self.ipc_curve.setData(ipcs)


class CPUInfo:
    nr_of_cpues = psutil.cpu_count()

    def __init__(self):
        # setup cpu related
        self.cpu_plots_list = []
        self.cpu_plots_data_lists = []
        self.cpu_plots_curves_list = []
        self.cpu_p_bars_list = []
        self.qlabels_pbars = []

        for cpu in range(CPUInfo.nr_of_cpues):
            # setup real-time plots
            temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title='CPU ' + str(cpu))
            temp_plot.setYRange(0, 100)
            temp_plot.setXRange(0, 60)
            self.cpu_plots_list.append(temp_plot)
            self.cpu_plots_data_lists.append([])
            self.cpu_plots_curves_list.append(
                temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))

            # setup progress bars
            temp_p_bar = utils.CustomProgressBar()
            temp_p_bar.setOrientation(QtCore.Qt.Vertical)
            self.cpu_p_bars_list.append(temp_p_bar)

            self.qlabels_pbars.append(QtWidgets.QLabel())

            version_of_os = platform.uname().version
            self.version_label = QtWidgets.QLabel(version_of_os)
            self.version_label.setAlignment(QtCore.Qt.AlignCenter)
            self.gridLayout_cpu_plots = QtWidgets.QGridLayout()

    def integrate(self, wrapper):
        wrapper.verticalLayout_cpu_plots.addWidget(self.version_label)
        row = 0
        column = 0
        for temp_plot in self.cpu_plots_list:
            self.gridLayout_cpu_plots.addWidget(temp_plot, row, column)
            if column == 0:
                column += 1
            else:
                column -= 1
                row += 1
        wrapper.verticalLayout_cpu_plots.addLayout(self.gridLayout_cpu_plots)

        col = 0
        for temp_p_bar in self.cpu_p_bars_list:
            wrapper.gridLayout_cpu_pbars.addWidget(temp_p_bar, 1, col)
            col += 1

        col = 0
        for temp_qlabel in self.qlabels_pbars:
            wrapper.gridLayout_cpu_pbars.addWidget(temp_qlabel, 2, col)
            col += 1

        new_font = QtGui.QFont()
        new_font.setPointSize(8)
        for col in range(CPUInfo.nr_of_cpues):
            temp = QtWidgets.QLabel('CPU' + str(col))
            temp.setFont(new_font)
            wrapper.gridLayout_cpu_pbars.addWidget(temp, 0, col)

    def change_info(self, active_widget=False):
        cpu_perc_list = psutil.cpu_percent(interval=None, percpu=True)
        # self.cpu_plots_X_values.insert(0, time())
        for cpu_index in range(len(cpu_perc_list)):
            self.cpu_plots_data_lists[cpu_index].insert(0, cpu_perc_list[cpu_index])
            if active_widget:
                self.cpu_plots_curves_list[cpu_index].setData(y=self.cpu_plots_data_lists[cpu_index])
                self.cpu_p_bars_list[cpu_index].setValue(cpu_perc_list[cpu_index])
                self.qlabels_pbars[cpu_index].setText(str(cpu_perc_list[cpu_index]))
        return self.create_json(cpu_perc_list)

    @staticmethod
    def create_json(cpu_perc_list):
        temp_json = {}
        for cpu_idx in range(len(cpu_perc_list)):
            temp_json[cpu_idx] = str(cpu_perc_list[cpu_idx])
        return {'cpu_perc': temp_json}


class CPUExtraInfo:
    cpu_extra_info_dict = {'ctx_sw': 0, 'intr': 0, 'sw_intr': 0}

    def __init__(self):
        self.info_list = []
        self.p_bar_battery = utils.BatteryProgressBar()
        self.info_list.append(self.p_bar_battery)

        self.label_ctx_switches = QtWidgets.QLabel("Context Switches:")
        self.label_ctx_sw_per_sec = QtWidgets.QLabel("Context Switches per sec:")
        self.label_interrupts = QtWidgets.QLabel("Interrupts:")
        self.label_intr_per_sec = QtWidgets.QLabel("Interrupts per sec:")
        self.label_soft_interrupts = QtWidgets.QLabel("Soft Interrupts:")
        self.label_sw_intr_per_sec = QtWidgets.QLabel("Soft Interrupts per sec:")
        self.label_up_time = QtWidgets.QLabel("Up time:")
        self.up_time = datetime.now().replace(microsecond=0) - datetime.fromtimestamp(psutil.boot_time())

        self.extra_cpu_info = QtWidgets.QGroupBox("CPU extra information:")
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.label_ctx_switches)
        self.vbox.addWidget(self.label_ctx_sw_per_sec)
        self.vbox.addWidget(self.label_interrupts)
        self.vbox.addWidget(self.label_intr_per_sec)
        self.vbox.addWidget(self.label_soft_interrupts)
        self.vbox.addWidget(self.label_sw_intr_per_sec)
        self.vbox.addWidget(self.label_up_time)

        self.extra_cpu_info.setLayout(self.vbox)
        self.info_list.append(self.extra_cpu_info)

        self.just_temperature_list = []
        for cpu in range(psutil.cpu_count(logical=False)):
            temp_p_bar_temperature = utils.CustomProgressBar()
            self.info_list.append(temp_p_bar_temperature)
            self.just_temperature_list.append(temp_p_bar_temperature)

    def integrate(self, wrapper):
        for elem in self.info_list:
            wrapper.verticalLayout_cpu_extra_info.addWidget(elem)

    def change_info(self, active_widget=False):
        info_tuple = psutil.cpu_stats()
        temperature_tuples = psutil.sensors_temperatures()['coretemp']
        battery_tuple = psutil.sensors_battery()

        if active_widget:
            self.label_ctx_switches.setText("Context Switches: " + str(info_tuple.ctx_switches))
            self.label_ctx_sw_per_sec.setText \
                ("Context Switches per sec: " +
                 str(info_tuple.ctx_switches - CPUExtraInfo.cpu_extra_info_dict['ctx_sw']))

            self.label_interrupts.setText("Interrupts: " + str(info_tuple.interrupts))
            self.label_intr_per_sec.setText \
                ("Interrupts per sec:" +
                 str(info_tuple.interrupts - CPUExtraInfo.cpu_extra_info_dict['intr']))

            self.label_soft_interrupts.setText("Software Interrupts: " + str(info_tuple.soft_interrupts))
            self.label_sw_intr_per_sec.setText \
                ("Software Interrupts per sec: " +
                 str(info_tuple.soft_interrupts - CPUExtraInfo.cpu_extra_info_dict['sw_intr']))

            self.up_time = self.up_time + timedelta(0, 1)
            self.label_up_time.setText("Up Time: " + str(self.up_time))

            self.p_bar_battery.setValue(battery_tuple.percent)
            self.p_bar_battery.setFormat("Battery: " + str(round(battery_tuple.percent, 1)) + '%')

            temperature_tuples.pop(0)
            for index in range(len(temperature_tuples)):
                self.just_temperature_list[index].setValue(temperature_tuples[index].current)
                self.just_temperature_list[index].setFormat(
                    'Core ' + str(index) + ' temperature: ' + str(temperature_tuples[index].current) + '°C')

        CPUExtraInfo.cpu_extra_info_dict['ctx_sw'] = info_tuple.ctx_switches
        CPUExtraInfo.cpu_extra_info_dict['intr'] = info_tuple.interrupts
        CPUExtraInfo.cpu_extra_info_dict['sw_intr'] = info_tuple.soft_interrupts

        return self.create_json(info_tuple, temperature_tuples, battery_tuple)

    @staticmethod
    def create_json(info_tuple, temperature_tuples, battery_tuple):
        temp_json = {'ctx_switches': info_tuple.ctx_switches, 'intr': info_tuple.interrupts,
                     'sw_intr': info_tuple.soft_interrupts, 'battery': round(battery_tuple.percent, 1)}

        for index in range(len(temperature_tuples)):
            temp_json['temperature' + str(index)] = temperature_tuples[index].current

        return {'cpu_extra_info': temp_json}


class Users:
    users_dict = {}

    def __init__(self):
        self.header_labels = ['name', 'uid', 'gid', 'home directory', 'shell']
        self.treeview_users_info = QtWidgets.QTreeWidget()
        self.treeview_users_info.setHeaderLabels(self.header_labels)
        self.treeview_users_info.setSortingEnabled(True)

        users = pwd.getpwall()
        for user in users:
            temp_list = [user.pw_name, str(user.pw_uid), str(user.pw_gid), user.pw_dir, user.pw_shell]
            user_row = utils.ProcessTreeWidgetItem(self.treeview_users_info, temp_list)
            Users.users_dict[user.pw_uid] = user_row

    def integrate(self, wrapper):
        wrapper.verticalLayout_users.addWidget(self.treeview_users_info)

    def change_info(self, active_widget=False):
        now_users = pwd.getpwall()
        now_users_dict = {}
        for user in now_users:
            now_users_dict[user.pw_uid] = user

        now_users_uids = set(now_users_dict.keys())
        then_users_uids = set(Users.users_dict.keys())

        # add new users
        added_users_uids = now_users_uids - then_users_uids
        for user_id in added_users_uids:
            added_user = now_users_dict[user_id]
            temp_list = [added_user.pw_name, str(added_user.pw_uid), str(added_user.pw_gid), added_user.pw_dir,
                         added_user.pw_shell]
            user_row = utils.ProcessTreeWidgetItem(self.treeview_users_info, temp_list)
            Users.users_dict[user.pw_uid] = user_row

        # removed users
        removed_users_uids = then_users_uids - now_users_uids
        for user_id in removed_users_uids:
            current = Users.users_dict[user_id]
            if current.parent() is not None:
                current.parent().removeChild(current)
            else:
                self.treeview_users_info.takeTopLevelItem(
                    self.treeview_users_info.indexOfTopLevelItem(current))
            del Users.users_dict[user_id]


class MemoryInfo:
    def __init__(self):
        self.header_labels = ['device', 'mountpoint', 'fstype', 'opts']
        self.info_list = []
        self.disk_partitions = []
        self.disk_rows = {}

        self.p_bar_disk_space = QtWidgets.QProgressBar()
        self.label_disk_usage = QtWidgets.QLabel()

        self.treeview_disk_part_info = QtWidgets.QTreeWidget()
        self.treeview_disk_part_info.setHeaderLabels(self.header_labels)

        self.change_info(active_widget=True)

    def integrate(self, wrapper):
        wrapper.verticalLayout_memory_info.addWidget(self.treeview_disk_part_info)
        wrapper.verticalLayout_memory_info.addWidget(self.label_disk_usage)
        wrapper.verticalLayout_memory_info.addWidget(self.p_bar_disk_space)

    def change_info(self, active_widget=False):
        self.set_disk_usage()

        now_disks = set()
        for elem in psutil.disk_partitions():
            # example:
            # sdiskpart(device='/dev/sda1', mountpoint='/', fstype='ext4',
            # opts='rw,relatime,errors=remount-ro,stripe=32750,data=ordered')

            new_partition = elem._asdict()
            temp_list = [str(new_partition[elem]) if elem in new_partition else '' for elem in self.header_labels]

            if new_partition['device'] not in self.disk_rows.keys():
                temp_widget_item = QtWidgets.QTreeWidgetItem(self.treeview_disk_part_info, temp_list)
                self.disk_rows[new_partition['device']] = temp_widget_item
            else:
                temp_widget_item = self.disk_rows[new_partition['device']]
                for idx in range(len(temp_list)):
                    temp_widget_item.setText(idx, temp_list[idx])

            now_disks.add(new_partition['device'])

        for key, current in self.disk_rows.items():
            if key not in now_disks:
                if current.parent() is not None:
                    current.parent().removeChild(current)
                else:
                    self.treeview_disk_part_info.takeTopLevelItem(
                        self.treeview_disk_part_info.indexOfTopLevelItem(current))

    def set_disk_usage(self):
        current_disk_usage = psutil.disk_usage('/')
        total, used, free, percent = current_disk_usage
        self.p_bar_disk_space.setValue(int(percent))
        self.label_disk_usage.setText(
            'Disk usage: total=' + str(round(total / (1024 * 1024 * 1024), 2)) + ' GB' +
            '   used=' + str(round(used / (1024 * 1024 * 1024), 2)) + ' GB' +
            '   free=' + str(round(free / (1024 * 1024 * 1024), 2)) + ' GB')


class NetworkInfo:
    def __init__(self):
        self.net_con_headers = ['Fd', 'PID', 'IP', 'Port', 'Status']
        self.net_con_rows = {}
        self.treeview_net_con = QtWidgets.QTreeWidget()
        self.treeview_net_con.setHeaderLabels(self.net_con_headers)

        self.net_io_headers = ['Network Interface', 'Bytes sent', 'Bytes received', 'Packets sent', 'Packets sent',
                               'B sent/sec', 'B recv/ sec']
        self.net_io_rows = {}
        self.treeview_net_io_info = QtWidgets.QTreeWidget()
        self.treeview_net_io_info.setHeaderLabels(self.net_io_headers)
        self.treeview_net_io_info.setSortingEnabled(True)

        self.change_info(active_widget=True)

    def integrate(self, wrapper):
        wrapper.verticalLayout_network_info.addWidget(self.treeview_net_con)
        wrapper.verticalLayout_network_info.addWidget(self.treeview_net_io_info)

    def change_info(self, active_widget=False):
        self.set_net_connections()
        self.set_net_io_counters()

    def set_net_connections(self):
        now_net_con = set()
        actual_net_con = psutil.net_connections()
        for elem in actual_net_con:
            # example:
            # sconn(fd=97, family=<AddressFamily.AF_INET: 2>, type=<SocketKind.SOCK_STREAM: 1>,
            # laddr=addr(ip='0.0.0.0', port=57621), raddr=(), status='LISTEN', pid=13056)
            one_net_con = [str(elem.fd), str(elem.pid), str(elem.laddr.ip), str(elem.laddr.port), elem.status]

            key = elem.pid
            if key in self.net_con_rows:
                temp_net_con_row = self.net_con_rows[elem.pid]
                for idx in range(len(one_net_con)):
                    temp_net_con_row.setText(idx, one_net_con[idx])
            else:
                temp_widget_item = QtWidgets.QTreeWidgetItem(self.treeview_net_con, one_net_con)
                self.net_con_rows[key] = temp_widget_item

            now_net_con.add(key)

        # check for networks no longer available
        for key, current in self.net_con_rows.items():
            if key not in now_net_con:
                if current.parent() is not None:
                    current.parent().removeChild(current)
                else:
                    self.treeview_net_con.takeTopLevelItem(
                        self.treeview_net_con.indexOfTopLevelItem(current))

    def set_net_io_counters(self):
        now_net_io_counters = set()
        actual_net_io_counters = psutil.net_io_counters(pernic=True)
        for key, value in actual_net_io_counters.items():
            if key in self.net_io_rows:
                one_net_info = [key,
                                str(actual_net_io_counters[key].bytes_sent),
                                str(actual_net_io_counters[key].bytes_recv),
                                str(actual_net_io_counters[key].packets_sent),
                                str(actual_net_io_counters[key].packets_recv),

                                str(actual_net_io_counters[key].bytes_sent -
                                    int(self.net_io_rows[key].text(1))),

                                str((actual_net_io_counters[key].bytes_recv -
                                     int(self.net_io_rows[key].text(2))))]

                temp_net_io_row = self.net_io_rows[key]
                for idx in range(len(one_net_info)):
                    temp_net_io_row.setText(idx, one_net_info[idx])

                now_net_io_counters.add(key)

            else:
                one_net_info = []
                one_net_info.append(key),
                one_net_info.append(str(actual_net_io_counters[key].bytes_sent))
                one_net_info.append(str(actual_net_io_counters[key].bytes_recv))
                one_net_info.append(str(actual_net_io_counters[key].packets_sent))
                one_net_info.append(str(actual_net_io_counters[key].packets_recv))
                one_net_info.append('0')
                one_net_info.append('0')

                temp_widget_item = QtWidgets.QTreeWidgetItem(self.treeview_net_io_info, one_net_info)
                self.net_io_rows[key] = temp_widget_item

                now_net_io_counters.add(key)

        # check for networks no longer available
        for key, current in self.net_io_rows.items():
            if key not in now_net_io_counters:
                if current.parent() is not None:
                    current.parent().removeChild(current)
                else:
                    self.treeview_net_io_info.takeTopLevelItem(
                        self.treeview_net_io_info.indexOfTopLevelItem(current))


class ProcessesInfo:
    nr_of_cpues = psutil.cpu_count()

    def __init__(self):
        self.slider = QSlideSwitch()
        self.slider.setCheckable(True)
        self.slider.setMaximumHeight(100)
        self.slider.setMaximumWidth(100)
        self.slider_label = QtWidgets.QLabel('Tree mode:')
        self.slider_option_layout = QtWidgets.QHBoxLayout()
        self.slider_option_layout.addWidget(self.slider_label)
        self.slider_option_layout.addWidget(self.slider)


        self.header_labels = ['pid', 'ppid', 'username', 'exe', 'create_time', 'status', 'num_threads', 'cpu_percent',
                              'cpu_num', 'memory_info']
        self.treeview_processes_info = QtWidgets.QTreeWidget()
        self.treeview_processes_info.setHeaderLabels(self.header_labels)
        self.treeview_processes_info.setSortingEnabled(True)
        self.treeview_processes_info.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.treeview_processes_info_ppid = QtWidgets.QTreeWidget()
        self.treeview_processes_info_ppid.setHeaderLabels(self.header_labels)
        self.treeview_processes_info_ppid.setSortingEnabled(False)
        self.treeview_processes_info_ppid.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.trace_process_action = QtWidgets.QAction("Trace process", None)
        self.trace_process_action.triggered.connect(self.trace_proc)
        self.treeview_processes_info.addAction(self.trace_process_action)

        self.trace_process_action_ppid = QtWidgets.QAction("Trace process", None)
        self.trace_process_action_ppid.triggered.connect(self.trace_proc_ppid)
        self.treeview_processes_info_ppid.addAction(self.trace_process_action_ppid)

        self.kill_process_action = QtWidgets.QAction("Kill process", None)
        self.kill_process_action.triggered.connect(self.kill_proc)
        self.treeview_processes_info.addAction(self.kill_process_action)

        self.kill_process_action_ppid = QtWidgets.QAction("Kill process", None)
        self.kill_process_action_ppid.triggered.connect(self.kill_proc_ppid)
        self.treeview_processes_info_ppid.addAction(self.kill_process_action_ppid)

        self.processes_rows = {}
        self.processes_rows_ppid = {}
        self.change_info(active_widget=True)
        self.root_nodes = set()


    def integrate(self, wrapper):
        wrapper.verticalLayout_processes_info.addLayout(self.slider_option_layout)
        wrapper.verticalLayout_processes_info.addWidget(self.treeview_processes_info)
        wrapper.verticalLayout_processes_info.addWidget(self.treeview_processes_info_ppid)
        self.treeview_processes_info_ppid.setVisible(False)

    def change_info(self, active_widget=False):
        if self.slider.state:
            self.treeview_processes_info.setVisible(True)
            self.treeview_processes_info_ppid.setVisible(False)

            now_pids = set()
            for proc in psutil.process_iter(attrs=self.header_labels):
                proc_dict = proc.info
                # proc_dict['cpu_percent'] = proc_dict['cpu_percent']  # / ProcessesInfo.nr_of_cpues
                proc_dict['create_time'] = datetime.utcfromtimestamp(proc_dict['create_time']).strftime(
                    '%Y-%m-%d %H:%M:%S')
                proc_dict['memory_info'] = round(proc_dict['memory_info'].vms / (1024 * 1024), 2)
                temp_list = [str(proc_dict[elem]) for elem in self.header_labels]

                if active_widget:
                    if proc_dict['pid'] not in self.processes_rows.keys():
                        temp_widget_item = utils.ProcessTreeWidgetItem(self.treeview_processes_info, temp_list)
                        self.processes_rows[proc_dict['pid']] = temp_widget_item
                    else:
                        temp_widget_item = self.processes_rows[proc_dict['pid']]
                        for idx in range(len(temp_list)):
                            temp_widget_item.setText(idx, temp_list[idx])

                now_pids.add(proc_dict['pid'])

            if active_widget:
                for key, current in self.processes_rows.items():
                    if key not in now_pids:
                        if current.parent() is not None:
                            current.parent().removeChild(current)
                        else:
                            self.treeview_processes_info.takeTopLevelItem(
                                self.treeview_processes_info.indexOfTopLevelItem(current))
        else:
            self.create_ppid_tree(active_widget)

    def create_ppid_tree(self, active_widget):
        self.treeview_processes_info.setVisible(False)
        self.treeview_processes_info_ppid.setVisible(True)

        now_pids = set()

        for proc in psutil.process_iter(attrs=self.header_labels):
            proc_dict = proc.info
            proc_dict['create_time'] = datetime.utcfromtimestamp(proc_dict['create_time']).strftime(
                '%Y-%m-%d %H:%M:%S')
            proc_dict['memory_info'] = round(proc_dict['memory_info'].vms / (1024 * 1024), 2)
            temp_list = [str(proc_dict[elem]) for elem in self.header_labels]

            if active_widget:
                if proc_dict['pid'] not in self.processes_rows_ppid.keys():
                    temp_widget_item = utils.ProcessTreeWidgetItem(temp_list)

                    if proc_dict['ppid'] != 0:
                        self.processes_rows_ppid[proc_dict['ppid']].addChild(temp_widget_item)
                    else:
                        if proc_dict['pid'] not in self.root_nodes:
                            self.root_nodes.add(proc_dict['pid'])
                    self.processes_rows_ppid[proc_dict['pid']] = temp_widget_item
                else:
                    temp_widget_item = self.processes_rows_ppid[proc_dict['pid']]
                    for idx in range(len(temp_list)):
                        temp_widget_item.setText(idx, temp_list[idx])
            now_pids.add(proc_dict['pid'])

        for root_node in self.root_nodes:
            self.treeview_processes_info_ppid.addTopLevelItem(self.processes_rows_ppid[root_node])

        if active_widget:
            for key, current in self.processes_rows_ppid.items():
                if key not in now_pids:
                    if current.parent() is not None:
                        current.parent().removeChild(current)
                    else:
                        self.treeview_processes_info.takeTopLevelItem(
                            self.treeview_processes_info.indexOfTopLevelItem(current))

    def kill_proc(self):
        my_item = self.treeview_processes_info.currentItem()
        pid = int(my_item.text(0))
        try:
            p = psutil.Process(pid)
            p.terminate()
        except psutil.AccessDenied:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('This process cannot be terminated!')
            msg.setWindowTitle('Process Information')
            msg.exec()

    def trace_proc(self):
        my_item = self.treeview_processes_info.currentItem()
        pid = int(my_item.text(0))
        dialog = TracePidDialog(pid=pid)
        dialog.exec()

    def kill_proc_ppid(self):
        my_item = self.treeview_processes_info_ppid.currentItem()
        pid = int(my_item.text(0))
        try:
            p = psutil.Process(pid)
            p.terminate()
        except psutil.AccessDenied:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('This process cannot be terminated!')
            msg.setWindowTitle('Process Information')
            msg.exec()

    def trace_proc_ppid(self):
        my_item = self.treeview_processes_info_ppid.currentItem()
        pid = int(my_item.text(0))
        dialog = TracePidDialog(pid=pid)
        dialog.exec()

class HPCInfo:
    cpu_count = psutil.cpu_count()

    def __init__(self):
        self.hpc_counters = {}
        self.hpc_counters_keys = []

        self.get_hpc_thread = utils.GetHPCInfoThread()
        self.get_hpc_thread.finished_signal.connect(self.got_hpc)
        self.get_hpc_thread.start()

        self.hpc_data = []
        self.hpc_plots = []
        self.hpc_curves = []
        self.hpc_codes = {0: '', 1: '', 2: '', 3: ''}
        self.hpc_codes_new = {}

        self.hpc_record_button = QtWidgets.QPushButton()
        self.hpc_setup_comboboxes = []
        self.hpc_set_button = QtWidgets.QPushButton()
        self.hpc_details_text = QtWidgets.QTextEdit()
        self.gridLayout_hpc_info = QtWidgets.QGridLayout()
        self.hpc_verify_crypto_button = QtWidgets.QPushButton()

        self.init_hpc()

        self.perf_handler = None
        # self.textEdit_hpc = QtWidgets.QTextEdit()
        self.start_popen()
        self.q = Queue()
        self.t = None

        self.check = False

    def init_hpc(self):
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)

        for idx in range(4):
            temp_data_list = []
            temp_plots_list = []
            temp_curves_list = []
            for idx2 in range(HPCInfo.cpu_count):
                temp_data_list.append([])

                title = 'CPU ' + str(idx2) + ' - ' + self.hpc_codes[idx]
                temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')}, title=title)
                temp_plot.setSizePolicy(size_policy)
                temp_plot.setXRange(0, 60)
                temp_plots_list.append(temp_plot)
                temp_curves_list.append(temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))

            self.hpc_data.append(temp_data_list)
            self.hpc_plots.append(temp_plots_list)
            self.hpc_curves.append(temp_curves_list)

        # init ui elements for setup part of hpc
        self.hpc_record_button.setText('Record Mode')
        self.hpc_record_button.clicked.connect(self.select_record)
        self.hpc_set_button.setText('Set Counters')
        self.hpc_set_button.clicked.connect(self.update_perf)
        self.hpc_details_text.setReadOnly(True)
        for idx in range(4):
            temp = QtWidgets.QComboBox()
            self.hpc_setup_comboboxes.append(temp)
            temp.currentIndexChanged.connect(self.combo_selection_change)

        self.hpc_verify_crypto_button.setText('Crypto Analysis')
        self.hpc_verify_crypto_button.clicked.connect(self.crypto_anl)

    def start_popen(self):
        if self.perf_handler:
            self.perf_handler.kill()

        events_str = ''
        for key, val in self.hpc_codes.items():
            if val:
                events_str = events_str + '-e ' + val + ' '
                for plt_widget in self.hpc_plots[key]:
                    plt_widget.hide()
                    plt_widget.show()
            else:
                for plt_widget in self.hpc_plots[key]:
                    plt_widget.hide()
        if events_str:
            args = shlex.split('perf stat ' + events_str + '-I 1000 -a -A -x ,')
            # self.hpc_details_text.append(' '.join(args))
            self.perf_handler = psutil.Popen(args, stderr=PIPE)

            self.t = Thread(target=enqueue_output, args=(self.perf_handler.stderr, self.q))
            self.t.daemon = True  # thread dies with the program
            self.t.start()

    def integrate(self, wrapper):
        for i in range(HPCInfo.cpu_count):
            self.gridLayout_hpc_info.setRowMinimumHeight(i, 143)
        wrapper.scrollArea.setWidgetResizable(True)
        for column in range(len(self.hpc_plots)):
            for row in range(len(self.hpc_plots[0])):
                self.gridLayout_hpc_info.addWidget(self.hpc_plots[column][row], row, column)
        wrapper.scrollAreaWidgetContents.setLayout(self.gridLayout_hpc_info)

        wrapper.verticalLayout_hpc_config.addWidget(self.hpc_record_button)
        for elem in self.hpc_setup_comboboxes:
            wrapper.verticalLayout_hpc_config.addWidget(elem)
        wrapper.verticalLayout_hpc_config.addWidget(self.hpc_set_button)
        wrapper.verticalLayout_hpc_config.addWidget(self.hpc_details_text)
        wrapper.verticalLayout_hpc_config.addWidget(self.hpc_verify_crypto_button)

    def change_info(self, active_widget=False):
        temp_json = {}

        while True:
            try:
                if self.q:
                    # line = q.get_nowait()
                    line = self.q.get(timeout=.1)
                    # self.textEdit_hpc.append(line.decode('ascii'))
                    cpu, value, hpc = self.update_data(line)
                    temp_json[str(cpu) + '_' + hpc] = value
                else:
                    break
            except Empty:
                break

        if active_widget:
            self.update_curves()
        return {'hpc_info': temp_json}

    def update_data(self, input_line):
        #  1.000418172 CPU1                40.462      r205
        #  1.000472956,CPU5,25933,,r105,1000277655,100,00,,
        input_line = input_line.decode('ascii').strip()
        splitted = input_line.split(',')
        cpu = int(splitted[1][-1])
        value = int(splitted[2])
        hpc = splitted[4]

        for key, hpc_val in self.hpc_codes.items():
            if hpc in hpc_val:
                self.hpc_data[key][cpu].insert(0, value)

        return cpu, value, hpc

    def update_curves(self):
        for idx in range(4):
            for idx2 in range(HPCInfo.cpu_count):
                self.hpc_curves[idx][idx2].setData(y=self.hpc_data[idx][idx2])

    def got_hpc(self, hpc_cnts):
        self.hpc_counters = hpc_cnts
        self.hpc_counters_keys = [''] + list(hpc_cnts)
        for combo in self.hpc_setup_comboboxes:
            combo.addItems(self.hpc_counters_keys)

    def combo_selection_change(self, index):
        self.hpc_details_text.clear()
        # self.hpc_details_text.append('Current config:')

        self.hpc_codes_new = {}
        idx = 0
        for combo in self.hpc_setup_comboboxes:
            txt = combo.currentText()
            if txt:
                self.hpc_codes_new[idx] = self.get_code(txt)
            else:
                self.hpc_codes_new[idx] = ''
            idx += 1

        # self.hpc_details_text.append(str(self.hpc_codes_new))

        if index > 0:
            key_set = self.hpc_counters_keys[index]
            self.hpc_details_text.append(self.hpc_counters[key_set]['PublicDescription'])

    def get_code(self, txt):
        temp_json = self.hpc_counters[txt]
        return 'r' + temp_json['UMask'][2:] + temp_json['EventCode'][2:]

    def update_perf(self):
        smth_changed = False
        for new_elem_key, new_elem_val in self.hpc_codes_new.items():
            if self.hpc_codes[new_elem_key] == new_elem_val:
                continue
            else:
                smth_changed = True
                self.hpc_codes[new_elem_key] = new_elem_val
                self.hpc_data[new_elem_key] = []
                for idx in range(HPCInfo.cpu_count):
                    self.hpc_data[new_elem_key].append([])

        if smth_changed:
            self.start_popen()

    def select_record(self):
        if self.hpc_counters:
            if self.perf_handler:
                self.perf_handler.kill()
            dialog = HPCDialog(hpc_cnt=self.hpc_counters)
            dialog.exec()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('No Hardware Performance Counters available!')
            msg.setWindowTitle('Hardware Performance Counters Monitor')
            msg.exec()

    def crypto_anl(self):
        if self.perf_handler:
            self.perf_handler.kill()
        dialog = CryptoAnalysisDialog()
        dialog.exec()


class UIWrapped(Ui_MainWindow):

    def __init__(self):
        self.elements = {}
        self.f = open('info_file.txt', 'a')

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        self.elements[0] = CPUInfo()
        self.elements[1] = CPUExtraInfo()
        self.elements[2] = Users()
        self.elements[3] = MemoryInfo()
        self.elements[4] = NetworkInfo()
        self.elements[5] = ProcessesInfo()
        self.elements[6] = HPCInfo()

        self.integrate_all()

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

    def integrate_all(self):
        for key, elem in self.elements.items():
            elem.integrate(self)

    def update_all(self):
        current_index = self.tabWidget.currentIndex()
        info_json = {'t': int(time())}
        tabs = []
        for key, value in self.elements.items():
            if key != current_index:
                json_received = value.change_info()
            else:
                json_received = value.change_info(active_widget=True)

            if json_received:
                tabs.append(json_received)

        if tabs:
            info_json['tabs'] = tabs

        self.f.write(json.dumps(info_json))
        self.f.write('\n')

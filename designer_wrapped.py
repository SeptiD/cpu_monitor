from PyQt5 import QtCore, QtGui, QtWidgets
from designer import Ui_MainWindow
import pyqtgraph as pg
import utils
from time import time
from datetime import datetime
import psutil
import shlex
from subprocess import PIPE
import sys
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [datetime.utcfromtimestamp(value).strftime('%M:%S') for value in values]


class CPU_Extra_Info:
    def __init__(self):
        self.info_list = []
        self.p_bar_battery = utils.BatteryProgressBar()
        self.info_list.append(self.p_bar_battery)

        self.label_ctx_switches = QtWidgets.QLabel("Context Switches:")
        self.label_interrupts = QtWidgets.QLabel("Interrupts:")
        self.label_soft_interrupts = QtWidgets.QLabel("Soft Interrupts:")

        self.extra_cpu_info = QtWidgets.QGroupBox("CPU extra information:")
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.label_ctx_switches)
        self.vbox.addWidget(self.label_interrupts)
        self.vbox.addWidget(self.label_soft_interrupts)
        self.extra_cpu_info.setLayout(self.vbox)
        self.info_list.append(self.extra_cpu_info)

        self.just_temperature_list = []
        for cpu in range(psutil.cpu_count(logical=False)):
            temp_p_bar_temperature = utils.CustomProgressBar()
            self.info_list.append(temp_p_bar_temperature)
            self.just_temperature_list.append(temp_p_bar_temperature)

    def change_info(self):
        info_touple = psutil.cpu_stats()
        temperature_tuples = psutil.sensors_temperatures()['coretemp']
        battery_tuple = psutil.sensors_battery()

        self.label_ctx_switches.setText("Context Switches:" + str(info_touple.ctx_switches))
        self.label_interrupts.setText("Interrupts:" + str(info_touple.interrupts))
        self.label_soft_interrupts.setText("Software Interrupts:" + str(info_touple.soft_interrupts))

        self.p_bar_battery.setValue(battery_tuple.percent)
        self.p_bar_battery.setFormat("Battery: " + str(round(battery_tuple.percent, 1)) + '%')

        temperature_tuples.pop(0)
        for index in range(len(temperature_tuples)):
            self.just_temperature_list[index].setValue(temperature_tuples[index].current)
            self.just_temperature_list[index].setFormat(
                'Core ' + str(index) + ' temperature: ' + str(temperature_tuples[index].current) + '°C')


class Memory_Info:
    def __init__(self):
        self.header_labels = ['device', 'mountpoint', 'fstype', 'opts']
        self.info_list = []
        self.disk_partitions = []
        self.disk_rows = {}

        self.p_bar_diskspace = QtWidgets.QProgressBar()
        self.label_disk_usage = QtWidgets.QLabel()

        self.treeview_disk_part_info = QtWidgets.QTreeWidget()
        self.treeview_disk_part_info.setHeaderLabels(self.header_labels)

        self.change_info()

    def change_info(self):
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
        self.p_bar_diskspace.setValue(int(percent))
        self.label_disk_usage.setText(
            'Disk usage: total=' + str(round(total / (1024 * 1024 * 1024), 2)) + ' GB' +
            '   used=' + str(round(used / (1024 * 1024 * 1024), 2)) + ' GB' +
            '   free=' + str(round(free / (1024 * 1024 * 1024), 2)) + ' GB')


class Network_Info:
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

        self.change_info()

    def change_info(self):
        self.set_net_connections()
        self.set_net_io_counters()

    def set_net_connections(self):
        now_net_con = set()
        actual_net_con = psutil.net_connections()
        for elem in actual_net_con:
            # example:
            # sconn(fd=97, family=<AddressFamily.AF_INET: 2>, type=<SocketKind.SOCK_STREAM: 1>,
            # laddr=addr(ip='0.0.0.0', port=57621), raddr=(), status='LISTEN', pid=13056)
            one_net_con = []
            one_net_con.append(str(elem.fd))
            one_net_con.append(str(elem.pid))
            one_net_con.append(str(elem.laddr.ip))
            one_net_con.append(str(elem.laddr.port))
            one_net_con.append(elem.status)

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


class Processes_Info:
    nr_of_cpues = psutil.cpu_count()

    def __init__(self):
        self.header_labels = ['pid', 'ppid', 'username', 'exe', 'create_time', 'status', 'num_threads', 'cpu_percent',
                              'cpu_num', 'memory_info']
        self.treeview_processes_info = QtWidgets.QTreeWidget()
        self.treeview_processes_info.setHeaderLabels(self.header_labels)
        self.treeview_processes_info.setSortingEnabled(True)
        self.processes_rows = {}
        self.change_info()

    def change_info(self):
        now_pids = set()
        for proc in psutil.process_iter(attrs=self.header_labels):
            proc_dict = proc.info
            proc_dict['cpu_percent'] = proc_dict['cpu_percent'] / Processes_Info.nr_of_cpues
            proc_dict['create_time'] = datetime.utcfromtimestamp(proc_dict['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            proc_dict['memory_info'] = round(proc_dict['memory_info'].vms / (1024 * 1024), 2)
            temp_list = [str(proc_dict[elem]) for elem in self.header_labels]

            if proc_dict['pid'] not in self.processes_rows.keys():
                temp_widget_item = QtWidgets.QTreeWidgetItem(self.treeview_processes_info, temp_list)
                self.processes_rows[proc_dict['pid']] = temp_widget_item
            else:
                temp_widget_item = self.processes_rows[proc_dict['pid']]
                for idx in range(len(temp_list)):
                    temp_widget_item.setText(idx, temp_list[idx])

            now_pids.add(proc_dict['pid'])

        for key, current in self.processes_rows.items():
            if key not in now_pids:
                if current.parent() is not None:
                    current.parent().removeChild(current)
                else:
                    self.treeview_processes_info.takeTopLevelItem(
                        self.treeview_processes_info.indexOfTopLevelItem(current))


class CPU_Info:
    nr_of_cpues = psutil.cpu_count()

    def __init__(self):
        # setup cpu related
        self.cpu_plots_list = []
        self.cpu_plots_data_lists = []
        self.cpu_plots_curves_list = []
        self.cpu_p_bars_list = []
        for cpu in range(CPU_Info.nr_of_cpues):
            # setup real-time plots
            temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
            temp_plot.setYRange(0, 100)
            temp_plot.setXRange(0, 60)
            self.cpu_plots_list.append(temp_plot)
            self.cpu_plots_data_lists.append([])
            self.cpu_plots_curves_list.append(
                temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))

            # setup progress bars
            temp_p_bar = utils.CustomProgressBar()
            self.cpu_p_bars_list.append(temp_p_bar)

    def change_info(self):
        cpu_perc_list = psutil.cpu_percent(interval=None, percpu=True)
        # self.cpu_plots_X_values.insert(0, time())
        for cpu_index in range(len(cpu_perc_list)):
            self.cpu_plots_data_lists[cpu_index].insert(0, cpu_perc_list[cpu_index])
            self.cpu_plots_curves_list[cpu_index].setData(y=self.cpu_plots_data_lists[cpu_index])

            self.cpu_p_bars_list[cpu_index].setValue(cpu_perc_list[cpu_index])


class HPC_Info:
    cpu_count = psutil.cpu_count()

    def __init__(self):
        self.hpc_data = []
        self.hpc_plots = []
        self.hpc_curves = []

        self.init_hpc()
        self.hpc_codes = {0: 'r203', 1: 'r803', 2: 'r105', 3: 'r205'}

        self.perf_handler = None
        # self.textEdit_hpc = QtWidgets.QTextEdit()
        self.start_popen()
        self.q = Queue()
        t = Thread(target=enqueue_output, args=(self.perf_handler.stderr, self.q))
        t.daemon = True  # thread dies with the program
        t.start()

        self.check = False

    def init_hpc(self):
        for idx in range(4):
            temp_data_list = []
            temp_plots_list = []
            temp_curves_list = []
            for idx2 in range(HPC_Info.cpu_count):
                temp_data_list.append([])

                temp_plot = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
                temp_plot.setXRange(0, 60)
                temp_plots_list.append(temp_plot)
                temp_curves_list.append(temp_plot.plot(pen=(200, 200, 200), symbolBrush=(255, 0, 0), symbolPen='w'))

            self.hpc_data.append(temp_data_list)
            self.hpc_plots.append(temp_plots_list)
            self.hpc_curves.append(temp_curves_list)

    def start_popen(self):
        args = shlex.split('perf stat -e r203 -e r803 -e r105 -e r205 -I 1000 -a -A -x ,')
        self.perf_handler = psutil.Popen(args, stderr=PIPE)

    def change_info(self):
        # if not self.check:
        #     self.check = True
            # self.textEdit_hpc.append('-----------\n')

        while True:
            try:
                # line = q.get_nowait()
                line = self.q.get(timeout=.1)
                # self.textEdit_hpc.append(line.decode('ascii'))
                self.update_data(line)
            except Empty:
                break

        self.update_curves()

    def update_data(self, input_line):
        #  1.000418172 CPU1                40.462      r205
        #  1.000472956,CPU5,25933,,r105,1000277655,100,00,,
        input_line = input_line.decode('ascii').strip()
        splitted = input_line.split(',')
        cpu = int(splitted[1][-1])
        value = int(splitted[2])
        hpc = splitted[4]

        for key, hpc_val in self.hpc_codes.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
            if hpc in hpc_val:
                self.hpc_data[key][cpu].insert(0, value)

    def update_curves(self):
        for idx in range(4):
            for idx2 in range(HPC_Info.cpu_count):
                self.hpc_curves[idx][idx2].setData(y=self.hpc_data[idx][idx2])


class UI_Wrapped(Ui_MainWindow):
    combobox_system_info_options = ['CPU PERCENTAGE', 'CPU INFO', 'MEMORY', 'NETWORK', 'PROCESSES']

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.cpu_perc_info = CPU_Info()
        self.cpu_e_i = CPU_Extra_Info()
        self.mem_info = Memory_Info()
        self.net_info = Network_Info()
        self.proc_info = Processes_Info()
        self.hpc_info = HPC_Info()

        self.setup_combobox_system_info()
        self.setup_cpu_extra_percentages()
        self.setup_cpu_percentage()
        self.setup_memory_info()
        self.setup_net_info()
        self.setup_processes_info()
        self.setup_hpc_info()

    def setup_cpu_percentage(self):
        row = 0
        column = 0
        for temp_plot in self.cpu_perc_info.cpu_plots_list:
            self.gridLayout_cpu_plots.addWidget(temp_plot, row, column)
            if column == 0:
                column += 1
            else:
                column -= 1
                row += 1
        for temp_p_bar in self.cpu_perc_info.cpu_p_bars_list:
            self.verticalLayout_cpu_progress_bars.addWidget(temp_p_bar)

    def setup_cpu_extra_percentages(self):
        for elem in self.cpu_e_i.info_list:
            self.verticalLayout_cpu_extra_info.addWidget(elem)

    def setup_memory_info(self):
        self.verticalLayout_memory_info.addWidget(self.mem_info.treeview_disk_part_info)
        self.verticalLayout_memory_info.addWidget(self.mem_info.label_disk_usage)
        self.verticalLayout_memory_info.addWidget(self.mem_info.p_bar_diskspace)

    def setup_net_info(self):
        self.verticalLayout_network_info.addWidget(self.net_info.treeview_net_con)
        self.verticalLayout_network_info.addWidget(self.net_info.treeview_net_io_info)

    def setup_processes_info(self):
        self.verticalLayout_processes_info.addWidget(self.proc_info.treeview_processes_info)

    def setup_hpc_info(self):
        # self.verticalLayout_hpc.addWidget(self.hpc_info.textEdit_hpc)
        for column in range(len(self.hpc_info.hpc_plots)):
            for row in range(len(self.hpc_info.hpc_plots[0])):
                self.gridLayout_hpc_info.addWidget(self.hpc_info.hpc_plots[column][row], row, column)


    def setup_combobox_system_info(self):
        self.comboBox_system_info.addItems(UI_Wrapped.combobox_system_info_options)
        self.comboBox_system_info.activated[str].connect(self.combobox_system_info_selected)

    def combobox_system_info_selected(self, combo_text):
        self.textEdit.append(combo_text)
        pass

    def cpu_views_button_pushed(self):
        pass

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

    def update_cpu_perc(self):
        self.cpu_perc_info.change_info()

    def update_cpu_extra_info(self):
        self.cpu_e_i.change_info()

    def update_memory_info(self):
        self.mem_info.change_info()

    def update_net_info(self):
        self.net_info.change_info()

    def update_processes_info(self):
        self.proc_info.change_info()

    def update_hpc_info(self):
        self.hpc_info.change_info()

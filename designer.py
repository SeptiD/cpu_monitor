# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer2.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1091, 671)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 107, 511))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_options = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_options.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_options.setObjectName("verticalLayout_options")
        self.comboBox_system_info = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBox_system_info.setObjectName("comboBox_system_info")
        self.verticalLayout_options.addWidget(self.comboBox_system_info)
        self.button_cpu_views = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_cpu_views.setAutoDefault(False)
        self.button_cpu_views.setObjectName("button_cpu_views")
        self.verticalLayout_options.addWidget(self.button_cpu_views)
        self.pushButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_options.addWidget(self.pushButton)
        self.textEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.textEdit.setEnabled(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_options.addWidget(self.textEdit)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(120, 10, 951, 511))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_cpu_perc_plots = QtWidgets.QWidget()
        self.tab_cpu_perc_plots.setObjectName("tab_cpu_perc_plots")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab_cpu_perc_plots)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 941, 481))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_cpu_plots = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_cpu_plots.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_plots.setObjectName("verticalLayout_cpu_plots")
        self.tabWidget.addTab(self.tab_cpu_perc_plots, "")
        self.tab_cpu_per_bars = QtWidgets.QWidget()
        self.tab_cpu_per_bars.setObjectName("tab_cpu_per_bars")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.tab_cpu_per_bars)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 951, 481))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_cpu_progress_bars = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_cpu_progress_bars.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_progress_bars.setObjectName("verticalLayout_cpu_progress_bars")
        self.tabWidget.addTab(self.tab_cpu_per_bars, "")
        self.tab_extra_info = QtWidgets.QWidget()
        self.tab_extra_info.setObjectName("tab_extra_info")
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.tab_extra_info)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(0, 0, 951, 481))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_cpu_extra_info = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_cpu_extra_info.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_extra_info.setObjectName("verticalLayout_cpu_extra_info")
        self.tabWidget.addTab(self.tab_extra_info, "")
        self.tab_memory_info = QtWidgets.QWidget()
        self.tab_memory_info.setObjectName("tab_memory_info")
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.tab_memory_info)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(0, 0, 941, 481))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_memory_info = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_memory_info.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_memory_info.setObjectName("verticalLayout_memory_info")
        self.tabWidget.addTab(self.tab_memory_info, "")
        self.tab_net_info = QtWidgets.QWidget()
        self.tab_net_info.setObjectName("tab_net_info")
        self.verticalLayoutWidget_6 = QtWidgets.QWidget(self.tab_net_info)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(0, 0, 951, 481))
        self.verticalLayoutWidget_6.setObjectName("verticalLayoutWidget_6")
        self.verticalLayout_network_info = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_6)
        self.verticalLayout_network_info.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_network_info.setObjectName("verticalLayout_network_info")
        self.tabWidget.addTab(self.tab_net_info, "")
        self.tab_proc_info = QtWidgets.QWidget()
        self.tab_proc_info.setObjectName("tab_proc_info")
        self.verticalLayoutWidget_7 = QtWidgets.QWidget(self.tab_proc_info)
        self.verticalLayoutWidget_7.setGeometry(QtCore.QRect(0, 0, 951, 481))
        self.verticalLayoutWidget_7.setObjectName("verticalLayoutWidget_7")
        self.verticalLayout_processes_info = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_7)
        self.verticalLayout_processes_info.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_processes_info.setObjectName("verticalLayout_processes_info")
        self.tabWidget.addTab(self.tab_proc_info, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1091, 20))
        self.menuBar.setObjectName("menuBar")
        self.menufile = QtWidgets.QMenu(self.menuBar)
        self.menufile.setObjectName("menufile")
        MainWindow.setMenuBar(self.menuBar)
        self.actionFIl = QtWidgets.QAction(MainWindow)
        self.actionFIl.setObjectName("actionFIl")
        self.menufile.addSeparator()
        self.menuBar.addAction(self.menufile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CPU Monitor"))
        self.button_cpu_views.setText(_translate("MainWindow", "BARS"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_cpu_perc_plots), _translate("MainWindow", "CPU %"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_cpu_per_bars), _translate("MainWindow", "CPU % Bars"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_extra_info), _translate("MainWindow", "Extra Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_memory_info), _translate("MainWindow", "Memory Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_net_info), _translate("MainWindow", "Networks Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_proc_info), _translate("MainWindow", "Processes Info"))
        self.menufile.setTitle(_translate("MainWindow", "File"))
        self.actionFIl.setText(_translate("MainWindow", "FIl"))



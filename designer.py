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
        MainWindow.resize(1091, 597)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_cpu_perc_plots = QtWidgets.QWidget()
        self.tab_cpu_perc_plots.setObjectName("tab_cpu_perc_plots")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_cpu_perc_plots)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_cpu_pbars = QtWidgets.QGridLayout()
        self.gridLayout_cpu_pbars.setObjectName("gridLayout_cpu_pbars")
        self.horizontalLayout_2.addLayout(self.gridLayout_cpu_pbars)
        self.gridLayout_cpu_plots = QtWidgets.QGridLayout()
        self.gridLayout_cpu_plots.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_cpu_plots.setObjectName("gridLayout_cpu_plots")
        self.horizontalLayout_2.addLayout(self.gridLayout_cpu_plots)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        self.tabWidget.addTab(self.tab_cpu_perc_plots, "")
        self.tab_extra_info = QtWidgets.QWidget()
        self.tab_extra_info.setObjectName("tab_extra_info")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_extra_info)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_cpu_extra_info = QtWidgets.QVBoxLayout()
        self.verticalLayout_cpu_extra_info.setObjectName("verticalLayout_cpu_extra_info")
        self.verticalLayout_4.addLayout(self.verticalLayout_cpu_extra_info)
        self.tabWidget.addTab(self.tab_extra_info, "")
        self.tab_memory_info = QtWidgets.QWidget()
        self.tab_memory_info.setObjectName("tab_memory_info")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_memory_info)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_memory_info = QtWidgets.QVBoxLayout()
        self.verticalLayout_memory_info.setObjectName("verticalLayout_memory_info")
        self.verticalLayout.addLayout(self.verticalLayout_memory_info)
        self.tabWidget.addTab(self.tab_memory_info, "")
        self.tab_net_info = QtWidgets.QWidget()
        self.tab_net_info.setObjectName("tab_net_info")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_net_info)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_network_info = QtWidgets.QVBoxLayout()
        self.verticalLayout_network_info.setObjectName("verticalLayout_network_info")
        self.verticalLayout_5.addLayout(self.verticalLayout_network_info)
        self.tabWidget.addTab(self.tab_net_info, "")
        self.tab_proc_info = QtWidgets.QWidget()
        self.tab_proc_info.setObjectName("tab_proc_info")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_proc_info)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_processes_info = QtWidgets.QVBoxLayout()
        self.verticalLayout_processes_info.setObjectName("verticalLayout_processes_info")
        self.verticalLayout_6.addLayout(self.verticalLayout_processes_info)
        self.tabWidget.addTab(self.tab_proc_info, "")
        self.tab_hpc = QtWidgets.QWidget()
        self.tab_hpc.setObjectName("tab_hpc")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_hpc)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_hpc_config = QtWidgets.QVBoxLayout()
        self.verticalLayout_hpc_config.setObjectName("verticalLayout_hpc_config")
        self.horizontalLayout_3.addLayout(self.verticalLayout_hpc_config)
        self.gridLayout_hpc_info = QtWidgets.QGridLayout()
        self.gridLayout_hpc_info.setObjectName("gridLayout_hpc_info")
        self.horizontalLayout_3.addLayout(self.gridLayout_hpc_info)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 4)
        self.tabWidget.addTab(self.tab_hpc, "")
        self.horizontalLayout.addWidget(self.tabWidget)
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
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CPU Monitor"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_cpu_perc_plots), _translate("MainWindow", "CPU %"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_extra_info), _translate("MainWindow", "Extra Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_memory_info), _translate("MainWindow", "Memory Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_net_info), _translate("MainWindow", "Networks Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_proc_info), _translate("MainWindow", "Processes Info"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_hpc), _translate("MainWindow", "Hardware Performance Counters"))
        self.menufile.setTitle(_translate("MainWindow", "File"))
        self.actionFIl.setText(_translate("MainWindow", "FIl"))



# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1547, 918)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 107, 851))
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
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_options.addWidget(self.textEdit)
        self.frame_cpu_plots = QtWidgets.QFrame(self.centralwidget)
        self.frame_cpu_plots.setGeometry(QtCore.QRect(120, 10, 1411, 851))
        self.frame_cpu_plots.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_cpu_plots.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_cpu_plots.setObjectName("frame_cpu_plots")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.frame_cpu_plots)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(-1, -1, 1411, 851))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_cpu_plots = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_cpu_plots.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_plots.setObjectName("verticalLayout_cpu_plots")
        self.frame_progress_bars = QtWidgets.QFrame(self.centralwidget)
        self.frame_progress_bars.setGeometry(QtCore.QRect(120, 10, 1411, 851))
        self.frame_progress_bars.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_progress_bars.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_progress_bars.setObjectName("frame_progress_bars")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.frame_progress_bars)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(-1, -1, 1411, 851))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_cpu_progress_bars = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_cpu_progress_bars.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_progress_bars.setObjectName("verticalLayout_cpu_progress_bars")
        self.frame_cpu_extra_info = QtWidgets.QFrame(self.centralwidget)
        self.frame_cpu_extra_info.setGeometry(QtCore.QRect(119, 9, 1411, 851))
        self.frame_cpu_extra_info.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_cpu_extra_info.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_cpu_extra_info.setObjectName("frame_cpu_extra_info")
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.frame_cpu_extra_info)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(-1, 9, 1411, 841))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_cpu_extra_info = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_cpu_extra_info.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_cpu_extra_info.setObjectName("verticalLayout_cpu_extra_info")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1547, 20))
        self.menuBar.setObjectName("menuBar")
        self.menufile = QtWidgets.QMenu(self.menuBar)
        self.menufile.setObjectName("menufile")
        MainWindow.setMenuBar(self.menuBar)
        self.actionFIl = QtWidgets.QAction(MainWindow)
        self.actionFIl.setObjectName("actionFIl")
        self.menufile.addSeparator()
        self.menuBar.addAction(self.menufile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CPU Monitor"))
        self.button_cpu_views.setText(_translate("MainWindow", "BARS"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.menufile.setTitle(_translate("MainWindow", "File"))
        self.actionFIl.setText(_translate("MainWindow", "FIl"))



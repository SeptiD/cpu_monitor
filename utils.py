from PyQt5 import QtCore, QtGui, QtWidgets


class CustomProgressBar(QtWidgets.QProgressBar):
    th1 = 40
    th2 = 80

    def __init__(self, parent = None):
        # super.__init__(parent)
        QtWidgets.QProgressBar.__init__(self, parent)
        self.customPallete = QtGui.QPalette(self.palette())

    def setValue(self, value):
        QtGui.QProgressBar.setValue(self, value)
        # palette = QtGui.QPalette(self.palette())

        if value < CustomProgressBar.th1:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.blue))
        elif CustomProgressBar.th1 <= value < CustomProgressBar.th2:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.darkYellow))
        else:
            self.customPallete.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.red))
        self.setPalette(self.customPallete)

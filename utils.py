from PyQt5 import QtCore, QtGui, QtWidgets


class CustomProgressBar(QtGui.QProgressBar):
    th1 = 40
    th2 = 80

    def setValue(self, value):
        QtGui.QProgressBar.setValue(self, value)
        if value < 40:
            palette = QtGui.QPalette(self.palette())
            palette.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.blue))
        elif value >= 40 and value < 80:
            palette = QtGui.QPalette(self.palette())
            palette.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.darkYellow))
            self.setPalette(palette)
        else:
            palette = QtGui.QPalette(self.palette())
            palette.setColor(QtGui.QPalette.Highlight,
                             QtGui.QColor(QtCore.Qt.red))
            self.setPalette(palette)

import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi
from designer_wrapped import UI_Wrapped


app = QApplication(sys.argv)
ex = UI_Wrapped()
w = QMainWindow()
ex.setupUi(w)

w.show()
sys.exit(app.exec_())

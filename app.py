import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from designer_wrapped import UI_Wrapped
import psutil
from PyQt5 import QtCore
from argparse import ArgumentParser
import utils_anl


def handler_psutil():
    ex.update_all()


parser = ArgumentParser()
parser.add_argument('-a', '--crypto_anl', help='Just do the cryptomining risk analysis', action='store_true')
args = parser.parse_args()

if args.crypto_anl:
    utils_anl.crypto_anl()
else:
    app = QApplication(sys.argv)
    ex = UI_Wrapped()
    w = QMainWindow()
    ex.setupUi(w)

    w.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(handler_psutil)
    timer.start(1000)

    sys.exit(app.exec_())

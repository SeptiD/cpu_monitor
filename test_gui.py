from PyQt5 import QtGui  # (the example applies equally well to PySide)
import pyqtgraph as pg
import time
import psutil
import numpy as np

# Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

# Define a top-level widget to hold everything
w = QtGui.QWidget()

# Create some widgets to be placed inside
btn = QtGui.QPushButton('press me')
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
plot = pg.PlotWidget()
curve = plot.plot()
plot.setYRange(0, 100)
windowWidth = 500                       # width of the window displaying the curve
# create array that will contain the relevant time series
Xm = np.linspace(0, 0, windowWidth)
ptr = -windowWidth

# Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

# Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(text, 1, 0)   # text edit goes in middle-left
layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows
layout.setColumnStretch(0, 1)
layout.setColumnStretch(1, 4)
# Display the widget as a new window
w.show()

# Start the Qt event loop
app.exec_()

arr = []
while True:
    time.sleep(1)
#     arr.append(psutil.cpu_percent(interval=None))
    Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
    value = psutil.cpu_percent(interval=None)                # read line (single value) from the serial port
    Xm[-1] = float(value)                 # vector containing the instantaneous values      
    ptr += 1                              # update x position for displaying the curve
    curve.setData(Xm)                     # set the curve with this data
    curve.setPos(ptr, 0)                   # set x position in the graph to 0
    QtGui.QApplication.processEvents() 


# from PyQt5.QtWidgets import QApplication, QMainWindow
# import pyqtgraph as pg
# import sys

#         ex.groupBox.addWidget(pg.PlotWidget())
#         ex.groupBox.addWidget(pg.PlotWidget())


# app = QApplication(sys.argv)
# ex = Ui_MainWindow()
# w = QMainWindow()
# ex.setupUi(w)
# w.show()
# sys.exit(app.exec_())

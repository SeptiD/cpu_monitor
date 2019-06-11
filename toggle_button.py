from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QAbstractButton
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QLinearGradient, QGradient
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QEasingCurve
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtProperty, pyqtSlot


class QSlideSwitchPrivate(QObject):

    def __init__(self, q):
        QObject.__init__(self)

        self._position = 0
        self._sliderShape = QRectF()
        self._gradient = QLinearGradient()
        self._gradient.setSpread(QGradient.PadSpread)
        self._qPointer = q

        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setTargetObject(self)
        # self.animation.setPropertyName()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutExpo)

    def __del__(self):
        del self.animation

    @pyqtProperty(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self._qPointer.repaint()

    def drawSlider(self, painter):
        margin = 3
        r = self._qPointer.rect().adjusted(0, 0, -1, -1)
        dx = (r.width() - self._sliderShape.width()) * self._position
        sliderRect = self._sliderShape.translated(dx, 0)
        painter.setPen(Qt.NoPen)

        # basic settings
        shadow = self._qPointer.palette().color(QPalette.Dark)
        light = self._qPointer.palette().color(QPalette.Light)
        button = self._qPointer.palette().color(QPalette.Button)

        # draw background
        # draw outer background
        self._gradient.setColorAt(0, shadow.darker(130))
        self._gradient.setColorAt(1, light.darker(130))
        self._gradient.setStart(0, r.height())
        self._gradient.setFinalStop(0, 0)
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(r, 15, 15)

        # draw background
        # draw inner background
        self._gradient.setColorAt(0, shadow.darker(140))
        self._gradient.setColorAt(1, light.darker(160))
        self._gradient.setStart(0, 0)
        self._gradient.setFinalStop(0, r.height())
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(r.adjusted(margin, margin, -margin, -margin), 15, 15)

        # draw slider
        self._gradient.setColorAt(0, button.darker(130))
        self._gradient.setColorAt(1, button)

        # draw outer slider
        self._gradient.setStart(0, r.height())
        self._gradient.setFinalStop(0, 0)
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(sliderRect.adjusted(margin, margin, -margin, -margin), 10, 15)

        # draw inner slider
        self._gradient.setStart(0, 0)
        self._gradient.setFinalStop(0, r.height())
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(sliderRect.adjusted(2.5 * margin, 2.5 * margin, -2.5 * margin, - 2.5 * margin), 5, 15)

        # draw text
        if self.animation.state() == QPropertyAnimation.Running:
            return  # don't draw any text while animation is running

        font = self._qPointer.font()
        self._gradient.setColorAt(0, light)
        self._gradient.setColorAt(1, shadow)
        self._gradient.setStart(0, r.height() / 2.0 + font.pointSizeF())
        self._gradient.setFinalStop(0, r.height() / 2.0 - font.pointSizeF())
        painter.setFont(font)
        painter.setPen(QPen(QBrush(self._gradient), 0))

        if self._qPointer.isChecked():
            painter.drawText(0, 0, r.width() / 2, r.height() - 1, Qt.AlignCenter, "ON")
        else:
            painter.drawText(r.width() / 2, 0, r.width() / 2, r.height() - 1, Qt.AlignCenter, "OFF")

    def updateSliderRect(self, size):
        self._sliderShape.setWidth(size.width() / 2.0)
        self._sliderShape.setHeight(size.height() - 1.0)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked):
        self.animation.setDirection(QPropertyAnimation.Forward if checked else QPropertyAnimation.Backward)
        self.animation.start()


class QSlideSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super(QAbstractButton, self).__init__(parent)

        self.d_ptr = QSlideSwitchPrivate(self)
        self.clicked.connect(self.d_ptr.animate)
        self.d_ptr.animation.finished.connect(self.update)

        self.state = True
        self.cnt = 0

    def __del__(self):
        del self.d_ptr

    def sizeHint(self):
        return QSize(48, 28)

    def hitButton(self, point):
        self.cnt += 1
        if self.cnt == 2:
            self.state = not self.state
            self.cnt = 0
        return self.rect().contains(point)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.d_ptr.drawSlider(painter)

    def resizeEvent(self, event):
        self.d_ptr.updateSliderRect(event.size())
        self.repaint()


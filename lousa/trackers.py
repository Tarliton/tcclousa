#Copyright (C) 2014, 2015  Tarliton Godoy
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QWidget, QSlider, QLabel, QVBoxLayout

class Trackers(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.v_layout = QVBoxLayout()

        self.hSliderMin = QSlider()
        self.hSliderMin.setOrientation(Qt.Horizontal)
        self.hLabelMin = QLabel('H min: 0')
        self.hSliderMin.setMinimum(0)
        self.hSliderMin.setMaximum(179)

        self.hSliderMax = QSlider()
        self.hSliderMax.setOrientation(Qt.Horizontal)
        self.hLabelMax = QLabel('H max: 0')
        self.hSliderMax.setMinimum(0)
        self.hSliderMax.setMaximum(179)

        self.sSliderMin = QSlider()
        self.sSliderMin.setOrientation(Qt.Horizontal)
        self.sLabelMin = QLabel('S min: 0')
        self.sSliderMin.setMinimum(0)
        self.sSliderMin.setMaximum(255)

        self.sSliderMax = QSlider()
        self.sSliderMax.setOrientation(Qt.Horizontal)
        self.sLabelMax = QLabel('S max: 0')
        self.sSliderMax.setMinimum(0)
        self.sSliderMax.setMaximum(255)

        self.vSliderMin = QSlider()
        self.vSliderMin.setOrientation(Qt.Horizontal)
        self.vLabelMin = QLabel('V min: 0')
        self.vSliderMin.setMinimum(0)
        self.vSliderMin.setMaximum(255)

        self.vSliderMax = QSlider()
        self.vSliderMax.setOrientation(Qt.Horizontal)
        self.vLabelMax = QLabel('V max: 0')
        self.vSliderMax.setMinimum(0)
        self.vSliderMax.setMaximum(255)

        self.v_layout.addWidget(self.hLabelMin)
        self.v_layout.addWidget(self.hSliderMin)
        self.v_layout.addWidget(self.hLabelMax)
        self.v_layout.addWidget(self.hSliderMax)

        self.v_layout.addWidget(self.sLabelMin)
        self.v_layout.addWidget(self.sSliderMin)
        self.v_layout.addWidget(self.sLabelMax)
        self.v_layout.addWidget(self.sSliderMax)

        self.v_layout.addWidget(self.vLabelMin)
        self.v_layout.addWidget(self.vSliderMin)
        self.v_layout.addWidget(self.vLabelMax)
        self.v_layout.addWidget(self.vSliderMax)

        self.setLayout(self.v_layout)

        self.hSliderMin.valueChanged.connect(self.slider_movedHmin)
        self.sSliderMin.valueChanged.connect(self.slider_movedSmin)
        self.vSliderMin.valueChanged.connect(self.slider_movedVmin)
        self.hSliderMax.valueChanged.connect(self.slider_movedHmax)
        self.sSliderMax.valueChanged.connect(self.slider_movedSmax)
        self.vSliderMax.valueChanged.connect(self.slider_movedVmax)

    def keyPressEvent(self, event):
        if event.key()==Qt.Key_Right:
            self.slider.setValue(self.slider.value() + 1)
        elif event.key()==Qt.Key_Left:
            self.slider.setValue(self.slider.value() - 1)
        else:
            QWidget.keyPressEvent(self, event)

    def slider_movedHmin(self, position):
        self.hLabelMin.setText('H min: %d' % position)
    def slider_movedSmin(self, position):
        self.sLabelMin.setText('S min: %d' % position)
    def slider_movedVmin(self, position):
        self.vLabelMin.setText('V min: %d' % position)
    def slider_movedHmax(self, position):
        self.hLabelMax.setText('H max: %d' % position)
    def slider_movedSmax(self, position):
        self.sLabelMax.setText('S max: %d' % position)
    def slider_movedVmax(self, position):
        self.vLabelMax.setText('V max: %d' % position)


if __name__ == '__main__':
  app = QApplication(sys.argv)

  widget = Trackers()
  widget.show()

  sys.exit(app.exec_())
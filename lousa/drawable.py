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

from PyQt4 import QtCore, QtGui

class ScribbleArea(QtGui.QWidget):
    
    def __init__(self, size, parent=None):
        super(ScribbleArea, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 5
        self.myPenColor = QtGui.QColor(255, 0, 0, 255)
        self.erase = False
        self.image = []
        self.lastPoint = QtCore.QPoint()
        self.pos = 0
        self.pressed = False
        self.pressedx = -1
        self.pressedy = -1
        self.visible = False
        self.drawings = []
        self.curPos = 0
        self.IMAGE_WIDTH = size.width()
        self.IMAGE_HEIGHT = size.height()
        self.can_draw = False

    def addPage(self):
        self.image.append(QtGui.QImage(QtCore.QSize(self.IMAGE_WIDTH, self.IMAGE_HEIGHT), QtGui.QImage.Format_ARGB32_Premultiplied))
        self.image[len(self.image)-1].fill(QtGui.qRgba(0, 0, 0, 0))

    def advance(self):
        self.pos = self.pos + 1

    def back(self):
        self.pos = self.pos - 1

    def setErasing(self, case):
        self.erase = case

    def setDrawing(self, case):
        self.can_draw = case

    def setPenColor(self, newColor):
        newQtColor = QtGui.QColor(255*float(newColor[0]), 255*float(newColor[1]), 255*float(newColor[2]), 255*float(newColor[3]))
        self.myPenColor = newQtColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = float(newWidth)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.can_draw:
            relPoint = QtCore.QPoint(event.pos().x()*1.0/self.size().width()*self.IMAGE_WIDTH, event.pos().y()*1.0/self.size().height()*self.IMAGE_HEIGHT)
            self.lastPoint = relPoint
            self.scribbling = True
            painter = QtGui.QPainter(self.image[self.pos])
            if (self.erase):
                rad = self.myPenWidth / 2 + 2
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
                painter.fillRect(QtCore.QRect(relPoint, relPoint).normalized().adjusted(-rad, -rad, +rad, +rad),QtCore.Qt.transparent)
            else:
                painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                    QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                painter.drawPoint(relPoint)
            
        self.repaint()

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            relPoint = QtCore.QPoint(event.pos().x()*1.0/self.size().width()*self.IMAGE_WIDTH, event.pos().y()*1.0/self.size().height()*self.IMAGE_HEIGHT)
            self.drawLineTo(relPoint)
            self.repaint()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            relPoint = QtCore.QPoint(event.pos().x()*1.0/self.size().width()*self.IMAGE_WIDTH, event.pos().y()*1.0/self.size().height()*self.IMAGE_HEIGHT)
            self.drawLineTo(relPoint)
            self.scribbling = False
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if (len(self.image)>0):
            painter.drawImage(event.rect(), self.image[self.pos])

    def resizeEvent(self, event):
        if (len(self.image)>0):
            self.resizeImage(self.image[self.pos])
            self.update()

    def drawLineTo(self, endPoint):
        if (len(self.image)>0):
            painter = QtGui.QPainter(self.image[self.pos])
            if (self.erase):
                rad = self.myPenWidth / 2 + 2
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
                painter.fillRect(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad),QtCore.Qt.transparent)
            else:
                painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                    QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                painter.drawLine(self.lastPoint, endPoint)
            self.modified = True

            rad = self.myPenWidth / 2 + 2
            self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
            self.lastPoint = QtCore.QPoint(endPoint)

    def resizeImage(self, image):
        if image.isNull():
            return
        newImage = image.scaled(image.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image[self.pos] = newImage

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth

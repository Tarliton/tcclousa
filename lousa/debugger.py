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
import cv2
from pymouse import PyMouse
import numpy as np
import qimage2ndarray
import trackers

class ClickedArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ClickedArea, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.pos_click = 1
        self.cantos = np.ndarray((4, 1, 2), buffer=np.array([0, 0, 0, 0, 0, 0, 0, 0]), dtype=np.float32)
        self.calibrated = False
        self.clickPosition = [-1, -1]
        self.sent = False

    def gotPosition(self):
        self.sent = True

    def getClickedPos(self):
        return not self.sent, self.clickPosition

    def get_cantos(self):
        return self.cantos

    def is_calibrated(self):
        return self.calibrated

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            relPoint = QtCore.QPoint(event.pos().x()*1.0/self.size().width()*640.0, event.pos().y()*1.0/self.size().height()*480.0)
            self.clickPosition = [relPoint.x(),relPoint.y()]
            self.sent = False

        if event.button() == QtCore.Qt.RightButton:
            relPoint = QtCore.QPoint(event.pos().x()*1.0/self.size().width()*640.0, event.pos().y()*1.0/self.size().height()*480.0)
            if (self.pos_click != 5):
                if (self.pos_click == 1):
                    self.cantos[0, 0, 0] = relPoint.x()
                    self.cantos[0, 0, 1] = relPoint.y()
                elif (self.pos_click == 2):
                    self.cantos[1, 0, 0] = relPoint.x()
                    self.cantos[1, 0, 1] = relPoint.y()
                elif (self.pos_click == 3):
                    self.cantos[2, 0, 0] = relPoint.x()
                    self.cantos[2, 0, 1] = relPoint.y()
                elif (self.pos_click == 4):
                    self.cantos[3, 0, 0] = relPoint.x()
                    self.cantos[3, 0, 1] = relPoint.y()
                    self.calibrated = True
                self.pos_click = self.pos_click + 1
                print self.cantos
            else:
                print 'recalibrando...'
                self.calibrated = False
                self.pos_click = 1
                self.cantos = np.ndarray((4, 1, 2), buffer=np.array([0, 0, 0, 0, 0, 0, 0, 0]), dtype=np.float32)


class Debugger(QtGui.QMainWindow):
    def __init__(self):
        super(Debugger, self).__init__()
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setMinimumSize(240, 160)

        self.originalPixmap = None

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setCentralWidget(self.scrollArea)


        self.setWindowTitle("Debugger")
        
        self.setup_camera()

        self.mouse = PyMouse()
        self.element1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        self.element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        
        self.lou = np.zeros((480, 640, 3), np.uint8)
        self.nova_lou = np.zeros((480, 640, 3), np.uint8)
        self.HSV = [0,0,0]
        self.activated = False
        self.clickedArea = ClickedArea(self.centralWidget())
        self.resize(self.geometry().width()+10, self.geometry().height()+10)
        self.only_one = False
        self.pressed = False
        self.mostra = 1
        self.HSV = [0,0,0]

        self.current_frame = None
        self.next_frame = None
        self.prev_frame = None
        self.first_frame = False

        self.tracker = trackers.Trackers()
        self.tracker.hSliderMin.setValue(40)
        self.tracker.sSliderMin.setValue(130)
        self.tracker.vSliderMin.setValue(130)
        self.tracker.hSliderMax.setValue(90)
        self.tracker.sSliderMax.setValue(255)
        self.tracker.vSliderMax.setValue(255)
        self.tracker.show()

    def setup_camera(self):
        self.capture = cv2.VideoCapture(0)
 
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(30)

    def keyPressEvent(self, event):
        if (type(event) == QtGui.QKeyEvent and (event.key() == QtCore.Qt.Key_1 or event.key() == 
        QtCore.Qt.Key_2 or event.key() == QtCore.Qt.Key_3 or event.key() == QtCore.Qt.Key_4 or event.key() == QtCore.Qt.Key_5 or
        event.key() == QtCore.Qt.Key_6 or event.key() == QtCore.Qt.Key_7 or event.key() == QtCore.Qt.Key_8
        or event.key() == QtCore.Qt.Key_9 or event.key() == QtCore.Qt.Key_0)):
            print event.key()
            self.mostra = event.key()

    def stop_timer(self):
        self.timer.stop()

    def start_timer(self):
        self.timer.start(30)
 

    def cv2Qt(self, frame):
        if (len(frame.shape)==3):
            frame = cv2.cvtColor(frame, cv2.cv.CV_BGR2RGB)
            image = QtGui.QImage(frame, frame.shape[1], frame.shape[0], 
                           frame.strides[0], QtGui.QImage.Format_RGB888)
        else:
            image = qimage2ndarray.array2qimage(frame, normalize =True)
        
        self.showImage(image)

    def display_video_stream(self):
        self.prev_frame = self.current_frame
        self.current_frame = self.next_frame
        ret, self.next_frame = self.capture.read()
        if (not ret):
            self.next_frame = np.zeros((480, 640, 3), np.uint8)
        if (not self.first_frame):
            self.prev_frame = self.next_frame
            self.current_frame = self.next_frame
            self.first_frame = True
        self.detector(self.next_frame)
        
    def resizeEvent(self, event):
        if (self.originalPixmap):
            scaledSize = self.originalPixmap.size()
            scaledSize.scale(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio)

            self.clickedArea.resize(scaledSize)
            xLong = self.imageLabel.size().width()
            yLong = self.imageLabel.size().height()
            self.clickedArea.move(xLong/2-self.clickedArea.size().width()/2, yLong/2-self.clickedArea.size().height()/2)

            if not self.imageLabel.pixmap() or scaledSize != self.imageLabel.pixmap().size():
                self.updateScreenshotLabel()

    def updateScreenshotLabel(self):
        self.imageLabel.setPixmap(self.originalPixmap.scaled(
                self.imageLabel.size(), QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))

    def showImage(self, image):
        self.originalPixmap = QtGui.QPixmap.fromImage(QtGui.QImage(image))
        if (not self.only_one):
            self.resize(self.geometry().width()+10, self.geometry().height()+10)
            self.only_one=True
        self.updateScreenshotLabel()

    def detect(self, mask):
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.visible = False
        maiorarea = 0
        currentx = 0
        currenty = 0
        dh = 0
        dw = 0
        center = (0,0)
        radius = 1
        maior_radius = 0
        best_center = (0,0)
        best_radius = 0
        for i in range(0, len(contours)):
            cnt = contours[i]
            (x,y),radius = cv2.minEnclosingCircle(cnt)
            center = (int(x),int(y))
            radius = int(radius)
            x, y, w, h = cv2.boundingRect(cnt)
            cordx = abs(x - (x + w))
            cordy = abs(y - (y + h))
            area = cordx * cordy
            if radius > maior_radius:
                best_radius = radius
                best_center = center
                maior_radius = radius
            if area > maiorarea:
                currentx = x
                currenty = y
                dw = w
                dh = h
                maiorarea = area
                self.visible = True
        if (self.mostra == QtCore.Qt.Key_6):
            self.cv2Qt(mask)
        if self.visible:
            print currentx, currenty
            if self.activated:
                #self.mouse.move(currentx/640.0*1920.0, currenty/480.0*1080.0)
                self.mouse.press(currentx/640.0*1920.0, currenty/480.0*1080.0)
            self.pressed = True
            self.pressedx = currentx/640.0*1920.0
            self.pressedy = currenty/480.0*1080.0
        else:
            if self.pressed and self.activated:
                self.mouse.release(self.pressedx, self.pressedy)
                self.pressed = False
        return currentx, currenty, dw, dh, best_center, best_radius


    def perspecTransform(self, src):
        aproximado = cv2.approxPolyDP(self.clickedArea.get_cantos(), cv2.arcLength(self.clickedArea.get_cantos(), True) * 0.2, True)
        newSrc=None
        if aproximado.size != 4:
            return newSrc
        else:
            novos_cantos = np.ndarray((4, 1, 2), buffer=np.array([0, 0, 640, 0, 640, 480, 0, 480]), dtype=np.float32)
            novos_cantos[0, 0, 0] = 0
            novos_cantos[0, 0, 1] = 0
            novos_cantos[1, 0, 0] = 640
            novos_cantos[1, 0, 1] = 0
            novos_cantos[2, 0, 0] = 640
            novos_cantos[2, 0, 1] = 480
            novos_cantos[3, 0, 0] = 0
            novos_cantos[3, 0, 1] = 480
            trans = cv2.getPerspectiveTransform(self.clickedArea.get_cantos(), novos_cantos)
            newSrc = cv2.warpPerspective(src, trans, (640, 480))
            return newSrc

    def findMotion(self, src):
        d1 = cv2.absdiff(self.prev_frame, src)
        d2 = cv2.absdiff(src, self.current_frame)
        result = cv2.bitwise_and(d1, d2)
        result = cv2.cvtColor(result, cv2.cv.CV_BGR2GRAY)
        ret, motion = cv2.threshold(result, 0, 255, cv2.cv.CV_THRESH_BINARY+cv2.cv.CV_THRESH_OTSU)
        if (ret == 1.0):
            return np.zeros((480, 640), np.uint8)
        return motion

    def mudaHSV(self, src):
        mudar, position = self.clickedArea.getClickedPos()
        if (mudar and position[0]!=-1 and position[1]!=-1):
            hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
            self.clickedArea.gotPosition()
            hsv_color = hsv[position[1]][position[0]]
            self.HSV[0] = hsv_color[0]
            self.HSV[1] = hsv_color[1]
            self.HSV[2] = hsv_color[2]
            self.tracker.hSliderMin.setValue(self.HSV[0])
            self.tracker.sSliderMin.setValue(self.HSV[1])
            self.tracker.vSliderMin.setValue(self.HSV[2])
            self.tracker.hSliderMax.setValue(self.HSV[0])
            self.tracker.sSliderMax.setValue(self.HSV[1])
            self.tracker.vSliderMax.setValue(self.HSV[2])
            print self.HSV


    def detector(self, src):
        self.cv2Qt(src)
        if (self.clickedArea.is_calibrated()):
            self.mudaHSV(src)
            persp_src = self.perspecTransform(src)
            if (self.mostra == QtCore.Qt.Key_2):
                self.cv2Qt(persp_src)

            hsv = cv2.cvtColor(persp_src, cv2.COLOR_BGR2HSV)

            if (self.mostra == QtCore.Qt.Key_3):
                self.cv2Qt(hsv)
            
            min_color = np.array([self.tracker.hSliderMin.value(), self.tracker.sSliderMin.value(), self.tracker.vSliderMin.value()])
            max_color = np.array([self.tracker.hSliderMax.value(), self.tracker.sSliderMax.value(), self.tracker.vSliderMax.value()])
            mask = cv2.inRange(hsv, min_color, max_color)

            if (self.mostra == QtCore.Qt.Key_4):
                self.cv2Qt(mask)
            dx, dy, dw, dh, center, radius = self.detect(mask)
            if (self.mostra == QtCore.Qt.Key_5):
                cv2.rectangle(persp_src,(dx,dy),(dx+dw,dy+dh),(0,255,0),2)
                print center, radius
                cv2.circle(persp_src,center,radius,(0,255,0),2)
                self.cv2Qt(persp_src)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    debug = Debugger()
    debug.show()
    sys.exit(app.exec_())

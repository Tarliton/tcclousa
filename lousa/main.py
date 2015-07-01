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
import popplerqt4
import drawable
import debugger
import server

class Lousa(QtGui.QMainWindow):
    def __init__(self):
        super(Lousa, self).__init__()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color:black;")

        self.doc = None
        self.sheets = []

        self.pageNumber = 0
        self.numberOfPages = 0
        self.DRAW_SIZE = QtCore.QSize(1280, 720)

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

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Lousa")
        self.resize(500, 400)
        self.fitToWindowAct.setEnabled(True)
        self.overlay = drawable.ScribbleArea(self.DRAW_SIZE, self.centralWidget())

        self.thread = server.Server()
        self.connect(self.thread, QtCore.SIGNAL("message(QString)"), self.handleMessage)
        self.thread.start()

    def handleMessage(self, message):
        print 'message: '+ message
        message = str(message)
        if 'advance' in message:
            self.advance()
        elif 'back' in message:
            self.back()
        elif 'color' in message:
            message = message[7:]
            message = message.split(',')
            self.overlay.setPenColor(message)
        elif 'pen' in message:
            message = message[5:]
            self.activatePen(message=='down')
            self.overlay.setDrawing(message=='down')
        elif 'erase' in message:
            message = message[7:]
            self.overlay.setErasing(message=='down')
        elif 'tam' in message:
            message = message[5:]
            self.overlay.setPenWidth(message)
            pass

    def closeEvent(self, event):
        self.setAttribute(QtCore.Qt.WA_TintedBackground)
        self.setStyleSheet("background-color:solid;")
        debug.stop_timer()
        reply = QtGui.QMessageBox.question(self, 'Mensagem',
            "Tem certeza que deseja fechar?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            app.quit()
        else:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setStyleSheet("background-color:black;")
            debug.start_timer()
            event.ignore()

    def resizeEvent(self, event):
        if (self.originalPixmap):
            scaledSize = self.originalPixmap.size()
            scaledSize.scale(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio)
            fitToWindow = self.fitToWindowAct.isChecked()
            if (fitToWindow):
                self.overlay.resize(self.imageLabel.size())
            else:
                self.overlay.resize(scaledSize)
            xLong = self.imageLabel.size().width()
            yLong = self.imageLabel.size().height()
            self.overlay.move(xLong/2-self.overlay.size().width()/2, yLong/2-self.overlay.size().height()/2)

            if not self.imageLabel.pixmap() or scaledSize != self.imageLabel.pixmap().size():
                self.updateScreenshotLabel()

    def updateScreenshotLabel(self):
        self.imageLabel.setPixmap(self.originalPixmap.scaled(
                self.imageLabel.size(), QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))

    def open(self):
        debug.stop_timer()
        del self.sheets[:]
        self.pageNumber = 0
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Abrir arquivo", QtCore.QDir.currentPath()+'/media')
        if fileName:
            image = QtGui.QImage(fileName)

            self.doc = popplerqt4.Poppler.Document.load(fileName)
            self.doc.setRenderHint(popplerqt4.Poppler.Document.Antialiasing)
            self.doc.setRenderHint(popplerqt4.Poppler.Document.TextAntialiasing)
            self.numberOfPages = self.doc.numPages()
            for i in range(self.numberOfPages):
                page = self.doc.page(i)
                image = page.renderToImage(150, 150)
                if image.isNull():
                    QtGui.QMessageBox.information(self, "Lousa", "Arquivo nao suportado %s." % fileName)
                    return
                self.sheets.append(image)
                self.overlay.addPage()

            self.originalPixmap = QtGui.QPixmap.fromImage(self.sheets[self.pageNumber])
            self.updateScreenshotLabel()
            
            self.fitToWindowAct.setEnabled(True)

            self.resize(self.geometry().width()+10, self.geometry().height()+10)
            debug.start_timer()

    def calibrate(self):
        debug.show()
        debug.tracker.show()

    def advance(self):
        if (self.pageNumber < (self.numberOfPages - 1)):
            self.pageNumber = self.pageNumber + 1
            self.originalPixmap = QtGui.QPixmap.fromImage(self.sheets[self.pageNumber])
            self.updateScreenshotLabel()
            self.overlay.advance()

    def back(self):
        if (self.pageNumber > 0):
            self.pageNumber = self.pageNumber - 1
            self.originalPixmap = QtGui.QPixmap.fromImage(self.sheets[self.pageNumber])
            self.updateScreenshotLabel()
            self.overlay.back()

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.imageLabel.setScaledContents(fitToWindow)
        scaledSize = self.originalPixmap.size()
        scaledSize.scale(self.imageLabel.size(), QtCore.Qt.KeepAspectRatio)
        fitToWindow = self.fitToWindowAct.isChecked()
        if (fitToWindow):
            self.overlay.resize(self.imageLabel.size())
        else:
            self.overlay.resize(scaledSize)
        xLong = self.imageLabel.size().width()
        yLong = self.imageLabel.size().height()
        self.overlay.move(xLong/2-self.overlay.size().width()/2, yLong/2-self.overlay.size().height()/2)

    def fullscreen(self):
        if (self.fullscreenAct.isChecked()):
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def activate(self):
        debug.activated = not debug.activated

    def activatePen(self, case):
        debug.activated = case

    def createActions(self):
        self.openAct = QtGui.QAction("&Abrir...", self, shortcut="Ctrl+O", triggered=self.open)
        self.exitAct = QtGui.QAction("Sair", self, shortcut="Ctrl+Q", triggered=self.close)
        self.advancePage = QtGui.QAction("Avancar slide", self, shortcut="Right", triggered=self.advance)
        self.backPage = QtGui.QAction("Voltar slide", self, shortcut="Left", triggered=self.back)
        self.fitToWindowAct = QtGui.QAction("&Preencher tela", self, enabled=False, checkable=True, shortcut="Ctrl+W", triggered=self.fitToWindow)
        self.fullscreenAct = QtGui.QAction("&Tela Cheia", self, checkable=True, shortcut="Ctrl+F", triggered=self.fullscreen)
        self.calibrateAct = QtGui.QAction("&Calibrar Camera", self, triggered=self.calibrate)
        self.activateAct = QtGui.QAction("&Ativar Camera", self, triggered=self.activate)

    def createMenus(self):
        self.fileMenu = QtGui.QMenu("&Arquivo", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QtGui.QMenu("&Imagem", self)
        self.viewMenu.addAction(self.advancePage)
        self.viewMenu.addAction(self.backPage)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)
        self.viewMenu.addAction(self.fullscreenAct)

        self.actionsMenu = QtGui.QMenu("&Acoes", self)
        self.actionsMenu.addAction(self.calibrateAct)
        self.actionsMenu.addAction(self.activateAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.actionsMenu)



if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    lousa = Lousa()
    lousa.show()
    debug = debugger.Debugger()
    debug.tracker.hide()
    sys.exit(app.exec_())

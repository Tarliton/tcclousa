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

from bluetooth import *
from PyQt4 import QtCore

class Server(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.server_stop = False

    def __del__(self):
        self.server_stop = True
        self.wait()

    def run(self):
        while not self.server_stop:
            self.server_sock=BluetoothSocket( RFCOMM )
            self.server_sock.bind(("",PORT_ANY))
            self.server_sock.listen(1)

            self.port = self.server_sock.getsockname()[1]

            self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

            advertise_service( self.server_sock, "SampleServer",
                               service_id = self.uuid,
                               service_classes = [ self.uuid, SERIAL_PORT_CLASS ],
                               profiles = [ SERIAL_PORT_PROFILE ], 
                            #                   protocols = [ OBEX_UUID ] 
                )
            print("Waiting for connection on RFCOMM channel %d" % self.port)

            self.client_sock, self.client_info = self.server_sock.accept()
            print("Accepted connection from ", self.client_info)
            try:
                while True:
                    data = self.client_sock.recv(1024)
                    if len(data) == 0: break
                    self.emit(QtCore.SIGNAL("message(QString)"), data)

            except IOError:
                pass

            print("disconnected")

            self.client_sock.close()
            self.server_sock.close()
            print("all done")
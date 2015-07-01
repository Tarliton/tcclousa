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

import kivy
kivy.require('1.9.0')

from kivy.app import App
from navigationDrawer import NavigationDrawer
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import  ObjectProperty
from kivy.properties import  NumericProperty
from kivy.properties import  ListProperty
from kivy.uix.popup import Popup
from kivy.lib import osc
from kivy.clock import Clock
from kivy.utils import platform


__author__ = 'tarliton'
__version__ = '1'


RootApp = None
serviceport = 3000
activityport = 3001

if platform == 'android':
	from jnius import autoclass
	autoclass('java.lang.System').out.println('Hello world')
	BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
	BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
	BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
	UUID = autoclass('java.util.UUID')
 
def get_socket_stream(name):
    paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
    socket = None
    for device in paired_devices:
        if device.getName() == name:
            socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee"))
            recv_stream = socket.getInputStream()
            send_stream = socket.getOutputStream()
            break
    socket.connect()
    return recv_stream, send_stream


class MainPanel(GridLayout):
	grid = ObjectProperty(None)
	top_lbl = ObjectProperty(None)
	pen_size = NumericProperty(1.0)
	pen_color = ListProperty([1,0,0,1])

class SidePanel(BoxLayout):
	pass


class NavDrawer(NavigationDrawer):
	def __init__(self, **kwargs):
		super(NavDrawer, self).__init__( **kwargs)

	def close_sidepanel(self, animate=True):
		if self.state == 'open':
			if animate:
				self.anim_to_state('closed')
			else:
				self.state = 'closed'

	def open_sidepanel(self, animate=True):
		if self.state == 'closed':
			if animate:
				self.anim_to_state('open')
			else:
				self.state = 'open'

class ColorSelector(Popup):
    pass


class SizeSelector(Popup):
	pass

class AndroidApp(App):
	def open_settings(self):
		if self.navigationdrawer.state == 'open':
			self.navigationdrawer.close_sidepanel()
		else:
			self.navigationdrawer.open_sidepanel()
		pass

	def reCallback(self, message, *args):
		pass

	def build(self):
		self.service = None
		self.start_service()
		global RootApp
		RootApp = self

		# NavigationDrawer
		self.navigationdrawer = NavDrawer()

		# SidePanel
		side_panel = SidePanel()
		self.navigationdrawer.add_widget(side_panel)

		# MainPanel
		self.main_panel = MainPanel()

		# color picker
		self.color_selector = ColorSelector()

		# size selector
		self.size_selector = SizeSelector()

		self.navigationdrawer.anim_type = 'slide_above_simple'
		self.navigationdrawer.add_widget(self.main_panel)

		osc.init()
		oscid = osc.listen(port=3002)
		osc.bind(oscid, self.reCallback, '/date')
		Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)

		return self.navigationdrawer

	def start_service(self):
		if platform == 'android':
			from android import AndroidService
			service = AndroidService('controle', 'running')
			service.start('service started')
			self.service = service

	def toggle_sidepanel(self):
		self.navigationdrawer.toggle_state()


	def on_pause(self):
		return True

	def on_resume(self):
		pass

	def on_stop(self):
		osc.dontListen()
		if self.service:
			self.service.stop()
			self.service = None
		return True

	def connect(self, name):
		try:
			self.recv_stream, self.send_stream = get_socket_stream(name)
		except:
			pass

	def send(self, cmd):
		if hasattr(self, 'send_stream'):
			self.send_stream.write('{}'.format(cmd))
			self.send_stream.flush()
		else:
			pass	

	def printColor(self):
		print self.color_selector.color


if __name__ == '__main__':
	AndroidApp().run()

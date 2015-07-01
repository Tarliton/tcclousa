#Copyright (C) 2015  Tarliton Godoy
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

from kivy.lib import osc
from time import localtime, asctime, sleep


def send_date():
	osc.sendMsg('/date', [asctime(localtime()), ], port=3002)


if __name__ == '__main__':
	osc.init()
	oscid = osc.listen(ipAddr='0.0.0.0', port=3000)
	while True:
		osc.readQueue(oscid)
		send_date()
		sleep(.1)
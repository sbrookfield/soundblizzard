
'''
Serves Soundblizzard on Dbus - hopefully MPRIS compatible
'''
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
#session_bus = dbus.SessionBus()
class dbus(dbus.service.Object):
	def __init__(self, soundblizzard):
		bus_name = dbus.service.BusName('apps.SoundBlizzard', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/apps/SoundBlizzard')
	
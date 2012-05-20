import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

class mediakeys(object):
	'''
	Connects to Gnome Media Keys on dbus for control
	'''
	def __init__(self):
		self.getkeys()

	def getkeys(self):
		DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
		self.bus_object.GrabMediaPlayerKeys('Name of app', 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
		self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakeys)

	def handle_mediakeys(self, caller, command):
		print ''.join(['Media Key Pressed: ', command])
		if command =='Next':
			print 'Processing Next Key'
		elif command =='Previous':
			print 'Processing Previous Key'
if __name__ == "__main__":
	mediakeys()
	gobject.MainLoop().run()

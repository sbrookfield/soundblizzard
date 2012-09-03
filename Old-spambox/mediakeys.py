try:
	import gobject
	import dbus
	from dbus.mainloop.glib import DBusGMainLoop
	import player
except:
	loggy.log( "Required libraries not found! gobject dbus dbus.mainloop.glib player\n")
class mediakeys(object):
	'''
	Connects to Gnome Media Keys on dbus for control
	'''
	def __init__(self, player):
		self.getkeys()
		self.player = player

	def getkeys(self):
		DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
		self.bus_object.GrabMediaPlayerKeys('spambox', 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
		self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakeys)

	def handle_mediakeys(self, caller, command):
		print ''.join(['Media Key Pressed: ', command])
		if command =='Next':
			self.player.get_next()
		elif command =='Previous':
			print self.player.db.get_row('music','uri','file:///home/sam/Music/10 - Girl Talk - Steady Shock.mp3')
if __name__ == "__main__":
	mediakeys( 'b')
	gobject.MainLoop().run()

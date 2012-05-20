import dbus

class mediakey(object):
	def __init__(self):
		self.bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
		self.bus_object = self.bus.get_object(
			'org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')

		self.bus_object.GrabMediaPlayerKeys(
			'spambox', 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')

		self.bus_object.connect_to_signal(
			'MediaPlayerKeyPressed', self.handle_mediakey)



	def handle_mediakey(self, application, *mmkeys):
		if application != self.app:
			return
		for key in mmkeys:
			if key == "Play":
				app.widgetapp.on_play_clicked()
			elif key == "Stop":
				app.widgetapp.on_stop_clicked()
			elif key == "Next":
				app.widgetapp.on_forward_clicked()
			elif key == "Previous":
				app.widgetapp.on_previous_clicked()

	def on_window_focus(self, window):
		self.bus_object.GrabMediaPlayerKeys(
			self.app, 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
		return False

def get_media_key_handler():
	"""
	Creates and returns a MediaKeyHandler or returns None if such a thing
	is not available on this platform.

	:param window: a Gtk.Window instance
	"""
	try:
		mediakey()
		print 'okay'
	except dbus.DBusException:
		logging.exception("cannot load MediaKeyHandler")

get_media_key_handler()



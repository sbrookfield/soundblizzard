from gi.repository import Gtk, GdkX11
class GTKGui(object):
	def __init__(self):
		self.builder = Gtk.Builder()
		self.builder.add_from_file("gui.glade")
		self.builder.connect_signals(self)
		#widgets = self.builder.get_objects()
		self.window = self.builder.get_object("window1")
		self.window.show()
		self.ben = self.builder.get_object("albumartdrawingarea1")
		print(self.ben.get_property('window').get_xid())

if __name__ == "__main__":
	app = GTKGui()
	Gtk.main()

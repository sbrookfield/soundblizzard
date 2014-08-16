#!/usr/bin/python
from gi.repository import Gtk, Gdk, GdkPixbuf
#Thanks to Bobble - https://developer.gnome.org/gtk3/stable/GtkScrolledWindow.html
#Not sure if theres a better way to do this
class TestWindow(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="Button Demo")
		self.connect("delete-event", Gtk.main_quit)
		temp = Gtk.Box()
		self.add(temp)
		temp.add(AspectImage('logo.png'))
class AspectImage(Gtk.Viewport):
	oldx = 0
	oldy = 0
	def __init__(self,image):
		Gtk.Viewport.__init__(self)
		self.connect("check-resize", self.on_check_resize)
		self.aspect = Gtk.AspectFrame()
		self.scrollwindow = Gtk.ScrolledWindow()
		self.scrollwindow.set_policy(Gtk.PolicyType.ALWAYS,Gtk.PolicyType.ALWAYS) # Needs this otherwise cannot reduce in size
		self.add(self.aspect)
		self.aspect.add(self.scrollwindow)		
		self.box = Gtk.Box()
		self.scrollwindow.add_with_viewport(self.box)		
		self.pixbuf = GdkPixbuf.Pixbuf().new_from_file(image)
		self.image = Gtk.Image().new_from_pixbuf(self.pixbuf)
		self.box.add(self.image)
		self.show_all()		
	def resizeImage(self, x, y):
		print('Resizing Image to ('+str(x)+','+str(y)+')....')
		pixbuf = self.pixbuf.scale_simple(x, y, GdkPixbuf.InterpType.BILINEAR)
		self.image.set_from_pixbuf(pixbuf)
	def on_check_resize(self, window, data=None):
		print("Checking resize....")		
		alloc = self.scrollwindow.get_allocation()
		if ((self.oldx == alloc.width)and (self.oldy == alloc.width)): return True# checks if size has actually changed
		self.oldx = alloc.width
		self.oldy = alloc.height
		self.box.set_allocation(alloc)
		self.resizeImage(alloc.width,alloc.height)
if __name__ == "__main__":
	win = TestWindow()
	win.show_all()
	Gtk.main()
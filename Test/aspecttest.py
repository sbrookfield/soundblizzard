#!/usr/bin/env python
#try:
import soundblizzard
import player, loggy, gst, cairo
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GdkX11
from gi.repository import GObject
#TODO: look at kiwi for pygtk lists etc.
#pyGtk.require("2.0")
#except:
#	print "gui - Required libraries not found - pyGtk, Gtk, player, loggy, gst, sbdb! Please install\n"
#TODO: while gtk.gtk_events_pending(): gtk.gtk_main_iteration() - does this work?
class GTKGui(object):
	def __init__(self, sb):
		loggy.log('Gui loading...')
		#self.play_buttons = []
		#self.progress_bars    = []
		#self.position_labels    = []
		self.volume_scales =[]
		#self.info_labels = []
		self.album_arts = []
		self.main_trees = []
		self.slave_windows = []
		self.main_tree_modes = {}
		self.WIDGETS = 3


		self.widgets={'consume_toggles':[],'repeat_toggles':[],'single_toggles':[],'random_toggles':[],'play_buttons':[], 'progress_bars':[], 'position_labels':[], 'info_labels':[], 'fullscreen_widgets':[]}
		self.sb = soundblizzard.soundblizzard # fakes for tab completion
		self.sb = sb

		self.builder = Gtk.Builder()
		self.builder.add_from_file("gui.glade")
		self.builder.connect_signals(self)
		#widgets = self.builder.get_objects()
		self.window = self.builder.get_object("window1")
		self.window.set_title("SoundBlizzard")
		self.window.connect('delete-event', Gtk.main_quit)
		#pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/sam/Code/Eclipse workspace/soundblizzard/logo.png')
		self.window.set_icon_from_file('../logo.png')
		self.window.show()
		#self.window.fullscreen() #TODO: fullscreen
	def is_album_art(self, widget):
		frame = Gtk.AspectFrame(0.5, 0.5, 0.8, False)
		image = Gtk.Image()
		image.set_from_file("../logo.png")
		frame.add(image)
		widget.add(frame)
		#widget.show_all()
		self.album_arts.append(image)
		print('got image '+str(widget))
		#widget.set_from_file('../logo32.png')
		#self.on_image_resize(widget, None)
#	def redraw_album_art(self, widget, event):
#		print 'image redraw'
#		x , y, width, height = event.area
#		file = self.sbdb.config.get('Main', 'imagefile') #TODO: - does this result in file read?
#		pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file, width , height)
#		widget.draw_pixbuf(widget.get_style().fg_gc[STATE_NORMAL],pixbuf, x, y, x, y, width, height, Gtk.gdk.RGB_DITHER_NONE, 0 , 0)
#

#        print 'image resize'
#        #src_width, src_height = widget.get_pixmap().get_width(), widget.get_pixmap().get_height()
#        #allocation = widget.get_allocation()# thanks to http://stackoverflow.com/questions/4939734/automatic-image-scaling-on-resize-with-pyGtk
#        #ben = widget.get_pixbuf()
#        for widget in self.album_arts:
#            file = '/home/sam/temp.img' #TODO: - does this result in file read?
#            pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file,widget.allocation.height , widget.allocation.width)
#            #pixbuf = widget.get_pixbuf().scale_simple(widget.allocation.width, widget.allocation.height, Gtk.gdk.INTERP_BILINEAR)
#            widget.set_from_pixbuf(pixbuf)


if __name__ == "__main__":
	temp = ''
	app = GTKGui(temp)
	Gtk.main()


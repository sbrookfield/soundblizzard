#!/usr/bin/env python
#try:
from gi.repository import Gtk
import player, loggy, gst, cairo
#pyGtk.require("2.0")
#except:
#	print "gui - Required libraries not found - pyGtk, Gtk, player, loggy, gst, sbdb! Please install\n"

class GTKGui(object):
	def __init__(self, soundblizzard):
		loggy.warn('Gui loading...')
		#self.playbuttons = []
		#self.progress_bars    = []
		#self.position_labels    = []
		self.volume_scales =[]
		#self.info_labels = []
		self.album_arts = []
		self.main_trees = []
		self.slave_windows = []
		self.main_tree_modes = {}
		self.WIDGETS = 3


		self.widgets={'playbuttons':[], 'progress_bars':[], 'position_labels':[], 'info_labels':[]}
		self.soundblizzard = soundblizzard
		self.player = soundblizzard.player
		self.sbdb = soundblizzard.sbdb
		self.player.connect('async-done', self.on_async_done)
		self.master_tree_load()

		self.builder = Gtk.Builder()
		self.builder.add_from_file("glade/gui.glade")
		self.builder.connect_signals(self)
		#widgets = self.builder.get_objects()
		self.window = self.builder.get_object("window1")
		self.get_widgets('window')
		for window in self.widgets['window']:
			window.show()
			self.window.show()
		#self.window.fullscreen() #TODO fullscreen

		self.get_widgets('albumartdrawingarea')
		for alb in self.widgets['albumartdrawingarea']:
			self.album_arts.append(alb)
		#    self.player.videosink.set_xwindow_id(alb.window.xid)

		self.player.on_update_play_state.append(self.on_play_state_change)
		self.player.on_update_volume.append(self.on_volume_change)
		self.player.on_update_tags.append(self.on_update_tags)
		self.player.connect('hemisecond', self.on_position_change)
		self.player.connect('play-state-change', self.on_play_state_change)
	def debug(self, data=None):
		print 'debug got'
		print data

	def get_widgets(self, name):
		'''Searches Gtkbuilder for widgets with name1, name2, name3 etc and adds them to self.widgets[name]'''
		self.widgets[name]=[]
		for x in range(self.WIDGETS):
			if self.builder.get_object(name + str(x)):
				self.widgets[name].append(self.builder.get_object(name + str(x)))
	def get_next(self, widget):
		self.player.get_next()
	def get_prev(self, widget):
		self.player.get_prev()
	def on_playbutton_click(self, widget):
		loggy.debug('gui.on_playbutton_click')
		self.player.playpause()
	def on_position_change(self, player):
		'''What to do when position change signal recieved'''
		#loggy.debug('gui.on_position_change')
		#print "on pos change" + str(pos) + str(dur)
		pos = self.player.getpos()
		dur = self.player.getdur()
		for progress_bar in self.widgets['progress_bars']:
			progress_bar.set_range(0, dur)
			progress_bar.set_value(pos)
		label = self.gst_time_string(pos) + ' / ' + self.gst_time_string(dur)
		#print label
		for position_label in self.widgets['position_labels']:
			position_label.set_label(label)
	def on_play_state_change(self,temp):
		#TODO - make player only emit one signal for each event
		state = self.player.getstate()
		loggy.debug('gui.on_play_state_change ' + state)
		if (state == 'play'):
			for playbutton in self.widgets['playbuttons']:
				playbutton.set_label(Gtk.STOCK_MEDIA_PAUSE)
		elif (state == 'pause'):
			for playbutton in self.widgets['playbuttons']:
				playbutton.set_label(Gtk.STOCK_MEDIA_PLAY)
		else:
			loggy.warn('gui.on_play_state_change got unknown state: ' + state)
	def is_play_button(self, widget):
		#print 'playbutton found'
		self.widgets['playbuttons'].append(widget)#TODO check for duplicates
	def on_progress_bar_change_value (self, range, scroll, value, data=None):
		self.player.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, value)
	def is_progress_bar(self, widget):
		#print 'progress bar found'
		self.widgets['progress_bars'].append(widget)
	def is_position_label(self, widget):
		self.widgets['position_labels'].append(widget)
	def gst_time_string(self, nanosecs):
		# This method was submitted by Sam Mason.
		# It's much shorter than the original one.
		s,ns = divmod(nanosecs, self.player.SECOND)
		m,s = divmod(s, 60)
		if m < 60:
			return "%02i:%02i" %(m,s)
		else:
			h,m = divmod(m, 60)
			return "%i:%02i:%02i" %(h,m,s)
	def is_volume_scale(self, widget):
		self.volume_scales.append(widget)
		widget.get_adjustment().set_upper(100)
		widget.set_value(self.player.getvol())
		#widget.set_from_icon_name(Gtk.STOCK_OPEN, 36)
	def on_volume_change(self, volume):
		for volume_scale in self.volume_scales:
			volume_scale.set_value(volume)
	def on_volume_scale_change(self, widget, value):
		self.player.setvol(value)
	def is_info_label(self, widget):
		self.widgets['info_labels'].append(widget)
	def on_async_done(self, player):
		loggy.debug('gui.on_async_done')
		self.on_update_tags()
	def on_update_tags(self):
		text = ''
		if 'title' in self.player.tags: #TODO do this after async done, not every time
			text += self.player.tags['title']
		if 'artist' in self.player.tags:
			text += '\n by ' + self.player.tags['artist']
		if 'album' in self.player.tags:
			text += ' from ' + self.player.tags['album'] #TODO make font italic
		#print text
		for label in self.widgets['info_labels']:
			label.set_label(text)
		#TODO - get this on timer not on async
		if 'image' in self.player.tags:
			file = '/home/sam/.temp.img'
			img = open(file, 'w')
			img.write(self.player.tags['image'])
			img.close()
			for album_art in self.album_arts:
				album_arts.connect('draw', self.draw_album_art, album_art)
				cairo.ImageSurface.create_from_png("w")
				#album_art.set_from_file(file)
				#self.on_image_resize(album_art, None)
#    def draw_album_art(self, widget):
#        print (widget + 'fart')

	def is_album_art(self, widget):
		self.album_arts.append(widget)
		#self.on_image_resize(widget, None)
#	def redraw_album_art(self, widget, event):
#		print 'image redraw'
#		x , y, width, height = event.area
#		file = self.sbdb.config.get('Main', 'imagefile') #TODO - does this result in file read?
#		pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file, width , height)
#		widget.draw_pixbuf(widget.get_style().fg_gc[STATE_NORMAL],pixbuf, x, y, x, y, width, height, Gtk.gdk.RGB_DITHER_NONE, 0 , 0)
#
	def on_image_resize(self, widgetty, event): #TODO on_image_resize
		None
#        print 'image resize'
#        #src_width, src_height = widget.get_pixmap().get_width(), widget.get_pixmap().get_height()
#        #allocation = widget.get_allocation()# thanks to http://stackoverflow.com/questions/4939734/automatic-image-scaling-on-resize-with-pyGtk
#        #ben = widget.get_pixbuf()
#        for widget in self.album_arts:
#            file = '/home/sam/temp.img' #TODO - does this result in file read?
#            pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file,widget.allocation.height , widget.allocation.width)
#            #pixbuf = widget.get_pixbuf().scale_simple(widget.allocation.width, widget.allocation.height, Gtk.gdk.INTERP_BILINEAR)
#            widget.set_from_pixbuf(pixbuf)
	def is_video_out(self, widget):
		loggy.debug('is_video_out')

		self.player.vidout['xid'] = widget.window.xid
		#self.player.add_vid(widget.window.xid)
	def is_master_tree(self, widget):
		self.main_trees.append(widget)
		#self.main_tree_load()
		widget.set_modobjectel(self.main_tree_store)
		widget.tv_column = Gtk.TreeViewColumn('Spambox')
		widget.append_column(widget.tv_column)
		widget.cell = Gtk.CellRendererText()
		widget.tv_column.pack_start(widget.cell, True)
		widget.tv_column.add_attribute(widget.cell, 'text', 0)
		widget.set_reorderable(True)
		widget.connect('cursor-changed', self.master_tree_cursor_changed)
	def master_tree_cursor_changed(self, widget):
		#TODO set position in all trees
		loggy.debug('gui.master_tree_cursor_changed')
		(model, iter) = widget.get_selection().get_selected()
		#print self.slave_windows[0].get_children()
		try:
			self.slave_view.destroy()
		except:
			None

		if iter:
			self.main_tree_modes[model.get_value(iter,0)]['open_func']()
	def master_tree_add(self, name, open_func):
		self.main_tree_store.append(None, [name])
		self.main_tree_modes[name] = {'open_func' : open_func}

	def master_tree_load(self):
		self.main_tree_store = Gtk.TreeStore(str)
		self.master_tree_add('Now Playing', self.slave_enter_now_playing_view)
		self.master_tree_add('Media', self.slave_enter_media_view)
		self.master_tree_add('Preferences', self.slave_enter_preferences_view)

#TODO connect signals other than map automatically
	def is_slave_area(self, widget):
		loggy.debug('gui.is_slave_area')
		self.slave_windows.append(widget) #TODO allow multiple separate master/slave combos
	def slave_enter_media_view(self):
		loggy.debug('gui.slave_enter_media_view')
		#TODO check slave_window is a hbox
		self.slave_view = GTK_media_view(self)
		self.slave_windows[0].pack_start(self.slave_view, True, True)
		self.slave_windows[0].show_all()
		self.builder.connect_signals(self)
	def slave_enter_now_playing_view(self):
		loggy.debug('gui.slave_enter_now_playing_view')
	def slave_enter_preferences_view(self):
		self.slave_view = GTK_preferences()
		self.slave_windows[0].pack_start(self.slave_view, True, True)
		self.slave_windows[0].show_all()
		self.builder.connect_signals(self)
class GTK_media_view(Gtk.HBox):
	def __init__(self, gui):
		Gtk.HBox.__init__(self) # load glade
		self.builder = Gtk.Builder()
		self.builder.add_from_file('glade/media_view.glade')
		widget = self.builder.get_object("vbox1")
		widget.reparent(self)
		self.builder.connect_signals(self)
		self.gui = gui
		self.keystoshow = ('artist', 'title', 'album', 'date', 'genre', 'duration', 'rating','mimetype', 'atime', 'mtime', 'ctime', 'dtime', 'size')
		self.keystoshowdict = {} # dic of name, col position
		for i, a in enumerate(self.keystoshow):
			self.keystoshowdict[a] = i
		#print self.keystoshowdict
		#print 'GOOB' + str( player.sbdb.keytypelist )
		self.list_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, )
		#print player.sbdb.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3")
		self.list_store.append(self.gui.sbdb.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3"))
		self.gui.sbdb.iter(self.list_store.append)
	def is_listview(self, widget):
		loggy.debug('gui.GTK_media_view.is_listview')
		self.treeview = widget
		widget.connect('row-activated', self.treeview_activated)
		widget.set_model(self.list_store) # init treeview

		widget.tv_columns = {}
		for i, name in enumerate(self.gui.sbdb.totkeys): # go through all keys
			if name in self.keystoshowdict: #check if column is to display
				widget.tv_columns[name] = Gtk.TreeViewColumn(name)
				widget.insert_column(widget.tv_columns[name], self.keystoshowdict[name]) # inserts column in order from keystoshow
				widget.tv_columns[name].cell = Gtk.CellRendererText()
				widget.tv_columns[name].pack_start(widget.tv_columns[name].cell, True)
				widget.tv_columns[name].add_attribute(widget.tv_columns[name].cell, 'text', i)
				widget.tv_columns[name].set_resizable(True)
				#widget.tv_columns[name].set_clickable(True)
				widget.tv_columns[name].connect('clicked', self.tv_clicked, i)
				#widget.tv_columns[name].set_sort_indicator(True)
		widget.columns_autosize()
		#widget.set_headers_clickable(True)
		#widget.tv_column = Gtk.TreeViewColumn('Spambox')
		#widget.append_column(widget.tv_column)
		#widget.cell = Gtk.CellRendererText()
		#widget.tv_column.pack_start(widget.cell, True)
		#widget.tv_column.add_attribute(widget.cell, 'text', 0)
		#widget.set_reorderable(True)
	def treeview_activated(self, treeview, path, view_column):
		loggy.debug('gui.GTK_media_view.treeview_activated')
		(model, iter) = treeview.get_selection().get_selected()
		if iter:
			self.gui.player.load_uri(self.list_store.get_value(iter,0))
	def tv_clicked(self, widget, i):
		loggy.debug('gui.GTK_media_view.tv_clicked')
		widget.set_sort_column_id(i)
		#prevorder = widget.get_sort_order()
		#if prevorder = Gtk.SORT_ASCENDING:
		#	widget.set_sort_order(Gtk.SORT_DESCENDING)
		#else:
		#	widget.set_sort_order(Gtk.SORT_ASCENDING)

class GTK_preferences(Gtk.HBox): # thanks to http://stackoverflow.com/questions/2129369/Gtk-builder-and-multiple-glade-files-breaks
	def __init__(self):
		Gtk.HBox.__init__(self)
		self.builder = Gtk.Builder()
		self.builder.add_from_file('glade/preferences.glade')
		some_widget = self.builder.get_object("notebook1")
		some_widget.reparent(self)
		#self.show_all()
		#self.add(some_widget)
		#some_widget.show()
		self.builder.connect_signals(self)
#	def __destroy__(self):
#		loggy.log('GTK_media_view destroyed')
#		self.builder.destroy()
	def on_button3_clicked(self):
		loggy.debug('GTK_media_view.on_button3_clicked')
	def on_button2_clicked(self):
		True
	def on_button1_clicked(self):
		True
class GTK_now_playing(object):
	def __init__(self):
		True

if __name__ == "__main__":
	temp = ''
	player1 = player.player(temp)
	#sbdb1 = sbdb.sbdb()
	loggy.debug_setting = True
	app = GTKGui(temp)
	#player1.load_playlist('ben')
	Gtk.main()


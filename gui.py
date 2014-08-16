#!/usr/bin/env python
#try:
try:
	import gi, loggy, player
	gi.require_version('Gst', '1.0')
	from gi.repository import GObject, Gst, Gtk, GdkPixbuf, GdkX11
except:
	loggy.warn('Gui could not import required libraries')
# import soundblizzard
# import player, loggy, gst, cairo, aspectimage
# from gi.repository import Gtk
# from gi.repository import GdkPixbuf
# from gi.repository import GdkX11
# from gi.repository import GObject
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
		#self.sb = soundblizzard.soundblizzard # fakes for tab completion
		self.sb = sb
		self.sb.player.connect('async-done', self.on_async_done)
		self.master_tree_load()

		self.builder = Gtk.Builder()
		self.builder.add_from_file("glade/gui.glade")
		self.builder.connect_signals(self)
		#widgets = self.builder.get_objects()
		self.window = self.builder.get_object("window1")
		self.window.set_title("SoundBlizzard")
		self.window.connect('delete-event', Gtk.main_quit)
		#pixbuf = GdkPixbuf.Pixbuf.new_from_file('/home/sam/Code/Eclipse workspace/soundblizzard/logo.png')
		self.window.set_icon_from_file('logo.png')
		self.get_widgets('window')
		for window in self.widgets['window']:
			window.show()
			self.window.show()
		#self.window.fullscreen() #TODO: fullscreen

		#self.get_widgets('albumartdrawingarea')
		#for alb in self.widgets['albumartdrawingarea']:
			#self.album_arts.append(alb)
			#print alb.window
			#self.sb.player.videosink.set_xwindow_id(alb.window.xid)
			#print(alb.get_window_xid())

		#self.sb.player.on_update_play_state.append(self.on_play_state_change)
		#self.sb.player.on_update_volume.append(self.on_volume_change)
		#self.sb.player.on_update_tags.append(self.on_update_tags)
		self.sb.player.connect('async-done', self.on_update_tags)
		self.sb.player.connect('volume-changed', self.on_volume_change)
		self.sb.player.connect('position-changed', self.on_position_change)
		self.sb.player.connect('play-state-changed', self.on_play_state_change)
	def debug(self, data=None):
		print ('debug got')
		print (data)

	def get_widgets(self, name):
		'''Searches Gtkbuilder for widgets with name1, name2, name3 etc and adds them to self.widgets[name]'''
		self.widgets[name]=[]
		for x in range(self.WIDGETS):
			if self.builder.get_object(name + str(x)):
				self.widgets[name].append(self.builder.get_object(name + str(x)))
	def get_next(self, widget):
		self.sb.playlist.get_next()
	def get_prev(self, widget):
		self.sb.playlist.get_prev()
	def on_playbutton_click(self, widget):
		loggy.debug('gui.on_playbutton_click')
		widget.set_relief(Gtk.ReliefStyle.NONE)
		self.sb.player.playpause()
	def on_position_change(self, player):
		'''What to do when position change signal recieved'''
		#loggy.debug('gui.on_position_change')
		for progress_bar in self.widgets['progress_bars']:
			progress_bar.set_range(0, self.sb.player.durns)
			progress_bar.set_value(self.sb.player.posns)
		label = self.sb.player.posstr + ' / ' + self.sb.player.durstr
		for position_label in self.widgets['position_labels']:
			position_label.set_label(label)
	def on_play_state_change(self, player):
		#TODO: - make player only emit one signal for each event
		#state = self.sb.player.getstate()
		loggy.debug('gui.on_play_state_change ' + self.sb.player.state)
		if (self.sb.player.state == 'play'):
			for playbutton in self.widgets['play_buttons']:
				playbutton.set_label(Gtk.STOCK_MEDIA_PAUSE)
		elif (self.sb.player.state == 'pause' or self.sb.player.state == 'stop'):
			for playbutton in self.widgets['play_buttons']:
				playbutton.set_label(Gtk.STOCK_MEDIA_PLAY)
		else:
			loggy.warn('gui.on_play_state_change got unknown state: ' + self.sb.player.state)
	def is_play_button(self, widget):
		#print 'playbutton found'
		self.widgets['play_buttons'].append(widget)#TODO: check for duplicates
	def is_fullscreen_toggle(self,widget):
		self.widgets['fullscreen_widgets'].append(widget)
		widget.get_parent_window()
		widget.connect('toggled',self.on_fullscreen_toggle)
		#def change_fullscreen_toggle(self):
		#widget.get_parent_window().connect('window-state-event',self.on_window_state_event)
	def on_window_state_event(self):
		print (widget)
		print ('LoL')
	def on_fullscreen_toggle(self, widget):
		if (widget.get_label() == 'gtk-fullscreen'):
			widget.get_parent_window().fullscreen()
			widget.set_label('gtk-leave-fullscreen')
		else:
			widget.get_parent_window().unfullscreen()
			widget.set_label('gtk-fullscreen')
	def on_progress_bar_change_value (self, value_range, scroll, value, data=None):
		self.sb.player.setpos(value)
		#self.sb.player.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, value)
	def is_progress_bar(self, widget):
		#print 'progress bar found'
		self.widgets['progress_bars'].append(widget)
	def is_position_label(self, widget):
		self.widgets['position_labels'].append(widget)
	def gst_time_string(self, nanosecs):
		# This method was submitted by Sam Mason.
		# It's much shorter than the original one.
		s,ns = divmod(nanosecs, self.sb.player.SECOND)
		m,s = divmod(s, 60)
		if m < 60:
			return "%02i:%02i" %(m,s)
		else:
			h,m = divmod(m, 60)
			return "%i:%02i:%02i" %(h,m,s)
	def is_volume_scale(self, widget):
		self.volume_scales.append(widget)
		widget.set_adjustment(Gtk.Adjustment(value=self.sb.player.vol, lower=0, upper=100, step_incr=5, page_incr=10, page_size=0))
		widget.connect('value-changed', self.on_volume_scale_change)
		#widget.set_value(self.sb.player.getvol())
		#widget.set_from_icon_name(Gtk.STOCK_OPEN, 36)
	def on_volume_change(self, caller):
		for volume_scale in self.volume_scales:
			if (int(round(volume_scale.get_value()))!=self.sb.player.vol): 
				volume_scale.set_value(self.sb.player.vol)
	def on_volume_scale_change(self, widget, value):
		if (int(round(value)) == self.sb.player.vol):
			return True
		self.sb.player.setvol(int(round(value)))
	def is_info_label(self, widget):
		self.widgets['info_labels'].append(widget)
	def is_single_toggle(self, widget):
		self.widgets['single_toggles'].append(widget)
		self.single_toggle_update(self.sb.playlist.single, self.sb.playlist.single.get(), widget)
		widget.connect('toggled', self.on_single_toggle)
		self.sb.playlist.single.connect('changed', self.single_toggle_update, widget)
	def on_single_toggle(self, widget):
		if self.sb.playlist.single.get() != widget.get_active():
			self.sb.playlist.single.set(widget.get_active())
		loggy.log ('toggle button ' + str(widget.get_active()))
	#TODO: combine this into one function not four
	def single_toggle_update(self, toggle, value, widget):
		if widget.get_active() != value:
			widget.set_active(value) 
	def is_consume_toggle(self, widget):
		self.widgets['consume_toggles'].append(widget)
		self.consume_toggle_update(self.sb.playlist.consume, self.sb.playlist.consume.get(), widget)
		widget.connect('toggled', self.on_consume_toggle)
		self.sb.playlist.consume.connect('changed', self.consume_toggle_update, widget)
	def on_consume_toggle(self, widget):
		if self.sb.playlist.consume.get != widget.get_active():
			self.sb.playlist.consume.set(widget.get_active())
		loggy.log ('toggle button ' + str(widget.get_active()))
	def consume_toggle_update(self, toggle, value, widget):
		if widget.get_active() != value:
			widget.set_active(value) 
	def is_repeat_toggle(self, widget):
		self.widgets['repeat_toggles'].append(widget)
		self.repeat_toggle_update(self.sb.playlist.repeat, self.sb.playlist.repeat.get(), widget)
		widget.connect('toggled', self.on_repeat_toggle)
		self.sb.playlist.repeat.connect('changed', self.repeat_toggle_update, widget)
	def on_repeat_toggle(self, widget):
		if self.sb.playlist.repeat.get() != widget.get_active():
			self.sb.playlist.repeat.set(widget.get_active())
		loggy.log ('toggle button ' + str(widget.get_active()))
	def repeat_toggle_update(self, toggle, value, widget):
		if widget.get_active() != value:
			widget.set_active(value) 
	def is_random_toggle(self, widget):
		self.widgets['random_toggles'].append(widget)
		self.random_toggle_update(self.sb.playlist.random, self.sb.playlist.random.get(), widget)
		widget.connect('toggled', self.on_random_toggle)
		self.sb.playlist.random.connect('changed', self.random_toggle_update, widget)
	def on_random_toggle(self, widget):
		if self.sb.playlist.random.get() != widget.get_active():
			self.sb.playlist.random.set(widget.get_active())
		loggy.log ('toggle button ' + str(widget.get_active()))
	def random_toggle_update(self, toggle, value, widget):
		if widget.get_active() != value:
			widget.set_active(value) 
	def on_async_done(self, player):
		loggy.debug('gui.on_async_done')
		self.on_update_tags()
	def on_update_tags(self, *player):
		text = ''
		if 'title' in self.sb.player.tags: #TODO: do this after async done, not every time
			text += self.sb.player.tags['title']
		if 'artist' in self.sb.player.tags:
			text += '\n by ' + self.sb.player.tags['artist']
		if 'album' in self.sb.player.tags:
			text += ' from ' + self.sb.player.tags['album'] #TODO: make font italic
		#print text
		for label in self.widgets['info_labels']:
			label.set_label(text)
		#TODO: - get this on timer not on async
		if 'image' in self.sb.player.tags:
			filename = '/home/sam/.temp.img'#TODO: replace file to temp file or better interface
			img = open(filename, 'w')
			img.write(self.sb.player.tags['image'])
			img.close()
			for album_art in self.album_arts:
				pass
				#album_art.connect('draw', self.draw_album_art, album_art)
				#cairo.ImageSurface.create_from_png(filename)
				#album_art.set_from_file(file)
				#self.on_image_resize(album_art, None)
#    def draw_album_art(self, widget):
#        print (widget + 'fart')

	def is_album_art(self, widget):
		#image = aspectimage.AspectImage('logo.png')
		image = Gtk.Image()
		image.set_from_file('logo.png')
		widget.pack_start(image,True, True, 0)
		widget.show_all()
		#widget.add(art)
		widget.show()
		self.album_arts.append(widget)
		print('got image '+str(widget))
		#widget.set_from_file('logo16.png')
		
		#self.on_image_resize(widget, None)
#	def redraw_album_art(self, widget, event):
#		print 'image redraw'
#		x , y, width, height = event.area
#		file = self.sbdb.config.get('Main', 'imagefile') #TODO: - does this result in file read?
#		pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file, width , height)
#		widget.draw_pixbuf(widget.get_style().fg_gc[STATE_NORMAL],pixbuf, x, y, x, y, width, height, Gtk.gdk.RGB_DITHER_NONE, 0 , 0)
#
	def on_image_resize(self, widgetty, event): #TODO: on_image_resize
		None
#        print 'image resize'
#        #src_width, src_height = widget.get_pixmap().get_width(), widget.get_pixmap().get_height()
#        #allocation = widget.get_allocation()# thanks to http://stackoverflow.com/questions/4939734/automatic-image-scaling-on-resize-with-pyGtk
#        #ben = widget.get_pixbuf()
#        for widget in self.album_arts:
#            file = '/home/sam/temp.img' #TODO: - does this result in file read?
#            pixbuf = Gtk.gdk.pixbuf_new_from_file_at_size(file,widget.allocation.height , widget.allocation.width)
#            #pixbuf = widget.get_pixbuf().scale_simple(widget.allocation.width, widget.allocation.height, Gtk.gdk.INTERP_BILINEAR)
#            widget.set_from_pixbuf(pixbuf)
	def is_video_out(self, widget):
		loggy.debug('is_video_out')
		self.sb.player.vidout['xid'] = widget.get_property('window').get_xid() # don't forget to import GdkX11!
		self.sb.player.videosink.set_xwindow_id(self.sb.player.vidout['xid'])
		#print (widget)
		#self.sb.player.add_vid(widget.window.xid)
	def is_master_tree(self, widget):
		self.main_trees.append(widget)
		#self.main_tree_load()
		widget.set_model(self.main_tree_store)
		widget.tv_column = Gtk.TreeViewColumn('Spambox')
		widget.append_column(widget.tv_column)
		widget.cell = Gtk.CellRendererText()
		widget.tv_column.pack_start(widget.cell, True)
		widget.tv_column.add_attribute(widget.cell, 'text', 0)
		widget.set_reorderable(True)
		widget.connect('cursor-changed', self.master_tree_cursor_changed)
	def master_tree_cursor_changed(self, widget):
		#TODO: set position in all trees
		loggy.debug('gui.master_tree_cursor_changed')
		(model, iterat) = widget.get_selection().get_selected()
		#print self.slave_windows[0].get_children()
		try:
			self.slave_view.destroy()
		except:
			None

		if iter:
			self.main_tree_modes[model.get_value(iterat,0)]['open_func']()
	def master_tree_add(self, name, open_func):
		self.main_tree_store.append(None, [name])
		self.main_tree_modes[name] = {'open_func' : open_func}

	def master_tree_load(self):
		self.main_tree_store = Gtk.TreeStore(str)
		self.master_tree_add('Now Playing', self.slave_enter_now_playing_view)
		self.master_tree_add('Media', self.slave_enter_media_view)
		self.master_tree_add('Preferences', self.slave_enter_preferences_view)

#TODO: connect signals other than map automatically
	def is_slave_area(self, widget):
		loggy.debug('gui.is_slave_area')
		self.slave_windows.append(widget) #TODO: allow multiple separate master/slave combos
	def slave_enter_media_view(self):
		loggy.debug('gui.slave_enter_media_view')
		#TODO: check slave_window is a hbox
		self.slave_view = GTK_media_view(self.sb)
		self.slave_windows[0].pack_start(self.slave_view, True, True,0)
		self.slave_windows[0].show_all()
		self.builder.connect_signals(self)
	def slave_enter_now_playing_view(self):
		self.slave_view = GTK_now_playing(self.sb)
		self.slave_windows[0].pack_start(self.slave_view, True, True,0)
		self.slave_windows[0].show_all()
		self.builder.connect_signals(self)
		loggy.debug('gui.slave_enter_now_playing_view')
	def slave_enter_preferences_view(self):
		self.slave_view = GTK_preferences(self.sb)
		self.slave_windows[0].pack_start(self.slave_view, True, True,0)
		self.slave_windows[0].show_all()
		self.builder.connect_signals(self)
class GTK_media_view(Gtk.HBox):
	def __init__(self, sb):
		self.sb = sb
		self.gui = sb.gtkgui
		Gtk.HBox.__init__(self) # load glade
		self.builder = Gtk.Builder()
		self.builder.add_from_file('glade/media_view.glade')
		widget = self.builder.get_object("vbox1")
		widget.reparent(self)
		self.builder.connect_signals(self)
		self.keystoshow = ('artist', 'title', 'album', 'date', 'genre', 'duration', 'rating','mimetype', 'atime', 'mtime', 'ctime', 'dtime', 'size')
		self.keystoshowdict = {} # dic of name, col position
		for i, a in enumerate(self.keystoshow):
			self.keystoshowdict[a] = i
		#print self.keystoshowdict
		#print 'GOOB' + str( player.sbdb.keytypelist )
		#creates list store with as many string columns as there are keys for
		#print player.sbdb.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3")
		#self.list_store.append(self.sb.sbdb.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3"))

		arsy = (GObject.TYPE_STRING,)*len(self.sb.sbdb.keys)
		self.list_store = Gtk.ListStore(*arsy)
		print( ' row length = ' + str(self.list_store.get_n_columns()))
		self.sb.sbdb.iter(self.list_store.append)
	def is_listview(self, widget):
		loggy.debug('gui.GTK_media_view.is_listview')
		self.treeview = widget
		widget.connect('row-activated', self.treeview_activated)
		widget.set_model(self.list_store) # init treeview

		widget.tv_columns = {}
		for i, name in enumerate(self.sb.sbdb.keys): # go through all keys
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
		(model, iterat) = treeview.get_selection().get_selected()
		if iterat:
			self.sb.playlist.load_id(self.list_store.get_value(iterat,len(self.sb.sbdb.keys)-1))
			self.sb.playlist.playlist = [self.list_store.get_value(iterat,len(self.sb.sbdb.keys)-1)]
	def tv_clicked(self, widget, i):
		loggy.debug('gui.GTK_media_view.tv_clicked')
		widget.set_sort_column_id(i)
		#prevorder = widget.get_sort_order()
		#if prevorder = Gtk.SORT_ASCENDING:
		#	widget.set_sort_order(Gtk.SORT_DESCENDING)
		#else:
		#	widget.set_sort_order(Gtk.SORT_ASCENDING)

class GTK_preferences(Gtk.HBox): # thanks to http://stackoverflow.com/questions/2129369/Gtk-builder-and-multiple-glade-files-breaks
	def __init__(self, sb):
		self.sb = sb
		Gtk.HBox.__init__(self)
		self.builder = Gtk.Builder()
		self.builder.add_from_file('glade/preferences.glade')
		some_widget = self.builder.get_object("notebook1")
		some_widget.reparent(self)

		
		self.builder.connect_signals(self)
		#self.show_all()
		#self.add(some_widget)
		#some_widget.show()
		
#	def __destroy__(self):
#		loggy.log('GTK_media_view destroyed')
#		self.builder.destroy()
	def on_button3_clicked(self, button):
		loggy.debug('GTK_media_view.on_button3_clicked')
		self.sb.sbdb.recreate_db()
	def on_button1_clicked(self, button):
		Folderbox = Gtk.FileChooserDialog("Please select a folder containing media", self.sb.gtkgui.window, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		Folderbox.set_default_size(800,400)
		Folderbox.set_select_multiple(True)
		Folderbox.set_local_only(False)
		
		response = Folderbox.run()
		if response == Gtk.ResponseType.OK:
			loggy.log("Gui adding media folder: " + str(Folderbox.get_filenames()))
			self.sb.config.config['libraryfolders'] = self.sb.config.config['libraryfolders'] + Folderbox.get_filenames()
			
		Folderbox.destroy()
		True
	def on_button2_clicked(self, button):
		True
class GTK_now_playing(Gtk.DrawingArea):
	def __init__(self,sb):
		print ("in the monkey")
		Gtk.DrawingArea.__init__(self)
		sb.gtkgui.is_video_out(self)
		True

if __name__ == "__main__":
	temp = ''
	player1 = player.player
	#sbdb1 = sbdb.sbdb()
	temp.player = player1
	loggy.debug_setting = True
	app = GTKGui(temp)
	Gtk.main()


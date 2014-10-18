try:
	import loggy, player, random, soundblizzard
except:
	loggy.warn('Could not find required libraries: loggy, player, gobject')
from gi.repository import GObject, Gio
class playlist():
	playlist = []
	position = -1
	history = []
	playlists = {}
	def __init__(self, sb):
		self.sb = soundblizzard.soundblizzard # fakes for tab completion - assigns it to the class
		self.sb = sb #self.sb is now the parent soundblizzard instance
		self.sb.player.connect("eos", self.get_next)
		self.random = self.toggle(False) #TODO emit signal when these change - see set attr
		self.repeat = self.toggle(False)
		self.consume = self.toggle(False)
		self.single = self.toggle(False)
		self.read_playlist_dir()
	def read_playlist_dir(self):
		self.plfolder = Gio.File.new_for_path(path=self.sb.config.config['playlistfolder'])
		query = self.plfolder.query_file_type(Gio.FileQueryInfoFlags.NONE, None)
		if (query != Gio.FileType.DIRECTORY):
			loggy.warn('Playlist folder is not a directory:' + self.sb.config.config['playlistfolder'])
			return
		childrenenumerator = self.plfolder.enumerate_children('standard::display-name,time::modified', Gio.FileQueryInfoFlags.NONE, None)#fills childrenenumerator with fileinfos of child files of directory with information on display name and modified (only). Follows symlinks. See https://developer.gnome.org/pygobject/2.18/gio-constants.html#gio-file-attribute-constants. Content type does not seem to be particularly useful in this context
		while True:
			fl = childrenenumerator.next_file()
			if fl:
				if fl.get_display_name().lower().endswith('.m3u'):
					#loggy.log('found playlist'+ fl.get_display_name())
					self.read_playlist_from_giofile(self.plfolder.get_child_for_display_name(fl.get_display_name()), )
			else:
				loggy.log('Done reading playlist folder')
				break
		self.plmonitor = self.plfolder.monitor_directory(Gio.FileMonitorFlags.NONE, None)
		if self.plmonitor == None: loggy.warn('unable to monitor playlist directory')
		self.plmonitor.connect('changed', self.playlist_monitor_changed)
	def playlist_monitor_changed(self, monitor, file1, file2, event):
		#print ("Changed:",monitor, file1, file2, event)
		if event == Gio.FileMonitorEvent.CREATED or event == Gio.FileMonitorEvent.CHANGED:
			print ( 'file created/changed '+file1.get_path())
			if file1.get_path().lower().endswith('.m3u'):
				self.read_playlist_from_giofile(file1)
		elif event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
			True # ignore for now
		elif event == Gio.FileMonitorEvent.DELETED:
			print ('file deleted' + file1.get_path())
			self.sb.player.emit('deleted-playlist', file1.get_path())
			if file1.get_path() in self.playlists.keys(): del self.playlists[file1.get_path()]
		else:
			loggy.debug('File Monitor released unimplemented event'+str(monitor)+str(file1)+str(file2)+str(event))
	def read_playlist_from_giofile(self, giofile):
		name = giofile.get_path()
		(success, contents, tag) =  giofile.load_contents()
		contents = contents.decode().splitlines()
		#print(contents)
		if contents.pop(0).startswith('#EXTM3U'):
			#playlist found, wipe/create playlist with that name
			self.playlists[name] = []
			for line in contents:
				if line.startswith('/'):
					self.playlists[name].append('file://'+line)
				elif (line.startswith('#')): None
				else:
					loggy.warn('Could not analyse line in playlist '+name+' :'+line)
			loggy.log('Found '+str(len(self.playlists[name]))+' items in m3u playlist '+name)
			self.playlist=self.playlists[name]
			self.sb.player.emit('new-playlist',name)
	class toggle(GObject.GObject):
		toggle = False # holds boolean
		__gsignals__ = {'changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,(GObject.TYPE_BOOLEAN,)),}	
		def __init__(self, value=None):	
			GObject.GObject.__init__(self)
			if value:
				self.toggle = value
		def get(self):
			return self.toggle
		def set(self, value):
			value = bool(value)
			if self.toggle != value:
				self.toggle = value
				loggy.debug('playlist.set {0}'.format(value))
				self.emit('changed', value)				
	def load_playlist(self, array):
		self.playlist = array
		self.position = -1
		self.history = []
		self.get_next()
	def load_playlist_from_uri(self, uri):
		pass # TODO: implement playlist.load_playlist_from_uri
	def get_next(self, *data):
		if self.single.get():
			if self.repeat.get():
				None #stay on same file
			else:
				return #TODO: emit end of playlist signal
		elif self.random.get():
			self.position = random.randint(0, len[self.playlist]-1)
		else:
			self.position += 1
			if self.position >= (len(self.playlist)):
				if self.repeat.get():
					self.position = 0
				else:
					self.position = 0
					return #TODO: emit end of playlist signal
		#TODO: implement consume
		self.load_uri(self.playlist[self.position])
	def load_pos(self, pos):
		'''
		Starts playing playlist at position pos
		'''
		self.position = pos
		self.load_uri(self.playlist[self.position])
	def load_uri(self, uri):
		#self.sb.player.load_uri(self.sb.sbdb.get_id_db_info(id)['uri'])
		try:
			self.sb.player.load_uri(uri)
		except TypeError:
			loggy.warn('could not get next playlist item, skipping')
			self.get_next()
		#TODO: move to right position if in playlist
	def get_prev(self):
		self.position -= 1
		if (self.position<0):
			self.position = 0
		self.load_uri(self.playlist[self.position])
	def add_uri(self, uri, pos=None):
		loggy.debug('playlist.add_uri '+str(uri)+str(pos))
		songid = self.sb.sbdb.get_uri_db_info(uri)
		if songid:
			songid = songid['songid']
			if pos is not None:
				self.add_songid(songid, pos)
			else:
				self.add_songid(songid)
			return songid
		else:
			loggy.warn('could not add uri {0} to playlist - not in db')
			return False				
	def add_songid(self, songid, pos=None):
		loggy.debug('playlist.add_songid |{0}|{1}'.format(songid, pos))
		if pos is not None:
			self.playlist.insert(pos, songid)
		else:
			self.playlist.append(songid)
	def delete_pos(self, start, end=None):
		loggy.debug('playlist.delete_pos |{0}|{1}'.format(start, end))
		if end is not None:
			output = self.playlist[start:end]
			del self.playlist[start:end]
		else:
			output = self.playlist[start:start]
			del self.playlist[start]
		return output
	def delete_songid(self, songid):
		pos =  self.playlist.index(int(songid))
		del self.playlist[pos]
	def move(self, fromstart, fromend, moveto):
		if moveto is None:
			moveto = len(self.playlist)
		if fromend is None:
			fromend = fromstart + 1
		items = self.delete(fromstart, fromend)
		for item in items.reverse():
			self.playlist.insert(moveto, item)
	def move_id(self, songid, moveto):
		pos = self.playlist.index(int(songid))
		self.move(pos, pos, moveto)
	def shuffle(self):
		pass #TODO: implement playlist.shuffle
#TODO: docstrings and doctest
	

if __name__ == "__main__":
	player1 = player.player()
	player1.playlist = playlist(player1)

	GObject.MainLoop().run()
	#TODO: handle address lost


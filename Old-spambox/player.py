try:
	import pygst, gobject, loggy, config
	pygst.require("0.10")
	import gst
except:
	loggy.warn('player - Could not find required libraries: pygst, gst, gobject, loggy, config')

class player(gobject.GObject):
	'''
	Player - gst player
	'''
	__gproperties__ = {
						'vol' : (gobject.TYPE_INT, 'volume',
						'Current volume of gstreamer pipeline',
						0, 100, 50, gobject.PARAM_READWRITE)
					   }
	__gsignals__ = {
					'async-done' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
										()),
					'hemisecond' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
										())
					}
#    def do_get_property(self, property):
#        if property.name == 'vol':
#            return self.vol
#        else:
#            raise AttributeError, 'unknown property %s' % property.name
	def do_set_property(self, property, value):
		loggy.log('player.do_set_property')
		if property.name == 'vol':
			self.vol = value
			self.player.set_property('volume', float(value)/100)
		else:
			raise AttributeError, 'unknown property %s' % property.name
	def debug(self, widget, param):
		print 'temp' + str(widget) + str(param)
	def __init__(self):  #Thanks to http://pygstdocs.berlios.de/pygst-tutorial/playbin.html
		gobject.GObject.__init__(self)
		#gobject.signal_new("async-done", gobject.GObject, (gobject.SIGNAL_RUN_LAST | gobject.SIGNAL_ACTION | gobject.SIGNAL_DETAILED), gobject.TYPE_BOOLEAN, gobject.TYPE_NONE)
		self.connect('notify::vol', self.debug)
		self.debug = False
		self.on_update_play_state = []
		self.on_update_position = []
		self.on_update_volume = []
		self.on_update_tags = []
		self.vidout = {}
		self.position = 0
		#self.pipeline = gst.Pipeline('pipeline')
		self.player = gst.element_factory_make("playbin", "player")
		self.vis = gst.element_factory_make("goom", "vis")
		self.videosink = gst.element_factory_make("xvimagesink", 'videosink')
		#self.videosink = gst.element_factory_make('fakesink', 'videosink')
		#self.videosink.set_property('async', False) # required for fakesink otherwise pipeline stops
		self.audiosink = gst.element_factory_make("autoaudiosink", 'audiosink')
		#self.pipeline.add(self.player, self.vis, self.videosink, self.audiosink)
		self.player.set_property("vis-plugin", self.vis)
		self.player.set_property("video-sink", self.videosink)
		self.player.set_property("audio-sink", self.audiosink)
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect("message", self.on_message)
		self.reset()
		#self.videosink.connect('sync-message::element', self.load_file)
		#self.bus.connect("sync-message::element", self.on_sync_message)
		self.conf = config.config()
		self.conf.load()
		self.playlist = []
		self.random = False
		self.repeat = False
		self.dur = 1
		gobject.timeout_add(500, self.hemisecond_signal_emit)
	def hemisecond_signal_emit(self):
		#print 'DEMISECOND'
		self.emit('hemisecond')
		return True
	def load_file(self, filename):
		self.load_uri('file://' + filename) #TODO: make all uri
	def load_uri(self, uri):
		self.reset()
		loggy.log( "Player loading " + uri )
		self.uri = uri
		self.player.set_property("uri", uri)
		self.player.set_state(gst.STATE_PLAYING)
	def reset(self):
		self.player.set_state(gst.STATE_NULL)
		#for tag in self.
		self.tags = {}
	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_EOS: #TODO: reorder for speed , or take signals out individually...
			self.get_next()
		elif message.type == gst.MESSAGE_ERROR:
			self.reset()
			err, debug = message.parse_error()
			loggy.log( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug))
			self.get_next()
		elif message.type == gst.MESSAGE_STATE_CHANGED:
			self.update_play_state()
		elif message.type == gst.MESSAGE_STREAM_STATUS:
			self.update_position()
		elif message.type == gst.MESSAGE_NEW_CLOCK:
			None
		elif message.type == gst.MESSAGE_ASYNC_DONE:
			self.emit('async-done')
			for comm in self.on_update_tags:
				comm()
			loggy.log('Player Async Done')
		elif message.type == gst.MESSAGE_TAG: # thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
			taglist = message.parse_tag()
			for key in taglist.keys():
				self.tags[key] = taglist[key]
#                if key == 'image':
#                    img = open('temp', 'w')
#                    img.write(taglist[key])
#                    img.close()
#                else:
#                    True
					#loggy.log('Player GST tag:' + key + ' : ' + str(taglist[key]) )
			#gst_tag_list_free()?
		elif message.type == gst.MESSAGE_DURATION:
			format = gst.Format(gst.FORMAT_TIME)
			self.dur = self.player.query_duration(format)[0]
			self.dursec = int(self.dur / gst.SECOND)
		elif message.type == gst.MESSAGE_ELEMENT:
			if message.structure is None:
				return
			message_name = message.structure.get_name()
			if message_name == "prepare-xwindow-id":
				imagesink = message.src
				loggy.warn('Player prepare-xwindow-id got')
				imagesink.set_property("force-aspect-ratio", True)
				#gtk.gdk.threads_enter()
				if self.vidout.has_key('xid'): imagesink.set_xwindow_id(self.vidout['xid'])
				#imagesink.set_xwindow_id(self.VID.window.xid)
				#gtk.gdk.threads_leave()
			elif message_name == "have-xwindow-id":
				None
			else:
				loggy.log( "Player GST message unhandled:" + str(message.type))
		else:
			loggy.warn('Player - unknown messge' + str(message.type))
		#TODO: remove message from buffer?
		#self.update_play_state()
#    def on_sync_message(self, bus, message):
#        loggy.warn('Player got sync message, unhandled')
	def play(self):
		self.player.set_state(gst.STATE_PLAYING)
	def pause(self):
		self.player.set_state(gst.STATE_PAUSED)
	def stop(self):
		self.player.set_state(gst.STATE_NULL)
	def playpause(self):
		loggy.debug('player.playpause')
		if self.player.get_state()[1] == gst.STATE_PLAYING:
			self.player.set_state(gst.STATE_PAUSED)
		else:
			self.player.set_state(gst.STATE_PLAYING)
	def setpos(self, pos):
		if (pos<(self.dur) and pos>=0):
			self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, pos)
			loggy.log('seeking to |' + str(secs) + '|')
			return True #TODO: check pipeline changes?
		else:
			loggy.log('player.seeksecs could not understand seek to ' + str(secs))
			return False
	def getpos(self):
		pos = int(self.player.query_position(gst.FORMAT_TIME, None)[0])
		return pos
	def setvol(self, vol):
		loggy.debug('player.setvol')
		self.vol = vol
		#self.set_property('vol', vol)
		#vol = float(vol)/100
		#self.player.set_property('volume', vol)
		return True
	def getvol(self):
		vol = round(self.player.get_property('volume')*100)
		if (vol>100): vol = 100
		if (vol<0): vol = 0
		return vol
	def getstate(self):
		if self.player.get_state()[1] == gst.STATE_PLAYING:
			return 'play'
		elif self.player.get_state()[1] == gst.STATE_PAUSED:
			return 'pause'
		else:
			return 'stop'
	def update_play_state(self):
		#self.update_position()
		state = self.getstate()
		for comm in self.on_update_play_state:
			comm(state)
		#loggy.log('Play state changed')
	def update_position(self):
		pos = self.getpos()
		dur = self.dur
		if (dur<pos or dur<1): dur=pos +1
		for comm in self.on_update_position:
			comm(pos, dur)
		True #TODO: update hscale
	def update_volume(self):
		volume = self.getvol()
		for comm in self.on_update_volume:
			comm(volume)
	def load_playlist(self, filename):
		self.playlist = ['file:///data/Music/Alien Ant Farm/ANThology/01 Courage.mp3', 'file:///data/Music/Armand Van Helden/NYC Beat/02 - NYC Beat (Original).mp3', 'file:///data/Music/Various Artists/Reloaded 4/13. Flavor Of The Weak.mp3', 'file:///home/sam/Music/', 'file:///home/sam/Music/POPCORN.MP3']
		self.position = -1
		self.get_next()
	def get_next(self):
		if self.random:
			True
		else:
			self.position += 1
			if self.position >= (len(self.playlist)):
				if self.repeat:
					self.position = 0
					self.load_uri(self.playlist[self.position])
				else:
					self.position -= 1
			else:
				self.load_uri(self.playlist[self.position])
	def get_prev(self):
		if self.random:
			True
		else:
			self.position -= 1
			if (self.position < 0): self.position = 0
			self.load_uri(self.playlist[self.position])
#    def add_vid(self, xid):
#        self.videosink = gst.element_factory_make("xvimagesink", 'videosink')
#        self.videosink.set_property("force-aspect-ratio", True)
#        self.player.set_property("video-sink", self.videosink)
#        self.videosink.set_xwindow_id(xid)
#        self.vidout['xid'] = xid
gobject.type_register(player)

if __name__ == "__main__":
	player1 = player()
	player1.load_file('/data/Music/Girl Talk/All Day/01 - Girl Talk - Oh No.mp3')
	gobject.MainLoop().run()

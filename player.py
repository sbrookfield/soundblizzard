#!/usr/bin/python
from gi.repository import GObject
import pygst, loggy
pygst.require("0.10")
import gst
#TODO: manage import dependencies
#TODO: use xrange instead of range, see http://wiki.python.org/moin/PythonSpeed/PerformanceTips
#TODO: try profiling http://wiki.python.org/moin/PythonSpeed/PerformanceTips
class player(GObject.GObject):
	'''
	Player - gst player object
	'''
	SECOND = 1000000000
	__gproperties__ = {
						#'vol' : (GObject.TYPE_INT, 'volume','Current volume of gstreamer pipeline',	0, 100, 50, GObject.PARAM_READWRITE)
					}
	__gsignals__ = {
					'async-done' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when gstreamer emits async-done, after file and tags loaded'''
					'play-state-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when play/pause/stop state changes'''
					'volume-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when volume changes with volume as integer 0-100'''
					'position-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when position changes (every second) with time in nanoseconds, seconds and as formatted string'''
					'duration-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when play state changes with time in nanoseconds, seconds and as formatted string'''
					'eos' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,())
					#'''emitted when end of file reached'''
					}
	def __init__(self, soundblizzard):  #Thanks to http://pygstdocs.berlios.de/pygst-tutorial/playbin.html
		GObject.GObject.__init__(self)
		self.state = 'stop'
		self.soundblizzard = soundblizzard
		#self.debug = False
		self.vidout = {}
		self.player = gst.Pipeline('pipeline')
		self.playbin = gst.element_factory_make("playbin", "player")
		self.vis = gst.element_factory_make("goom", "vis")
		self.videosink = gst.element_factory_make("xvimagesink", 'videosink')
		#self.videosink = gst.element_factory_make('fakesink', 'videosink')
		#self.videosink.set_property('async', False) # required for fakesink otherwise pipeline stops
		self.audiosink = gst.element_factory_make("autoaudiosink", 'audiosink')

		self.playbin.set_property("vis-plugin", self.vis)
		self.playbin.set_property("video-sink", self.videosink)
		self.playbin.set_property("audio-sink", self.audiosink)
		self.player.add(self.playbin)
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect("message", self.on_message)
		self.reset()
		#self.videosink.connect('sync-message::element', self.load_file)
		#self.bus.connect("sync-message::element", self.on_sync_message)
		self.vol = 100
		self.durns = 1
		self.posns = 0
		self.dursec = 0
		self.possec = 0
		self.durstr = "0:00"
		self.posstr = "0:00"
		self.state = 'stop'
		GObject.timeout_add(1000, self.updatepos)
#		self.connect('position-changed', self.debug, '1more sec')
#		self.emit('position-changed')
#	def debug(self, message=None):
#		loggy.log(str(message))
	def load_file(self, filename):
		self.load_uri('file://' + filename) #TODO: make all uri
	def load_uri(self, uri):
		self.reset()
		loggy.log( "Player loading " + uri )
		self.uri = uri
		self.playbin.set_property("uri", uri)
		self.player.set_state(gst.STATE_PLAYING)
	def reset(self):
		self.player.set_state(gst.STATE_NULL)
		#for tag in self.
		self.tags = self.soundblizzard.sbdb.blanktags.copy()
	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_EOS: #TODO: reorder for speed , or take signals out individually...
			self.emit('eos')#called when end of stream reached
		elif message.type == gst.MESSAGE_ERROR:
			self.reset()
			err, debug = message.parse_error()
			loggy.warn( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug))
			self.emit('eos')
		elif message.type == gst.MESSAGE_STATE_CHANGED:
			if message.src == self.player:
				self.updatestate()
		elif message.type == gst.MESSAGE_STREAM_STATUS:
			#loggy.log('ss') appears to be related to buffering status
			#self.update_position()
			None
		elif message.type == gst.MESSAGE_NEW_CLOCK:
			None
		elif message.type == gst.MESSAGE_ASYNC_DONE:
			self.emit('async-done')
			loggy.log('Player Async Done')
		elif message.type == gst.MESSAGE_TAG: # thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
			taglist = message.parse_tag()
			for key in taglist.keys():
				self.tags[key] = taglist[key]
			#gst_tag_list_free()?
		elif message.type == gst.MESSAGE_DURATION:
			self.updatedur()
		elif message.type == gst.MESSAGE_QOS:
			loggy.log('QOS')
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
				loggy.log('have xwindow id')
			else:
				loggy.log( "Player GST message unhandled:" + str(message.type))
		else:
			loggy.warn('Player - unknown messge' + str(message.type))
		#TODO: remove message from buffer?
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
	def setpos(self, posns):
		'''Sets current position of track in nanoseconds'''
		if (posns<(self.durns) and posns>=0):
			self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, posns)
			loggy.log('seeking to |' + str(posns) + 'ns|')
			return True #TODO: check pipeline changes?
		else:
			loggy.log('player.seeksecs could not understand seek to ' + str(posns))
			return False
	def updatepos(self, *args):
		'''Updates current position of track to internal variables'''
		if self.state == 'stop':
			return False
		else:
			ns = int(self.player.query_position(gst.FORMAT_TIME, None)[0])
			if (self.posns != ns):
				self.posns = ns
				self.possec = int(self.posns / gst.SECOND)
				self.posstr = "%02d:%02d" % (self.possec // 60, self.possec % 60)
				self.emit('position-changed')
			return True
	def updatedur(self):
		'''Updates duration of current track to internal variables'''
		if self.state == 'stop':
			return 0
		else:
			ns = int(self.player.query_duration(gst.FORMAT_TIME)[0])
			if (self.durns != ns and ns != None):
				self.durns = int(ns)
				self.dursec = int(self.durns / gst.SECOND)
				self.durstr = "%02d:%02d" % (self.dursec // 60, self.dursec % 60)
				self.emit('duration-changed')
	def setvol(self, vol):
		loggy.debug('player.setvol: ' + str(vol))
		if (vol>100): vol = 100
		if (vol<0): vol = 0
		vol = int(round(vol))
		if (vol != self.vol):
			self.vol = vol
			self.playbin.set_property('volume', float(self.vol)/100)
			self.emit('volume-changed')
		return True
	def updatestate(self):
		state = self.player.get_state()[1]
		if state == gst.STATE_PLAYING:
			state = 'play'
		elif state == gst.STATE_PAUSED:
			state =  'pause'
		else:
			state = 'stop'
		if (self.state != state):
			self.state = state
			self.emit('play-state-changed')
			if (state != 'stop'):
				GObject.timeout_add(1000, self.updatepos)


GObject.type_register(player)

if __name__ == "__main__":
	player1 = player(None)
	player1.load_uri('file:///home/sam/Music/Popcorn.mp3')
	GObject.MainLoop().run()

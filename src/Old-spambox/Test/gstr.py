try:
	import pygst
	pygst.require("0.10")
	import gst
	import gobject
	import loggy
	import datetime
except:
	loggy.warn('Could not find required libraries: pygst, gst, gobject, datetime')

class gstr(object):
	'''
	Player - gst player
	'''
	def __init__(self):
		self.player = gst.element_factory_make("playbin", "player")
		#self.vis = gst.element_factory_make("goom", "vis")
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.enable_sync_message_emission()
		self.bus.connect("message", self.on_message)
		self.bus.connect("sync-message::element", self.on_sync_message)
		self.reset
	def load_file(self, filename):
		self.reset()
		loggy.log( "Player loading " + filename )
		self.player.set_property("uri", "file://" + filename)
		#self.player.set_state(gst.STATE_PLAYING)
		self.player.set_state(gst.STATE_PAUSED)
		#self.player.set_property("vis-plugin", self.vis)
	def reset(self):
		self.player.set_state(gst.STATE_NULL)
		self.tags = {}
		#self.button.set_label(gtk.STOCK_MEDIA_PLAY)
		#self.posstr = 0
		#self.durstr = 0
		#self.statusbar.push(0, "0:00 / 0:00")
	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_EOS:
			self.reset()
			#TODO get next song
		elif message.type == gst.MESSAGE_ERROR:
			self.reset()
			err, debug = message.parse_error()
			loggy.log( "Player GST_MESSAGE_ERROR: " + err + debug)
		elif message.type == gst.MESSAGE_STATE_CHANGED:
			self.update_play_state()
		elif message.type == gst.MESSAGE_STREAM_STATUS:
			self.update_play_state()
#        elif message.type == gst.MESSAGE_NEW_CLOCK:
#            None #TODO
#        elif message.type == gst.MESSAGE_QOS:
#            None #TODO
		elif message.type == gst.MESSAGE_ASYNC_DONE:
			None #TODO
		elif message.type == gst.MESSAGE_TAG: # thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
			taglist = message.parse_tag()
			for key in taglist.keys():
				self.tags[key] = taglist[key]
				if key == 'image':
					img = open('temp', 'w')
					img.write(taglist[key])
					img.close()
				else:
					loggy.log('Player GST tag:' + key + ' : ' + str(taglist[key]) )
			#gst_tag_list_free()
		elif message.type == gst.MESSAGE_DURATION:
			#loggy.log( 'GST duration' + str( duration[0] ))
			format = gst.Format(gst.FORMAT_TIME)
			self.dur = self.player.query_duration(format)[0]
			self.duration = datetime.timedelta(seconds=(self.dur / gst.SECOND))
			loggy.log(str(self.duration))
#        elif message.type == gst.MESSAGE_ELEMENT:
#            None #TODO
		else:
			loggy.log( "Player GST message unhandled:" + str(message.type))
		#self.update_play_state()
	def update_play_state(self):
		True
		#loggy.log('Play state changed')
	def on_sync_message(self):
		loggy.warn('Player got sync message, unhandled')
if __name__ == "__main__":
	gstr1 = gstr()
	gstr1.load_file('/data/Music/Girl Talk/All Day/01 - Girl Talk - Oh No.mp3')
	gobject.MainLoop().run()

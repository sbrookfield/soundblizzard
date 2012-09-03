#!/usr/bin/python
try:
	import pygst
	pygst.require("0.10")
	import gst
	import gobject
	import loggy
	import datetime
except:
	loggy.warn('Could not find required libraries: pygst, gst, gobject, datetime')

class tagger(object):
	'''
	Tagger - opens gstreamer pipeline, gets tags and duration
	''' #TODO Meta mux stream? Tidy all starts to files!, comments
	def init(self):  #wait till load_file?
		self.player = gst.parse_launch('uridecodebin name=source ! fakesink')
		self.source = self.player.get_by_name("source")
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_message)
	def load_file(self, filename, callback):
		self.load_uri("file://"+filename, callback)
	def load_uri(self, uri, callback):
		self.init()
		self.reset()
		self.uri = uri
		self.callback = callback
		loggy.log( "Player loading " + uri)
		self.source.set_property("uri", uri)
		self.player.set_state(gst.STATE_PAUSED)

	def test(self):
		print str(self.tags)# + str(self.duration)
		loggy.log('Got callback, would normally exit')
	def reset(self):
		self.player.set_state(gst.STATE_NULL)
		self.source.set_state(gst.STATE_NULL)
		self.player = None
		self.source = None
		self.tags = {}
		self.uri = ''
		self.init()
		#self.button.set_label(gtk.STOCK_MEDIA_PLAY)
		#self.posstr = 0
		#self.durstr = 0
		#self.statusbar.push(0, "0:00 / 0:00")
	def on_message(self, bus, message):
		if message.type == gst.MESSAGE_TAG: # thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
			taglist = message.parse_tag()
			for key in taglist.keys():
				self.tags[key] = taglist[key]
#                if key == 'image':
#                    img = open('temp', 'w')
#                    img.write(taglist[key])
#                    img.close()
#                else:
#                    loggy.log('Player GST tag:' + key + ' : ' + str(taglist[key]) )
			#gst_tag_list_free()
		elif message.type == gst.MESSAGE_ASYNC_DONE:
			self.tags['duration'] = int ((self.player.query_duration(gst.FORMAT_TIME)[0]) / gst.SECOND)
			self.tags['date'] = self.tags['date'].year
			self.player.set_state(gst.STATE_NULL)
			#TODO replace mime types with gstreamer alternative from gst.extend
			self.callback()
		elif message.type == gst.MESSAGE_DURATION:
			self.tags['duration'] = int ((self.player.query_duration(gst.FORMAT_TIME)[0]) / gst.SECOND)
			#loggy.log('duration xx' + str(self.tags['length']))
		elif message.type == gst.MESSAGE_ERROR:
			err, debug = message.parse_error()
			loggy.warn( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug)) #TODO sort out unicode
			self.callback()
		else:
			None
			#loggy.log( "Player GST message unhandled:" + str(message.type))
if __name__ == "__main__":
	tagger1 = tagger()
	tagger1.load_uri('file:///music/06 - Gorillaz - Superfast Jellyfish.mp3', tagger1.test)
	gobject.MainLoop().run()

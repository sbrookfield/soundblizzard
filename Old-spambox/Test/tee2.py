#!/usr/bin/env python

import sys
import gst
import time
class myPlayer ():
	def __init__(self):
		self.pipeline = gst.Pipeline()
		self.player = gst.element_factory_make("playbin", "player")
		self.vis = gst.element_factory_make("goom", "vis")
		self.videosink = gst.element_factory_make("tee", 'vidtee')
		self.audiosink = gst.element_factory_make("autoaudiosink", 'audiosink')
		self.aqueue = gst.element_factory_make("queue", 'aqueue')
		self.bqueue = gst.element_factory_make("queue", 'bqueue')
		self.avidsink = gst.element_factory_make('autovideosink', 'avidsink')
		self.bvidsink = gst.element_factory_make('autovideosink', 'bvidsink')
		self.acolorspace = gst.element_factory_make("ffmpegcolorspace","acolor")
		self.bcolorspace = gst.element_factory_make("ffmpegcolorspace","bcolor")
		#self.pipeline.add(self.acolorspace, self.bcolorspace, self.player, self.vis, self.videosink, self.audiosink, self.aqueue, self.bqueue, self.avidsink, self.bvidsink)
		self.pipeline.add(self.videosink, self.aqueue, self.bqueue, self.acolorspace, self.bcolorspace, self.avidsink, self.bvidsink)
		self.videosink.link(self.aqueue)
		self.videosink.link(self.bqueue)
		gst.element_link_many(self.aqueue, self.acolorspace, self.avidsink)
		gst.element_link_many(self.bqueue, self.bcolorspace, self.bvidsink)
		self.player.set_property("vis-plugin", self.vis)
		#self.player.set_property("video-sink", self.pipeline)
		self.player.set_property("audio-sink", self.audiosink)
		self.bus = self.player.get_bus()
		#self.bus.add_signal_watch()
		#self.bus.enable_sync_message_emission()
		#self.bus.connect("message", self.on_message)
		print self.player


	def playfile(self,file):
		self.player.set_property('uri', file)
		self.player.set_state(gst.STATE_PLAYING)
		pipelinestate = self.player.get_state()

		while pipelinestate[1] == gst.STATE_PLAYING:
			time.sleep(1)
			pipelinestate = self.player.get_state()
		sys.exit()

if __name__ == '__main__':
	player = myPlayer()
	player.playfile('file:///home/sam/Music/POPCORN.MP3')

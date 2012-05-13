#!/usr/bin/python

''' Main soundblizzard program'''
from gi.repository import GObject
class soundblizzard():

	def __init__(self):

		import player
		self.player = player.player(self)
		import config
		self.config = config.config(self)
		import mediakeys
		self.mediakeys = mediakeys.mediakeys(self)
		import debug
		debug.soundblizzard = self
		import mpdserver
		self.mpdserver = mpdserver.mpdserver(self)
		self.mpdserver.startserver('', 6600)
		import sbdb
		self.sbdb = sbdb.sbdb(self)
		import loggy
		loggy.debug_setting = True
		import gui
		self.gtkgui = gui.GTKGui(self)
		None

if __name__ == "__main__":
	soundblizzard = soundblizzard()
	soundblizzard.player.load_uri('file:///home/sam/Music/Popcorn.mp3')

	GObject.MainLoop().run()


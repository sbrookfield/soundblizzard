#!/usr/bin/python

''' Main soundblizzard program'''
from gi.repository import GObject


class soundblizzard():

	def __init__(self):
		self.mainloop = GObject.MainLoop()
		import loggy
		loggy.debug_setting = True
		loggy.sb = self
		import config
		self.config = config.config(self)
		import sbdb
		self.sbdb = sbdb.sbdb(self)
		import player
		self.player = player.player(self)
		import playlist
		self.playlist = playlist.playlist(self)
		import mediakeys
		self.mediakeys = mediakeys.mediakeys(self)
		import debug
		debug.soundblizzard = self
		import mpdserver
		self.mpdserver = mpdserver.mpdserver(self)
		self.mpdserver.startserver('localhost', 6601)
		#import dbus_mpris
		#self.dbus_mpris = dbus_mpris.dbus_mpris(self)
		import gui
		self.gtkgui = gui.GTKGui(self)
		
if __name__ == "__main__":
	sb = soundblizzard()
	#sb.playlist.load_playlist([0,1,2,3,4,5])
	#sb.playlist.get_next()
	sb.player.load_file('/home/sam/Music/Darwin Deez/Darwin Deez/04. DNA.mp3')
	sb.player.pause()
	#TODO player quits when no file to play instead of returning error
	sb.mainloop.run()


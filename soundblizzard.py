#!/usr/bin/python

''' Main soundblizzard program'''
from gi.repository import GObject
mainloop = GObject.MainLoop()

class soundblizzard():

	def __init__(self):
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
		#self.mpdserver.startserver('192.168.0.4', 6601)

		import loggy
		loggy.debug_setting = True
		#import dbus_mpris
		#self.dbus_mpris = dbus_mpris.dbus_mpris(self)
		import gui
		self.gtkgui = gui.GTKGui(self)
		

if __name__ == "__main__":
	sb = soundblizzard()
	sb.playlist.load_playlist('ben')

	mainloop.run()


'''
Created on 8 Apr 2012

@author: sam
'''
from gi.repository import GObject
GObject.threads_init()

SoundBlizzard = GObject.GObject()
SoundBlizzard.loop = GObject.MainLoop()
print (SoundBlizzard.loop)
if __name__ != '__main__':
	raise Exception('Leaving as not main')
import config, player, config#, mediakeys
#debug initialises automatically
SoundBlizzard.player = player.player()
SoundBlizzard.config = config.config()
#SoundBlizzard.mediakeys = mediakeys.mediakeys(SoundBlizzard)
SoundBlizzard.player.load_uri('file://home/sam/Popcorn.mp3')
import debug
debug.SoundBlizzard = SoundBlizzard
print (SoundBlizzard.loop)
#SoundBlizzard.loop.run()
GObject.MainLoop().run()


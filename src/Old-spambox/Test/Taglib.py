#!/usr/bin/env python
try:
	import Mutagen
except:
	print "Required libraries not found! Please install\n"
from mutagen.easyid3 import EasyID3
print EasyID3.valid_keys.keys()

from mutagen.easyid3 import EasyID3
audio = EasyID3("/home/sam/Music/new_orleans.mp3")
print audio["title"][0] # returns list of tags

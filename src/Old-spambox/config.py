try:
	import ConfigParser, os, loggy
except:
	loggy.warn('config - Could not find required libraries: ConfigParser')

class config( ConfigParser.SafeConfigParser ): #TODO use linux format, not ini (could not find suitable python module
	def load(self):
		self.file = os.path.expanduser('~') + "/.spambox/spambox.ini"
		self.read(self.file)
	def defaults(self):
		try:
			self.add_section('Main')
		except:
			None
		self.set('Main', 'dbfile', os.path.expanduser('~') + "/.spambox/spambox.sqlite")
		self.set('Main', 'imagefile', os.path.expanduser('~') + "/.spambox/image")
		self.set('Main', 'playlistsfolder', os.path.expanduser('~') + "/Music/Playlists")
		self.set('Main', 'libraryfolders', os.path.expanduser('~') + "/Music " + os.path.expanduser('~') + "/Videos ")
		self.set('Main', 'mediatags', ' '.join(['uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating']))
	def __del__(self):
		with open(self.file, 'wb') as configfile:
			self.write(configfile)

if __name__ == "__main__":
	conf = config()
	conf.load()
	conf.defaults()

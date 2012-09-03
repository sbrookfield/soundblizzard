try:
	import loggy, player, gobject
except:
	loggy.warn('Could not find required libraries: loggy, player, gobject')

class playlist(object):
	playlist = []
	random = False
	repeat = True
	def __init__(self, soundblizzard):
		self.player = soundblizzard.player
#		self.playlist = []
#		self.random = False
#		self.repeat = True
		self.player.connect("eos", self.get_next)
		#self.load_playlist('ben')
		#self.get_next()
	def load_playlist(self, filename):
		self.playlist = ['file:///music/Alex Turner/Submarine Soundtrack/02 Alex Turner - Hiding Tonight.mp3']
		self.position = -1
		self.get_next()
	def get_next(self, data=None):
		if self.random:
			True
		else:
			self.position += 1
			if self.position >= (len(self.playlist)):
				if self.repeat:
					self.position = 0
					self.player.load_uri(self.playlist[self.position])
			else:
				self.player.load_uri(self.playlist[self.position])
	def get_prev(self):
		self.position -= 1
		if (self.position<0):
			self.position = 0
		self.player.load_uri(self.playlist[self.position])

if __name__ == "__main__":
	player1 = player.player()
	player1.playlist = playlist(player1)

	gobject.MainLoop().run()
	#todo handle address lost


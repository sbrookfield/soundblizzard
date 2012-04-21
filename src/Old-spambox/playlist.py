try:
    import loggy, player, gobject
except:
    loggy.warn('Could not find required libraries: loggy, player, gobject')
    
class playlist(object):
    def __init__(self, player):
        self.player = player
        self.playlist = []
        self.random = False
        self.repeat = True
        self.player.bus.connect("message::eos", self.get_next)
        self.load_playlist('ben')
        self.get_next()
    def load_playlist(self, filename):
        self.playlist = ['file:///data/Music/Alien Ant Farm/ANThology/01 Courage.mp3', 'file:///data/Music/Armand Van Helden/NYC Beat/02 - NYC Beat (Original).mp3', 'file:///data/Music/Various Artists/Reloaded 4/13. Flavor Of The Weak.mp3']
        self.position = -1
    def get_next(self):
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
        
if __name__ == "__main__":
    player1 = player.player()
    player1.playlist = playlist(player1)

    gobject.MainLoop().run()
    #todo handle address lost
    
        
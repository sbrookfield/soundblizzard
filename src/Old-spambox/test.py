#!/usr/bin/python

try:
    import socket
    import gobject, loggy, player, sbdb
except:
    loggy.warn('Could not find required libraries: socket gobject loggy player database')
import gobject, loggy, player, sbdb, socket, mediakeys, config, mpdserver
if __name__ == "__main__":
    player1 = player.player()
    player1.db = sbdb.sbdb()
    player1.mediakeys = mediakeys.mediakeys(player1)
    mpdserver1 = mpdserver.mpdserver(player1)
    mpdserver1.startserver('', 6601)
    player1.load_playlist('ben')
    gobject.MainLoop().run()

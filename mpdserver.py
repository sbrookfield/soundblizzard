#!/usr/bin/python
'''
Created on 20 Mar 2011

@author: sam
'''
#try:
#TODO: out = "<html>%(head)s%(prologue)s%(query)s%(tail)s</html>" % locals() change all var substitutions to this, it's faster, see http://wiki.python.org/moin/PythonSpeed/PerformanceTips
import socket, loggy, soundblizzard, config
from gi.repository import GObject
#except:
#    loggy.warn('Could not find required libraries: socket GObject loggy player')

class mpdserver(object):
	'''
	MPD Server Class - creates MPD Server connection
	Settings - self.port = tcp_port
	self.host = tcp_host
	'''
	def __init__(self, sb):
		self.sb = soundblizzard.soundblizzard
		self.sb = sb
		self.queue = ''
		self.queueing = False
		self.ok_queueing = False
		self.startserver(self.sb.config.config['mpdhost'],int(self.sb.config.config['mpdport']))
	def startserver(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.sock.bind((self.host, self.port)) #TODO: check port empty first
		except:
			loggy.warn('mpdserver failed to start on host %s port %s' % (self.host, self.port))
			return False
		self.sock.listen(1)
		loggy.log('mpdserver Interface Running on ' + host + ':' + str(port) )
		GObject.io_add_watch(self.sock, GObject.IO_IN, self.listener)
	def listener(self, sock, *args):
		'''Asynchronous connection listener. Starts a handler for each connection.'''
		self.conn, temp = sock.accept()
		loggy.log( "mpdserver connected from " + str(self.conn.getsockname()))
		GObject.io_add_watch(self.conn, GObject.IO_IN, self.handler)
		self.conn.send('OK MPD 0.16.0\n')
		return True
	def handler(self, conn, *args):
		'''Asynchronous connection handler. Processes each line from the socket.'''
		buff = conn.recv(4096) #TODO: handle if more on conn to recieve than 4096
		if not len(buff):
			loggy.log( "mpdserver Connection closed - no input." )
			return False
		elif len(buff)>4000:
			loggy.warn('mpdserver Connection buff full, data may be lost' . buff)
		#loggy.log('MPD Server got:' +buff)
		while '\n' in buff:
			(line, buff) = buff.split("\n", 1)
			output = ''
			if not len(line):
				loggy.log( "mpdserver Connection closed - no input." )
				return False
			else:
				arg = line.rstrip().lstrip().split(' ', 1) #strips whitespace from right and left, then splits first word off as command
				command = arg[0].lower() # prevents case sensitivity
				#TODO: reimplement using a dict?
				if (len(arg)>1): # if there are arguments to the command
					args = arg[1].lstrip().rstrip()
				else:
					args = ''
				#Tries to recognise command
				#Playback control
				func = None
				loggy.debug('mpdserver got {0} {1}'.format(command, args))
				# Makes sure command is not internal function
				if command in ('startsever', 'trackdetails', 'handler', 'listner'):
					loggy.warn('mpdserver attempt to access internals {0}'.format(command))
				else:
					#Searches for command in current class
					try:
						func = getattr(self, command)
					except Exception as detail:
						output = 'ACK 50@1 {{{0}}} COMMAND NOT RECOGNISED {1} {2}\n'.format (command, detail, str(type(detail)))
						loggy.warn('mpdserver: {0}'.format(output))
						self.queueing = False
						self.ok_queueing = False
					else:
						#Executes command
						try:
							output = func(args)
						except Exception as detail:
							output = 'ACK 50@1 {{{0}}} {1} {2}\n'.format (command, detail, str(type(detail))) 
							loggy.warn('mpdserver: {0}'.format(output))
							self.queueing = False
							self.ok_queueing = False
				#Handles output - with respect to list queueing
				if output.startswith('ACK'):
					self.queueing = False
					self.ok_queueing = False
					output = self.queue + output
					self.queue = ''
				elif self.ok_queueing:
					#if output[-3:-1] == 'OK':
						#output = output[:-3] + 'list_OK\n'
					output = output.replace("OK", "list_OK")
					self.queue += output
					output = ''
				elif self.queueing:
					self.queue += output
					output = ''
				#send output
				if (output != None):
					loggy.debug( 'MPD Server sending: {0}'.format( output) )
					conn.send(output)
		return True
				#TODO: reflection, stickers, client to client
	def trackdetails (self, pl):
		output = ""
		for i in range (0, len(pl)):
			uri = pl[i]
			values = self.sb.sbdb.get_uri_db_info(uri)
			print str(values)+"\n"
			
			print type(values)
			if (values == None):
				output = 'ACK\n'
				return output
			output += "file: %s\nLast-Modified: %s\nTime: %s\nArtist: %s\nAlbumArtist: %s\nTitle: %s\nAlbum: %s Track: %s/%s\nDate: %s\nPos: %s\nId: %s\n" % \
			(values['uri'], values['mtime'], values['duration'], values['artist'], values['album-artist'], values['title'], values['album'], \
			values['track-number'], values['track-count'], values['date'],i,0)
		print output
		return output
		#TODO: tidy	this function					
						
								
#Command list functions
	def command_list_begin(self, arg):
		self.queueing = True
		return ''
	def command_list_ok_begin(self, arg):
		self.ok_queueing = True
		return ''
	def command_list_end(self, arg):
		self.queueing = False
		self.ok_queueing = False
		output = self.queue + 'OK\n'
		self.queue = ''
		return output
#Querying MPD Status
	def clearerror(self, arg):
		return 'OK\n'
	def currentsong(self, arg):
			output = 'file: %s\n' % (self.sb.player.uri)#TODO: convert from uri low priority
			output += 'Last-Modified: 2012-08-21T21:18:58Z\n' # TODO: change to format instead of % and not +=
			output += 'Time: %i\n' % (self.sb.player.dursec)
			output += 'Artist: %s\n' % str(self.sb.player.tags.get('artist'))
			output += 'AlbumArtist: %s\n' % str(self.sb.player.tags.get('album-artist'))
			output += 'Title: %s\n' % str(self.sb.player.tags.get('title'))
			output += 'Album: %s\n' % str(self.sb.player.tags.get('artist'))
			output += 'Track: %s\n' % (str(self.sb.player.tags.get('track-number'))+'/'+str(self.sb.player.tags.get('track-count')))
			output += 'Date: %s\n' % str(self.sb.player.tags.get('date').year)
			output += 'Genre: %s\n' % str(self.sb.player.tags.get('genre'))
			output += 'Pos: %i\n' % (self.sb.playlist.position)
			output += 'Id: %i\n' % (self.sb.sbdb.get_uri_db_info(self.sb.player.uri)['songid'])#TODO: put all info into tags
			output += 'OK\n'
			return output
	def idle(self, arg):
		return 'changed: database update stored_playlist playlist player mixer output options sticker subscription message\nOK\n'#TODO: handle properly
	def status(self, arg):
		output = 'volume: %i\n' % (self.sb.player.vol) #TODO: get rid of % and +=
		output += 'repeat: %i\n' % (int(self.sb.playlist.repeat))
		output += 'random: %i\n' % (int(self.sb.playlist.random))
		output += 'single: %i\n' % (int(self.sb.playlist.single))
		output += 'consume: %i\n' % (int(self.sb.playlist.consume))
		output += 'playlist: %i\n' % (1)
		output += 'playlistlength: %i\n' % (2)
		output += 'xfade: %i\n' % (0)
		output += 'state: %s\n' % (self.sb.player.state)
		output += 'song: %i\n' % (1)
		output += 'songid: %i\n' % (1)
		output += 'time: %s:%s\n' % (self.sb.player.possec, self.sb.player.dursec)
		output += 'elapsed: %s.000\n' % (self.sb.player.possec)
		output += 'bitrate: %i\n' % (1)
		output += 'audio: %s\n' % ('x')
		output += 'nextsong: %i\n' % (1)
		output += 'nextsongid: %i\n' % (1)
		output += 'OK\n'
		return output
	def stats(self, arg):
		return 'artists: %i\nalbums: %i\nsongs: %i\nuptime: %i\nplaytime: %i\ndb_playtime: %i\ndb_update: %i\nOK\n' % (1,1,1,1,1,1,1) #TODO: stats

	
	def play(self, arg):
		return 'OK\n'	
	def test(self, arg):
		command = ''
		args = ''
		if command == 'play':
			try:
				if args:
					self.sb.playlist.load_pos(pos)
				self.sb.player.play()
				output = 'OK\n'
			except Exception as detail:
				output = 'ACK 1@1 %s %s' % (command, detail) 
				loggy.warn('mpdserver: %s' % output)
		elif command == 'next':
			self.sb.playlist.get_next()
			output = 'OK\n' #TODO:handle errors? or not...
		elif command == 'pause':
			self.sb.player.pause()
			output = 'OK\n'
		elif command == 'playid':
			output = 'OK\n' #TODO:
		elif command == 'previous':
			self.sb.playlist.get_prev()
			output = 'OK\n'
		elif command == 'seek':
			#TODO: handle songpos
			try:
				self.sb.player.setpos(int(args))
				output = 'OK\n'
			except:
				output = 'ACK MPD setpos failed %s'% int(args)
				loggy.warn('mpserver ACK MPD setpos failed %s'% int(args))
		elif command == 'seekid': #TODO:
			output = 'OK\n'
		elif command == 'stop':
			self.sb.player.stop()
			output = 'OK\n'

		#Playback Options
		elif command == 'consume':
			print 'Recognised consume command'
			if args == '0':
				output = 'OK\n'
				self.sb.playlist.consume = 0
			elif args == '1':
				output = 'OK\n'
				self.sb.playlist.consume = 1
			else:
				output = 'ACK [2@0] {consume} usage consume 0 or consume 1\n'
		elif command == 'crossfade':
			output = 'OK\n'
		elif command == 'mixrampdb':
			output = 'OK\n'
		elif command == 'mixrampdelay':
			output = 'OK\n'
		elif command == 'random':
			loggy.log('MPDserver set playlist.random to ' + args)
			if args == '0':
				output = 'OK\n'
				self.sb.playlist.random = False
			elif args == '1':
				output = 'OK\n'
				self.sb.playlist.random = True
			else:
				output = 'ACK [2@0] {random} usage random 0 or random 1\n'
			output = 'OK\n'
		elif command == 'repeat':
			output = 'OK\n'
		elif command == 'setvol':
			vol = args.strip('"')
			if vol.isdigit() and int(vol) <=100 and int(vol) >=0 and self.sb.player.setvol(vol):
				output = 'OK\n'
			else:
				loggy.log('mpdserver - could not understand setvol to ' + args[0])
				output = 'ACK could not understand arguments\n'

		elif command == 'single':
			output = 'OK\n'
		elif command == 'replay_gain_mode':
			output = 'OK\n'
		elif command == 'replay_gain_status':
			output = 'OK\n'
		#Current Playlist
		elif command == 'add':
			output = 'OK\n'
		elif command == 'addid':
			output = 'OK\n'
		elif command == 'clear':
			output = 'OK\n'
		elif command == 'delete':
			output = 'OK\n'
		elif command == 'deleteid':
			output = 'OK\n'
		elif command == 'move':
			output = 'OK\n'
		elif command == 'moveid':
			output = 'OK\n'
		elif command == 'playlist':
			output = 'OK\n'
		elif command == 'playlistfind':
			output = 'OK\n'
		elif command == 'playlistid':
			output = 'OK\n'
		elif command == 'playlistinfo':
			output = 'OK\n'
		elif command == 'playlistsearch':
			output = 'OK\n'
		elif command == 'plchanges':
			output = self.trackdetails(self.sb.playlist.playlist)
			output += 'OK\n'
		elif command == 'plchangesposid':
			output = 'OK\n'
		elif command == 'shuffle':
			output = 'OK\n'
		elif command == 'swap':
			output = 'OK\n'
		elif command == 'swapid':
			output = 'OK\n'
		#Stored playlists
		elif command == 'listplaylist':
			output = 'OK\n'
		elif command == 'listplaylistinfo':
			output = 'OK\n'
		elif command == 'listplaylists':
			output = 'OK\n'
		elif command == 'load':
			output = 'OK\n'
		elif command == 'playlistadd':
			output = 'OK\n'
		elif command == 'playlistclear':
			output = 'OK\n'
		elif command == 'playlistdelete':
			output = 'OK\n'
		elif command == 'playlistmove':
			output = 'OK\n'
		elif command == 'rename':
			output = 'OK\n'
		elif command == 'rm':
			output = 'OK\n'
		elif command == 'save':
			output = 'OK\n'
		#Music db
		elif command == 'count':
			output = 'OK\n'
		elif command == 'find':
			output = 'OK\n'
		elif command == 'findadd':
			output = 'OK\n'
		elif command == 'list':
			output = 'OK\n'
		elif command == 'listall':
			output = 'OK\n'
		elif command == 'listallinfo':
			output = 'OK\n'
		elif command == 'lsinfo':
			output = 'OK\n'
		elif command == 'search':
			output = 'OK\n'
		elif command == 'update':
			output = 'OK\n'
		elif command == 'rescan':
			output = 'OK\n'
		elif command == '':
			output = 'OK\n'
		#Command queueing

		#Connection
		elif command == 'close':
			self.conn.send('OK\n')
			self.conn.close()
			loggy.log('MPD Connection closed by client')
			return False
		elif command == 'ping':
			output = 'OK\n'
		elif command == 'kill':
			conn.send('OK\n')
			conn.close()
			loggy.die('MPD Client Killed spambox, weep!')
		#Output
		elif command == 'disableoutput':
			output = 'OK\n'
		elif command == 'enableoutput':
			output = 'OK\n'
		elif command == 'outputs':
			output = 'OK\n'




	
if __name__ == "__main__":
	#player1 = player.player()
	#player1.load_file('/data/Music/Girl Talk/All Day/01 - Girl Talk - Oh No.mp3')
	mpdserver1 = mpdserver(None)
	mpdserver1.startserver('', 6600)
	GObject.MainLoop().run()
	#TODO: handle address lost

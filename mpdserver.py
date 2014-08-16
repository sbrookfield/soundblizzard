#!/usr/bin/python
'''
Created on 20 Mar 2011

@author: sam

Big thanks to the excellent documentation of MPD at http://www.musicpd.org/doc/protocol/index.html
'''
#try:
#TODO: out = "<html>%(head)s%(prologue)s%(query)s%(tail)s</html>" % locals() change all var substitutions to this, it's faster, see http://wiki.python.org/moin/PythonSpeed/PerformanceTips
import socket, loggy, re, config, soundblizzard
from gi.repository import GObject
import traceback #TODO: put this in loggy
import shlex
from time import strftime, gmtime

#except:
#    loggy.warn('Could not find required libraries: socket GObject loggy player')
#TODO: use is not ==

class mpdserver(object):
	'''
	MPD Server Class - creates MPD Server connection
	Settings - self.port = tcp_port
	self.host = tcp_host
	'''
	#internal_commands = ('__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'handler', 'host', 'trackdetails', 'listener', 'sb', 'startserver', 'sock', 'queue', 'queueing', 'port', 'ok_queueing', 'conn', 'internal_commands')
	list_of_commands = ('add', 'addid', 'channels', 'clear', 'clearerror', 'close', 'command_list_begin', 'command_list_end', 'command_list_ok_begin', 'commands', 'config', 'consume', 'count', 'crossfade', 'currentsong', 'decoders', 'delete', 'deleteid', 'disableoutput', 'enableoutput', 'find', 'findadd', 'idle', 'kill', 'list', 'listall', 'listallinfo', 'listplaylist', 'listplaylistinfo', 'listplaylists', 'load', 'lsinfo', 'mixrampdb', 'mixrampdelay', 'move', 'moveid', 'next', 'noidle', 'notcommands', 'outputs', 'password', 'pause', 'ping', 'play', 'playid', 'playlist', 'playlistadd', 'playlistclear', 'playlistdelete', 'playlistfind', 'playlistid', 'playlistinfo', 'playlistmove', 'playlistsearch', 'plchanges', 'plchangesposid', 'previous', 'prio', 'prioid', 'random', 'readmessages', 'rename', 'repeat', 'replay_gain_mode', 'replay_gain_status', 'rescan', 'rm', 'save', 'search', 'searchadd', 'searchaddpl', 'seek', 'seekcur', 'seekid', 'sendmessage', 'setvol', 'shuffle', 'single', 'stats', 'status', 'sticker', 'stop', 'subscribe', 'swap', 'swapid', 'tagtypes', 'unsubscribe', 'update', 'urlhandlers')
	#for mapping mpd to sbdb tags
	mpdtags = ('Artist', 'ArtistSort', 'Album', 'AlbumArtist', 'AlbumArtistSort', 'Title', 'Track', 'Name', 'Genre', 'Date', 'Composer', 'Performer', 'Disc', 'MUSICBRAINZ_ARTISTID', 	'MUSICBRAINZ_ALBUMID', 'MUSICBRAINZ_ALBUMARTISTID', 'MUSICBRAINZ_TRACKID')
	mpdlcasetags = ('artist', 'artistsort', 'album', 'albumartist', 'albumartistsort', 'title', 'track', 'name', 'genre', 'date', 'composer', 'performer', 'disc', 'musicbrainz_artistid', 'musicbrainz_albumid', 'musicbrainz_albumartistid', 'musicbrainz_trackid')
	sbtags = ('artist', 'artist', 'album', 'album', 'album', 'title', None, None, 'genre', 'date', None, None, None, None, None, None, None, None)
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
		print('fishes\n')
		self.conn.sendall(bytes('OK MPD 0.16.0\n', 'UTF-8'))
		#self.conn.
		return True
	def handler(self, conn, *args):
		'''Asynchronous connection handler. Processes each line from the socket.'''
		buff = conn.recv(65536).decode('UTF-8') #TODO: handle if more on conn to recieve than 4096
		
		if not len(buff):
			loggy.log( "mpdserver Connection closed - no input." )
			return False
		elif len(buff)>60000:
			loggy.warn('mpdserver Connection buff full, data may be lost' . buff)
		#loggy.log('MPD Server got:' +buff)
		while '\n' in buff:
			(line, buff) = buff.split("\n", 1)
		#lines = buff.split('\n')
		#for line in lines:
			output = ''
			if not len(line):
				loggy.log( "mpdserver Connection closed - no input." )
				return False
			else:
				arg = line.strip().split(' ', 1) #strips whitespace from right and left, then splits first word off as command
				command = arg[0].lower() # prevents case sensitivity
				#TODO: reimplement using a dict?
				if (len(arg)>1): # if there are arguments to the command
					args = arg[1].strip()
				else:
					args = ''
				#Tries to recognise command
				#Playback control
				func = None
				loggy.debug('mpdserver got {0} {1}'.format(command, args))
				# Makes sure command is not internal function
				if command in self.list_of_commands:
					#loggy.warn('mpdserver attempt to access internals {0}'.format(command))
				#Searches for command in current class
					try:
						func = getattr(self, command)
					except Exception as detail:
						output = 'ACK 50@1 {{{0}}} Command not recognised\n'.format (command)
						loggy.warn('mpdserver: {0}'.format(output))
						self.queueing = False
						self.ok_queueing = False
					else:
						#Executes command
						try:
							output = func(args)
						except Exception as detail:
							output = 'ACK 50@1 {{{0}}} {1} {2} {3}\n'.format(command, detail, str(type(detail)), traceback.format_exc().replace('\n', '|')) 
							loggy.warn('mpdserver: {0}'.format(output))
							self.queueing = False
							self.ok_queueing = False
				else: # not in list_of_commands
					output = 'ACK 50@1 {{{0}}} Command not in command list\n'.format (command)
					loggy.debug('mpdserver {0} not in command list'.format(command))
				#Handles output - with respect to list queueing
				if not output:
					output = 'ACK 1@1 {{{0}}} Command returned no output - not implemented yet\n'.format(command)
					loggy.warn('mpdserver: {0}'.format(output))
				elif output.startswith('ACK'):
					self.queueing = False
					self.ok_queueing = False
					output = self.queue + output
					self.queue = ''
				if self.ok_queueing:
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
					conn.sendall(bytes(output, 'UTF-8'))
		return True
				#TODO: reflection, stickers, client to client
	def trackdetails (self, pl):
		output = ''
		for index, item in enumerate(pl):
			values = self.sb.sbdb.get_id_db_info(item)
			if not values:
				values = self.sb.sbdb.blanktags
			mtime = strftime("%Y-%M-%dT%H:%M:%SZ", gmtime(values['mtime']))
			filename = values['uri']
			filename = filename[len('file:///' + self.sb.config.config['libraryfolders'][0]):]
			#print values
			#output = "%sfile: %s\nLast-Modified: %s\nTime: %s\nArtist: %s\nAlbumArtist: %s\nTitle: %s\nAlbum: %s Track: %s/%s\nDate: %s\nPos: %s\nId: %s\n" % \
			#(output, values['uri'], values['mtime'], values['duration'], values['artist'], values['album-artist'], values['title'], values['album'], \
			#values['track-number'], values['track-count'], values['date'],index, values['songid'])
			songinfo ='''{output}file: {filename}
Last-Modified: {mtime}
Time: {values[duration]}
Artist: {values[artist]}
AlbumArtist: {values[album-artist]}
Title: {values[title]}
Album: {values[album]}
Track: {values[track-number]}/{values[track-count]}
Date: {values[date]}
Pos: \nId: {values[songid]}\n'''
			output = songinfo.format(output=output, values=values, mtime = mtime, filename = filename)
			if item in self.sb.playlist.playlist:
				output = output.replace('Pos: \n','Pos: {0}\n'.format(self.sb.playlist.playlist.index(item)))
			else:
				output = output.replace('Pos: \n', '')
		return output

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
		return ' '#changed: database update stored_playlist playlist player mixer output options sticker subscription message\nOK\n'#TODO: handle properly
	def noidle(self,arg):
		return 'OK\n'
	def status(self, arg):
		output = 'volume: %i\n' % (self.sb.player.vol) #TODO: get rid of % and +=
		output += 'repeat: %i\n' % (int(self.sb.playlist.repeat.get()))
		output += 'random: %i\n' % (int(self.sb.playlist.random.get()))
		output += 'single: %i\n' % (int(self.sb.playlist.single.get()))
		output += 'consume: %i\n' % (int(self.sb.playlist.consume.get()))
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
		return 'artists: %i\nalbums: %i\nsongs: %i\nuptime: %i\nplaytime: %i\ndb_playtime: %i\ndb_update: %i\nOK\n' % (self.sb.sbdb.get_total_artists(),self.sb.sbdb.get_total_albums(),self.sb.sbdb.get_total_songs(),loggy.uptime(),1,self.sb.sbdb.get_total_duration(),self.sb.config.config['dbupdatetime']) #TODO: stats
#Playback options
	def consume(self, arg):
		self.sb.playlist.consume.set(int(arg))
		return 'OK\n'
	def crossfade(self, arg):
		return 'OK\n'
	def mixrampdb(self, arg):
		return 'OK\n'
	def mixrampdelay(self, arg):
		return 'OK\n'	
	def random(self, arg):
		self.sb.playlist.random.set(int(arg))
		return 'OK\n'
	def repeat(self, arg):
		self.sb.playlist.repeat.set(int(arg))
		return 'OK\n'
	def setvol(self, arg):
		self.sb.player.setvol(int(arg))
		return 'OK\n'
	def single(self, arg):
		self.sb.playlist.single.set(int(arg))
		return 'OK\n'
	def replay_gain_mode(self, arg):
		return 'OK\n'
	def replay_gain_status(self, arg):
		return 'OK\n'
#Controlling playback
	def next(self, arg):
		self.sb.playlist.get_next()
		return 'OK\n'
	def pause(self, arg):
		if len(arg)>0:
			if int(arg):
				self.sb.player.play()
			else:
				self.sb.player.pause()
		else:
			self.sb.player.playpause()
		return 'OK\n'
	def play(self, arg):
		if len(arg)>0:
			self.sb.playlist.load_pos(int(arg))
		else:
			self.sb.player.play()
		return 'OK\n'
	def playid(self, arg):
		self.sb.playlist.load_id(int(arg))
		return 'OK\n'
	def previous(self, arg):
		self.sb.playlist.get_prev()
		return'OK\n'
	def seek(self, arg):
		arg = arg.split()
		if len(arg)>1:
			self.sb.playlist.load_pos(int(arg[0]))
			self.sb.player.setpos(int(arg[1])*self.sb.player.SECOND)
			#TODO: seek doesn't work after load on this or seekid
		else:
			self.sb.player.setpos(int(arg[0])*self.sb.player.SECOND)
		return 'OK\n'
	def seekid(self, arg):
		arg = arg.split()
		if len(arg)>1:
			self.sb.playlist.load_id(int(arg[0]))
			self.sb.player.setpos(int(arg[1]) * self.sb.player.SECOND)
		else:
			self.sb.player.setpos(int(arg[0]) * self.sb.player.SECOND)
		return 'OK\n'
	def seekcur(self, arg):
		if len(arg) > 0:
			self.sb.player.setpos(int(arg) * self.sb.player.SECOND)
		return 'OK\n'
	def stop(self, arg):
		self.sb.player.stop()
		return 'OK\n'
#Current Playlist
	def add(self, arg):
		songid = self.sb.playlist.add_uri(str(arg).strip('\"\''))
		if songid is not False:
			output = 'OK\n'
		else:
			output = 'ACK could not add file - not located in db\n'
		return output
	def addid(self, arg):
		match = re.search('(.*)\s+(\d+)$', arg) #TODO: implement mpdserver.addid - does not remove pos
		if match:
			pos = int(match.group(2))
			uri = match.group(1).strip('\s\'\"')
		else:
			uri = arg.strip('\s\'\"')
			pos = None
		loggy.debug('mpdserver.addid {0}:{1}'.format(uri,pos))
		songid = self.sb.playlist.add_uri(uri, pos)
		if songid is not False:
			return'OK\n'
		raise Exception('could not add file - not located in db')
	def clear(self, arg):
		self.sb.playlist.load_playlist([])
		return 'OK\n'
	def delete(self, arg):
		arg = arg.split(':')
		if len(arg)>1:
			self.sb.playlist.delete_pos(int(arg[0]),int(arg[1]))
		else:
			self.sb.playlist.delete_pos(int(arg[0]))
		return 'OK\n'
#TODO: which is faster regex or string formatting - see above?
#		match = re.search('(\d+):*(\d*)', arg)
#		if match:
#			self.sb.playlist.delete(int(match.group(1)), int(match.group(2)))
#		else:
#			return 'ACK 50@1 {{delete}} incorrect format - delete [{POS} | {START:END}]\n'
	def deleteid(self, arg):
		self.sb.playlist.delete_songid(int(arg))
		return 'OK\n'
	def move(self, arg):
		match = re.search('(?P<fromstart>\d+):*(?P<fromend>\d*)\s*(?P<moveto>\d*)', arg)
		if match:
			fromstart = int(match.group('fromstart'))
			if match.group('fromend').isdigit():
				fromend = int(match.group('fromend'))
			else:
				fromend = fromstart+1
			if match.group('moveto').isdigit():
				moveto = int(match.group('fromend'))
			else:
				moveto = None
			self.sb.playlist.move(fromstart, fromend, moveto)
			return 'OK\n'
		else:
			return 'ACK 50@1 {{move}} incorrect format - move [{FROM} | {START:END}] {TO}\n'  #TODO: switch all these to raise
	def moveid(self, arg):
		songid,pos = arg.split
		self.sb.playlist.move_id(songid, pos)
		return 'OK\n'
		#TODO implement -ve item
	def playlist(self, arg):
		output = []
		for index, item in enumerate(self.sb.playlist.playlist):
			uri = self.sb.sbdb.get_id_db_info(item)
			if uri:
				uri = uri['uri']
			else:
				uri = ''
			output.append('{0}:file: {1}\n'.format(index,uri)) #TODO: ?need to strip uri to file?
		output.append('OK\n')
		return ''.join(output)
	def playlistfind(self, arg):
		return 'OK\n' #TODO: implement mpdserver.playlistfind
	def playlistid(self, arg):
		'''playlistid {SONGID} Displays a list of songs in the playlist. SONGID is optional and specifies a single song to display info for.'''
		arg = arg.strip('\'\" ')
		if len(arg)>0:
			output = self.trackdetails([int(arg)])
		else:
			output = self.trackdetails(self.sb.playlist.playlist)
		output += 'OK\n'
		return output
	def playlistinfo(self, arg):
		'''playlistinfo [[SONGPOS] | [START:END]] Displays a list of all songs in the playlist, or if the optional argument is given, displays information only for the song SONGPOS or the range of songs START:END'''
		temp = arg.split(':')
		if len(temp)>1:
			start = temp[0].strip('\'\" ')
			end = temp[1].strip('\'\" ')
		elif len(temp)>0:
			start = temp[0].strip('\'\" ')
			end = start+1
		else:
			start = 0
			end = len(temp)
		output = self.trackdetails(self.sb.playlist.playlist[start:end])
		output.append('OK\n')
		return ''.join(output)
	def playlistsearch(self, arg):
		return 'OK\n' #TODO: implement mpdserver.playlistsearch
	def plchanges(self, arg):
		return self.playlistid('') #TODO: implement mpdserver.plchanges
	def plchangesposid(self, arg):
		return self.playlistid('') #TODO: implement mpdserver.plchanges
	def prio(self, arg):
		return 'OK\n' #TODO: implement mpdserver.prio and mpdserver.prioid
	def prioid(self, arg):
		return 'OK\n'
	def swap(self, arg): # TODO: implement mpdserver.swap and mpdserver.swapid
		return 'OK\n'
	def swapid(self, arg):
		return 'OK\n'
	def shuffle(self,arg):
		pass
	def	listplaylist(self, arg):
		''' listplaylist {NAME} Lists the songs in the playlist. Playlist plugins are supported.'''
		pass
	def listplaylistinfo(self, arg):
		'''listplaylistinfo {NAME} Lists the songs with metadata in the playlist. Playlist plugins are supported.'''
		output =  'ACK [50@0] {listplaylistinfo} No such playlist\n'
		return output
	def listplaylists(self,arg):
		'''listplaylists Prints a list of the playlist directory. After each playlist name the server sends its last modification time as attribute "Last-Modified" in ISO 8601 format. To avoid problems due to clock differences between clients and the server, clients should not compare this value with their local clock.'''
		pass
	def load(self, arg):
		'''load {NAME} [START:END]Loads the playlist into the current queue. Playlist plugins are supported. A range may be specified to load only a part of the playlist.'''
		pass
	def playlistadd(self, arg):
		'''playlistadd {NAME} {URI} Adds URI to the playlist NAME.m3u. NAME.m3u will be created if it does not exist.'''
		pass
	def playlistclear(self,arg):
		'''playlistclear {NAME} Clears the playlist NAME.m3u.'''
		pass
	def playlistdelete(self, arg):
		'''playlistdelete {NAME} {SONGPOS} Deletes SONGPOS from the playlist NAME.m3u.'''
		pass
	def playlistmove (self, arg):
		'''playlistmove {NAME} {SONGID} {SONGPOS} Moves SONGID in the playlist NAME.m3u to the position SONGPOS.'''
		pass
	def rename(self, arg):
		'''rename {NAME} {NEW_NAME} Renames the playlist NAME.m3u to NEW_NAME.m3u.'''
		pass
	def rm(self, arg):
		'''rm {NAME} Removes the playlist NAME.m3u from the playlist directory.'''
		pass
	def save(self, arg):
		'''save {NAME} Saves the current playlist to NAME.m3u in the playlist directory.'''
		pass
	def count(self, arg):
		'''count {TAG} {NEEDLE} Counts the number of songs and their total playtime in the db matching TAG exactly.'''
		pass
	def find(self, arg):
		'''find {TYPE} {WHAT} [...] Finds songs in the db that are exactly WHAT. TYPE can be any tag supported by MPD, or one of the two special parameters  file to search by full path (relative to database root), and any to match against all available tags. WHAT is what to find.'''
		pass
	def findadd(self, arg):
		'''findadd {TYPE} {WHAT} [...] Finds songs in the db that are exactly WHAT and adds them to current playlist. Parameters have the same meaning as for find.'''
		pass
	def list(self, arg):
		'''list {TYPE} [ARTIST] Lists all tags of the specified type. TYPE can be any tag supported by MPD or file. ARTIST is an optional parameter when type is album, this specifies to list albums by an artist.'''
		args = shlex.split(arg)
		typetag = args[0].lower()
		if len(args)<2:
			args.append(None)
		if typetag in self.mpdlcasetags:
			pos = self.mpdlcasetags.index(typetag)
			if self.sbtags[pos]:
				arr = self.sb.sbdb.get_distinct(self.sbtags[pos], args[1])
				#print self.sbtags[pos]
				output=''
				for i in arr:
					output = '{0}{1}: {2}\n'.format(output,self.mpdtags[pos],i[0])
				output += 'OK\n'
				return output
			else:
				output = '{0}: \nOK\n'.format(self.mpdtags[pos])
				return output
		raise Exception('list function inadequate')
		return
	def listall(self, arg):
		'''listall [URI] Lists all songs and directories in URI.'''
		arg = arg.strip()
		urilist = self.sb.sbdb.get_files()
		output = ''
		if len(urilist) == 0:
			raise Exception('no media found in that location')
		elif arg:
			for uri in urilist:
				if uri[0].startswith(arg):
					output = '{0}file: {1}\n'.format(output, uri[0])
		else:
			for uri in urilist:
				output = '{0}file: {1}\n'.format(output, uri[0])
		return output
	def listallinfo(self, arg):
		'''listallinfo [URI] Same as listall, except it also returns metadata info in the same format as lsinfo.'''
		pass
	def lsinfo(self, arg):
		'''lsinfo [URI] Lists the contents of the directory URI. When listing the root directory, this currently returns the list of stored playlists. This behavior is deprecated; use "listplaylists" instead. Clients that are connected via UNIX domain socket may use this command to read the tags of an arbitrary local file (URI beginning with "file:///").'''
		pass
	def search(self, arg):
		'''search {TYPE} {WHAT} [...] Searches for any song that contains WHAT. Parameters have the same meaning as for find, except that search is not case sensitive.'''
		pass
	def searchadd(self, arg):
		'''searchadd {TYPE} {WHAT} [...] Searches for any song that contains WHAT in tag TYPE and adds them to current playlist. Parameters have the same meaning as for find, except that search is not case sensitive.'''
		pass
	def searchaddpl(self, arg):
		'''searchaddpl {NAME} {TYPE} {WHAT} [...] Searches for any song that contains WHAT in tag TYPE and adds them to the playlist named NAME. If a playlist by that name doesn't exist it is created. Parameters have the same meaning as for find, except that search is not case sensitive.'''
		pass
	def update(self, arg):
		'''update [URI] Updates the music database: find new files, remove deleted files, update modified files. URI is a particular directory or song/file to update. If you do not specify it, everything is updated. Prints "updating_db: JOBID" where JOBID is a positive number identifying the update job. You can read the current job id in the status response.'''
		pass
	def rescan(self, arg):
		'''rescan [URI] Same as update, but also rescans unmodified files.'''
		pass
#stickers not yet implemented
	def close(self, arg):
		'''close Closes the connection to MPD.'''
		pass
	def kill(self, arg):
		'''kill Kills MPD.'''
		pass
	def password(self, arg):
		'''password {PASSWORD} This is used for authentication with the server. PASSWORD is simply the plaintext password.'''
		pass
	def ping(self, arg):
		'''ping Does nothing but return "OK".'''
		return 'OK\n'	
# OUTPUTS
	def disableoutput(self, arg):
		'''disableoutput {ID} Turns an output off.'''
		pass
	def enableoutput(self, arg):
		'''enableoutput {ID} Turns an output on.'''
		pass
	def outputs(self, arg):
		'''outputs Shows information about all outputs.'''
		return '''outputid: 0\noutputname: My Pulse Output\noutputenabled: 1\nOK\n'''
#Reflection
	def config(self, arg):
		'''config Dumps configuration values that may be interesting for the client. This command is only permitted to "local" clients (connected via UNIX domain socket).'''
		pass
	def commands(self, arg):
		'''commands Shows which commands the current user has access to.'''
#		output = ''
#		temp = []
#		for i in self.list_of_commands:
#			output = '{output}command: {command}\n'.format(output=output, command=i)
#		output += 'OK\n'		
#		print temp
#		return output
		return '''command: add
command: addid
command: clear
command: clearerror
command: close
command: commands
command: consume
command: count
command: crossfade
command: currentsong
command: decoders
command: delete
command: deleteid
command: disableoutput
command: enableoutput
command: find
command: findadd
command: idle
command: kill
command: list
command: listall
command: listallinfo
command: listplaylist
command: listplaylistinfo
command: listplaylists
command: load
command: lsinfo
command: mixrampdb
command: mixrampdelay
command: move
command: moveid
command: next
command: notcommands
command: outputs
command: password
command: pause
command: ping
command: play
command: playid
command: playlist
command: playlistadd
command: playlistclear
command: playlistdelete
command: playlistfind
command: playlistid
command: playlistinfo
command: playlistmove
command: playlistsearch
command: plchanges
command: plchangesposid
command: previous
command: random
command: rename
command: repeat
command: replay_gain_mode
command: replay_gain_status
command: rescan
command: rm
command: save
command: search
command: seek
command: seekid
command: setvol
command: shuffle
command: single
command: stats
command: status
command: sticker
command: stop
command: swap
command: swapid
command: tagtypes
command: update
command: urlhandlers\nOK\n'''
		
	def notcommands(self, arg):
		'''notcommands Shows which commands the current user does not have access to.'''
		return 'OK\n'
	def tagtypes(self, arg):
		'''tagtypes Shows a list of available song metadata.'''
		output = ''
		for i in self.mpdtags:
			output = '{0}tagtype: {1}\n'.format(output, i)
		output += 'OK\n'
		return output
	def urlhandlers(self, arg):
		'''urlhandlers Gets a list of available URL handlers.'''
		return '''handler: http://\nhandler: mms://\nhandler: mmsh://\nhandler: mmst://\nhandler: mmsu://\nhandler: gopher://\nhandler: rtp://\nhandler: rtsp://\nhandler: rtmp://\nhandler: rtmpt://\nhandler: rtmps://\nOK\n'''
	def decoders(self, arg):
		'''decoders Print a list of decoder plugins, followed by their supported suffixes and MIME types. Example response: 
			plugin: mad
			suffix: mp3
			suffix: mp2
			mime_type: audio/mpeg
			plugin: mpcdec
			suffix: mpc'''
		pass

# CLIENT TO CLIENT
	def subscribe(self, arg):
		'''subscribe {NAME} Subscribe to a channel. The channel is created if it does not exist already. The name may consist of alphanumeric ASCII characters plus underscore, dash, dot and colon.'''
		pass
	def unsubscribe(self, arg):
		'''unsubscribe {NAME} Unsubscribe from a channel.'''
		pass
	def channels(self, arg):
		'''channels Obtain a list of all channels. The response is a list of "channel:" lines.'''
		pass
	def readmessages(self, arg):
		'''readmessages Reads messages for this client. The response is a list of "channel:" and "message:" lines.'''
		pass
	def sendmessage(self, arg):
		'''sendmessage {CHANNEL} {TEXT} Send a message to the specified channel.'''
		pass	
		
		
if __name__ == "__main__":
	#player1 = player.player()
	#player1.load_file('/data/Music/Girl Talk/All Day/01 - Girl Talk - Oh No.mp3')
	print('Test section mpdserver')
	mpdserver1 = mpdserver(None)
	mpdserver1.startserver('', 6600)
	GObject.MainLoop().run()
	#TODO: handle address lost

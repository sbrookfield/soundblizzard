try:
	import loggy, os, sqlite3, mimetypes, tagger
except:
	loggy.warn('sbdb - Could not find required libraries: loggy, os, sqlite3, mimetypes, tagger, gobject, config')
from gi.repository import GObject

class sbdb(GObject.GObject):
	__gsignals__ = {
					'database-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when database changes'''
					}
	#keys = ('uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating') # + mimetype , atime, mtime, ctime, dtime
	def __init__(self, soundblizzard):
		GObject.GObject.__init__(self)
		self.config = soundblizzard.config.config #provides direct access to config dictionary
		if (not(os.path.isdir(os.path.dirname(self.config['databasefile'])))):
			loggy.warn ('Creating directories for requested database file')
			os.makedirs(os.path.dirname(self.config['databasefile'])) or loggy.warn ('...could not create config dir')
		self.dbpath = self.config['databasefile'] #TODO test db folder exists and allow ~ to mean home
		loggy.log("Database: Loading database from " + self.dbpath)
		self.conn = sqlite3.connect(self.dbpath) or loggy.warn('Could not connect to database')
		self.conn.row_factory = sqlite3.Row
		self.curs = self.conn.cursor()
		self.conn.row_factory = sqlite3.Row
		self.keys = ('uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating','album-artist', 'track-count', 'track-number') # + mimetype , atime, mtime, ctime, dtime
		self.addkeys = ('mimetype', 'atime', 'mtime', 'ctime', 'dtime', 'size')
		self.totkeys = self.keys + self.addkeys
		self.blanktags ={} # creates blank key set so no type errors when key looked up does not exist
		for key in self.totkeys:
			self.blanktags[key] = None # TODO move gubbins to config
		self.conn.commit()
		#TODO check database is okay, contains tables and necessary fields etc.
		#self.conn.close()
	def sqlexec(self, string):
		loggy.log('Database sqlexec:' + string)
		self.curs.execute(string) # vulnerable to sql injection attacks - should assemble strings within execute -- use *args
		#self.conn.commit()
	def create_table(self, name, fields):
		self.sqlexec('create table if not exists "%s" ( "%s" )' % (name, '" , "'.join(fields)))
	def recreate_table(self, name, fields):
		self.sqlexec('drop table if exists "%s" ' % name)
		self.sqlexec('create table "%s" ("%s")' % (name, '" , "'.join(fields)))
	def insert_row(self, table, data):
		self.emit('database-changed')
		data = [str(item) for item in data]
		self.sqlexec('insert into "%s" values ( "%s" )' % (table, str('" , "'.join(data))))
	def delete_row(self, table, field, value):
		self.emit('database-changed')
		self.sqlexec('delete from "%s" where "%s"="%s"' % (table, field, value))
	def get_row(self, table, field, value):
		self.sqlexec('select * from "%s" where "%s"="%s"' % (table, field, value))
		return self.curs.fetchone()
	def iter(self, callback):
		self.curs.execute('select * from media')
		for row in self.curs:
			callback(row)
	def get_uri_db_info(self, uri):
		self.sqlexec('select * from "media" where "uri"="' + uri + '" ')
		#return zip((self.totkeys), self.curs.fetchone())
		return self.curs.fetchone()
	def get_uri_db_info_dict(self, uri):
		self.sqlexec('select * from "media" where "uri"="' + uri + '" ')
		print self.curs.fetchone()
		return zip((self.totkeys), list(self.curs.fetchone()))
	def recreate_db(self):
		self.recreate_table("media", (self.keys + self.addkeys)) #TODO delete database and restart from scratch
		#self.recreate_table("videos", self.keys)
		#self.insert_row('music', ['fart.avi', 'farter', 'fart song'])
		self.totag = []
		self.tagger = tagger.tagger()
		self.tagger.init()

		for folder in self.config['libraryfolders']:
			loggy.log('ELE '+folder)
			for path, dirs, files in os.walk(folder):
				for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files ]:
					mime = mimetypes.guess_type(filename)[0] #TODO get rid of mimetype
					if not mime:
						None
					elif mime.startswith("audio"):
						loggy.log("Database recreate_db Adding Audio :" + filename)
						self.totag.append(filename)
					elif mime.startswith("video"):
						loggy.log("Database recreate_db Adding Video :" + filename)
						self.totag.append(filename)
					else:
						None
	#                    loggy.log("Database recreate_db Unknown mime type:" +mime+", ignoring:" +filename)
		self.totaltotag = len(self.totag)
		loggy.log('Database:' + str(self.totaltotag) + ' files to scan')
		self.gettag()
	def gettag(self):
		if len(self.totag)>0:
			self.tagger.load_file(self.totag.pop(), self.settag)
		else:
			self.conn.commit()
			loggy.log('finished getting tags...')
			#gobject.MainLoop().quit()
			#print self.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3")


	def settag(self):
#        if len(self.tagger.tags):
#           loggy.log( str(self.tagger.tags))
		loggy.log(str(len(self.totag))+' of '+str(self.totaltotag)+' remaining')
		mime = mimetypes.guess_type(self.tagger.uri)[0] # take mime out into function?
		if not mime:
			loggy.warn('Mime type error in settag - no mime info')
		elif mime.startswith("audio"):
			type = 'audio'
		elif mime.startswith("video"):
			type = 'video'
		else:
			loggy.warn('Mime type error in settag - mime info incorrect')
		self.tagger.tags['uri'] = self.tagger.uri
		if len(type)>0:
			#try:
				row = []
				for key in self.keys:
					if key in self.tagger.tags:
						row.append(self.tagger.tags[key])
					else:
						row.append('')
				row.append(type)
				#(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(self.tagger.filename)
				row = row + [1,2,3,4,5]
				#print row
				self.insert_row('media', row)
				#self.insert_row(type, [self.tagger.filename, self.tagger.tags['artist'], self.tagger.tags['title']])
			#except:
				#loggy.log('OOOOOOOOOOOOOOOOOOOOOOOOOOOO')#TODO - deal with errors properly
		self.gettag()
		#TODO convert to gio/uris, see test/gio       stat, etc




if __name__ == "__main__":
	db = sbdb()
	db.recreate_db()



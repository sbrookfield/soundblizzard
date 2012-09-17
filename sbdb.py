try:
	import loggy, os, sqlite3, mimetypes, tagger
except:
	loggy.warn('sbdb - Could not find required libraries: loggy, os, sqlite3, mimetypes, tagger, gobject, config')
from gi.repository import GObject
#from gi.repository import Gio

class sbdb(GObject.GObject):
	__gsignals__ = {
					'database-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,()),
					#'''emitted when database changes'''
					}
	tagger = None
	def __del__(self,arg):
		self.conn.commit()
		self.conn.close()
		loggy.log('Database closing')
	def __init__(self, soundblizzard):
		GObject.GObject.__init__(self)
		self.config = soundblizzard.config.config #provides direct access to config dictionary
		if (not(os.path.isdir(os.path.dirname(self.config['databasefile'])))):
			loggy.warn ('Creating directories for requested database file')
			os.makedirs(os.path.dirname(self.config['databasefile'])) or loggy.warn ('...could not create config dir')
		self.dbpath = self.config['databasefile'] 
		loggy.log("Database: Loading database from " + self.dbpath)
		if loggy.debug:
			sqlite3.enable_callback_tracebacks(True)
		self.conn = sqlite3.connect(self.dbpath) or loggy.warn('Could not connect to database')
		self.conn.row_factory = sqlite3.Row
		self.curs = self.conn.cursor()
		self.conn.row_factory = sqlite3.Row
		self.keys = ('artist',
											'title',
											'album',
											'date', 
											'genre', 
											'duration', 
											'rating',
											'album-artist', 
											'track-count', 
											'track-number',
											'mimetype', 
											#'atime', 
											'mtime', 
											#'ctime', 
											#'dtime', 
											#'size',
											'uri',
											'songid')
		self.blanktags = {'artist':'',
											'title':'',
											'album':'',
											'date':0, 
											'genre':'', 
											'duration':0, 
											'rating':0,
											'album-artist':'', 
											'track-count':1, 
											'track-number':1,
											'mimetype':'', 
											#'atime':0, 
											'mtime':0, 
											#'ctime':0, 
											#'dtime':0, 
											#'size':0,
											'uri':'',
											'songid':None
											}
		#self.keys = self.blanktags.keys()[0:10]#('uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating','album-artist', 'track-count', 'track-number') # + mimetype , atime, mtime, ctime, dtime #TODO:autogenerate from blank dict
		#self.addkeys = self.blanktags.keys()[10:] #('mimetype', 'atime', 'mtime', 'ctime', 'dtime', 'size')
		#self.totkeys = self.keys + self.addkeys +('songid',)
#		self.blanktags = {} # creates blank key set so no type errors when key looked up does not exist
#		for key in self.totkeys:
#			self.blanktags[key] = None # TODO: move gubbins to config
#		self.conn.commit()
		#TODO: check database is okay, contains tables and necessary fields etc.
		try:
			self.curs.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media'")
			self.curs.execute("SELECT * from 'media'")
		except sqlite3.OperationalError:
			loggy.log('Database: no media table, recreating')
			self.recreate_media_table()
		#self.conn.close()
	def sqlexec(self, string):
		loggy.log('Database sqlexec:' + string)
		self.curs.execute(string) #TODO: vulnerable to sql injection attacks - should assemble strings within execute -- use *args
		#self.conn.commit()
	def get_distinct(self,col, artist=None):
		if col in self.keys:
			if artist:
				string ='select distinct {0} from media where artist = \'{1}\''.format(col,artist)
			else:
				string = 'select distinct {0} from media'.format(col)
			self.curs.execute(string)
			arr = self.curs.fetchall()
			return arr
		else:
			raise TypeError('sbdb.get_distinct column not in keys')
	def create_table(self, name, fields):
		self.sqlexec('create table if not exists "%s" ( "%s" )' % (name, '" , "'.join(fields)))
	def recreate_media_table(self):
		self.sqlexec('drop table if exists \'media\' ')
		self.sqlexec('create table if not exists "%s" ("%s" INTEGER PRIMARY KEY ASC )' % ('media', '" , "'.join(self.keys)))
		#NB id must be last to make primary key
	def recreate_table(self, name, fields):
		self.sqlexec('drop table if exists "%s" ' % name)
		self.sqlexec('create table "%s" ("%s")' % (name, '" , "'.join(fields)))
#	def insert_row(self, table, data):
#		self.emit('database-changed')
#		data = [str(item) for item in data]
#		self.sqlexec('insert into "%s" values ( "%s" )' % (table, str('" , "'.join(data))))
	def insert_media(self, data):
		data = tuple(data)
		string = "insert into 'media' values ( ?" + " , ? "*(len(data)-1) + " )"
		self.curs.execute(string, data)
	def delete_row(self, table, field, value):
		self.emit('database-changed')
		self.sqlexec('delete from "%s" where "%s"="%s"' % (table, field, value))
	def get_row(self, table, field, value):
		self.sqlexec('select * from "%s" where "%s"="%s"' % (table, field, value))
		return self.curs.fetchone()
	def iter(self, callback):
		self.curs.execute('select * from media')
		row_arr = []
		for row_array in self.curs:
			for i in row_array:
				row_arr.append(unicode(i))
			callback(row_arr)
			row_arr=[]
#	def get_types(self):
#		self.curs.execute('select * from media')
#		temp = self.curs.fetchone()
	def get_uri_db_info(self, uri):
		self.sqlexec('select * from "media" where "uri"="' + str(uri) + '" ')
		return self.curs.fetchone()
	def get_id_db_info(self, songid):
		self.sqlexec('select * from "media" where "songid"="' + str(songid) + '" ')
		return self.curs.fetchone()
		#return zip((self.totkeys), self.curs.fetchone())
#	def get_uri_db_info_with_id(self,uri):
#		self.sqlexec('select * from "media" where "uri"="' + uri + '" ')
#		return self.curs.lastrowid,self.curs.fetchone()
#	def get_uri_db_info_dict(self, uri):
#		self.sqlexec('select * from "media" where "uri"="' + uri + '" ')
#		print self.curs.fetchone()
#		return zip((self.totkeys), list(self.curs.fetchone()))
	def update_db(self):
		#self.recreate_media_table() 
		self.totag = []
		if not self.tagger:
			self.tagger = tagger.tagger()
		for folder in self.config['libraryfolders']:
			loggy.log('ELE '+folder)
			for path, dirs, files in os.walk(folder):
				for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files ]:
					row = self.get_uri_db_info('file://'+filename)
					if row:
						(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
						#print ' old {0}, new {1} mtimes'.format(row['mtime'], mtime)
						if mtime <= row['mtime']:
							continue
					mime = mimetypes.guess_type(filename)[0] #TODO: get rid of mimetype
					if not mime:
						loggy.log('Update database - no mime type for '+filename)
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
	def recreate_db(self):
		self.recreate_media_table() 
		self.totag = []
		if not self.tagger:
			self.tagger = tagger.tagger()
		for folder in self.config['libraryfolders']:
			loggy.log('ELE '+folder)
			for path, dirs, files in os.walk(folder):
				for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files ]:
					mime = mimetypes.guess_type(filename)[0] #TODO: get rid of mimetype
					if not mime:
						loggy.log('Update database - no mime type for '+filename)
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
	def settag(self):
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
		self.tagger.tags['mime'] = type
		#print self.tagger.uri[7:]
		(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(self.tagger.uri[7:])
		#filetemp = Gio.file_new_for_uri(self.tagger.uri) #file_new_for_uri
		#temp.query_info('*',flags=gio.FILE_QUERY_INFO_NONE, cancellable=None)
		#info = filetemp.query_info('standard::mtime')
		self.tagger.tags['mtime'] = mtime
		if len(type)>0:
			#try:
				row = []
				for key in self.keys:
					if key in self.tagger.tags:
						row.append(self.tagger.tags[key])
					else:
						row.append(None)
				self.insert_media(row)
				self.insert_media(row)
		self.gettag()
		#TODO: convert to gio/uris, see test/gio       stat, etc




if __name__ == "__main__":
	db = sbdb()
	db.get_types()
	db.recreate_db()



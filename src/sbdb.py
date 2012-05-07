try:
    import loggy, os, sqlite3, config, mimetypes, tagger, gobject, config
except:
    loggy.warn('sbdb - Could not find required libraries: loggy, os, sqlite3, mimetypes, tagger, gobject, config')
    
class sbdb(object):
    keys = ('uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating') # + mimetype , atime, mtime, ctime, dtime
    def __init__(self):
        self.config = config.config()
        self.config.load()
        self.dbpath = self.config.get('Main', 'dbfile')
        loggy.log("Database: Loading database from " + self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.curs = self.conn.cursor()
        self.conn.row_factory = sqlite3.Row
        self.keys = ('uri', 'artist', 'title', 'album', 'date', 'genre', 'duration', 'rating') # + mimetype , atime, mtime, ctime, dtime
        self.addkeys = ('mimetype', 'atime', 'mtime', 'ctime', 'dtime', 'size')
        self.totkeys = self.keys + self.addkeys
        self.conn.commit()
        #self.conn.close()
    def sqlexec(self, string):
        loggy.log('Database sqlexec:' + string)
        self.curs.execute(string) # vulnerable to sql injection attacks - should assemble strings within execute
        #self.conn.commit()
    def create_table(self, name, fields):
        self.sqlexec('create table if not exists "%s" ( "%s" )' % (name, '" , "'.join(fields)))
    def recreate_table(self, name, fields):
        self.sqlexec('drop table if exists "%s" ' % name)
        self.sqlexec('create table "%s" ("%s")' % (name, '" , "'.join(fields)))
    def insert_row(self, table, data):
        data = [str(item) for item in data]
        self.sqlexec('insert into "%s" values ( "%s" )' % (table, str('" , "'.join(data))))
    def delete_row(self, table, field, value):
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
    def recreate_db(self):
        self.recreate_table("media", (self.keys + self.addkeys)) #TODO delete database and restart from scratch
        #self.recreate_table("videos", self.keys)
        #self.insert_row('music', ['fart.avi', 'farter', 'fart song'])
        self.totag = []
        self.tagger = tagger.tagger()
        self.tagger.init()

        for folder in self.config.get('Main', 'libraryfolders').split(" "):
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
            gobject.MainLoop().quit()
            print self.get_uri_db_info("file:///home/sam/Music/POPCORN.MP3")
            
            
    def settag(self):
#        if len(self.tagger.tags):
#           loggy.log( str(self.tagger.tags))
        loggy.log(str(len(self.totag))+' of '+str(self.totaltotag)+' remaining')
        mime = mimetypes.guess_type(self.tagger.filename)[0] # take mime out into function?
        if not mime:
            loggy.warn('Mime type error in settag - no mime info')
        elif mime.startswith("audio"):
            type = 'audio'
        elif mime.startswith("video"):
            type = 'video'
        else:
            loggy.warn('Mime type error in settag - mime info incorrect')
        self.tagger.tags['uri'] = self.tagger.filename
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
                print row
                self.insert_row('media', row)
                #self.insert_row(type, [self.tagger.filename, self.tagger.tags['artist'], self.tagger.tags['title']])
            #except:
                #loggy.log('OOOOOOOOOOOOOOOOOOOOOOOOOOOO')#TODO - deal with errors properly
        self.gettag()
        #TODO convert to gio/uris, see test/gio       stat, etc
            
                              


if __name__ == "__main__":
    db = sbdb()
    db.recreate_db()
    gobject.MainLoop().run()

  

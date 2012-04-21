#!/usr/bin/env python
import os
import mimetypes
#import magic # only load when necessary
from mutagen.easyid3 import EasyID3
try:
    import sqlite3
except:
    print "Python sqlite3 library not found"

#sort out loading
class sbdb(object):
    def __init__(self):
        self.dbpath = "".join([os.path.expanduser('~'),"/.spambox/spambox.sqlite"])
        print "Loading database from {0}".format(self.dbpath)
        self.conn = sqlite3.connect(self.dbpath)
        self.curs = self.conn.cursor()
    def __del__(self):
        self.conn.commit()
        self.conn.close()
    def create_table(self, name, fields):
        #self.curs.execute("drop table if exists " + name) # remove drop tables
        string = "create table if not exists \"{0}\" ( \"{1}\" )".format(name, "\" , \"".join(fields))
        print string
        self.curs.execute(string)
        self.conn.commit()    
    def recreate_table(self, name, fields):
        self.curs.execute("drop table if exists " + name) # remove drop tables
        string = "create table if not exists \"{0}\" ( \"{1}\" )".format(name, "\" , \"".join(fields))
        print string
        self.curs.execute(string)
        self.conn.commit()
    def insert_row(self, table, data):
        string ="insert into \"{0}\" values ( \"{1}\" )".format(table,  "\" , \"".join(data))
        print string # get rid of spare variable
        self.curs.execute(string)
        self.conn.commit()
    def delete_row(self, table, field, value):
        string = "delete from \"{0}\" where \"{1}\"=\"{2}\"".format(table, field, value)
        print string # get rid of spare variable
        self.curs.execute(string)
        self.conn.commit
    def recreate_db(self):
        #self.create_table("library_folders", ["folder"])
        #self.insert_row("library_folders", ["/".join([os.path.expanduser('~'),"Music"])])
        self.recreate_table("music", ["filename", "artist", "title"])
        self.recreate_table("videos", ["filename", "artist", "title"])
        self.create_table("library_folders", ["folder"])
        self.curs.execute("select folder from library_folders")
        print EasyID3.valid_keys.keys()
        for row in self.curs:
            print row[0]
            for path, dirs, files in os.walk(row[0]):
                for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files ]:
                    print filename
                    mime = mimetypes.guess_type(filename)[0]
                    print mime
                    if not mime.find("audio"): 
                        tag = EasyID3(filename)
                        print " Adding Music {0} - {1} ".format(tag['artist'][0], tag['title'][0])
                        self.insert_row("music", [filename, tag['artist'][0], tag['title'][0]])
                    elif not mime.find("video"):
                        #tag = EasyID3(filename)
                        #if not tag['title']:
                        #    tag['title'] = filename
                        print " Adding Video " + filename
                        self.insert_row("videos", [filename, "", filename])
                    else:
                        print " Could not determine mime type, ignoring"                    
        self.conn.commit
if __name__ == "__main__":
    db = sbdb()
    db.recreate_db()

    
#remember to commit!
                    #if mime:
                    #    if mime.split("/")[0] == "audio"
                    #    elif mime.split("/")[0] == "video"
                    #    else:
                    #        print " not audio, ignoring"
                    #else:
                    #    print " Could not determine mime type, ignoring"
                    #add support for playlists
                    #ms = magic.open(magic.MAGIC_NONE)
                    #ms.load()
                    #type =  ms.file(filename)
                    #print type
                            #ms = magic.open(magic.MAGIC_NONE)
        #ms.load()
                #self.curs.execute("create table library_folders (folder)")
        #self.curs.execute
                        #if fnmatch.fnmatch(filename, pattern)
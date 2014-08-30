#!/usr/bin/python
from gi.repository import Gio
#import os
folder = Gio.File.new_for_uri('file:///home/sam/Music/Playlists')
query = folder.query_file_type(Gio.FileQueryInfoFlags.NONE, None)
if (query == Gio.FileType.DIRECTORY):
    print ('got a directory')
childrenenumerator = folder.enumerate_children('standard::display-name,time::modified', Gio.FileQueryInfoFlags.NONE, None)#fills childrenenumerator with fileinfos of child files of directory with information on display name and modified (only). Follows symlinks. See https://developer.gnome.org/pygobject/2.18/gio-constants.html#gio-file-attribute-constants. Content type does not seem to be particularly useful in this context
while True:
    ben = childrenenumerator.next_file()
    if ben:
        #print (ben.list_attributes('time::*'))doesn't seem to work
        print (ben.get_modification_time().to_iso8601())
        #print (ben.get_content_type())doesn't seem to work
        print (ben)
        print (ben.get_display_name())
        print (folder.get_child_for_display_name(ben.get_display_name()))
        if ben.get_display_name().lower().endswith('.m3u'): #' True if is a .m3u file'
            (success, contents, tag) = folder.get_child_for_display_name(ben.get_display_name()).load_contents() # reads contents of file into memory
            #Thanks to M3Uparser
            contents = contents.decode().splitlines()
            print (contents)
            #print (contents.pop().lower())
            if contents.pop(0).startswith('#EXTM3U'):
                print ('Found m3u playlist '+ ben.get_display_name()[:-4])
                for line in contents:
                    if (not line.startswith('#')):
                        if line.startswith('/'):
                            print ('adding file file://' + line)
                        elif (line.startswith('file:') or line.startswith('http:')
                            print ('adding uri ' + line)
                        print('not root for file')


    else: break
print ('end')

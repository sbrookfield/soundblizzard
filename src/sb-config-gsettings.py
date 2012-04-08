'''
Created on 8 Apr 2012


@author: sam
'''
from gi.repository import Gio
#Bind Gsettings
class sb_config_gsettings(object):
  '''Module which hold configuration settings using gconf backend
    Requires /usr/share/glib-2.0/schemas/apps.sb-config.gschema.xml to be in place
    and run glib-compile-schemas /usr/share/glib-2.0/schemas/ once file present
    Module is type specific as appears to be the convention
    Thanks to http://www.micahcarrick.com/gsettings-python-gnome-3.html'''

  def __init__(self):
    '''Initialises class'''
    from gi.repository import Gio
    self.settings = Gio.Settings.new("apps.soundblizzard")    
  def test(self):
    dbfile = conf.settings.get_string('dbfile')
    dbfile = Gio.File.new(path=dbfile)
    if (dbfile.query_file_type != gio.FILE_TYPE_REGULAR):
        print('dbfile not normal file')
if __name__ == "__main__":
    print('Testing...')
    conf = sb_config_gsettings()
    conf.settings.set_boolean('test-setting', True)
    conf.test()
    print('done\n')
    
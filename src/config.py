'''
Created on 8 Apr 2012
@author: sam
'''
from gi.repository import Gio
#Bind Gsettings
#?needs class
class config(object):
	'''Module which hold configuration settings using gconf backend
	Requires /usr/share/glib-2.0/schemas/apps.sb-config.gschema.xml to be in place
	and run glib-compile-schemas /usr/share/glib-2.0/schemas/ once file present
	Module is type specific as appears to be the convention
	Thanks to http://www.micahcarrick.com/gsettings-python-gnome-3.html'''
	def __init__(self, soundblizzard):
		'''Initialises class'''
		from gi.repository import Gio
		self.settings = Gio.Settings.new("apps.soundblizzard")
	def test(self):
		dbfile = self.settings.get_string('dbfile')
		print(dbfile)
		dbfile = Gio.file_new_for_uri(dbfile)
		if (dbfile.query_file_type(Gio.FileQueryInfoFlags.NONE, None) == Gio.FileType.REGULAR):
			print('dbfile not normal file'+ dbfile)
if __name__ == "__main__":
	print('Testing...')
	conf = config()
	conf.settings.set_boolean('test-setting', True)
	conf.test()
	print('done\n')

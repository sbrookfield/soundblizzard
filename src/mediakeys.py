import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject
class mediakeys(object):
    '''
    Connects to Gnome Media Keys on dbus for control
    '''
    def __init__(self, soundblizzard):  
        self.soundblizzard = soundblizzard #'''saves parent soundblizzard for access'''
        self.getkeys()
    def getkeys(self):
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
        self.bus_object.GrabMediaPlayerKeys('soundblizzard', 0, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
        self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakeys)
        
    def handle_mediakeys(self, caller, command):
        print (''.join(['Media Key Pressed: ', command]))
        if command =='Play':
            self.soundblizzard.player.playpause()
        elif command =='Next':
            print ('poo')
        #TODO implement other keys
if __name__ == "__main__":
    mediakeys( 'b')
    GObject.MainLoop().run()

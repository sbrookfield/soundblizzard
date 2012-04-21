#import pyGst
#pyGst.require("0.10")
#import Gst
from gi.repository import GObject, Gst
import loggy
#thanks to http://jderose.blogspot.co.uk/2011/09/porting-gstreamer-apps-to-pygi.html
class player(GObject.GObject):
    SECOND = 1000000000
    '''
    Player - Gst player
    '''
    __gsignals__ = { 
                    'async-done' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                                        ()),
                    'state-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                                        ()),
                    'vol-changed' : (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                                        ()),
                    }
#    def debug(self, widget, param):#TODO is this needed?
#        print (('temp' + str(widget) + str(param)))
    def __init__(self):  #Thanks to http://pyGstdocs.berlios.de/pyGst-tutorial/playbin.html
        GObject.GObject.__init__(self)
        GObject.threads_init()
        Gst.init(None)
        #GObject.signal_new("async-done", GObject.GObject, (GObject.SIGNAL_RUN_LAST | GObject.SIGNAL_ACTION | GObject.SIGNAL_DETAILED), GObject.TYPE_BOOLEAN, GObject.TYPE_NONE)
        self.debug = False
        self.vidout = {}
        self.position = 0
        self.player = Gst.ElementFactory.make("playbin", "player")
        self.vis = Gst.ElementFactory.make("goom", "vis")
        self.videosink = Gst.ElementFactory.make("xvimagesink", 'videosink')
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", 'audiosink')
        self.player.set_property("vis-plugin", self.vis)
        self.player.set_property("video-sink", self.videosink)
        self.player.set_property("audio-sink", self.audiosink)
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch_full(1)
        #self.bus.add_signal_watch()
        #self.bus.enable_sync_message_emission()
        self.bus.connect("message", self.on_message) # changed with gio, was message originally
        self.reset()
        #self.bus.connect("sync-message::element", self.on_sync_message)
        self.dur = 1
    def load_uri(self, uri):
        self.reset()
        loggy.log( "Player loading " + uri ) 
        self.uri = uri
        self.player.set_property("uri", uri)
        self.player.set_state(Gst.State.PLAYING)
    def reset(self):
        self.player.set_state(Gst.State.NULL)
        self.tags = {}
    def on_message(self, bus, message):
#        if message == None:
#            return
        print('go!')
        print (self.bus.pop())
        return
        if message.type == Gst.MESSAGE_EOS: #TODO reorder for speed , or take signals out individually...
            self.get_next() 
        elif message.type == Gst.MESSAGE_ERROR:
            self.reset()
            err, debug = message.parse_error()
            loggy.log( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug))
            self.get_next()
        elif message.type == Gst.MESSAGE_STATE_CHANGED:
            self.emit('state-changed')  
        elif message.type == Gst.MESSAGE_STREAM_STATUS:
            self.update_position()
        elif message.type == Gst.MESSAGE_NEW_CLOCK:
            None
        elif message.type == Gst.MESSAGE_ASYNC_DONE:
            self.emit('async-done')
            for comm in self.on_update_tags:
                comm()
            loggy.log('Player Async Done')
        elif message.type == Gst.MESSAGE_TAG: # thanks to http://www.jezra.net/blog/use_python_and_Gstreamer_to_get_the_tags_of_an_audio_file
            taglist = message.parse_tag()
            for key in taglist.keys():
                self.tags[key] = taglist[key]
        elif message.type == Gst.MESSAGE_DURATION:
            format = Gst.Format(Gst.FORMAT_TIME)
            self.dur = self.player.query_duration(format)[0]
            self.dursec = int(self.dur / Gst.SECOND)
        elif message.type == Gst.MESSAGE_ELEMENT:
            if message.structure is None:
                return
            message_name = message.structure.get_name()
            if message_name == "prepare-xwindow-id":
                imagesink = message.src
                loggy.warn('Player prepare-xwindow-id got')
                imagesink.set_property("force-aspect-ratio", True)
                #gtk.gdk.threads_enter()
                if self.vidout.has_key('xid'): imagesink.set_xwindow_id(self.vidout['xid'])
                #imagesink.set_xwindow_id(self.VID.window.xid)
                #gtk.gdk.threads_leave()
            elif message_name == "have-xwindow-id":
                None
            else:
                loggy.log( "Player GST message unhandled:" + str(message.type))
        else:
            loggy.warn('Player - unknown messge' + str(message.type))
        #TODO remove message from buffer?
        #self.update_play_state()
#    def on_sync_message(self, bus, message):
#        loggy.warn('Player got sync message, unhandled')
    def play(self):
        self.player.set_state(Gst.State.PLAYING)
    def pause(self):
        self.player.set_state(Gst.State.PAUSED)
    def stop(self):
        self.player.set_state(Gst.State.NULL)
    def playpause(self):
        loggy.debug('player.playpause')
        if self.player.get_state()[1] == Gst.State.PLAYING:
            self.pause()
        else:
            self.play()
    def getstate(self):
        if self.player.get_state()[1] == Gst.State.PLAYING:
            return 'play'
        elif self.player.get_state()[1] == Gst.State.PAUSED:
            return 'pause'
        else:
            return 'stop'
    def setpos(self, pos):
        if (pos<(self.dur) and pos>=0):
            self.player.seek_simple(Gst.FORMAT_TIME, Gst.SEEK_FLAG_FLUSH, (pos*SECOND))
            loggy.log('seeking to |' + str(pos) + '|')
            return True #TODO convert setpos/getpos to seconds
        else:
            loggy.log('player.seeksecs could not understand seek to ' + str(pos))
            return False
    def getpos(self):
        pos = int(self.player.query_position(Gst.FORMAT_TIME, None)[0])
        return (round (pos/SECOND))
    def setvol(self, vol):
        self.set_property('vol', vol)
        vol = float(vol)/100
        self.player.set_property('volume', vol)
        self.emit('vol-changed')
        return True
    def getvol(self):
        vol = round(self.player.get_property('volume')*100)
        if (vol>100): vol = 100
        if (vol<0): vol = 0
        return vol
GObject.type_register(player)
        
if __name__ == "__main__":
    player1 = player()
    player1.load_uri('file:///data/Music/Benny Benassi/Cinema/01. Cinema (Radio Edit).mp3')
    #import time
    #time.sleep(5)
    GObject.MainLoop().run()

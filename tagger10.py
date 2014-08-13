#!/usr/bin/python

try:
    import gi, loggy
    gi.require_version('Gst', '1.0')
    from gi.repository import GObject, Gst
except:
    loggy.warn('Tagger 3 could not import required libraries')

GObject.threads_init()
Gst.init(None)

dbtags = {'artist':'',
        'title':'',
        'album':'',
        'date':0, 
        'genre':'', 
        'duration':0, 
        'rating':0,
        'album-artist':'', 
        'track-count':1, 
        'track-number':1,
        #'mimetype':'', 
        #'atime':0, 
        #'mtime':0, 
        #'ctime':0, 
        #'dtime':0, 
        #'size':0,
        #'uri':'',
        #'songid':None
        }

class tagger(object):
    '''
    Tagger - opens gstreamer pipeline, gets tags and duration
    ''' #TODO: Meta mux stream? Tidy all starts to files!, comments
    def __init__(self):  #wait till load_file
        self.player = Gst.parse_launch('uridecodebin name=source ! fakesink name=sink')
        self.source = self.player.get_by_name("source")
        #self.sink = self.player.get_by_name("sink")
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch() # or as async message ?difference
        self.bus.connect("message", self.on_message)
    def load_file(self, filename, callback):
        self.load_uri("file://"+filename, callback)
    def load_uri(self, uri, callback):
        self.tags = {}
        self.uri = uri
        self.callback = callback
        loggy.warn( "Tagger loading " + uri)
        self.source.set_property("uri", uri)
        self.player.set_state(Gst.State.PLAYING)
    def test(self):
        print (str(self.tags))# + str(self.duration)
        print('Got callback, would normally exit')
    def on_message(self, bus, message):
        #Gst.MESSAGE_TAG:thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
        #msgtype = (Gst.message_type_get_name(message.type))
        if ((message.type == Gst.MessageType.STREAM_STATUS) or (message.type == Gst.MessageType.STATE_CHANGED) or (message.type == Gst.MessageType.STREAM_START)):
            True
        elif (message.type == Gst.MessageType.TAG):
            taglist = message.parse_tag()
            #other ways of accessing list are taglist.to_string() or taglist.foreach() or taglist.get_string('artist')
            for key in dbtags.keys():
                self.tags[key] = taglist.get_value_index(key, 0)
        elif (message.type == Gst.MessageType.ASYNC_DONE):   #Gst.MESSAGE_ASYNC_DONE:
            self.tags['duration'] = int ((self.player.query_duration(Gst.Format.TIME)[0]) / Gst.SECOND)
            #print str(self.player.query_duration(Gst.Format.TIME))
            self.tags['uri'] = self.uri
            #self.tags['date'] = self.tags['date'].year
            loggy.log('Tagger got ' + str(self.tags))
            self.player.set_state(Gst.State.NULL)
            #TODO: replace mime types with Gstreamer alternative from Gst.extend
            self.callback()
        elif (message.type == Gst.MessageType.DURATION):   #Gst.MESSAGE_DURATION: ?does this ever happen
            self.tags['duration'] = int ((self.player.query_duration(Gst.Format.TIME)[0]) / Gst.SECOND)
            loggy.warn('got duration huzzah!') #TODO not working at present
        elif (message.type == Gst.MessageType.ERROR):   #Gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            loggy.warn( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug)) #TODO: sort out unicode
            self.callback()
        else:
            loggy.warn( "Player GST message unhandled:" + str(message.type))

if __name__ == "__main__":
    tagger1 = tagger()
    tagger1.load_uri('file:///home/sam/Music/Darwin Deez/Songs for Imaginative People/04. No Love.mp3', tagger1.test)
    GObject.MainLoop().run()

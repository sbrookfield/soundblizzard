#!/usr/bin/python

try:
    import gi, loggy
    #gi.require_version('Gst', '1.0')
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
        self.player = Gst.Pipeline()
        self.playbin = Gst.ElementFactory.make("playbin", "player")    #TODO: implement with uridecodebin
        self.videosink = Gst.ElementFactory.make("autovideosink", 'videosink')
        #self.videosink = Gst.element_factory_make('fakesink', 'videosink')
        #self.videosink.set_property('async', False) # required for fakesink otherwise pipeline stops
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", 'audiosink')
        #self.audiosink.set_property('async', False)
        self.playbin.set_property("video-sink", self.videosink)
        self.playbin.set_property("audio-sink", self.audiosink)
        self.player.add(self.playbin)
        #self.sink = self.player.get_by_name("sink")
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch() # or as async message ?difference
        self.bus.connect("message", self.on_message)
    def load_file(self, filename, callback):
        self.load_uri("file://"+filename, callback)
    def load_uri(self, uri, callback):
        self.__init__()#TODO work out how to load file without recreating pipeline
        self.tags = {}
        self.uri = uri
        self.error = None
        self.callback = callback
        loggy.warn( "Tagger loading " + uri)
        self.playbin.set_property("uri", uri)
        self.player.set_state(Gst.State.PLAYING)
    def test(self):
        print (str(self.tags))# + str(self.duration)
        print('Got callback, would normally exit')
        testmainloop.quit()
    def get_duration(self):
        query = Gst.Query.new_duration(Gst.Format.TIME)
        (success, dur) = self.playbin.query(query)
        if success: return (dur / Gst.SECOND)
        else: return None
    def on_message(self, bus, message):
        #Gst.MESSAGE_TAG:thanks to http://www.jezra.net/blog/use_python_and_gstreamer_to_get_the_tags_of_an_audio_file
        #msgtype = (Gst.message_type_get_name(message.type))
        #print('message') 'TODO implement as dict rather than if elif for speed
        if ((message.type == Gst.MessageType.STREAM_STATUS) or (message.type == Gst.MessageType.STATE_CHANGED) or (message.type == Gst.MessageType.STREAM_START)):
            True
        elif (message.type == Gst.MessageType.TAG):
            print('tag MESSAGE')
            print (self.player.query_duration(Gst.Format.TIME))
            taglist = message.parse_tag()
            #other ways of accessing list are taglist.to_string() or taglist.foreach() or taglist.get_string('artist')
            for key in dbtags.keys():
                self.tags[key] = taglist.get_value_index(key, 0)
        elif (message.type == Gst.MessageType.ASYNC_DONE):   #Gst.MESSAGE_ASYNC_DONE:
            query = Gst.Query.new_duration(Gst.Format.TIME)
            print(self.playbin.query(query))
            print (self.player.query_duration(Gst.Format.TIME))
            #print (self.player.get_state(1))
            self.tags['duration'] = int ((self.playbin.query_duration(Gst.Format.TIME)[1]) / Gst.SECOND)
            #print str(self.player.query_duration(Gst.Format.TIME))
            self.tags['uri'] = self.uri
            #self.tags['date'] = self.tags['date'].year
            loggy.log('Tagger got ' + str(self.tags))
            #self.player.set_state(Gst.State.NULL)
            #TODO: replace mime types with Gstreamer alternative from Gst.extend
            self.callback()
        elif (message.type == Gst.MessageType.DURATION_CHANGED):   #Gst.MESSAGE_DURATION: ?does this ever happen
            
            self.tags['duration'] = int ((int(self.playbin.query_duration(Gst.Format.TIME)[1]) / Gst.SECOND))
            loggy.warn('got duration huzzah!') #TODO not working at present
        elif (message.type == Gst.MessageType.ERROR):   #Gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            loggy.warn( "Player GST_MESSAGE_ERROR: " + str(err) + str(debug)) #TODO: sort out unicode
            self.error = str(debug)
            if self.error:
                self.player.set_state(Gst.State.NULL)
                self.__init__()
                self.callback()
        else:
            loggy.warn( "Player GST message unhandled:" + str(message.type))

if __name__ == "__main__":
    # Setting GST_DEBUG_DUMP_DOT_DIR environment variable enables us to have a dotfile generated
    import os
    os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "tmp"
    os.putenv('GST_DEBUG_DUMP_DIR_DIR', 'tmp')
    
    tagger1 = tagger()
    tagger1.load_uri(Gst.filename_to_uri('/home/sam/Music/Darwin Deez/Songs for Imaginative People/04. No Love.mp3'), tagger1.test)
    global testmainloop
    testmainloop = GObject.MainLoop()
    testmainloop.run()

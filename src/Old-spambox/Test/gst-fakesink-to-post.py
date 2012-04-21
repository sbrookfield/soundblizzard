import gst
import gobject

player = gst.element_factory_make("playbin", "player")
vis = gst.element_factory_make("goom", "vis")
#self.videosink = gst.element_factory_make("autovideosink", 'videosink')
videosink = gst.element_factory_make('fakesink', 'videosink')
videosink.set_property('async', False) # required for fakesink otherwise hangs on pause (although not implemented in this code!
audiosink = gst.element_factory_make("autoaudiosink", 'audiosink')
player.set_property("vis-plugin", vis)
player.set_property("video-sink", videosink)
player.set_property("audio-sink", audiosink)
player.set_property("uri", 'file:///data/Music/Girl Talk/All Day/01 - Girl Talk - Oh No.mp3')
player.set_state(gst.STATE_PLAYING)
gobject.MainLoop().run()
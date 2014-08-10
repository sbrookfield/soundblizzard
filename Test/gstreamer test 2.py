#!/usr/bin/env python
# Simple example GTK3 + GStreamer 0.10.x Application for transcoding 
# GTK3 using gobject introspection for bindings, GStreamer using manual bindings 
# Also includes how to set up dotfile generation
#http://blogs.gnome.org/uraeus/2011/10/04/tutorial-for-python-gstreamer-and-gtk-3/
#christian schaller

import sys
import os
import which

# Setting GST_DEBUG_DUMP_DOT_DIR environment variable enables us to have a dotfile generated
os.environ["GST_DEBUG_DUMP_DOT_DIR"] = "/tmp"
os.putenv('GST_DEBUG_DUMP_DIR_DIR', '/tmp')
try:
    import gi
except:
    pass
try:
    from gi.repository import Gtk
except:
    sys.exit(1)
try:
    import pygst
    pygst.require("0.10")
    import gst
except:
    pass

# creating a basic transcoder class
class Transcoder:
    def __init__(self):
        self.pipeline = gst.Pipeline("TranscodingPipeline") # creating overall pipeline object

        # Creating GStreamer filesrc element and sets it to read a specific mp3 file
        self.filesrc = gst.element_factory_make("filesrc", "filesrc")
        self.filesrc.set_property("location", """/home/cschalle/Music/tok.mp3""")
        self.pipeline.add(self.filesrc) # add this first plugin to the pipeline object

        # Use highlevel decodebin2 element to choose which GStreamer elments to use
        # for decoding automatically
        self.decoder = gst.element_factory_make("decodebin2", "decoder")

        # Connect to signal that will let us know that decodebin2 got a pad we can connect
        # to which has the decoded media file on it
        self.decoder.connect("new-decoded-pad", self.OnDynamicPad)
        self.pipeline.add(self.decoder)

        # create an audioconvert element to convert bitrate if needed
        self.audioconverter = gst.element_factory_make("audioconvert", "audioconverter")
        self.pipeline.add(self.audioconverter)

        # create audioencoder, in this case the Vorbis encoder
        self.audioencoder = gst.element_factory_make("vorbisenc", "audioencoder")
        self.pipeline.add(self.audioencoder)

        # create ogg muxer to hold vorbis audio
        self.oggmuxer = gst.element_factory_make("oggmux", "oggmuxer")
        self.pipeline.add(self.oggmuxer)

        # create file output element to write new file to disk
        self.filesink = gst.element_factory_make("filesink", "filesink")
        self.filesink.set_property("location", """/home/cschalle/Music/tok.ogg""")
        self.pipeline.add(self.filesink)

        # Now that all elements for the pipeline are create we link them together
        self.filesrc.link(self.decoder)
        self.audioconverter.link(self.audioencoder)
        self.audioencoder.link(self.oggmuxer)
        self.oggmuxer.link(self.filesink)

        # set pipeline to playing which means all the connected elements in the pipeline
        # starts pushing data to each other
        self.pipeline.set_state(gst.STATE_PLAYING)

    # create a simple function that is run when decodebin gives us the signal to let us 
    # know it got audio data for us. Use the get_pad call on the previously 
    #created audioconverter element asking to a "sink" pad.
    def OnDynamicPad(self, dbin, pad, islast):
        pad.link(self.audioconverter.get_pad("sink"))

# extremely simple UI using a GtkBuilder UI generated with Glade, just two buttons. 
# One to start transcode and one to run pipeline debug
class SuperSimpleUI:
    def __init__(self):
       self.builder = Gtk.Builder()
       self.uifile = "supersimple-gtk3.ui"
       self.builder.add_from_file(self.uifile)
        self.window = self.builder.get_object ("MainWindow")
       self.window.connect ("destroy", self.dialog_destroyed) # this allows the application
                                                              # to be cleanly killed
       # Call the two buttons in the UI
       self.transcodebutton = self.builder.get_object("transcodebutton")
       self.debugbutton = self.builder.get_object("debugbutton")

       # Connect to the clicked signal on both buttons
       self.transcodebutton.connect ("clicked", self.on_TranscodeButton_clicked)
       self.debugbutton.connect ("clicked", self.on_debug_activate)

      # set window size to avoid it being so small it gets lost on the desktop
      self.window.set_default_size (580, 435)
      self.window.show ()

    def on_TranscodeButton_clicked(self, widget):
        self._transcoder = Transcoder()
        print "transcoding"

    def dialog_destroyed (self, dialog):
        Gtk.main_quit ()

    # this function generates the dot file, checks that graphviz in installed and
    # then finally generates a png file, which it then displays
    def on_debug_activate(self, widget):
        dotfile = "/tmp/supersimple-debug-graph.dot"
        pngfile = "/tmp/supersimple-pipeline.png"
        if os.access(dotfile, os.F_OK):
            os.remove(dotfile)
        if os.access(pngfile, os.F_OK):
            os.remove(pngfile)
        gst.DEBUG_BIN_TO_DOT_FILE (self._transcoder.pipeline, \
        gst.DEBUG_GRAPH_SHOW_ALL, 'supersimple-debug-graph')
        # check if graphviz is installed with a simple test
        try:
            dot = which.which("dot")
            os.system(dot + " -Tpng -o " + pngfile + " " + dotfile)
            Gtk.show_uri(None, "file://"+pngfile, 0)
        except which.WhichError:
            print "The debug feature requires graphviz (dot) to be installed."
            print "Transmageddon can not find the (dot) binary."

if __name__ == "__main__":
hwg = SuperSimpleUI()
Gtk.main()


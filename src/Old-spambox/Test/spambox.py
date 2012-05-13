#!/usr/bin/python
#
# main.py
# Copyright (C) Sam Brookfield 2010 <sbrookfield@gmail.com>
#
# Spambox is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spambox is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#!/usr/bin/env python

#TODO Press play when no file loaded causes error
try:
  import pygtk
  pygtk.require("2.0")
  import pygtk, gtk, gobject
  import pygst
  pygst.require("0.10")
  import gst
  import database
except:
  print "Required libraries not found! Please install\n"
class spambox(object):
  def __init__(self):
    self.gst_init()
    self.gtk_init()
    self.db = database.sbdb() # share database conn?
    self.mode_dic = { "Now Playing" : self.mode_now_playing,
      "Music" : self.mode_music,
      "Videos" : self.mode_videos,
      }
    #import mpdserver
    #mpdserver1 = mpdserver.mpdserver()
    #mpdserver1.startserver('', 8801)
    import mediakeys
    #mediakeys.mediakeys()
  def gtk_init (self):
    self.builder = gtk.Builder()
    self.builder.add_from_file("spambox.glade")
    dic = { "on_window1_destroy" : self.on_window1_destroy,
    "on_button1_clicked" : self.on_button1_clicked,
    "on_filechooserbutton1_file_set" : self.on_filechooserbutton1_file_set,
    "on_imagemenuitem11_activate" : self.on_imagemenuitem11_activate,
    "on_hscale1_change_value" : self.on_hscale1_change_value,
    "on_treeview1_cursor_changed" : self.on_treeview1_cursor_changed,
    "on_treeview2_row_activated" : self.on_treeview2_row_activated,
    }#python doesn't seem to have autoconnect... annoying!
    self.builder.connect_signals(dic)
    self.window = self.builder.get_object("window1")
    self.button = self.builder.get_object("button1")
    self.FCB = self.builder.get_object("filechooserbutton1")
    self.FCB.set_current_folder('/home/sam/Music/')
    self.VID = self.builder.get_object("drawingarea1")
    self.statusbar = self.builder.get_object("statusbar1")
    self.master_view = self.builder.get_object("treeview1")
    self.slave_view = self.builder.get_object("treeview2")
    self.hscale = self.builder.get_object("hscale1")
    self.window.set_title(u'Spambox Media Player')
    self.load_master_tree()
    self.load_slave_tree()
    self.window.show()
  def on_window1_delete_event(self, widget, data=None):
    print 'Delete event'
    return False
  def on_button1_clicked(self, widget, data=None):
    if self.player.get_state()[1] == gst.STATE_PLAYING:
      self.player.set_state(gst.STATE_PAUSED)
    else:
      self.player.set_state(gst.STATE_PLAYING)
    self.update_play_state()
  def play(self):
    self.player.set_state(gst.STATE_PLAYING)
  def pause(self):
    self.player.set_state(gst.STATE_PAUSED)
  def gst_init (self):
    self.player = gst.element_factory_make("playbin", "player")
    self.vis = gst.element_factory_make("goom", "vis")
    bus = self.player.get_bus()
    bus.add_signal_watch()
    bus.enable_sync_message_emission()
    bus.connect("message", self.on_message)
    bus.connect("sync-message::element", self.on_sync_message)
    self.gst_reset
  def gst_load_file(self, filename):
    self.gst_reset()
    print "Loading %s" % (filename)
    self.player.set_property("uri", "file://" + filename)
    self.player.set_state(gst.STATE_PLAYING)
    self.player.set_property("vis-plugin", self.vis)
  def gst_reset(self):
    self.player.set_state(gst.STATE_NULL)
    self.button.set_label(gtk.STOCK_MEDIA_PLAY)
    self.posstr = 0
    self.durstr = 0
    self.statusbar.push(0, "0:00 / 0:00")
  def update_play_state(self):
    if self.player.get_state()[1] == gst.STATE_PLAYING:
      self.button.set_label(gtk.STOCK_MEDIA_PAUSE)
    else:
      self.button.set_label(gtk.STOCK_MEDIA_PLAY)
    self.posstr = self.player.query_position(gst.FORMAT_TIME, None)[0]
    self.statusbar.push(0, ''.join([self.convert_ns(self.posstr), " / ", self.convert_ns(self.durstr) ]))
    self.hscale.set_value(self.posstr)
    if self.durstr == 0:
      self.durstr = self.player.query_duration(gst.FORMAT_TIME, None)[0]
      self.hscale.set_range(0, self.player.query_duration(gst.FORMAT_TIME, None)[0])
      #avoid calling query twice?
    #should do this with signals
  def on_hscale1_change_value (self, range, scroll, value, data=None):
    self.player.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, value)
  def convert_ns(self, t):
    # This method was submitted by Sam Mason.
    s,ns = divmod(t, 1000000000)
    m,s = divmod(s, 60)
    if m < 60:
      return "%02i:%02i" %(m,s)
    else:
      h,m = divmod(m, 60)
      return "%i:%02i:%02i" %(h,m,s)
  def on_filechooserbutton1_file_set(self, widget, data=None):
    self.gst_load_file(widget.get_filename())
  def on_window1_destroy(self, callback_data):
    print 'Thanks for using spambox, now quitting'
    gtk.main_quit()
  def on_message(self, bus, message):
    t = message.type
    if t == gst.MESSAGE_EOS:
      self.gst_reset()
    elif t == gst.MESSAGE_ERROR:
      self.gst_reset()
      err, debug = message.parse_error()
      print "Error: %s" % err, debug
    elif t == gst.MESSAGE_STATE_CHANGED:
      self.update_play_state()
    elif t == gst.MESSAGE_STREAM_STATUS:
      self.update_play_state()
    elif t == gst.MESSAGE_NEW_CLOCK:
      None #TODO
    #elif t == gst.MESSAGE_QOS:
    #	None #TODO
    elif t == gst.MESSAGE_ASYNC_DONE:
      None #TODO
    elif t == gst.MESSAGE_TAG:
      None #TODO
    elif t == gst.MESSAGE_DURATION:
      None #TODO
    elif t == gst.MESSAGE_ELEMENT:
      None #TODO
    else:
      print t #handle theses
    self.update_play_state()
  def on_sync_message(self, bus, message):
    if message.structure is None:
      return
    message_name = message.structure.get_name()
    if message_name == "prepare-xwindow-id":
      imagesink = message.src
      imagesink.set_property("force-aspect-ratio", True)
      gtk.gdk.threads_enter()
      imagesink.set_xwindow_id(self.VID.window.xid)
      gtk.gdk.threads_leave()
  def on_imagemenuitem11_activate (self, widget, data=None):
    import preferences
    preferences.Main()
#TODO should i be using separate gtkbuilder? or same? - see start of pref module
  def load_master_tree(self):
    self.master_store =  gtk.TreeStore(str)
    self.master_view.set_model(self.master_store)
    self.master_tv_column = gtk.TreeViewColumn('Spambox')
    self.master_view.append_column(self.master_tv_column)
    self.cell = gtk.CellRendererText()
    self.master_tv_column.pack_start(self.cell, True)
    self.master_tv_column.add_attribute(self.cell, 'text', 0)
    self.master_view.set_reorderable(True)
    self.master_store.append(None, ["Now Playing"])
    self.master_store.append(None, ["Music"])
    self.master_store.append(None, ["Videos"])
  def load_slave_tree(self):
    self.slave_store =  gtk.TreeStore(str,str,str)
    slave_tv_column_artist = gtk.TreeViewColumn('Artist')
    self.slave_view.append_column(slave_tv_column_artist)
    cell_artist = gtk.CellRendererText()
    slave_tv_column_artist.pack_start(cell_artist, True)
    slave_tv_column_artist.add_attribute(cell_artist, 'text', 0)

    slave_tv_column_title = gtk.TreeViewColumn('Title')
    self.slave_view.append_column(slave_tv_column_title)
    cell_title = gtk.CellRendererText()
    slave_tv_column_title.pack_start(cell_title, True)
    slave_tv_column_title.add_attribute(cell_title, 'text', 1)

    self.slave_view.set_search_column(0)
    slave_tv_column_artist.set_sort_column_id(0)
    self.slave_view.set_model(self.slave_store)


  def mode_music(self):
    self.VID.hide()
    self.slave_view.show()
    self.slave_store.clear()
    self.db.curs.execute("select artist,title,filename from music")
    for row in self.db.curs:
      self.slave_store.append(None, row)
  def mode_videos(self):
    self.VID.hide()
    self.slave_view.show()
    self.slave_store.clear()
    self.db.curs.execute("select artist,title,filename from videos")
    for row in self.db.curs:
      self.slave_store.append(None, row)
  def mode_now_playing(self):
    self.slave_view.hide()
    self.VID.show()
  def on_treeview2_row_activated(self, treeview, path, view_column):
    print "Wahey"
    slave_tree_selection = self.slave_view.get_selection()
    (model, iter) = slave_tree_selection.get_selected()
    if iter:
      print self.slave_store.get_value(iter,2)
      self.gst_load_file(self.slave_store.get_value(iter,2))
  def on_treeview1_cursor_changed(self, treeview):
    master_tree_selection = self.master_view.get_selection()
    (model, iter) = master_tree_selection.get_selected()
    if iter:
      self.mode_dic.get(self.master_store.get_value(iter,0))()

if __name__ == "__main__":
  spambox1 = spambox()
  gtk.main()

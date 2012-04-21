#!/usr/bin/env python
try:
	import pygtk
	pygtk.require("2.0")
	import gtk
	import database
except:
			print "Required libraries not found! Please install\n"
class Main(object):       
	def __init__(self):
		builder = gtk.Builder()
		builder.add_from_file("preferences.glade")
		dic = { "on_window1_destroy" : loggy.quit,  
		"on_button1_clicked" : self.on_button1_clicked,
		"on_button2_clicked" : self.on_button2_clicked,
		"on_button3_clicked" : self.on_button3_clicked,
		}
		builder.connect_signals(dic)
		self.window = builder.get_object("window1")
		self.window.show()
		self.liststore =  gtk.ListStore(str)
		self.treeview = builder.get_object("treeview1")
		self.treeview.set_model(self.liststore)
		self.tvcolumn = gtk.TreeViewColumn('Folders')
		self.treeview.append_column(self.tvcolumn)
		self.liststore.connect("row_changed", self.update_library_folders)
		self.liststore.connect("row_deleted", self.update_library_folders)
		self.liststore.connect("rows_reordered", self.update_library_folders)
		self.cell = gtk.CellRendererText()
		self.tvcolumn.pack_start(self.cell, True)
		self.tvcolumn.add_attribute(self.cell, 'text', 0)
		
		self.db = database.sbdb() #load library folders from db
		self.db.curs.execute("select folder from library_folders")
		for row in self.db.curs:
			self.liststore.append(row)			
		
	def on_button1_clicked(self, widget):
		self.dialog = gtk.FileChooserDialog("Add Folder", None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK) )
		self.dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
		self.dialog.set_default_response(gtk.RESPONSE_OK)
		self.response = self.dialog.run()
		if self.response == gtk.RESPONSE_OK:
			self.liststore.append([self.dialog.get_filename()])
			self.db.insert_row("library_folders", [ self.dialog.get_filename() ])
		self.dialog.destroy()
	def on_button2_clicked(self, widget):
		self.treeselection = self.treeview.get_selection()
		(model, iter) = self.treeselection.get_selected()
		if iter:
			#print "delete from library_folders where folder={0}".format(self.liststore.get_value(iter,0))
			#self.db.curs.execute("delete from library_folders where folder={0}".format(self.liststore.get_value(iter,0)))
			self.db.delete_row("library_folders", "folder", self.liststore.get_value(iter,0))
			self.db.conn.commit()
			self.liststore.remove(iter)
	def on_button3_clicked(self, widget):
		self.db.recreate_db()
	def print_iter (self, model, path, iter):
		print self.liststore.get_value(iter, 0)
	def update_library_folders (self, liststore, path, iter=None, data=None):
		self.liststore.foreach(self.print_iter)
if __name__ == "__main__":
	Main()
	gtk.main()


#!/usr/bin/env python

# Copyright (c) 2009 Johannes Sasongko <sasongko@gmail.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Simple GIO file browser demonstration."""

from __future__ import division, with_statement

import locale
import gio, gtk

class FileBrowser(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)
		
		# Columns:
		# 0 = the GFile object
		# 1 = filename
		# 2 = size
		self.model = model = gtk.ListStore(gio.File, str, str)
		
		view = gtk.TreeView(model)
		view.set_rules_hint(True)
		view.connect('row-activated', self._row_activated)
		
		cell = gtk.CellRendererText()
		view.insert_column_with_attributes(-1, "Filename", cell, text=1)
		cell = gtk.CellRendererText()
		cell.props.xalign = 1
		view.insert_column_with_attributes(-1, "Size", cell, text=2)
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.add(view)
		sw.show_all()
		self.add(sw)
	
	def _row_activated(self, view, path, column):
		model = view.get_model()
		row = model[path]
		if row[2] == '<dir>':
			self.browse(row[0])
		else:
			print "Activating %s" % row[0].get_parse_name()
	
	def browse(self, directory):
		subdirs = []
		files = []
		
		infos = directory.enumerate_children('standard::is-hidden,'
				'standard::name,standard::display-name,standard::type,'
				'access::can-execute,standard::size')
		for info in infos:
			if info.get_is_hidden():
				continue
			name = info.get_name()
			child = directory.get_child(name)
			display = info.get_display_name()
			sortname = locale.strxfrm(display.decode('utf-8'))
			if info.get_file_type() == gio.FILE_TYPE_DIRECTORY:
				subdirs.append((sortname, child, display + '/'))
			else:
				if info.get_attribute_boolean('access::can-execute'):
					display += '*'
				size = round(info.get_size() / 1024)
				size = locale.format_string(u"%d KiB", size, True)
				files.append((sortname, child, display, size))
		
		subdirs.sort()
		files.sort()
		
		info = directory.query_info('standard::display-name')
		self.set_title(info.get_display_name())
		
		self.model.clear()
		parent = directory.get_parent()
		if parent:
			self.model.append((parent, '../', "<dir>"))
		for sortname, child, display in subdirs:
			self.model.append((child, display, "<dir>"))
		for sortname, child, display, size in files:
			self.model.append((child, display, size))
	
	def main(self):
		self.connect('destroy', gtk.main_quit)
		self.show_all()
		gtk.main()

def run(path='.'):
	f = gio.File(path)
	browser = FileBrowser()
	browser.browse(f)
	browser.main()

if __name__ == '__main__':
	import sys
	run(*sys.argv[1:])

# vi: noet sts=4 sw=4 ts=4 tw=80

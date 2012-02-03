#!/usr/bin/env python


import gtk.glade
import pygtk
pygtk.require("2.0")

class Basic():
	def on_window1_destroy(self, widget, data=None):
		gtk.main_quit()
	def on_treeview1_cursor_changed(self,treev):
		s = treev.get_selection()
		(ls, iter) = s.get_selected()
		#data0 = ls.get_value(iter, 0)
		data1 = ls.get_value(iter, 1)
		if data1=="open gnome-terminal":
			self.tview.get_buffer().set_text("This is the description for gnome-terminal")
		else:
			pass			
		if data1=="open nautilus":
			self.tview.get_buffer().set_text("This is the description for nautilus")
		else:
			pass			
	
	def event_toggle(self, cell, path, model):
		"""pasang toggle di list"""
		model[path][0] = not model[path][0]
	def event_select(self, widget, data=None):
		"""Select a row on the treeview"""
		x = self.treev.get_selection()
		self.current_iter = x.get_selected()[1]
		print "Current Iteration: %s" % (self.current_iter)		
	def __init__(self):
		builder=gtk.Builder()
		builder.add_from_file("11.glade")
		self.win	= builder.get_object("window1")
		self.tview      = builder.get_object("textview1")	
		
		# list of items to display
		self.list = gtk.ListStore(bool,str)
		iter = self.list.append( (False, "open gnome-terminal",) )
		self.list.set(iter)
		iter = self.list.append( (False, "open nautilus",) )
		self.list.set(iter)

		# the Treeview
		self.treev	= builder.get_object("treeview1")
		model = self.treev.get_selection()
		model.set_mode(gtk.SELECTION_SINGLE)
		r = gtk.CellRendererText()
		
		#toggle
		t = gtk.CellRendererToggle()
		t.set_property("activatable", True)
		q=self.treev.insert_column_with_attributes(0,"---",t)
		q.add_attribute(t, "active", 0)
		t.connect("toggled", self.event_toggle, self.list)
		#str
		self.treev.insert_column_with_attributes(-1, "List", r, text=1)
		#pack
		self.treev.set_model(self.list)
		builder.connect_signals(self)	
if __name__ == "__main__":
	wer = Basic()
	wer.win.show()
	gtk.main()

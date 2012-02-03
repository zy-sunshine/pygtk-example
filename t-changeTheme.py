#!/usr/bin/env python

# example progressbar.py

import pygtk
pygtk.require('2.0')
import gtk, gobject
import os, glob

# Update the value of the progress bar so that we get
 # some movement
def progress_timeout(pbobj):
    if pbobj.activity_check.get_active():
        pbobj.pbar.pulse()
    else:
         # Calculate the value of the progress bar using the
         # value range set in the adjustment object
        new_val = pbobj.pbar.get_fraction() + 0.01
        if new_val > 1.0:
            new_val = 0.0
    # Set the new value
        pbobj.pbar.set_fraction(new_val)

    # As this is a timeout function, return TRUE so that it
    # continues to get called
    return True

class ProgressBar:
 # Callback that toggles the text display within the progress
 # bar trough
    def toggle_show_text(self, widget, data=None):
        if widget.get_active():
            self.pbar.set_text("some text")
        else:
            self.pbar.set_text("")

        # Callback that toggles the activity mode of the progress
        # bar
    def toggle_activity_mode(self, widget, data=None):
        if widget.get_active():
            self.pbar.pulse()
        else:
            self.pbar.set_fraction(0.0)

    # Callback that toggles the orientation of the progress bar
    def toggle_orientation(self, widget, data=None):
        if self.pbar.get_orientation() == gtk.PROGRESS_LEFT_TO_RIGHT:
            self.pbar.set_orientation(gtk.PROGRESS_RIGHT_TO_LEFT)
        elif self.pbar.get_orientation() == gtk.PROGRESS_RIGHT_TO_LEFT:
            self.pbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

    # Clean up allocated memory and remove the timer
    def destroy_progress(self, widget, data=None):
        gobject.source_remove(self.timer)
        self.timer = 0
        gtk.main_quit()

    def __init__(self, rc_path_list):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)

        self.window.connect("destroy", self.destroy_progress)
        self.window.set_title("ProgressBar")
        self.window.set_border_width(0)
        vbox = gtk.VBox(False, 5)
        vbox.set_border_width(10)
        self.window.add(vbox)
        vbox.show()
    
        # Create a centering alignment object
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        vbox.pack_start(align, False, False, 5)
        align.show()
        
        # Create the ProgressBar
        self.pbar = gtk.ProgressBar()
        
        align.add(self.pbar)
        self.pbar.show()
        
        # Add a timer callback to update the value of the progress bar
        self.timer = gobject.timeout_add (100, progress_timeout, self)
        
        separator = gtk.HSeparator()
        vbox.pack_start(separator, False, False, 0)
        separator.show()
        
        # rows, columns, homogeneous
        table = gtk.Table(2, 2, False)
        vbox.pack_start(table, False, True, 0)
        table.show()
        
        # Add a check button to select displaying of the trough text
        check = gtk.CheckButton("Show text")
        table.attach(check, 0, 1, 0, 1,
        gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
        5, 5)
        check.connect("clicked", self.toggle_show_text)
        check.show()
        
        # Add a check button to toggle activity mode
        self.activity_check = check = gtk.CheckButton("Activity mode")
        table.attach(check, 0, 1, 1, 2,
        gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
        5, 5)
        check.connect("clicked", self.toggle_activity_mode)
        check.show()
        
        # Add a check button to toggle orientation
        check = gtk.CheckButton("Right to Left")
        table.attach(check, 0, 1, 2, 3,
        gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
        5, 5)
        check.connect("clicked", self.toggle_orientation)
        check.show()
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        # pack the table into the scrolled window
        #import math
        #cl = math.ceil(math.sqrt(len(rc_path_list)))
        cl = len(rc_path_list) / 2
        table = gtk.Table(cl, 2, True)
        scrolled_window.add_with_viewport(table)
        table.show()
        # change theme
        i = 0
        j = 0
        for gtkrc in rc_path_list:
            #print gtkrc
            themename = gtkrc.split(os.path.sep)[4]
            print themename
            if themename == '':
                print '-' * 20
                continue
            button = gtk.Button(themename)
            button.connect("clicked", self.change_theme, gtkrc)
            #scrolled_window.pack_start(button, False, False, 0)
            table.attach(button, i, i+1, j, j+1)
            j += 1
            i = j%2
            button.show()

        scrolled_window.show()
        vbox.pack_start(scrolled_window, True, True, 0)
        # Add a button to exit the program
        button = gtk.Button("close")
        button.connect("clicked", self.destroy_progress)
        vbox.pack_start(button, False, False, 0)
        
        # This makes it so the button is the default.
        button.set_flags(gtk.CAN_DEFAULT)
        
        # This grabs this button to be the default button. Simply hitting
        # the "Enter" key will cause this button to activate.
        button.grab_default ()
        button.show()
        
        #self.window.show()
        self.window.show_all()

    def change_theme(self, widget, data=None):
        #gtk.gdk.threads_init()
        #rc_path = '/usr/share/themes/Industrial/gtk-2.0/gtkrc'
        settings = gtk.settings_get_default()
        #settings.set_string_property('gtk-theme-name', 'Default', '')
        #print(gtk.rc_get_theme_dir())
        rc_path = data
        #gtk.rc_parse(rc_path)
        theme_dir = os.path.dirname(os.path.dirname(rc_path))
        print theme_dir
        #settings.set_string_property('gtk-theme-name', theme_dir, '')
        settings.set_string_property('gtk-theme-name',
                os.path.basename(theme_dir), '')
        #gtk.rc_parse_string(open(rc_path, 'rt').read())
    
    
def main():
    gtk.main()
    return 0
    
if __name__ == "__main__":
    rc_path_list = glob.glob('/usr/share/themes/*/*/gtkrc')
    #for rc in rc_path_list:
    #    print rc
    
    #gtk.gdk.threads_init()
    
    settings = gtk.settings_get_default()
    settings.set_string_property('gtk-theme-name', 'Default', '')
    print(gtk.rc_get_theme_dir())
    #gtk.rc_parse_string(open(rc_path_list[0], 'rt').read())
    gtk.rc_parse_string(open('gtkrc', 'rt').read())

    ProgressBar(rc_path_list)
    main()


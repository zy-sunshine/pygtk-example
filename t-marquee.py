import sys

import gtk
import pygtk
import gnomeapplet

pygtk.require('2.0')

def applet_factory(applet, iid):   
   label = gtk.Label("It works!")
   applet.add(label)
   applet.show_all()
   print('Factory started')
   return True
           
if __name__ == '__main__':   # testing for execution
   print('Starting factory')
   gnomeapplet.bonobo_factory('OAFIID:SampleApplet_Factory',
                              gnomeapplet.Applet.__gtype__,
                              'Sample Applet', '0.1',
                              applet_factory)

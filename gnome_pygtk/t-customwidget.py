#!/usr/bin/python
# -*- coding: utf-8 -*-

# ZetCode PyGTK tutorial 
#
# This example creates a burning
# custom widget
#
# author: Jan Bodnar
# website: zetcode.com 
# last edited: April 2011


import gtk
import cairo

class Burning(gtk.DrawingArea):

    def __init__(self, parent):
      
        self.par = parent
        super(Burning, self).__init__()
 
        self.num = ( "75", "150", "225", "300", 
            "375", "450", "525", "600", "675" )
 
        self.set_size_request(-1, 30)
        self.connect("expose-event", self.expose)
    

    def expose(self, widget, event):
      
        cr = widget.window.cairo_create()
        cr.set_line_width(0.8)

        cr.select_font_face("Courier", 
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(11)

        width = self.allocation.width
     
        self.cur_width = self.par.get_cur_value()

        step = round(width / 10.0)

        till = (width / 750.0) * self.cur_width
        full = (width / 750.0) * 700

        if (self.cur_width >= 700):
            
            cr.set_source_rgb(1.0, 1.0, 0.72)
            cr.rectangle(0, 0, full, 30)
            cr.save()
            cr.clip()
            cr.paint()
            cr.restore()
            
            cr.set_source_rgb(1.0, 0.68, 0.68)
            cr.rectangle(full, 0, till-full, 30)
            cr.save()
            cr.clip()
            cr.paint()
            cr.restore()

        else:     
            cr.set_source_rgb(1.0, 1.0, 0.72)
            cr.rectangle(0, 0, till, 30)
            cr.save()
            cr.clip()
            cr.paint()
            cr.restore()
       

        cr.set_source_rgb(0.35, 0.31, 0.24)
        
        for i in range(1, len(self.num) + 1):
            cr.move_to(i*step, 0)
            cr.line_to(i*step, 5)
            cr.stroke()
            
            (x, y, width, height, dx, dy) = cr.text_extents(self.num[i-1])
            cr.move_to(i*step-width/2, 15)
            cr.text_path(self.num[i-1])
            cr.stroke()
       
        
 
class PyApp(gtk.Window): 

    def __init__(self):
        super(PyApp, self).__init__()
        
        self.set_title("Burning")
        self.set_size_request(350, 200)        
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

        self.cur_value = 0
       
        vbox = gtk.VBox(False, 2)
        
        scale = gtk.HScale()
        scale.set_range(0, 750)
        scale.set_digits(0)
        scale.set_size_request(160, 40)
        scale.set_value(self.cur_value)
        scale.connect("value-changed", self.on_changed)
                
        fix = gtk.Fixed()
        fix.put(scale, 50, 50)
        
        vbox.pack_start(fix)
        
        self.burning = Burning(self)
        vbox.pack_start(self.burning, False, False, 0)

        self.add(vbox)
        self.show_all()
        
        
    def on_changed(self, widget):
        self.cur_value = widget.get_value()
        self.burning.queue_draw()
    
    
    def get_cur_value(self):
        return self.cur_value
    

PyApp()
gtk.main()

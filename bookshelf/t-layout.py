#!/usr/bin/python
import gtk
import pdb

ICO_BTN_DEL = 'img/icon_bsw_01.png'
ICO_BTN_REFRESH = 'img/icon_bsw_021.png'

_ = lambda x: x

class CSBookWidget(gtk.Fixed):
    def __init__(self, cover):
        gtk.Fixed.__init__(self)

        self.book_cover = gtk.gdk.pixbuf_new_from_file(cover)
        
        cover = gtk.Image()
        cover.set_from_pixbuf(self.book_cover)
        
        cover_w = self.book_cover.get_width()
        cover_h = self.book_cover.get_height()
        print cover_w, cover_h
        
        check_button = gtk.CheckButton()
        
        bbox = self.create_bbox()    
        bbox.set_size_request(cover_w, -1)
        
        bbox.show_all() # draw all button box widgets
        bbox_w, bbox_h = bbox.size_request() # get button box size
        
        print bbox_w, bbox_h
        
        #import pdb; pdb.set_trace()
        self.pos_x, self.pos_y = 0, 0
        
        bbox_pos_x = self.pos_x
        bbox_pos_y = self.pos_y + cover_h - bbox_h
        
        self.put(cover, self.pos_x, self.pos_y)
        self.put(check_button, self.pos_x, self.pos_y)
        self.put(bbox, bbox_pos_x, bbox_pos_y)
        
    def create_bbox(self):
        bbox = gtk.HBox()
        #bbox.set_spacing(spacing)

        img_gdk = gtk.gdk.pixbuf_new_from_file(ICO_BTN_DEL)
        img_w, img_h = img_gdk.get_width(), img_gdk.get_height()
        img = gtk.Image()
        img.set_from_pixbuf(img_gdk)
        
        button = gtk.Button()
        button.add(img)
        #button.set_size_request(img_w, img_h)
        bbox.add(button)

        img_gdk = gtk.gdk.pixbuf_new_from_file(ICO_BTN_REFRESH)
        img_w, img_h = img_gdk.get_width(), img_gdk.get_height()
        button = gtk.Button()
        img = gtk.Image()
        img.set_from_pixbuf(img_gdk)
        #button.set_size_request(img_w, img_h)
        button.add(img)
        bbox.add(button)

        return bbox

        
class Grid(gtk.Layout):
    def __init__(self):
        gtk.Layout.__init__(self)
        self.connect('size-allocate', self.on_size_allocate)
        
    def on_size_allocate(self, widget, rectangle):
        print 'on_size_allocate: maybe queue_resize have been called'
        self.update_layout(rectangle)
        
    def update_layout(self, rectangle):
        print rectangle
        
class PyApp(gtk.Window):
    ID_LIST_CHEKCBOX = 0
    ID_BOOTCOVER_URL = 1
    ID_BOOKNAME = 2
    ID_BOOKINFO_UNREAD = 3
    ID_BOOT_WIDGET = 4
    def __init__(self):
        super(PyApp, self).__init__()

        self.set_title("Fixed")
        self.set_size_request(300, 280)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(6400, 6400, 6440))
        self.set_position(gtk.WIN_POS_CENTER)
        self.main_vbox = gtk.VBox()
        
        btn_grid, btn_list = gtk.Button(_('grid')), gtk.Button(_('list'))
        btn_test = gtk.Button(_('test'))
        btn_grid.connect('clicked',  self.on_btn_grid)
        btn_list.connect('clicked',  self.on_btn_list)
        btn_test.connect('clicked',  self.on_btn_test)
        
        bbox = gtk.HButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_END)
        bbox.add(btn_grid)
        bbox.add(btn_list)
        bbox.add(btn_test)
        #hbox = gtk.HBox()
        #hbox.pack_start(bbox, False, False, 0)
        self.main_vbox.pack_start(bbox, False, False, 0)

        
        # bookname, bookcover_url, bookinfo
        self.liststore = gtk.ListStore(bool, str, str)
        self.liststore.append([False, 'bookname1', 'bookcover_url1'])
        self.liststore.append([False, 'bookname2', 'bookcover_url2'])
        
        ### Create a Book Widget with book cover
        book_widget = CSBookWidget("img/img_nocover.png")
        self.main_vbox.pack_start(book_widget, False, False, 0)
        
        ### Grid View
        self.gridview = Grid()
        self.main_vbox.pack_start(self.gridview, False, False, 0)
        self.fill_gridview(self.gridview)
        
        ### List View
        self.listview = gtk.TreeView(model=self.liststore)
        
        # bookname
        renderer_toggle = gtk.CellRendererToggle()
        renderer_toggle.set_property("activatable", True)

        column_toggle = gtk.TreeViewColumn("Toggle", renderer_toggle) #, activatable=True, active=True)
        column_toggle.add_attribute(renderer_toggle, "active", 0)
        self.listview.append_column(column_toggle)
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        
        # bookcover_url
        renderer_text = gtk.CellRendererText()
        column_text = gtk.TreeViewColumn("Text", renderer_text, text=1)
        self.listview.append_column(column_text)
        
        # bookinfo
        renderer_text = gtk.CellRendererText()
        column_text = gtk.TreeViewColumn("Text", renderer_text, text=2)
        self.listview.append_column(column_text)
        
        self.add(self.main_vbox)

        self.connect("destroy", gtk.main_quit)
        self.show_all()
        
    def fill_gridview(self, gridview):
        gridview.pack_start()
        
    def on_cell_toggled(self, widget, path):
        self.liststore[path][self.ID_LIST_CHEKCBOX] = not self.liststore[path][self.ID_LIST_CHEKCBOX]
        
    def on_btn_test(self, widget, data = None):
        if 0:
            for item in self.liststore:
                for i in item:
                    print i,
                print
        if 0:
            self.liststore[0][0] = True
        pass
        
    def on_btn_list(self, widget, data = None):
        if self.listview.parent and \
            self.listview in self.listview.parent:
            return
        self.replace_widget(self.gridview, self.listview)
        self.gridview.hide()
        self.listview.show()

        
    def on_btn_grid(self, widget, data = None):
        if self.gridview.parent and \
            self.gridview in self.gridview.parent:
            return
        self.replace_widget(self.listview, self.gridview)
        self.gridview.show()
        self.listview.hide()

    def replace_widget(self, current, new):
        """
        Replace one widget with another.
        'current' has to be inside a container (e.g. gtk.VBox).
        """
        container = current.parent
        assert container # is "current" inside a container widget?

        # stolen from gazpacho code (widgets/base/base.py):
        props = {}
        for pspec in gtk.container_class_list_child_properties(container):
            props[pspec.name] = container.child_get_property(current, pspec.name)

        gtk.Container.remove(container, current)
        container.add(new)

        for name, value in props.items():
            container.child_set_property(new, name, value)

PyApp()
gtk.main()

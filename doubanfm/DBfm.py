'''
Created on Sep 22, 2011

@author: yinseny
'''
import pygtk
pygtk.require("2.0")

import gtk
import gtk.glade

import pygst
pygst.require("0.10")
import gst

import gobject
import urllib
import ConfigParser
import os

import libdbfm

BASEDIR = os.path.dirname(os.path.realpath(__file__))

class DBfm(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.playlist = []
        self.cur = None
        self.user = ''
        self.pwd = ''
        self.fm = libdbfm.DoubanFM()
        self.config = ConfigParser.ConfigParser()

    def loadConfig(self):
        try:
            self.config.read(BASEDIR+'/config.ini')
            self.fm.loadConfig(self.config)
            return True
        except ConfigParser.NoSectionError,ConfigParser.NoOptionError:
            self.config.add_section('Cookie')
            self.config.add_section('UserInfo')
            self.config.set('Cookie', 'dbcl2',' ')
            self.config.set('UserInfo','uid',' ')
            self.config.set('UserInfo','channel','')
            self.saveConfig()
            return False

    def saveConfig(self):
        self.fm.saveConfig(self.config)
        self.config.write(open(BASEDIR+'/config.ini','w'))

    def login(self,name,pwd):
        print 'Logining...'
        self.user = name
        self.pwd = pwd
        self.fm.login(name, pwd)
        print 'Login Finished!'
        self.next()

    def __del__(self):
        print 'logout'
        del self.fm
        os.remove(BASEDIR+'/config.ini')
    
    def played(self):
        self.fm.played_song(self.cur.props['sid'], self.cur.props['aid'])
        self.next()
    
    def next(self):
        if len(self.playlist)==0 :
            self.playlist = self.fm.new_playlist()
        self.cur = self.playlist.pop(0)
    
    def get_detail(self,param):
        return self.cur.props[param]
    
    def get_channels(self):
        return self.fm.channels

    def get_channel(self):
        return self.fm.get_channel()
    
    def set_channel(self,ch):
        self.fm.set_channel(ch)
        self.playlist = self.fm.new_playlist()

    def fav(self):
        if not self.isfav():
            self.fm.fav_song(self.get_detail('sid'), self.get_detail('aid'))

    def unfav(self):
        if self.isfav():
            self.fm.unfav_song(self.get_detail('sid'), self.get_detail('aid'))

    def isfav(self):
        if self.cur.props['like'] == 1:
            return True
        else:
            return False
    
    def skip_song(self):
        self.fm.skip_song(self.cur.props['sid'], self.cur.props['aid'])
        


class MainForm(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        #setup player
        self.player = gst.element_factory_make("playbin", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        
        #setup douban fm
        self.dbfm = DBfm()

        #setup UI
        self.gladefile = BASEDIR+"/dbfm.glade"
        self.wTree = gtk.glade.XML(self.gladefile,"mainWindow")

        dic = { "on_mainWindow_destroy_event" : self.destroy,
               "on_mainWindow_delete_event" : self.delete_event,
               "on_loginWindowButton_clicked" : self.loginWindowButton_clicked,
               "on_logoutButton_clicked" : self.logoutButton_clicked,
               "on_pauseButton_toggled" : self.pauseButton_toggled,
               "on_skipButton_clicked" : self.skipButton_clicked,
               "on_nextButton_clicked" : self.nextButton_clicked,
               "on_favButton_toggled" : self.favButton_toggled,
               "on_channelList_changed" : self.channelList_changed,
               }

        self.wTree.signal_autoconnect(dic)

        self.loginWindowButton = self.wTree.get_widget("loginWindowButton")
        self.logoutButton = self.wTree.get_widget("logoutButton")
        self.pauseButton = self.wTree.get_widget("pauseButton")
        self.favButton = self.wTree.get_widget("favButton")
        self.skipButton = self.wTree.get_widget("skipButton")
        
        self.photo = self.wTree.get_widget("photo")
        self.photo.set_from_file(BASEDIR+"/DBfm.png")

        self.songDetail = self.wTree.get_widget("songDetail")
        #self.playProcess = self.wTree.get_widget('playProcess')

        self.mainWindow = self.wTree.get_widget("mainWindow")
        
        self.channelList = self.wTree.get_widget('channelList')

        # setup system tray
        self.systray=None
        self.setupSystray()
        
        if self.dbfm.loadConfig():
            self.loginWindowButton.set_sensitive(False)
            self.logoutButton.set_sensitive(True)
            self.prepare_channelList()
            self.channelList.set_active(self.dbfm.get_channel())
            self.play()

        self.mainWindow.show()

        
        #set processbar timer
        #self.timer = None

    def delete_event(self,widget,data=None):
        self.mainWindow.hide()
        return True

    def destroy(self,widget,data=None):
        self.dbfm.saveConfig()
        gtk.main_quit()

    def loginWindowButton_clicked(self, widget):
        print 'loginWindowButton_clicked'
        self.loginDialog = gtk.Dialog("Login",
                self.mainWindow,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        fixed = gtk.Fixed()
        self.loginDialog.vbox.pack_start(fixed)
        label1 = gtk.Label(u'ID:')
        fixed.put(label1,5,10)
        userNameEntry = gtk.Entry()
        fixed.put(userNameEntry,5,30)
        label2 = gtk.Label(u'Password:')
        fixed.put(label2,150,10)
        passwordEntry = gtk.Entry()
        fixed.put(passwordEntry,150,30)
        
        self.loginDialog.show_all()

        response = self.loginDialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.dbfm.login(
                            userNameEntry.get_text(),
                            passwordEntry.get_text())
            self.prepare_channelList()
            self.channelList.set_active(self.dbfm.get_channel())
            #print self.dbfm.get_channels().keys()
            self.get_next_song()
            self.play()
        self.loginDialog.destroy()
        self.dbfm.saveConfig()
        self.logoutButton.set_sensitive(True)
        widget.set_sensitive(False)

    def logoutButton_clicked(self,widget):
        print 'logout'
        self.player.set_state(gst.STATE_NULL)
        self.photo.set_from_file(BASEDIR+"/DBfm.png")
        self.channelList.set_active(-1)
        self.songDetail.set_text("songDetail")
        self.loginWindowButton.set_sensitive(True)
        del self.dbfm
        self.dbfm = DBfm()
        self.dbfm.loadConfig()
        widget.set_sensitive(False)
        
    def channelList_changed(self,widget):
        print 'channelList_changed'
        self.dbfm.set_channel(widget.get_active())
        self.get_next_song()
        self.play()

    def pauseButton_toggled(self,widget):
        print 'pauseButton_toggled'
        if widget.get_active():
            print 'Pause'
            self.player.set_state(gst.STATE_PAUSED)
        else :
            print 'Resume'
            self.player.set_state(gst.STATE_PLAYING)

    def nextButton_clicked(self,widget):
        self.get_next_song()
        self.play()
        
    def favButton_toggled(self,widget):
        print 'favButton_toggled'
        if widget.get_active():
            print 'fav'
            self.dbfm.fav()
        else:
            print 'unfav'
            self.dbfm.unfav()
    
    def skipButton_clicked(self,widget):
        print 'skipButton_clicked'
        self.dbfm.skip_song()
        self.get_next_song()
        self.play()

    def get_next_song(self):
        self.player.set_state(gst.STATE_NULL)
        self.dbfm.next()
        self.player.set_property('uri', self.dbfm.get_detail('url'))
        self.songDetail.set_text("Song:%s\nAlbum:%s\nArtist:%s"
                                 % (self.dbfm.get_detail('title'),
                                    self.dbfm.get_detail('albumtitle'),
                                    self.dbfm.get_detail('artist')
                                    )
                                 )
        #self.playProcess.set_fraction(0.0)
        #self.timer = gobject.timeout_add (self.dbfm.get_detail('length'), self.progress_timeout, self.playProcess)
        self.systray.set_tooltip(self.songDetail.get_text())
        urllib.urlretrieve(self.dbfm.get_detail('picture'),BASEDIR+"/picture.jpg")
        self.photo.set_from_file(BASEDIR+'/picture.jpg')
        if self.dbfm.isfav():
            self.favButton.set_active(True)
        else:
            self.favButton.set_active(False)
        
    def play(self):
        self.player.set_state(gst.STATE_PLAYING)
    
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_ERROR:
            self.get_next_song()
            self.play()
        elif t == gst.MESSAGE_EOS:
            self.dbfm.played()
            self.get_next_song()
            self.play()

    def setupSystray(self):
        self.systray = gtk.StatusIcon()
        self.systray.set_from_file(BASEDIR+'/DBfm.png')

        self.systray.connect("activate", self.show_hide_window)
        self.systray.connect('popup-menu', self.systrayPopup)
        self.systray.set_tooltip('Pydoubanfm')
        self.systray.set_visible(True)
    
    def show_hide_window(self, widget):
        if self.mainWindow.get_property('visible'):
            self.mainWindow.hide()
        else:
            self.mainWindow.show()
    
    def systrayPopup(self, statusicon, button, activate_time):
        popup_menu = gtk.Menu()
        restore_item = gtk.MenuItem(u"Show/Hide")
        restore_item.connect("activate",self.show_hide_window)
        popup_menu.append(restore_item)
        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", gtk.main_quit)
        popup_menu.append(quit_item)

        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None,None, None, 0, time)
        
    def prepare_channelList(self):
        list = gtk.ListStore(gobject.TYPE_STRING)
        chs = self.dbfm.get_channels()
        for ch in chs.items():
            list.insert(ch[1],[ch[0]])
            
        self.channelList.set_model(list)
        cell = gtk.CellRendererText()
        self.channelList.pack_start(cell, True)
        self.channelList.add_attribute(cell, 'text',0)
        

#    # Update the value of the progress bar so that we get
#    # some movement
#    def progress_timeout(self,pbar):
#        pbar.pulse()
#        if self.activity_check.get_active():
#            self.playProcess.pulse()
#        else:
#            # Calculate the value of the progress bar using the
#            # value range set in the adjustment object
#            new_val = self.pbar.get_fraction() + 0.01
#            if new_val > 1.0:
#                new_val = 0.0
#                # Set the new value
#                self.playProcess.set_fraction(new_val)
#
#        # As this is a timeout function, return TRUE so that it
#        # continues to get called
#        return True


if __name__ == '__main__':
    mf = MainForm()
    gtk.main()

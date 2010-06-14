import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.wordwrap import wordwrap

from .program_text import about_text
from .utils import get_bitmap_icon

OPEN           = wx.NewId()
EXIT           = wx.NewId()
PREFERENCES    = wx.NewId()
DEFAULT        = wx.NewId()
ABOUT          = wx.NewId()
NO_WORKSPACES  = wx.NewId()
WORKSPACES     = wx.NewId()

class SpikepyMenuBar(wx.MenuBar):
    def __init__(self, frame, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)
        

        file_menu = wx.Menu()
        file_menu.Append(OPEN, text="Open")
        file_menu.Append(EXIT, text="Exit")
        
        edit_menu = wx.Menu()
        edit_menu.Append(PREFERENCES, text="Preferences")
        
        view_menu = wx.Menu()
        workspaces_submenu = wx.Menu()
        workspaces_submenu.Append(DEFAULT, text="Default")
        workspaces_submenu.AppendSeparator()
        workspaces_submenu.Append(NO_WORKSPACES, 
                                  text="No saved custom workspaces")
        view_menu.AppendMenu(WORKSPACES, "Workspaces", workspaces_submenu)
        
        help_menu = wx.Menu()
        help_menu.Append(ABOUT, text="About")

        self.Append(file_menu, "File")
        self.Append(edit_menu, "Edit")
        self.Append(view_menu, "View")
        self.Append(help_menu, "Help")
        
        # define what menu items actually do
        frame.Bind(wx.EVT_MENU, self._close_window, id=EXIT)
        frame.Bind(wx.EVT_MENU, self._about_box, id=ABOUT)

    def _close_window(self, event):
        pub.sendMessage(topic='CLOSE APPLICATION', data=None)

    def _about_box(self, event):
        # dialog box to open when "About" is clicked
        info = wx.AboutDialogInfo()
        icon = wx.EmptyIcon() 
        icon.CopyFromBitmap(get_bitmap_icon('spikepy_logo'))
        info.Icon = icon
        info.Name = "Spikepy"
        info.Version = "0.0"
        line_width_in_pixels = 350
        info.Description = wordwrap(about_text, line_width_in_pixels, 
                                    wx.ClientDC(self))
        wx.AboutBox(info)
        
    
    

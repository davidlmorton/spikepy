import wx
import wx.aui
from wx.lib.pubsub import Publisher as pub
from wx.lib.wordwrap import wordwrap

from .utils import get_bitmap_icon
from .pyshell import PyShellDialog
from .look_and_feel_settings import lfs
from . import program_text as pt

OPEN             = wx.ID_OPEN
EXIT             = wx.ID_EXIT
PREFERENCES      = wx.NewId()
DEFAULT          = wx.NewId()
ABOUT            = wx.ID_ABOUT
SHELL            = wx.NewId()
WORKSPACES       = wx.NewId()
SHOW_TOOLBARS    = wx.NewId()
SAVE_PERSPECTIVE = wx.NewId()

class SpikepyMenuBar(wx.MenuBar):
    def __init__(self, frame, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)

        # --- FILE ---
        file_menu = wx.Menu()
        file_menu.Append(OPEN, text=pt.OPEN)
        file_menu.Append(EXIT, text=pt.EXIT)
        
        # --- EDIT ---
        edit_menu = wx.Menu()
        edit_menu.Append(PREFERENCES, text=pt.PREFERENCES)
        
        # --- VIEW ---
        view_menu = wx.Menu()
        self.workspaces_submenu = wx.Menu()
        self._update_perspectives()
        view_menu.AppendMenu(WORKSPACES, pt.WORKSPACES, self.workspaces_submenu)
        view_menu.Append(SHOW_TOOLBARS, text=pt.SHOW_TOOLBARS_MENU, 
                         kind=wx.ITEM_CHECK)
        
        # --- HELP ---
        help_menu = wx.Menu()
        help_menu.Append(SHELL, text=pt.PYTHON_SHELL_MENU)
        help_menu.Append(ABOUT, text=pt.ABOUT)

        self.Append(file_menu, pt.FILE)
        self.Append(edit_menu, pt.EDIT)
        self.Append(view_menu, pt.VIEW)
        self.Append(help_menu, pt.HELP)
        
        # --- BIND MENU EVENTS ---
        frame.Bind(wx.EVT_MENU, self._close_window, id=EXIT)
        frame.Bind(wx.EVT_MENU, self._about_box, id=ABOUT)
        frame.Bind(wx.EVT_MENU, self._python_shell, id=SHELL)
        frame.Bind(wx.EVT_MENU, self._open_file, id=OPEN)
        frame.Bind(wx.EVT_MENU, self._show_toolbars, id=SHOW_TOOLBARS)
        frame.Bind(wx.EVT_MENU, self._save_perspective, id=SAVE_PERSPECTIVE)

        self.frame = frame

        self._toolbars_shown = False

    def _python_shell(self, event=None):
        event.Skip()
        dlg = PyShellDialog(self, size=lfs.PYSHELL_DIALOG_SIZE)
        dlg.Show()

    def _update_perspectives(self, perspectives={}):
        workspaces_submenu_items = self.workspaces_submenu.GetMenuItems()
        for item in workspaces_submenu_items:
            self.workspaces_submenu.RemoveItem(item)

        perspective_names = perspectives.keys()
        
        perspective_ids = {}

        for name in perspective_names:
            perspective_ids[name] = wx.NewId()
            self.workspaces_submenu.Append(perspective_ids[name], text=name)
            self.frame.Bind(wx.EVT_MENU, self._load_perspective, 
                      id=perspective_ids[name])
        
        self.workspaces_submenu.AppendSeparator()
        self.workspaces_submenu.Append(SAVE_PERSPECTIVE, 
                                       text=pt.SAVE_WORKSPACE)
    
    def _load_perspective(self, event=None):
        chosen_item_id = event.GetId()
        chosen_item = self.workspaces_submenu.FindItemById(chosen_item_id)
        chosen_item_name = chosen_item.GetText()
        pub.sendMessage(topic='LOAD_PERSPECTIVE', data=chosen_item_name)
    
    def _save_perspective(self, event=None):
        pub.sendMessage(topic='SAVE_PERSPECTIVE', data=None)
    
    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_FILE', data=None)

    def _close_window(self, event):
        pub.sendMessage(topic='CLOSE_APPLICATION', data=None)

    def _show_toolbars(self, event):
        if self._toolbars_shown:
            pub.sendMessage(topic='HIDE_TOOLBAR', data=None)
            self._toolbars_shown = False
        else:
            pub.sendMessage(topic='SHOW_TOOLBAR', data=None)
            self._toolbars_shown = True

    def _about_box(self, event):
        # dialog box to open when "About" is clicked
        info = wx.AboutDialogInfo()
        icon = wx.EmptyIcon() 
        icon.CopyFromBitmap(get_bitmap_icon('spikepy_logo'))
        info.Icon = icon
        info.Name = "Spikepy"
        info.Version = "0.0"
        line_width_in_pixels = 350
        info.Description = wordwrap(pt.ABOUT_SPIKEPY, line_width_in_pixels, 
                                    wx.ClientDC(self))
        wx.AboutBox(info)
        
    
    

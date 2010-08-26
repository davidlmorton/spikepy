import os

import wx
import wx.aui
from wx.lib.pubsub import Publisher as pub
from wx.lib.wordwrap import wordwrap

from .utils import get_bitmap_icon, PlotPanelPrintout
from .pyshell import PyShellDialog
from .look_and_feel_settings import lfs
from . import program_text as pt
from .preferences_frame import PreferencesFrame

OPEN               = wx.ID_OPEN
EXIT               = wx.ID_EXIT
PREFERENCES        = wx.NewId()
DEFAULT            = wx.NewId()
ABOUT              = wx.ID_ABOUT
SHELL              = wx.NewId()
SHOW_TOOLBARS      = wx.NewId()
SAVE_SESSION       = wx.NewId()
LOAD_SESSION       = wx.NewId()
EXPORT_MARKED      = wx.NewId()
EXPORT_ALL         = wx.NewId()
PRINT_SUBMENU      = wx.NewId()
PRINT              = wx.NewId()
PRINT_PREVIEW      = wx.NewId()
PAGE_SETUP         = wx.NewId()

class SpikepyMenuBar(wx.MenuBar):
    def __init__(self, frame, *args, **kwargs):
        wx.MenuBar.__init__(self, *args, **kwargs)

        # --- FILE ---
        file_menu = wx.Menu()
        file_menu.Append(OPEN, text=pt.OPEN)
        file_menu.AppendSeparator()
        file_menu.Append(LOAD_SESSION,      text=pt.LOAD_SESSION)
        file_menu.Append(SAVE_SESSION,      text=pt.SAVE_SESSION)
        file_menu.AppendSeparator()
        file_menu.Append(EXPORT_MARKED,     text=pt.EXPORT_MARKED_TRIALS)
        file_menu.Append(EXPORT_ALL,        text=pt.EXPORT_ALL_TRIALS)
        print_menu = wx.Menu()
        print_menu.Append(PRINT,            text=pt.PRINT)
        print_menu.Append(PRINT_PREVIEW,    text=pt.PRINT_PREVIEW)
        print_menu.Append(PAGE_SETUP,       text=pt.PAGE_SETUP)
        file_menu.AppendSubMenu(print_menu,      pt.PRINT_SUBMENU)
        file_menu.AppendSeparator()
        file_menu.Append(EXIT,              text=pt.EXIT)
        
        # --- EDIT ---
        edit_menu = wx.Menu()
        edit_menu.Append(PREFERENCES, text=pt.PREFERENCES)
        
        # --- VIEW ---
        view_menu = wx.Menu()
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
        # File
        frame.Bind(wx.EVT_MENU, self._open_file,        id=OPEN)
        frame.Bind(wx.EVT_MENU, self._load_session,     id=LOAD_SESSION)
        frame.Bind(wx.EVT_MENU, self._save_session,     id=SAVE_SESSION)
        frame.Bind(wx.EVT_MENU, self._export_marked,    id=EXPORT_MARKED)
        frame.Bind(wx.EVT_MENU, self._export_all,       id=EXPORT_ALL)
        frame.Bind(wx.EVT_MENU, self._print,            id=PRINT)
        frame.Bind(wx.EVT_MENU, self._print_preview,    id=PRINT_PREVIEW)
        frame.Bind(wx.EVT_MENU, self._page_setup,       id=PAGE_SETUP)
        frame.Bind(wx.EVT_MENU, self._close_window,     id=EXIT)
        # Edit
        frame.Bind(wx.EVT_MENU, self._show_preferences, id=PREFERENCES)
        # View
        frame.Bind(wx.EVT_MENU, self._show_toolbars,    id=SHOW_TOOLBARS)
        # Help
        frame.Bind(wx.EVT_MENU, self._python_shell,     id=SHELL)
        frame.Bind(wx.EVT_MENU, self._about_box,        id=ABOUT)

        self.frame = frame

        self._toolbars_shown = False

    def _print(self, event=None):
        pub.sendMessage(topic="PRINT", data=None)
        pass

    def _print_preview(self, event=None):
        pub.sendMessage(topic="PRINT_PREVIEW", data=None)
        pass

    def _page_setup(self, event=None):
        pub.sendMessage(topic="PAGE_SETUP", data=None)
        pass

    def _export_marked(self, event=None):
        pub.sendMessage(topic="EXPORT_TRIALS", data="marked")

    def _export_all(self, event=None):
        pub.sendMessage(topic="EXPORT_TRIALS", data="all")

    def _show_preferences(self, event=None):
        preferences_frame = PreferencesFrame(self)

    def _load_session(self, event=None):
        wildcard = pt.SESSION_FILES + '|*.ses|'
        wildcard += pt.ALL_FILES + '|*'
        dlg = wx.FileDialog(self, message=pt.LOAD_SESSION, 
                                  style=wx.FD_OPEN, 
                                  wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
            pub.sendMessage(topic='LOAD_SESSION', data=save_path)
        dlg.Destroy()

    def _save_session(self, event=None):
        wildcard = pt.SESSION_FILES + '|*.ses|'
        wildcard += pt.ALL_FILES + '|*'
        dlg = wx.FileDialog(self, message=pt.SAVE_SESSION, 
                                  style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,
                                  wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            save_path = dlg.GetPath()
            save_path_minus_extention, save_path_extention =\
                    os.path.splitext(save_path)
            if 'ses' != save_path_extention:
                save_path = save_path_minus_extention + os.path.extsep + 'ses'
            pub.sendMessage(topic='SAVE_SESSION', data=save_path)
        dlg.Destroy()

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
        self.workspaces_submenu.Append(WORKSPACES_MANAGER,
                                       text=pt.WORKSPACES_MANAGER)
    
    def _open_file(self, event):
        pub.sendMessage(topic='OPEN_OPEN_FILE_DIALOG', data=None)

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
        icon.CopyFromBitmap(get_bitmap_icon('spikepy_splash'))
        info.Icon = icon
        info.Name = "Spikepy"
        info.Version = "0.0"
        line_width_in_pixels = 350
        info.Description = wordwrap(pt.ABOUT_SPIKEPY, line_width_in_pixels, 
                                    wx.ClientDC(self))
        wx.AboutBox(info)
        
    
    

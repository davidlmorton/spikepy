import os

import string

import wx

from .strategy_utils import (make_methods_set_name, make_settings_name, 
                             make_strategy_name)
from validators import CharacterSubsetValidator
from . import program_text as pt
from .named_controls import NamedTextCtrl 

valid_strategy_characters = ('-_.,%s%s' % 
                             (string.ascii_letters, string.digits))

class ExportDialog(wx.Dialog):
    def __init__(self, parent, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        export_directory_panel = ExportDirectoryPanel(self)
        select_stages_panel = wx.Panel(self)
        select_stages_panel.SetBackgroundColour("red")
        options_panel = wx.Panel(self)
        options_panel.SetBackgroundColour("green")
        buttons_panel = ButtonsPanel(self)

        sizer = wx.GridBagSizer(vgap=5, hgap=5)
        flag = wx.GROW
        sizer.Add(export_directory_panel, pos=(0,0), span=(1,2), flag=flag)
        sizer.Add(select_stages_panel, pos=(1,0), span=(1,1), flag=flag)
        sizer.Add(options_panel, pos=(1,1), span=(1,1), flag=flag)
        sizer.Add(buttons_panel, pos=(2,0), span=(1,2), flag=flag)

        self.SetSizerAndFit(sizer)

class ExportDirectoryPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        export_text = NamedTextCtrl(self, name=pt.EXPORT_TO_DIRECTORY, 
                                          style=wx.TE_READONLY)
        default_path = os.getcwd()
        export_text.SetValue(default_path)
        browse_button = wx.Button(self, label=pt.BROWSE)
        
        flag = wx.ALL
        border = 5
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(export_text,   proportion=1, flag=flag, 
                                            border=border)
        sizer.Add(browse_button, proportion=0, flag=flag, 
                                            border=border)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self._on_browse, browse_button)
        self.export_text = export_text

    def _on_browse(self, event=None):
        dlg = wx.DirDialog(self, message=pt.CHOOSE_EXPORT_DIRECTORY)
        if dlg.ShowModal() == wx.ID_OK:
            self.export_text.SetValue(dlg.GetPath()) 

class ButtonsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        make_default_button = wx.Button(self, 
                                        label=pt.MAKE_THESE_SETTINGS_DEFAULT)
        restore_defaults_button = wx.Button(self, 
                                        label=pt.RESTORE_DEFAULT_SETTINGS)
        ok_button = wx.Button(self, id=wx.ID_OK)
        cancel_button  = wx.Button(self, id=wx.ID_CANCEL)
         
        flag = wx.ALL
        border = 5
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(make_default_button,     proportion=0, flag=flag, 
                                            border=border)
        sizer.Add(restore_defaults_button, proportion=0, flag=flag, 
                                            border=border)
        sizer.Add(cancel_button,           proportion=0, flag=flag, 
                                            border=border)
        sizer.Add(ok_button,               proportion=0, flag=flag, 
                                            border=border)
        self.SetSizer(sizer)

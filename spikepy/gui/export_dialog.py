"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os

import wx
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.common import program_text as pt
from spikepy.gui.named_controls import NamedTextCtrl

from spikepy.gui.strategy_pane import OptionalControlPanel

class ExportDialog(wx.Dialog):
    def __init__(self, parent, data_interpreters, trials, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.data_interpreters_panel = DataInterpretersPanel(self, 
                data_interpreters, trials)
        self.export_directory_panel = ExportDirectoryPanel(self)
        self.buttons_panel = ButtonsPanel(self)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.EXPAND
        border = 3
        sizer.Add(self.data_interpreters_panel, proportion=0, flag=flag, 
                border=border)
        sizer.Add(self.export_directory_panel, proportion=0, flag=flag, 
                border=border)
        sizer.Add(self.buttons_panel, proportion=0, flag=flag, border=border)
        self.SetSizerAndFit(sizer)

    def pull(self):
        '''
        Return a dictionary of the settings the user chose in this dialog.
        '''
        path = self.export_directory_panel.export_text.GetValue()
        data_interpreters_info = self.data_interpreters_panel.pull()
        
        return_dict = {'path':path,
                       'data_interpreters_info':data_interpreters_info}
        return return_dict


class ExportDirectoryPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.export_text = NamedTextCtrl(self, name=pt.EXPORT_TO_DIRECTORY, 
                                          style=wx.TE_READONLY)
        default_path = os.getcwd()
        self.export_text.SetValue(default_path)
        browse_button = wx.Button(self, label=pt.BROWSE)
        
        flag = wx.ALL
        border = 5
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(self.export_text,   proportion=1, flag=flag, 
                                            border=border)
        sizer.Add(browse_button, proportion=0, flag=flag, 
                                            border=border)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self._on_browse, browse_button)

    def _on_browse(self, event=None):
        dlg = wx.DirDialog(self, message=pt.CHOOSE_EXPORT_DIRECTORY)
        if dlg.ShowModal() == wx.ID_OK:
            self.export_text.SetValue(dlg.GetPath()) 


class ButtonsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        ok_button = wx.Button(self, id=wx.ID_OK, label=pt.EXPORT_DATA)
        cancel_button  = wx.Button(self, id=wx.ID_CANCEL)
         
        flag = wx.ALL
        border = 5
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(cancel_button,           proportion=0, flag=flag, 
                                            border=border)
        sizer.Add(ok_button,               proportion=1, flag=flag, 
                                            border=border)
        self.SetSizer(sizer)


class ExportControlPanel(OptionalControlPanel):
    def layout_ui(self):
        vsizer = wx.BoxSizer(orient=wx.VERTICAL)
        hsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        tsizer = wx.BoxSizer(orient=wx.VERTICAL)

        active_checkbox = wx.CheckBox(self, label='')
        active_checkbox.Enable(self.optional)
        active_checkbox.Show(self.optional)
        self.Bind(wx.EVT_CHECKBOX, self._activate, active_checkbox)

        title = wx.StaticText(self, label=self.plugin.name)
        f = title.GetFont()
        f.SetWeight(wx.BOLD)
        title.SetFont(f)
        title_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        title_sizer.Add(active_checkbox, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, 
                border=5)
        title_sizer.Add(title, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL)

        vsizer.Add(title_sizer, flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        for ctrl_name in sorted(self.ctrls.keys()):
            vsizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)

        description = wx.StaticText(self, label=self.plugin.description)
        hsizer.Add(vsizer)
        hsizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 
                flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=8)
        hsizer.Add(description, proportion=1, flag=wx.ALL, border=5)

        tsizer.Add(hsizer)
        tsizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(tsizer)

        self.active_checkbox = active_checkbox
        self.title = title

class DataInterpretersPanel(ScrolledPanel):
    def __init__(self, parent, data_interpreters, trials):
        ScrolledPanel.__init__(self, parent)
        self.control_panels = {}

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        for di in data_interpreters.values():
            cp = ExportControlPanel(self, di)
            cp.Enable(di.is_available(trials))
            cp.active = False
            self.control_panels[di.name] = cp
            sizer.Add(cp, flag=wx.EXPAND)

        self.SetSizer(sizer)
        self.SetMinSize((600, 450))
        self.SetupScrolling()

    def pull(self):
        results_dict = {}
        for panel in self.control_panels.values():
            pp = panel.pull()
            if pp is not None:
                results_dict[panel.plugin.name] = pp

        return results_dict

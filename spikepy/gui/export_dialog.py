

import os

import wx
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.common import program_text as pt
from spikepy.gui.named_controls import NamedTextCtrl

from spikepy.gui.control_panels import ExportControlPanel

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

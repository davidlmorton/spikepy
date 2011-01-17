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

import string

import wx

from validators import CharacterSubsetValidator
from spikepy.common import program_text as pt
from .named_controls import NamedTextCtrl, NamedChoiceCtrl 

valid_strategy_characters = ('-_.,%s%s' % 
                             (string.ascii_letters, string.digits))

class ExportDialog(wx.Dialog):
    def __init__(self, parent, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.export_directory_panel = ExportDirectoryPanel(self)

        select_stages_box = wx.StaticBox(self, label=pt.SELECT_STAGES)
        select_stages = wx.StaticBoxSizer(select_stages_box)
        self.export_stages_panel = ExportStagesPanel(self)
        select_stages.Add(self.export_stages_panel)
        
        self.options_panel = ExportOptionsPanel(self)

        self.buttons_panel = ButtonsPanel(self)

        csizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = 3
        csizer.Add(select_stages, proportion=0, flag=wx.ALL, border=border)
        csizer.Add(self.options_panel, proportion=1, 
                                        flag=wx.ALL|wx.ALIGN_BOTTOM, 
                                        border=border)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.EXPAND
        sizer.Add(self.export_directory_panel, proportion=0, flag=flag, 
                                                border=border)
        sizer.Add(csizer,                      proportion=0, flag=flag, 
                                                border=border)
        sizer.Add(self.buttons_panel,          proportion=0, flag=flag, 
                                                border=border)
        self.SetSizerAndFit(sizer)


    def get_settings(self):
        '''
        Return a dictionary of the settings the user chose in this dialog.
        '''
        path = self.export_directory_panel.export_text.GetValue()
        stages_selected = []
        for stage_name, stage_box in self.export_stages_panel.stages.items():
            if stage_box.IsChecked():
                stages_selected.append(stage_name)
        options_panel = self.options_panel
        file_format = options_panel.file_format.GetStringSelection()
        settings = {'path': path,
                    'stages_selected': stages_selected,
                    'file_format': file_format}
        return settings

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

class ExportOptionsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        format_choices = [pt.PLAIN_TEXT_SPACES, 
                   pt.PLAIN_TEXT_TABS,
                   pt.CSV, pt.MATLAB, pt.NUMPY_BINARY]
        self.file_format = NamedChoiceCtrl(self, name=pt.FILE_FORMAT, 
                                      choices=format_choices)
    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.file_format,    proportion=0, flag=wx.EXPAND|wx.ALL, 
                                        border=3)
        self.SetSizer(sizer)


class ExportStagesPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        raw_traces_box         = wx.CheckBox(self, label=pt.RAW_TRACES)
        detection_filter_box   = wx.CheckBox(self, label=pt.DETECTION_FILTER)
        detection_box          = wx.CheckBox(self, label=pt.DETECTION)
        extraction_filter_box  = wx.CheckBox(self, label=pt.EXTRACTION_FILTER)
        extraction_box         = wx.CheckBox(self, label=pt.EXTRACTION)
        clustering_box         = wx.CheckBox(self, label=pt.CLUSTERING)

        self.element_list = [raw_traces_box, 
                             detection_filter_box, 
                             detection_box, 
                             extraction_filter_box, 
                             extraction_box, 
                             clustering_box]

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.ALIGN_LEFT
        border = 2
        for element in self.element_list:
            sizer.Add(element,  proportion=0, flag=flag, border=border)
        self.SetSizer(sizer)

        self.stages = {'raw_traces': raw_traces_box,
                       'detection_filter':detection_filter_box,
                       'detection': detection_box,
                       'extraction_filter': extraction_filter_box,
                       'extraction': extraction_box,
                       'clustering': clustering_box}

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

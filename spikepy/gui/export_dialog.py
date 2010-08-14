import os

import string

import wx

from .strategy_utils import (make_methods_set_name, make_settings_name, 
                             make_strategy_name)
from validators import CharacterSubsetValidator
from . import program_text as pt
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
        store_arrays_as = options_panel.store_arrays_as.GetStringSelection()
        file_format = options_panel.file_format.GetStringSelection()
        settings = {'path': path,
                    'stages_selected': stages_selected,
                    'store_arrays_as': store_arrays_as,
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

        choices = [pt.ROWS, pt.COLUMNS]
        self.store_arrays_as = NamedChoiceCtrl(self, name=pt.STORE_ARRAYS_AS, 
                                         choices=choices)

        choices = [pt.PLAIN_TEXT_SPACES, 
                   pt.PLAIN_TEXT_TABS,
                   pt.CSV, pt.MATLAB]
        self.file_format = NamedChoiceCtrl(self, name=pt.FILE_FORMAT, 
                                      choices=choices)
    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.store_arrays_as, proportion=0, flag=wx.EXPAND|wx.ALL, 
                                        border=3)
        sizer.Add(self.file_format,    proportion=0, flag=wx.EXPAND|wx.ALL, 
                                        border=3)
        self.SetSizer(sizer)

class ExportStagesPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        detection_filter_box   = wx.CheckBox(self, label=pt.DETECTION_FILTER)
        detection_box          = wx.CheckBox(self, label=pt.DETECTION)
        extraction_filter_box  = wx.CheckBox(self, label=pt.EXTRACTION_FILTER)
        extraction_box         = wx.CheckBox(self, label=pt.EXTRACTION)
        clustering_box         = wx.CheckBox(self, label=pt.CLUSTERING)

        self.element_list = [detection_filter_box, 
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

        self.stages = {'detection_filter':detection_filter_box,
                       'detection': detection_box,
                       'extraction_filter': extraction_filter_box,
                       'extraction': extraction_filter_box,
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

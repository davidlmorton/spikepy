import string

import wx

from .strategy_utils import (make_methods_set_name, make_settings_name, 
                             make_strategy_name)
from validators import CharacterSubsetValidator
from . import program_text as pt
from .named_controls import NamedTextCtrl 

valid_strategy_characters = ('-_.,%s%s' % 
                             (string.ascii_letters, string.digits))

class SaveStrategyDialog(wx.Dialog):
    def __init__(self, parent, old_name, all_names, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.old_name  = old_name
        self.all_names = all_names

        self.all_methods_set_names = list(set([str(make_methods_set_name(name))
                                               for name in all_names]))
        methods_set_name = make_methods_set_name(old_name)
        settings_name    = make_settings_name(old_name)

        # SAVE AS TEXT
        self.save_as_text = wx.StaticText(self, 
                            label=pt.STRATEGY_SAVE_AS)
        font = self.save_as_text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(16)
        self.save_as_text.SetFont(font)

        # METHODS SET TEXTCTRL
        self.methods_set_textctrl = NamedTextCtrl(self, 
                name=pt.METHODS_SET_NAME,
                validator=CharacterSubsetValidator(valid_strategy_characters))
        self.methods_set_textctrl.SetTextctrlSize((200,-1))
        self.methods_set_textctrl.SetValue(methods_set_name)
        if not old_name.lower().startswith(pt.CUSTOM_LC):
            self.methods_set_textctrl.Enable(False)

        # SETTINGS TEXTCTRL
        self.settings_textctrl   = NamedTextCtrl(self, name=pt.SETTINGS_NAME,
                validator=CharacterSubsetValidator(valid_strategy_characters))
        self.settings_textctrl.SetTextctrlSize((200,-1))
        self.settings_textctrl.SetValue(settings_name)

        # WARNING TEXT
        self.warning_text = wx.StaticText(self, label='')

        # BUTTONS
        self.ok_button = wx.Button(self, id=wx.ID_OK)
        cancel_button  = wx.Button(self, id=wx.ID_CANCEL)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALL|wx.EXPAND
        border = 5
        button_sizer.Add(cancel_button,  proportion=0, flag=flag, border=border)
        button_sizer.Add(self.ok_button, proportion=0, flag=flag, border=border)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        sizer.Add(self.save_as_text,         proportion=0, flag=flag, border=15)
        sizer.Add(self.methods_set_textctrl, proportion=0, flag=flag, border=5)
        sizer.Add(self.settings_textctrl,    proportion=0, flag=flag, border=5)
        sizer.Add(button_sizer,              proportion=0, flag=wx.ALIGN_RIGHT)
        sizer.Add(self.warning_text,         proportion=0, flag=flag, border=5)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.methods_set_textctrl.text_ctrl)
        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.settings_textctrl.text_ctrl)
        self._check_inputs()

    def get_strategy_name(self):
        methods_set_name = self.methods_set_textctrl.GetValue()
        settings_name    = self.settings_textctrl.GetValue()
        new_name = make_strategy_name(methods_set_name, settings_name)
        return new_name

    def _check_inputs(self, event=None):
        methods_set_name = self.methods_set_textctrl.GetValue()
        settings_name    = self.settings_textctrl.GetValue()
        new_name = make_strategy_name(methods_set_name, settings_name)
        self.save_as_text.SetLabel(pt.STRATEGY_SAVE_AS + 
                                   new_name)
        # ZERO LENGTH
        if len(methods_set_name) < 1 or len(settings_name) < 1:
            self.warning_text.SetLabel(pt.AT_LEAST_ONE_CHARACTER)
            self.ok_button.Enable(False)
            return
        new_methods_set_name = make_methods_set_name(new_name)
        new_settings_name   = make_settings_name(new_name)
        # METHODS SET NAME ALREADY USED
        if (pt.CUSTOM_LC in make_methods_set_name(self.old_name).lower() and 
            new_methods_set_name in self.all_methods_set_names):
            self.warning_text.SetLabel(pt.METHODS_SET_NAME_ALREADY_USED % 
                                       new_methods_set_name)
            self.ok_button.Enable(False)
            return
        # CUSTOM IN NAME
        if  pt.CUSTOM_LC in new_name:
            self.warning_text.SetLabel(pt.MAY_NOT_CONTAIN_CUSTOM)
            self.ok_button.Enable(False)
            return
        self.warning_text.SetLabel(pt.OK_TO_SAVE)
        self.ok_button.Enable(True)

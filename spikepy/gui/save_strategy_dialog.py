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

import string

import wx

from spikepy.common.strategy import (make_methods_used_name, 
                                     make_settings_name, 
                                     make_strategy_name)
from spikepy.gui.validators import CharacterSubsetValidator
from spikepy.common import program_text as pt
from spikepy.developer_tools.named_controls import NamedTextCtrl 

valid_strategy_characters = ('-_.,%s%s' % 
                             (string.ascii_letters, string.digits))

def get_unique_settings_names(names_list, methods_used_name):
    unique_names = set()
    for name in names_list:
        if make_methods_used_name(name) == methods_used_name:
            fname = make_settings_name(name)
        else:
            fname = pt.CUSTOM_LC
        unique_names.add(fname)
    return list(unique_names)

def get_unique_methods_used_names(names_list):
    unique_names = set()
    for name in names_list:
        fname = make_methods_used_name(name)
        unique_names.add(fname)
    return list(unique_names)

class SaveStrategyDialog(wx.Dialog):
    def __init__(self, parent, old_name, all_names, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.old_name  = old_name
        self.all_names = all_names

        # get all unique methods_used names
        self.all_methods_used_names = get_unique_methods_used_names(all_names) 
        
        methods_used_name = make_methods_used_name(old_name)
        settings_name    = make_settings_name(old_name)

        # SAVE AS TEXT
        self.save_as_text = wx.StaticText(self, 
                            label=pt.STRATEGY_SAVE_AS)
        font = self.save_as_text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        font.SetPointSize(16)
        self.save_as_text.SetFont(font)

        # METHODS USED TEXTCTRL
        self.methods_used_textctrl = NamedTextCtrl(self, 
                name=pt.METHODS_USED_NAME,
                validator=CharacterSubsetValidator(valid_strategy_characters))
        self.methods_used_textctrl.SetTextctrlSize((200,-1))
        self.methods_used_textctrl.SetValue(methods_used_name)
        if not old_name.lower().startswith(pt.CUSTOM_LC):
            self.methods_used_textctrl.Enable(False)

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
        sizer.Add(self.methods_used_textctrl, proportion=0, flag=flag, border=5)
        sizer.Add(self.settings_textctrl,    proportion=0, flag=flag, border=5)
        sizer.Add(button_sizer,              proportion=0, flag=wx.ALIGN_RIGHT)
        sizer.Add(self.warning_text,         proportion=0, flag=flag, border=5)
        self.SetSizerAndFit(sizer)

        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.methods_used_textctrl.text_ctrl)
        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.settings_textctrl.text_ctrl)
        self._check_inputs()

    def get_strategy_name(self):
        methods_used_name = self.methods_used_textctrl.GetValue()
        settings_name     = self.settings_textctrl.GetValue()
        new_name = make_strategy_name(methods_used_name, settings_name)
        return new_name

    def _check_inputs(self, event=None):
        methods_used_name = self.methods_used_textctrl.GetValue()
        settings_name     = self.settings_textctrl.GetValue()
        new_name = make_strategy_name(methods_used_name, settings_name)
        self.save_as_text.SetLabel(pt.STRATEGY_SAVE_AS + 
                                   new_name)
        # ZERO LENGTH
        if len(methods_used_name) < 1 or len(settings_name) < 1:
            self.warning_text.SetLabel(pt.AT_LEAST_ONE_CHARACTER)
            self.ok_button.Enable(False)
            return
        new_methods_used_name = make_methods_used_name(new_name)
        new_settings_name     = make_settings_name(new_name)
        # CUSTOM IN NAME
        if  pt.CUSTOM_LC in new_name:
            self.warning_text.SetLabel(pt.MAY_NOT_CONTAIN_CUSTOM)
            self.ok_button.Enable(False)
            return
        # METHODS USED NAME ALREADY USED
        if (pt.CUSTOM_LC in make_methods_used_name(self.old_name) and 
            new_methods_used_name in self.all_methods_used_names):
            self.warning_text.SetLabel(pt.METHODS_USED_NAME_ALREADY_USED % 
                                       new_methods_used_name)
            self.ok_button.Enable(False)
            return
        # SETTINGS NAME ALREADY USED
        if (new_settings_name in get_unique_settings_names(self.all_names,
                                                      new_methods_used_name)):
            self.warning_text.SetLabel(pt.SETTINGS_NAME_ALREADY_USED % 
                                       new_settings_name)
            self.ok_button.Enable(False)
            return
        self.warning_text.SetLabel(pt.OK_TO_SAVE)
        self.ok_button.Enable(True)

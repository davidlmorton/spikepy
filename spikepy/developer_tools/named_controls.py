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

from spikepy.gui.validators import FloatValidator
from spikepy.common.config_manager import config_manager as config

class NamedChoiceCtrl(wx.Panel):
    def __init__(self, parent, name="", choices=[], bar_width=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        if bar_width == None and len(choices) > 0:
            bar_width_in_characters = max(map(len, choices))
            bar_width = bar_width_in_characters*8
            self.choice = wx.Choice(self, choices=choices) 
        elif bar_width == None and len(choices) == 0:
            self.choice = wx.Choice(self, choices=choices)
        else:
            self.choice = wx.Choice(self, choices=choices)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = config.control_border
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(self.name, proportion=0, flag=flag, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.choice, proportion=1, flag=flag, border=border)
        
        self.SetSizer(sizer)

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, string):
        self.choice.SetStringSelection(string)

    def SetItems(self, item_list):
        self.choice.SetItems(item_list)

    def GetItems(self):
        return self.choice.GetItems()

class NamedSpinCtrl(wx.Panel):
    def __init__(self, parent, name="", min=0, max=100, **kwargs):
        wx.Panel.__init__(self, parent)

        self.name = wx.StaticText(self, label=name)
        if 'style' in kwargs.keys():
            kwargs['style'] = kwargs['style']|wx.SP_ARROW_KEYS
        else:
            kwargs['style'] = wx.SP_ARROW_KEYS
        self.spin_ctrl = wx.SpinCtrl(self, size=(50,-1), min=0, max=max, 
                                     **kwargs)
        self._original_background_color = self.spin_ctrl.GetBackgroundColour()
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border = config.control_border
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.spin_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_SPINCTRL, self._pre_check_value)
        self.Bind(wx.EVT_TEXT, self._pre_check_value)
        self.min = min

    def SetBackgroundColour(self, color):
        if wx.Platform != '__WXMAC__': 
            self.spin_ctrl.SetBackgroundColour(color)

    def _pre_check_value(self, event=None):
        '''
        Check (with a delay) if the inputted value is less than the minimum 
        and if so, set the value to the minimum.
        '''
        value = self.spin_ctrl.GetValue()
        
        wx.CallLater(10, self._check_and_color)
        wx.CallLater(1000, self._check_value)

    def _check_and_color(self):
        value = self.spin_ctrl.GetValue()
        if value < self.min:
            self.SetBackgroundColour('pink')
        else:
            self.SetBackgroundColour(self._original_background_color)

    def _check_value(self):
        value = self.spin_ctrl.GetValue()
        if value < self.min:
            self.spin_ctrl.SetValue(self.min)
            self.SetBackgroundColour(self._original_background_color)

    def SetRange(self, range_tuple):
        self.spin_ctrl.SetRange(*range_tuple)

    def GetValue(self):
        return self.spin_ctrl.GetValue()

    def SetValue(self, value):
        return self.spin_ctrl.SetValue(value)

class NamedFloatCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        self.text_ctrl = wx.TextCtrl(self, size=(50,-1),
                                     validator=FloatValidator())
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border=config.control_border
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.text_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)

    def SetTextctrlSize(self, size):
        self.text_ctrl.SetMinSize(size)

    def GetValue(self):
        return self.text_ctrl.GetValue()

    def SetValue(self, value):
        self.text_ctrl.SetValue(value)

class NamedTextCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent)

        self.name = wx.StaticText(self, label=name)
        self.text_ctrl = wx.TextCtrl(self, size=(50,-1), **kwargs)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border=config.control_border
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.text_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)

    def SetTextctrlSize(self, size):
        self.text_ctrl.SetMinSize(size)

    def GetValue(self):
        return self.text_ctrl.GetValue()

    def SetValue(self, value):
        self.text_ctrl.SetValue(value)

class OptionalNamedFloatCtrl(NamedFloatCtrl):
    def __init__(self, parent, name, enabled=False, **kwargs):
        NamedFloatCtrl.__init__(self, parent, name='', **kwargs)
        
        self.checkbox = wx.CheckBox(self, label=name)
        self.GetSizer().Insert(0, self.checkbox, proportion=0, flag=wx.ALL,
                                                 border=3)
        self.Bind(wx.EVT_CHECKBOX, self._enable, self.checkbox)
        self._enabled = enabled
        self._enable(state=enabled)

    def _enable(self, event=None, state=None):
        if event is not None:
            state = event.IsChecked()
        self._enabled = state
        self.name.Enable(state)
        self.checkbox.SetValue(state)
        self.text_ctrl.Enable(state)

    def GetValue(self):
        return self.text_ctrl.GetValue()

    def SetValue(self, value):
        self.text_ctrl.SetValue(value)

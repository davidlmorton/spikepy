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
import wx
from spikepy.common.errors import *
from spikepy.common.valid_types import *

class ValidControl(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

    def register_valid_entry_callback(self, valid_entry_callback):
        self.valid_entry_callback = valid_entry_callback 

    def SetFocusFromKbd(self):
        self.green.text_ctrl.SetFocus()

def make_control(parent, name, valid_type, background_color=None):
    type_dict = {ValidInteger:ValidNumberControl,
                 ValidFloat:ValidNumberControl,
                 ValidOption:ValidChoiceControl,
                 ValidBoolean:ValidBooleanControl}
    ctrl = type_dict[valid_type.__class__](parent, name=name, 
            valid_type=valid_type)
    if background_color is not None:
        ctrl.SetBackgroundColour(background_color)
    return ctrl

class ValidBooleanControl(ValidControl):
    def __init__(self, parent, name='', valid_type=None, 
            valid_entry_callback=None, **kwargs):
        ValidControl.__init__(self, parent, **kwargs)
            
        ctrl  = wx.CheckBox(self, label=name)
        self.Bind(wx.EVT_CHECKBOX, self._value_entered, ctrl)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(ctrl, proportion=1, flag=flag|wx.ALIGN_LEFT, border=2)
        self.SetSizer(sizer)

        self.ctrl = ctrl
        self.valid_type = valid_type 
        self.valid_entry_callback = valid_entry_callback
        self._last_value = None
        self.SetValue(valid_type(missing=True))

    def GetValue(self):
        return bool(self.valid_type(self.ctrl.GetValue()))
        
    def SetValue(self, value):
        temp, self.valid_entry_callback = self.valid_entry_callback, None
        self.ctrl.SetValue(value)
        self.valid_entry_callback = temp

    def _value_entered(self, event):
        event.Skip()
        my_value = self.GetValue()
        if my_value == self._last_value: 
            return
        else:
            self._last_value = my_value
            if self.valid_entry_callback is not None:
                self.valid_entry_callback(my_value)

class ValidNumberControl(ValidControl):
    def __init__(self, parent, name='', valid_type=None, 
            width=90, valid_entry_callback=None, **kwargs):
        ValidControl.__init__(self, parent, **kwargs)
            
        label = wx.StaticText(self, label=name)
        ctrl  = wx.TextCtrl(self, size=(width, -1))
        self.Bind(wx.EVT_TEXT, self._value_entered, ctrl)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(label, proportion=0, flag=flag|wx.ALIGN_RIGHT, border=2)
        sizer.Add((5,5), proportion=0)
        sizer.Add(ctrl, proportion=1, flag=flag|wx.ALIGN_LEFT, border=2)
        self.SetSizer(sizer)

        self.ctrl = ctrl
        self.valid_type = valid_type 
        self.valid_entry_callback = valid_entry_callback
        self._last_value = None
        self.SetValue(valid_type(missing=True))

    def GetValue(self):
        return self.valid_type(self.ctrl.GetValue())
        
    def SetValue(self, value):
        temp, self.valid_entry_callback = self.valid_entry_callback, None
        self.ctrl.SetValue(str(value))
        self.valid_entry_callback = temp

    def _value_entered(self, event):
        event.Skip()
        try:
            my_value = self.GetValue()
        except InvalidValueError:
            self.ctrl.SetBackgroundColour(wx.Colour(255, 200, 200))
            self._last_value = None
            return

        if my_value == self._last_value: 
            return
        self._last_value = my_value

        self.ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
        if self.valid_entry_callback is not None:
            self.valid_entry_callback(my_value)

class ValidChoiceControl(ValidControl):
    def __init__(self, parent, name='', valid_type=None, 
            width=90, valid_entry_callback=None, **kwargs):
        ValidControl.__init__(self, parent, **kwargs)
            
        label = wx.StaticText(self, label=name)
        ctrl  = wx.Choice(self, choices=valid_type.passed_args, 
                size=(width, -1))
        self.Bind(wx.EVT_CHOICE, self._value_entered, ctrl)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(label, proportion=0, flag=flag|wx.ALIGN_RIGHT, border=2)
        sizer.Add((5,5), proportion=0)
        sizer.Add(ctrl, proportion=1, flag=flag|wx.ALIGN_LEFT, border=2)
        self.SetSizer(sizer)

        self.ctrl = ctrl
        self.valid_type = valid_type 
        self.valid_entry_callback = valid_entry_callback
        self._last_value = None
        self.SetValue(valid_type(missing=True))

    def GetValue(self):
        return self.valid_type(self.ctrl.GetStringSelection())
        
    def SetValue(self, value):
        temp, self.valid_entry_callback = self.valid_entry_callback, None
        self.ctrl.SetStringSelection(str(value))
        self.valid_entry_callback = temp

    def _value_entered(self, event):
        event.Skip()
        my_value = self.GetValue()
        if my_value == self._last_value: 
            return
        else:
            self._last_value = my_value
            if self.valid_entry_callback is not None:
                self.valid_entry_callback(my_value)

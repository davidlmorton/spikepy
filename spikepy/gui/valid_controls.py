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

class ValidControl(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

    def SetFocusFromKbd(self):
        self.green.text_ctrl.SetFocus()

class ValidFloatControl(ValidControl):
    def __init__(self, parent, name='', min_value=None, max_value=None, 
            width=50, valid_entry_callback=None, **kwargs):
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
        self.min_value = min_value
        self.max_value = max_value 
        self.valid_entry_callback = valid_entry_callback
        self._last_value = None

    def GetValue(self):
        try:
            return float(self.ctrl.GetValue())
        except ValueError:
            return
        
    def SetValue(self, value):
        temp, self.valid_entry_callback = self.valid_entry_callback, None
        self.ctrl.SetValue(str(value))
        self.valid_entry_callback = temp

    def _value_entered(self, event):
        event.Skip()
        try:
            my_value = float(self.ctrl.GetValue())
        except ValueError:
            self.ctrl.SetBackgroundColour(wx.Colour(255, 200, 200))
            self._last_value = None
            return

        if my_value == self._last_value:
            return
        else:
            self._last_value = my_value 

        valid = True
        if self.min_value is not None and my_value < self.min_value:
            valid = False
        if self.max_value is not None and my_value > self.max_value:
            valid = False

        if valid:
            self.ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
            if self.valid_entry_callback is not None:
                self.valid_entry_callback(my_value)
        else:
            self.ctrl.SetBackgroundColour(wx.Colour(255, 200, 200))
            
        

        
    

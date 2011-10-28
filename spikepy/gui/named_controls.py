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

class NamedChoiceCtrl(wx.Panel):
    def __init__(self, parent, name="", choices=[], bar_width=None, 
            selection_callback=None, background_color=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.selection_callback = selection_callback

        if background_color is not None:
            self.SetBackgroundColour(background_color)

        self.name = wx.StaticText(self, label=name)
        if bar_width is None and len(choices) > 0:
            bar_width_in_characters = max(map(len, choices))
            bar_width = bar_width_in_characters*12
            self.choice = wx.Choice(self, choices=choices) 
            self.choice.SetMinSize((bar_width, -1))
        elif bar_width is None and len(choices) == 0:
            self.choice = wx.Choice(self, choices=choices)
        else:
            self.choice = wx.Choice(self, choices=choices)
            self.choice.SetMinSize((bar_width, -1))
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = 1
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(self.name, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.choice, proportion=1, flag=flag, border=border)
        
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CHOICE, self._selection_made, self.choice)

    @property
    def selection(self):
        return self.choice.GetStringSelection()

    @selection.setter
    def selection(self, new_selection):
        self.choice.SetStringSelection(str(new_selection))
        self._selection_made()

    def _selection_made(self, event=None):
        if self.selection_callback is not None:
            self.selection_callback(self.selection)
        if event is not None:
            event.Skip()

    def Enable(self, state):
        self.choice.Enable(state)
        self.name.Enable(state)

    def SetFocusFromKbd(self):
        self.choice_ctrl.SetFocus()

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, string):
        self.choice.SetStringSelection(string)

    def SetItems(self, item_list):
        self.choice.SetItems(item_list)

    def GetItems(self):
        return self.choice.GetItems()


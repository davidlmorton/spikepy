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
from scipy.io import loadmat

class MatlabDialog(wx.Dialog):
    def __init__(self, parent, fullpath):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, 
                           "Generic Matlab(tm) File Interpreter.",
                           style=wx.DEFAULT_DIALOG_STYLE)

        filename = os.path.split(fullpath)[1]

        filename_text = wx.StaticText(self, wx.ID_ANY, 
                                      label="Filename: %s" % filename)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(filename_text)
        self.SetSizerAndFit(sizer)

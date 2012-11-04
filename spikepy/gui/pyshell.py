#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import wx.py as py
from wx.lib.pubsub import Publisher as pub
import wx

# this is filled up when program runs, it is just a repository of
#   handy local variables for the pyshell.
locals_dict = {'pub': pub}


class PyShellDialog(wx.Dialog):
    def __init__(self, parent, **kwargs):
        if 'style' in kwargs.keys():
            kwargs['style'] = (kwargs['style']|wx.RESIZE_BORDER|
                                               wx.DEFAULT_DIALOG_STYLE)
        else:
            kwargs['style'] = wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, **kwargs)

        shell = py.shell.Shell(self, locals=locals_dict)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(shell, proportion=1, flag=wx.EXPAND|wx.ALL,
                         border=12)
        self.SetSizer(sizer)

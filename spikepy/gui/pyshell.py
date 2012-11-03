

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

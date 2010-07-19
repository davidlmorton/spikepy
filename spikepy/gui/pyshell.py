import wx.py as py
from wx.lib.pubsub import Publisher as pub
import wx


class PyShellDialog(wx.Dialog):
    def __init__(self, parent, **kwargs):
        if 'style' in kwargs.keys():
            kwargs['style'] = (kwargs['style']|wx.RESIZE_BORDER|
                                               wx.DEFAULT_DIALOG_STYLE)
        else:
            kwargs['style'] = wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, **kwargs)

        locals = {'pub':pub}
        locals['dict'] = {'stage_name':'Detection Filter', 
                          'method_name':'Infinite Impulse Response'}
        shell = py.shell.Shell(self, locals=locals)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(shell, proportion=1, flag=wx.EXPAND|wx.ALL,
                         border=12)
        self.SetSizer(sizer)

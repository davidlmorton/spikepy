import wx.py as py
import wx


class PyShellDialog(wx.Dialog):
    def __init__(self, parent, **kwargs):
        if 'style' in kwargs.keys():
            kwargs['style'] = (kwargs['style']|wx.RESIZE_BORDER|
                                               wx.DEFAULT_DIALOG_STYLE)
        else:
            kwargs['style'] = wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, **kwargs)

        shell = py.shell.Shell(self)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(shell, proportion=1, flag=wx.EXPAND|wx.ALL,
                         border=12)
        self.SetSizer(sizer)

import wx.py as py
from wx.lib.pubsub import Publisher as pub
import wx

# this is filled up when program runs, it is just a repository of
#   handy local variables for the pyshell.
locals_dict = {'pub': pub}


class PyShellDialog(wx.Dialog):
    def __init__(self, parent, locals={}, **kwargs):
        if 'style' in kwargs.keys():
            kwargs['style'] = (kwargs['style']|wx.RESIZE_BORDER|
                                               wx.DEFAULT_DIALOG_STYLE)
        else:
            kwargs['style'] = wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, **kwargs)

        # Assigning key value pairs to locals is used to save time during
        #     debugging.
        locals.update(locals_dict)
        locals['dict'] = {'stage_name':'Detection Filter', 
                          'method_name':'Infinite Impulse Response'}
        locals['dict'] = {'stage_name':'Spike Detection', 
                          'method_name':'Voltage Threshold'}
        locals['dict'] = {'stage_name':'Extraction', 
                          'method_name':'Waveform'}
        shell = py.shell.Shell(self, locals=locals)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(shell, proportion=1, flag=wx.EXPAND|wx.ALL,
                         border=12)
        self.SetSizer(sizer)

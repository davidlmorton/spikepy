import wx

from spikepy.gui.look_and_feel_settings import lfs


class ControlPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        instructions = wx.StaticText(self, 
                label='Press "Run" button to confirm.')

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = lfs.CONTROL_PANEL_BORDER
        sizer.Add(instructions, proportion=0, flag=flag, border=border)
        self.SetSizer(sizer)

    def get_parameters(self):
        parameters = {}
        return parameters

import wx

from spikepy.gui.named_controls import NamedTextCtrl, OptionalNamedTextCtrl
from spikepy.gui.look_and_feel_settings import lfs


class ControlPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        pre_window_ctrl = NamedTextCtrl(self, name='')
        spike_centered_checkbox = wx.Checkbox(self, 
                label='Window centered on spike.')
        post_window_ctrl = NamedTextCtrl(self, name='')

        self.Bind(wx.EVT_CHECKBOX, self._spike_centered, 
                spike_centered_checkbox)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = lfs.CONTROL_PANEL_BORDER
        sizer.Add(pre_window_ctrl,         proportion=0, flag=flag, 
                border=border)
        sizer.Add(spike_centered_checkbox, proportion=0, flag=flag, 
                border=border)
        sizer.Add(post_window_ctrl,        proportion=0, flag=flag, 
                border=border)
        self.SetSizer(sizer)

        # --- SET DEFAULTS ---
        pre_window_ctrl.SetValue('0.5')
        spike_centered_checkbox.SetValue('False')
        post_window_ctrl.SetValue('1.0')
        

    def _spike_centered(self, event=None):
        pass 

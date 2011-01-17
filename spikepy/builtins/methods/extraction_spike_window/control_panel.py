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

from spikepy.gui.named_controls import NamedFloatCtrl, OptionalNamedFloatCtrl
from spikepy.gui.look_and_feel_settings import lfs


class ControlPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        pre_window_ctrl = NamedFloatCtrl(self, name='Window Prepadding (ms)')
        spike_centered_checkbox = wx.CheckBox(self, 
                label='Window centered on spike.')
        post_window_ctrl = NamedFloatCtrl(self, name='Window Postpadding (ms)')
        exclude_overlappers_checkbox = wx.CheckBox(self, 
                label='Exclude windows that overlap.')
        truncation_info = wx.StaticText(self, label=
               '    * Note: spike windows overlapping ends\nof trace are always excluded.')

        self.Bind(wx.EVT_CHECKBOX, self._spike_centered, 
                spike_centered_checkbox)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = lfs.CONTROL_PANEL_BORDER
        sizer.Add(pre_window_ctrl,              proportion=0, flag=flag, 
                border=border)
        sizer.Add(spike_centered_checkbox,      proportion=0, flag=flag, 
                border=border)
        sizer.Add(post_window_ctrl,             proportion=0, flag=flag, 
                border=border)
        sizer.Add(exclude_overlappers_checkbox, proportion=0, flag=flag, 
                border=border)
        sizer.Add(truncation_info, proportion=0, flag=flag, 
                border=border)
        self.SetSizer(sizer)

        self.spike_centered_checkbox      = spike_centered_checkbox
        self.exclude_overlappers_checkbox = exclude_overlappers_checkbox
        self.pre_window_ctrl              = pre_window_ctrl
        self.post_window_ctrl             = post_window_ctrl

        # --- SET DEFAULTS ---
        pre_window_ctrl.SetValue('1.5')
        self._spike_centered(should_center_spike=True)
        post_window_ctrl.SetValue('3.25')
        exclude_overlappers_checkbox.SetValue(False)

    def _spike_centered(self, event=None, should_center_spike=None):
        if event is not None:
            should_center_spike = event.IsChecked()
        self.spike_centered_checkbox.SetValue(should_center_spike)
        self.post_window_ctrl.Enable(not should_center_spike)

    def set_parameters(self, pre_padding="1.5", post_padding="3.25", 
                       exclude_overlappers=False):
        pre_padding = str(pre_padding)
        post_padding = str(post_padding)
        self._spike_centered(should_center_spike=(pre_padding == post_padding))
        self.pre_window_ctrl.SetValue(pre_padding)
        self.post_window_ctrl.SetValue(post_padding)
        self.exclude_overlappers_checkbox.SetValue(exclude_overlappers)
        
    def get_parameters(self):
        pre_window = float(self.pre_window_ctrl.GetValue())
        if self.spike_centered_checkbox.IsChecked():
            post_window = pre_window
        else:
            post_window = float(self.post_window_ctrl.GetValue())
        exclude_overlappers = self.exclude_overlappers_checkbox.IsChecked()
        return {'pre_padding':pre_window, 'post_padding':post_window, 
                'exclude_overlappers':exclude_overlappers}

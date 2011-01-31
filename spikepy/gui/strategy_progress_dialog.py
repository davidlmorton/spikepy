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
from wx.lib.pubsub import Publisher as pub

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt

class NamedProgressIndicator(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name, 
                                  style=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
        self.gauge = wx.Gauge(self, wx.ID_ANY, 5)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = config.control_border
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add((10,5), proportion=1)
        sizer.Add(self.name, proportion=0, flag=flag, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.gauge, proportion=0, flag=flag, border=border)
        self.SetSizer(sizer)

    def set_value(self, value):
        self.gauge.SetValue(value)
        wx.Yield()
        
class StrategyProgressDialog(wx.Dialog):
    def __init__(self, parent, display_names, ids, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        info_text = wx.StaticText(self, label=pt.STRATEGY_PROGRESS_INFO)
        self.display_names = display_names
        self.ids = ids

        self.progress_indicators = []
        for display_name in self.display_names:
            pi = NamedProgressIndicator(self, display_name) 
            self.progress_indicators.append(pi)

        self.abort_button = wx.Button(self, label=pt.ABORT)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(info_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        for pi in self.progress_indicators:
            sizer.Add(pi, proportion=0, flag=wx.ALL|wx.EXPAND, border=3)
        sizer.Add(self.abort_button, proportion=0, flag=wx.ALL|wx.EXPAND,
                  border=6)

        self.SetSizerAndFit(sizer)

        self.stage_values = {'detection_filter':1,
                             'detection': 2,
                             'extraction_filter':3,
                             'extraction':4,
                             'clustering':5}

        self.Bind(wx.EVT_BUTTON, self._abort, self.abort_button)

    def update_progress(self, trial_id, stage_name):
        index = self.ids.index(trial_id)
        self.progress_indicators[index].set_value(self.stage_values[stage_name])
        end = True
        for pi in self.progress_indicators:
            if pi.gauge.GetValue() != 5:
                end = False
        if end:
            self.Show(False)
            self.Destroy()
        return end

    def _abort(self, event):
        pub.sendMessage("ABORT_STRATEGY", data='USER_PRESSED_ABORT')
        self.abort_button.SetLabel(pt.ABORTING)
        self.abort_button.Enable(False)

    def abort(self):
        self.Show(False)
        self.Destroy()
        


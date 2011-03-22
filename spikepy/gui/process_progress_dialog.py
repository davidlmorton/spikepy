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

class StrategyProgressDialog(wx.Dialog):
    def __init__(self, parent, trial_list, message_queue, abort_queue, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.trial_list = trial_list
        self.message_queue = message_queue
        self.abort_queue = abort_queue
        self.update_period = 333 # in ms

        info_text = wx.StaticText(self, label=pt.STRATEGY_PROGRESS_INFO)

        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, 
                              size=(350,20), style=wx.GA_HORIZONTAL)
        self.processing_text = wx.StaticText(self)
        self.abort_button = wx.Button(self, label=pt.ABORT)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(info_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.processing_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.gauge, proportion=0, flag=wx.ALL|wx.EXPAND, border=8)
        sizer.Add(self.abort_button, proportion=0, flag=wx.ALL|wx.ALIGN_RIGHT,
                  border=6)
        # ADD A GRID UNDER "SHOW DETAILS"

        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_BUTTON, self._abort, self.abort_button)
        self.Bind(wx.EVT_IDLE, self._update_processing)
        self._reset_should_update()

    def _reset_should_update(self):
        self._should_update = True

    def _update_processing(self, event):
        if self._should_update:
            self._update_count += 1
            self._should_update = False
            wx.CallLater(self.update_period, self._reset_should_update)

    def _abort(self, event):
        self.abort_queue.put(True)
        self.abort_button.Enable(False)

    def close(self):
        self.Show(False)
        self.Destroy()
        


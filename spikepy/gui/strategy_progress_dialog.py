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
    def __init__(self, parent, stage_names, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        info_text = wx.StaticText(self, label=pt.STRATEGY_PROGRESS_INFO)
        self.stage_names = stage_names

        self.gauge = wx.Gauge(self, wx.ID_ANY, 2*len(stage_names)+1, 
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

        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_BUTTON, self._abort, self.abort_button)
        self.Bind(wx.EVT_IDLE, self._update_processing)
        self._processing = pt.STARTUP
        self._reset_should_update()
        self._update_count = 0
        self._should_layout = False

    def _reset_should_update(self):
        self._should_update = True

    def _update_processing(self, event):
        if self._should_update:
            self._update_count += 1
            self._should_update = False
            wx.CallLater(333, self._reset_should_update)

            if self._should_layout:
                self._update_count = 0
            dots = ' '
            for i in range(self._update_count%4):
                dots += '.'

            if self._processing != pt.STARTUP:
                self.processing_text.SetLabel('Processing: %s%s' % 
                                          (self._processing, dots))
            else:
                self.processing_text.SetLabel('%s%s' % (self._processing, dots))
            if self._should_layout:
                self.Layout()
                self._should_layout = False

    def update_progress(self, stage_name):
        if stage_name == 'STARTUP':
            index = -1
        else:
            index = self.stage_names.index(stage_name)
        processing_index = min(index+1, len(self.stage_names)-1)
        processing_stage = self.stage_names[processing_index].upper()
        self._processing = getattr(pt, processing_stage)
        self._should_layout = True
        self.gauge.SetValue(2*(index+1)+1)
        end = (index == len(self.stage_names)-1)
        if end:
            wx.CallLater(750, self.abort)
        return end

    def _abort(self, event):
        pub.sendMessage("ABORT_STRATEGY", data='USER_PRESSED_ABORT')
        self._processing = pt.ABORTING
        self.abort_button.Enable(False)

    def abort(self):
        self.Show(False)
        self.Destroy()
        


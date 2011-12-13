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
import time
import Queue
from datetime import datetime

import wx
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.pubsub import Publisher as pub
import wx.grid as gridlib

from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt

class ProcessProgressDialog(wx.Dialog):
    def __init__(self, parent, message_queue, **kwargs):
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.STAY_ON_TOP

        width, height = config.get_size('main_frame')*0.75
        kwargs['style'] |= wx.RESIZE_BORDER
        kwargs['style'] |= wx.CAPTION
        kwargs['style'] |= wx.SYSTEM_MENU

        kwargs['title'] = pt.PROCESS_PROGRESS

        wx.Dialog.__init__(self, parent, **kwargs)

        self.message_queue = message_queue
        self.update_period = 200 # in ms

        info_text = wx.StaticText(self, label=pt.STRATEGY_PROGRESS_INFO)
        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, 
                              size=(int(width*0.8),20), style=wx.GA_HORIZONTAL)
        self.gauge2 = wx.Gauge(self, wx.ID_ANY, 100, 
                              size=(int(width*0.8), 5), style=wx.GA_HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_CLOSE)
        self.close_button.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.close, self.close_button)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(info_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.gauge, proportion=0, 
                flag=wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.LEFT|wx.RIGHT, 
                border=8)
        sizer.Add(self.gauge2, proportion=0, 
                flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=3)
        sizer.Add(self.close_button, proportion=0, flag=wx.ALIGN_RIGHT|wx.RIGHT,
                border=10)

        message_text = wx.TextCtrl(self, style=wx.TE_MULTILINE, 
                size=(int(width*0.8), int(height*0.6)))
        f = message_text.GetFont()
        f.SetPointSize(10)
        f.SetFaceName('Courier 10 Pitch')
        message_text.SetFont(f)
        message_text.SetBackgroundColour(wx.BLACK)
        message_text.SetForegroundColour(wx.WHITE)
        message_text.Enable(False)
        
        sizer.Add(message_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_LEFT, border=10)

        self.SetSizerAndFit(sizer)

        self.message_text = message_text 
        self._num_tasks = 1
        self._num_tasks_competed = 0
        self._display_messages = []
        self._should_update = True
        self.info_text = info_text
        self._start_time = time.time()
        self._plugin_runtime = 0.0
        self._just_once = True

        self.Bind(wx.EVT_TIMER, self._update_processing)
        self.timer = wx.Timer(self)
        self.timer.Start(self.update_period)

    def _update_processing(self, event):
        while True:
            try:
                new_message = self.message_queue.get(False)
            except Queue.Empty:
                new_message = None
            if new_message is not None:
                statement, data = new_message
                if statement == 'TASKS':
                    self._num_tasks = len(data)
                    self._update_messages('Created %d tasks.' % len(data))
                if statement == 'SKIPPED_TASK':
                    self._num_tasks_competed += 1
                    self._update_messages('Skipped %s' % data)
                if statement == 'RUNNING_TASK':
                    self._update_messages('Started %s' % data)
                if statement == 'FINISHED_TASK':
                    self._num_tasks_competed += 1
                    self._update_messages(
                            'Finished %s\n    Runtime:%8.4f seconds' % 
                            (data['task'], data['runtime']))
                    self._plugin_runtime += data['runtime']

                progress = int((self._num_tasks_competed/
                        float(self._num_tasks))*100.0)
                self.gauge.SetValue(progress)
                self.gauge2.Pulse()
            else:
                break

        progress = int((self._num_tasks_competed/
                float(self._num_tasks))*100.0)
        self.gauge2.Pulse()
        if progress == 100 and self._just_once:
            self._just_once = False
            self.close_button.Enable()
            self.info_text.SetLabel('Finished Processing')
            total_runtime = time.time()-self._start_time
            self._update_messages('Finished Processing:\n    Total Runtime = %f seconds (real time)\n    Time spent in plugins = %f seconds (cpu time, not real time)' % (total_runtime, self._plugin_runtime))

    def _update_messages(self, message):
        now = datetime.now()
        display_message = '%02d:%02d:%02d - %s' % (now.hour, now.minute, 
                now.second, message)
        self._display_messages.append(display_message)

        self.message_text.SetValue(
                '\n'.join(self._display_messages))
        self.message_text.ShowPosition(self.message_text.GetLastPosition())
        wx.Yield()

    def close(self, event):
        event.Skip()
        pub.sendMessage('SET_RUN_BUTTONS_STATE', data=[True, True])
        self.Show(False)
        self.Destroy()


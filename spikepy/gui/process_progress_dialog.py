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
from spikepy.plotting_utils.plot_panel import PlotPanel
from spikepy.common import program_text as pt
from spikepy.utils.wrap import wrap

class GraphArea(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        # navigation buttons
        beginning_button = wx.Button(self, label='|<')
        back_button = wx.Button(self, label='<')
        forward_button = wx.Button(self, label='>')
        end_button = wx.Button(self, label='>|')
        self.Bind(wx.EVT_BUTTON, self.on_beginning, beginning_button)
        self.Bind(wx.EVT_BUTTON, self.on_back, back_button)
        self.Bind(wx.EVT_BUTTON, self.on_forward, forward_button)
        self.Bind(wx.EVT_BUTTON, self.on_end, end_button)
        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        button_sizer.Add(beginning_button, 
                flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=5)
        button_sizer.Add(back_button,
                flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=5)
        button_sizer.Add(forward_button,
                flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=5)
        button_sizer.Add(end_button,
                flag=wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(button_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
        self.SetSizer(sizer)

        self.plot_panels = []
        self.sizer = sizer
        self.beginning_button = beginning_button
        self.back_button = back_button
        self.forward_button = forward_button
        self.end_button = end_button
        self.shown_panel = 0

    def on_beginning(self, event):
        self.show_panel(0)
        self.enable_navigation_buttons()

    def on_back(self, event):
        self.show_panel(max(0, self.shown_panel-1))
        self.enable_navigation_buttons()

    def on_forward(self, event):
        self.show_panel(min(self.shown_panel+1, len(self.plot_panels)-1))
        self.enable_navigation_buttons()

    def on_end(self, event):
        self.show_panel(len(self.plot_panels)-1)
        self.enable_navigation_buttons()

    def enable_navigation_buttons(self):
        first_two = self.shown_panel > 0
        self.beginning_button.Enable(first_two)
        self.back_button.Enable(first_two)
        last_two = self.shown_panel < (len(self.plot_panels) - 1)
        self.forward_button.Enable(last_two)
        self.end_button.Enable(last_two)

    def add_plot(self):
        plot_panel = PlotPanel(self, figsize=(4.0, 2.0))
        self.plot_panels.append(plot_panel)
        self.sizer.Insert(0, plot_panel, proportion=1, flag=wx.EXPAND)

    def show_panel(self, i):
        self.plot_panels[self.shown_panel].Show(False)
        self.shown_panel = i
        self.plot_panels[self.shown_panel].Show(True)

    def plot(self, scheduler):
        self.add_plot()
        plot_panel = self.plot_panels[-1]

        figure = plot_panel.figure
        figure.set_facecolor('white')
        figure.set_edgecolor('black')
        figure.clear()
        axes = figure.add_subplot(1, 1, 1)
        figure.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
        self.on_forward(None)

        scheduler.plot(ax=axes)
        figure.canvas.draw()

        self.GetParent().Layout()
        self.Layout()
        

        

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

        info_text = wx.StaticText(self, label=pt.COMPLETION_PROGRESS % '|')
        f = info_text.GetFont()
        f.SetPointSize(10)
        f.SetFaceName('Courier 10 Pitch')
        info_text.SetFont(f)
        self.gauge = wx.Gauge(self, wx.ID_ANY, 100, 
                              size=(int(width*0.8),20), style=wx.GA_HORIZONTAL)
        self.close_button = wx.Button(self, wx.ID_CLOSE)
        self.close_button.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.close, self.close_button)

        # plot panel
        #graph_area = GraphArea(self)
        #graph_area.SetMinSize((550, 200))

        # details text.
        message_text = wx.TextCtrl(self, style=wx.TE_MULTILINE, 
                size=(int(width*0.8), int(height*0.6)))
        f = message_text.GetFont()
        f.SetPointSize(10)
        f.SetFaceName('Courier 10 Pitch')
        message_text.SetFont(f)
        message_text.SetBackgroundColour(wx.BLACK)
        message_text.SetForegroundColour(wx.WHITE)
        message_text.Enable(False)
        
        # layout
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        #sizer.Add(graph_area, proportion=1, flag=wx.EXPAND|wx.ALL, border=10)
        sizer.Add(info_text, proportion=0, 
                  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.gauge, proportion=0, 
                flag=wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|
                        wx.LEFT|wx.RIGHT, 
                border=8)
        sizer.Add(self.close_button, proportion=0, flag=wx.ALIGN_RIGHT|wx.ALL,
                border=8)
        sizer.Add(message_text, proportion=0, 
                  flag=wx.EXPAND|wx.ALL|wx.ALIGN_LEFT, border=10)

        self.SetSizerAndFit(sizer)

        self.message_text = message_text 
        self._num_tasks = 1
        self._num_tasks_competed = 0
        self._display_messages = []
        self._should_update = True
        #self.graph_area = graph_area
        self.info_text = info_text
        self._start_time = time.time()
        self._plugin_runtime = 0.0
        self._just_once = True
        self._step = 0
        self._last_len = -1

        self.Bind(wx.EVT_TIMER, self._update_processing)
        self.timer = wx.Timer(self)
        self.timer.Start(self.update_period)

    def _spin(self):
        spin_steps = ['/', '-', '\\', '|']
        self._step = (self._step + 1) % len(spin_steps)
        spinner = spin_steps[self._step]
        self.info_text.SetLabel(pt.COMPLETION_PROGRESS % str(spinner))

    def _update_processing(self, event):
        while True:
            try:
                new_message = self.message_queue.get_nowait()
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
                if statement == 'IMPOSSIBLE_TASK':
                    self._num_tasks_competed += 1
                    self._update_messages('Removed %s\n    Reason: task was impossible to complete.' % data)
                if statement == 'RUNNING_TASK':
                    self._update_messages('Started %s' % data)
                if statement == 'TASK_ERROR':
                    self._update_messages('ERROR on %s:\n\n %s' % 
                            (data['task'], wrap(data['traceback'], 80)))
                    self._num_tasks_competed = self._num_tasks
                    self.close_button.SetLabel('ABORT')
                    self.info_text.SetLabel('An ERROR occured in a plugin!')
                if statement == 'FINISHED_TASK':
                    self._num_tasks_competed += 1
                    self._update_messages(
                            'Finished %s\n    Runtime:%8.4f seconds' % 
                            (data['task'], data['runtime']))
                    self._plugin_runtime += data['runtime']
                #if statement == 'DISPLAY_GRAPH':
                    #scheduler = data
                    #self.graph_area.plot(scheduler)

                progress = int((self._num_tasks_competed/
                        float(self._num_tasks))*100.0)
                self.gauge.SetValue(progress)
            else:
                break

        progress = int((self._num_tasks_competed/
                float(self._num_tasks))*100.0)
        if progress >= 100:
            if self._just_once:
                self._just_once = False
                self.close_button.Enable()
                if 'ERROR' not in self.info_text.GetLabel():
                    self.info_text.SetLabel('Finished Processing')
                total_runtime = time.time()-self._start_time
                self._update_messages('Finished Processing:\n    Total Runtime = %f seconds (real time)\n    Time spent in plugins = %f seconds (cpu time, not real time)' % (total_runtime, self._plugin_runtime))
        else:
            self._spin()

        self._draw_messages()

    def _update_messages(self, message):
        now = datetime.now()
        display_message = '%02d:%02d:%02d - %s' % (now.hour, now.minute, 
                now.second, message)
        self._display_messages.append(display_message)

    def _draw_messages(self):
        if len(self._display_messages) != self._last_len:
            self._last_len = len(self._display_messages)
            self.message_text.SetValue(
                    '\n'.join(self._display_messages))
            self.message_text.ShowPosition(self.message_text.GetLastPosition())

    def close(self, event):
        event.Skip()
        pub.sendMessage('SET_RUN_BUTTONS_STATE', data=[True, True])
        self.Show(False)
        self.Destroy()




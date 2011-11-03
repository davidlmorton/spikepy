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
import weakref

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config
from spikepy.plotting.plot_panel import PlotPanel

class SpikepyPlotPanel(ScrolledPanel):
    def __init__(self, parent, session, name, toolbar_visible=False):
        ScrolledPanel.__init__(self, parent)
        
        self.session = session
        self.name = name

        pc = config['gui']['plotting']
        figsize = config.get_size('figure')
        
        self._plot_panel = PlotPanel(self, figsize=figsize,
                facecolor=pc['face_color'],
                edgecolor=pc['face_color'],
                toolbar_visible=toolbar_visible,
                dpi=pc['dpi'])

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(self._plot_panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.SetupScrolling(scrollToTop=False)

        # ---- Setup Subscriptions
        pub.subscribe(self._plot_result, topic='PLOT_RESULT')
        pub.subscribe(self._clear_results,  topic='CLEAR_RESULTS')
        
        self._title = None
        self._plotted_trial_id = None
        self._change_ids = {}

    def _should_replot(self, trial_id):
        if self._plotted_trial_id != trial_id:
            return True
        if self._change_ids != self._get_change_ids(trial_id):
            return True
        return False

    def _get_change_ids(self, trial_id):
        pass # to be defined in subclasses

    def clear_plot(self, key=None):
        self._plot_panel.clear()

    def _resize_canvas(self, num_rows):
        plot_panel = self._plot_panel
        fig_size = config.get_size('figure')
        fig_width = fig_size[0]
        fig_height = fig_size[1]*num_rows
        plot_panel.set_minsize(fig_width, fig_height)

    def _plot_result(self, message):
        wx.Yield()
        # performs per-stage & per-trial lazy replotting.
        trial_id, stage_name = message.data
        if self.name != stage_name:
            return

        self._replot(trial_id)
        self._plotted_trial_id = trial_id

    def _clear_results(self, message):
        wx.Yield()
        stage_name = message.data
        if self.name == stage_name:
            self._plot_panel.clear()
            self.draw_canvas()

    def draw_canvas(self):
        figure = self._plot_panel.figure
        figure.canvas.draw()
        self.SetupScrolling()
        self.Layout()

    def _replot(self, trial_id):
        # define in subclasses
        pass

    def get_trial(self, trial_id):
        return self.session.get_trial(trial_id)


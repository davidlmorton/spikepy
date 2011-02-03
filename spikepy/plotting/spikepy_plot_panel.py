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

from spikepy.plotting.multi_plot_panel import MultiPlotPanel
from spikepy.plotting import utils
from spikepy.common import program_text as pt
from spikepy.common.config_manager import config_manager as config

class SpikepyPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        pc = config['gui']['plotting']
        self._dpi       = pc['dpi']
        self._figsize   = (4.0, 6.0)
        self._facecolor = pc['face_color']
        self.name       = name
        MultiPlotPanel.__init__(self, parent, figsize=self._figsize,
                                              facecolor=self._facecolor,
                                              edgecolor=self._facecolor,
                                              dpi=self._dpi)

        # ---- Setup Subscriptions
        pub.subscribe(self._trial_added,    topic='TRIAL_ADDED')
        pub.subscribe(self._trial_altered,  topic='TRIAL_ALTERED')
        pub.subscribe(self._trial_renamed,  topic='TRIAL_RENAMED')
        pub.subscribe(self._display_result, topic='DISPLAY_RESULT')
        pub.subscribe(self._clear_results,  topic='CLEAR_RESULTS')
        
        self._trials = weakref.WeakValueDictionary()
        self._replot_panels = set()
        self._last_phase_completed = {}
        self._replot_count = {}
        self._phase_functions = [self._basic_setup, 
                                 self._pre_run, 
                                 self._post_run]
        self._title_objs = {}

    def _resize_canvas(self, num_rows, trial_id):
        plot_panel = self._plot_panels[trial_id]
        fig_size = config.get_size('figure')
        fig_width = fig_size[0]
        fig_height = fig_size[1]*num_rows
        plot_panel.set_minsize(fig_width, fig_height)
        self._trial_renamed(trial_id=trial_id)

    def _basic_setup(self, trial_id):
        pass # override in children

    def _pre_run(self, trial_id):
        pass # override in children

    def _post_run(self, trial_id):
        pass # override in children

    def _find_proper_phase(self, trial_id):
        trial = self._trials[trial_id]
        if self.name == 'summary':
            name = 'clustering'
        else:
            name = self.name

        if trial.has_run_stage(name):
            return 2
        elif trial.can_run_stage(name):
            return 1
        else:
            return 0

    def _display_result(self, message):
        wx.Yield()
        # performs per-stage & per-trial lazy replotting.
        trial_id, stage_name = message.data
        if self.name != stage_name:
            return

        if trial_id in self._replot_panels:
            self._replot(trial_id)
            self._replot_panels.remove(trial_id)

        pub.sendMessage('SHOW_PLOT', data=trial_id)

    def _clear_results(self, message):
        wx.Yield()
        stage_name = message.data
        if self.name == stage_name:
            for trial_id in self._trials.keys():
                self._plot_panels[trial_id].clear()
                self._last_phase_completed[trial_id] = 0
                self._replot_panels.add(trial_id)
                self.draw_canvas(trial_id)

    def _replot(self, trial_id):
        proper_phase = self._find_proper_phase(trial_id)
        lpc = self._last_phase_completed[trial_id]

        if proper_phase < lpc:
            lpc = 0

        for phase_function in self._phase_functions[lpc:proper_phase+1]:
            phase_function(trial_id)

        self._last_phase_completed[trial_id] = proper_phase

        self._replot_count[trial_id] += 1
        if self._replot_count[trial_id] > 4:
            # this will replot from scratch next time, freeing up memory.
            self._last_phase_completed[trial_id] = 0
            self._replot_count[trial_id] = 0
        self.draw_canvas(trial_id)

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        trial_id = trial.trial_id
        self._trials[trial_id] = trial

        self.add_plot(trial_id, figsize=self._figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        self._trial_renamed(trial_id=trial_id)
        self._last_phase_completed[trial_id] = 0
        self._replot_count[trial_id] = 0
        self._replot_panels.add(trial_id)

    def _trial_altered(self, message):
        trial_id, stage_name = message.data
        trial = self._trials[trial_id]
        if self.name == 'summary':
            this_name = 'clustering'
        else:
            this_name = self.name
        if (stage_name == this_name or
            stage_name in trial.get_prereq_stage_names(this_name)):
            self._replot_panels.add(trial_id)

    def _trial_renamed(self, message=None, trial_id=None):
        if trial_id is None:
            trial = message.data
            trial_id = trial.trial_id

        if trial_id in self._title_objs.keys():
            old_title_obj = self._title_objs[trial_id]
        else:
            old_title_obj = None

        new_name = pt.TRIAL_NAME+self._trials[trial_id].display_name
        canvas_size = self._plot_panels[trial_id].GetMinSize()
        figure = self._plot_panels[trial_id].figure
        new_title_obj = utils.set_title(figure=figure,
                                        old_text_obj=old_title_obj,
                                        canvas_size_in_pixels=canvas_size,
                                        new_name=new_name)
        self._title_objs[trial_id] = new_title_obj
        self.draw_canvas(trial_id)


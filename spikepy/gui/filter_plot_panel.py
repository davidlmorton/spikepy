import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from .multi_plot_panel import MultiPlotPanel
from .utils import adjust_axes_edges
from .look_and_feel_settings import lfs
from . import program_text as pt

class FilterPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR
        self.name       = name
        MultiPlotPanel.__init__(self, parent, figsize=self._figsize,
                                              facecolor=self._facecolor,
                                              edgecolor=self._facecolor,
                                              dpi=self._dpi)
        pub.subscribe(self._remove_trial,   topic="REMOVE_PLOT")
        pub.subscribe(self._trial_added,    topic='TRIAL_ADDED')
        pub.subscribe(self._trial_filtered, topic='TRIAL_FILTERED')
        pub.subscribe(self._trial_renamed,  topic='TRIAL_RENAMED')

        if name == 'detection_filter':
            self.line_color = lfs.PLOT_COLOR_2
            self.line_width = lfs.PLOT_LINEWIDTH_2
        if name == 'extraction_filter':
            self.line_color = lfs.PLOT_COLOR_3
            self.line_width = lfs.PLOT_LINEWIDTH_3

        self._trials = {}
        self._trace_axes = {}
        self._psd_axes = {}

    def _remove_trial(self, message=None):
        trial_id = message.data
        del self._trials[trial_id]
        if trial_id in self._trace_axes.keys():
            del self._trace_axes[trial_id]
        if trial_id in self._psd_axes.keys():
            del self._psd_axes[trial_id]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        trial_id = trial.trial_id
        self._trials[trial_id] = trial
        num_traces = len(trial.raw_traces)
        # make room for multiple traces and a psd plot.
        figsize = (self._figsize[0], self._figsize[1]*(num_traces+1))
        self.add_plot(trial_id, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)
        self._replot_panels.add(trial_id)

    def _trial_renamed(self, message=None):
        trial = message.data
        trial_id = trial.trial_id
        new_name = trial.display_name
        psd_axes = self._psd_axes[trial_id]
        psd_axes.set_title(pt.TRIAL_NAME+new_name)
        self.draw_canvas(trial_id)

    def _trial_filtered(self, message=None):
        trial, stage_name = message.data
        if stage_name != self.name:
            return
        trial_id = trial.trial_id
        if trial_id == self._currently_shown:
            self.plot(trial_id)
            if trial_id in self._replot_panels:
                self._replot_panels.remove(trial_id)
        else:
            self._replot_panels.add(trial_id)

    def plot(self, trial_id):
        trial = self._trials[trial_id]
        figure = self._plot_panels[trial_id].figure

        if trial_id not in self._trace_axes.keys():
            self._plot_raw_traces(trial, figure, trial_id)
        self._plot_filtered_traces(trial, figure, trial_id)

        self.draw_canvas(trial_id)

    def _plot_raw_traces(self, trial, figure, trial_id):
        traces = trial.raw_traces
        times  = trial.times

        for i, trace in enumerate(traces):
            if i==0:
                self._trace_axes[trial_id] = [
                        figure.add_subplot(len(traces)+1, 1, i+2)]
                top_axes = self._trace_axes[trial_id][0]
            else:
                self._trace_axes[trial_id].append(
                        figure.add_subplot(len(traces)+1, 
                                           1, i+2,
                                           sharex=top_axes,
                                           sharey=top_axes))
            axes = self._trace_axes[trial_id][-1]
            axes.plot(times, trace, color=lfs.PLOT_COLOR_1, 
                             linewidth=lfs.PLOT_LINEWIDTH_1, 
                             label=pt.RAW)
            axes.set_ylabel('%s #%d' % (pt.TRACE, (i+1)))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel(pt.PLOT_TIME)

        # lay out subplots
        canvas_size = self._plot_panels[trial_id].GetMinSize()
        lfs.default_adjust_subplots(figure, canvas_size)

        # --- add psd plot ---
        all_traces = numpy.hstack(traces)
        self._psd_axes[trial_id] = figure.add_subplot(
                len(self._trace_axes[trial_id])+1, 1, 1)
        psd_axes = self._psd_axes[trial_id]
        psd_axes.psd(all_traces, Fs=trial.sampling_freq, NFFT=2**11,
                                 label=pt.RAW,
                                 linewidth=lfs.PLOT_LINEWIDTH_1, 
                                 color=lfs.PLOT_COLOR_1)
        psd_axes.set_ylabel(pt.PSD_Y_AXIS_LABEL)
        name = trial.display_name
        psd_axes.set_title(pt.TRIAL_NAME+name)

        bottom = lfs.AXES_BOTTOM
        adjust_axes_edges(psd_axes, canvas_size_in_pixels=canvas_size, 
                                    bottom=bottom)

    def _plot_filtered_traces(self, trial, figure, trial_id):
        stage_data = getattr(trial, self.name)
        if stage_data.results is not None:
            traces = stage_data.results
        else:
            return # this trial has never been filtered.
        times = trial.times

        for trace, axes in zip(traces, self._trace_axes[trial_id]):
            axes.set_autoscale_on(False)
            lines = axes.get_lines()
            if len(lines) == 2:
                filtered_line = lines[1]
                filtered_line.set_ydata(trace)
            else:
                axes.plot(times, trace, color=self.line_color, 
                                 linewidth=self.line_width, 
                                 label=pt.FILTERED_TRACE_GRAPH_LABEL)

        all_traces = numpy.hstack(traces)
        axes = self._psd_axes[trial_id]
        lines = axes.get_lines()
        if len(lines) == 2:
            del(axes.lines[1])
        axes.psd(all_traces, Fs=trial.sampling_freq, NFFT=2**11, 
                                   label=pt.FILTERED_TRACE_GRAPH_LABEL, 
                                   linewidth=self.line_width, 
                                   color=self.line_color)
        axes.set_ylabel(pt.PSD_Y_AXIS_LABEL)
        axes.legend(loc='lower right')



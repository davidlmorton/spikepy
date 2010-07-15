import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
from scipy import signal as scisig

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel
from .utils import rgb_to_matplotlib_color
from .look_and_feel_settings import lfs
from .program_text import (TRACE_TEXT, SAMPLE_NUMBER_TEXT, 
                           TIME_AXIS_TEXT, SPIKE_RATE_AXIS_TEXT, 
                           DETECTION_TRACE_GRAPH_LABEL_TEXT, 
                           SPIKES_GRAPH_LABEL_TEXT)

class ExtractionPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR
        self.name       = name
        MultiPlotPanel.__init__(self, parent, figsize=self._figsize,
                                              facecolor=self._facecolor,
                                              edgecolor=self._facecolor,
                                              dpi=self._dpi)
        pub.subscribe(self._remove_trial,  topic="REMOVE_PLOT")
        pub.subscribe(self._trial_added,   topic='TRIAL_ADDED')
        pub.subscribe(self._trial_altered, topic='TRIAL_DETECTIONED')
        pub.subscribe(self._trial_altered, topic="TRIAL_DETECTION_FILTERED")

        self._trials     = {}
        self._trace_axes = {}
        self._spike_axes = {}

    def _remove_trial(self, message=None):
        full_path = message.data
        del self._trials[full_path]
        del self._trace_axes[full_path]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        fullpath = trial.fullpath
        self._trials[fullpath] = trial
        num_traces = len(trial.traces['raw'])
        # make room for multiple traces and a spike-rate plot.
        figsize = (self._figsize[0], self._figsize[1]*(num_traces+1))
        self.add_plot(fullpath, figsize=figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)

    def _trial_altered(self, message=None):
        trial = message.data
        fullpath = trial.fullpath
        if fullpath == self._currently_shown:
            self.plot(fullpath)
            if fullpath in self._replot_panels:
                self._replot_panels.remove(fullpath)
        else:
            self._replot_panels.add(fullpath)

    def plot(self, fullpath):
        trial = self._trials[fullpath]
        figure = self._plot_panels[fullpath].figure
        
        if (fullpath not in self._trace_axes.keys() and
                'extraction' in trial.traces.keys()):
            self._create_axes(trial, figure, fullpath)
        self._plot_filtered_traces(trial, figure, fullpath)
        self._plot_spikes(trial, figure, fullpath)

        old_shown_state = self._plot_panels[fullpath].IsShown()
        self._plot_panels[fullpath].Show(False)
        figure.canvas.draw()
        self._plot_panels[fullpath].Show(old_shown_state)
        self.SetupScrolling()
        self.Layout()

    def _create_axes(self, trial, figure, fullpath):
        traces = trial.traces['extraction']
        for i, trace in enumerate(traces):
            if i==0:
                self._trace_axes[fullpath] = [
                        figure.add_subplot(len(traces)+1, 1, i+2)]
                top_axes = self._trace_axes[fullpath][0]
            else:
                self._trace_axes[fullpath].append(
                        figure.add_subplot(len(traces)+1, 
                                           1, i+2,
                                           sharex=top_axes,
                                           sharey=top_axes))
            axes = self._trace_axes[fullpath][-1]
            axes.set_ylabel('%s #%d' % (TRACE_TEXT, (i+1)))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel(SAMPLE_NUMBER_TEXT)
        # bottom is in percent, how big is text there in percent?
        factor = len(traces)+1
        original_bottom = 0.2
        figure.subplots_adjust(hspace=0.025, left=0.10, right=0.95, 
                               bottom=original_bottom/factor+0.01)

        # --- add axis for spike plot ---
        self._spike_axes[fullpath] = figure.add_subplot(
                len(self._trace_axes[fullpath])+1, 1, 1)
        spike_axes = self._spike_axes[fullpath]
        spike_axes.set_xlabel(TIME_AXIS_TEXT)
        spike_axes.set_ylabel(SPIKE_RATE_AXIS_TEXT)
        # move raster plot's bottom edge up a bit
        box = spike_axes.get_position()
        box.p0 = (box.p0[0], box.p0[1]+0.065)
        box.p1 = (box.p1[0], 0.99)
        spike_axes.set_position(box)
        

    def _plot_filtered_traces(self, trial, figure, fullpath):
        if "extraction" in trial.traces.keys():
            traces = trial.traces['extraction']
        else:
            return
        for trace, axes in zip(traces, self._trace_axes[fullpath]):
            while axes.lines:
                del(axes.lines[0])     
            axes.plot(trace, color=lfs.PLOT_COLOR_2, 
                             linewidth=lfs.PLOT_LINEWIDTH_2, 
                             label=DETECTION_TRACE_GRAPH_LABEL_TEXT)

    def _plot_spikes(self, trial, figure, fullpath):
        if len(trial.spikes):
            spikes = trial.spikes
        else:
            while self._spike_axes[fullpath].lines:
                del(self._spike_axes[fullpath].lines[0])
            return # this trial has never been spike detected.

        for spike_list, axes in zip(spikes, self._trace_axes[fullpath]):
            axes.set_autoscale_on(False)
            lines = axes.get_lines()
            # check if raster is already plotted
            if len(lines) == 2:
                del(axes.lines[1])
            
            raster_height_factor = 2.0
            raster_pos = lfs.SPIKE_RASTER_ON_TRACES_POSITION
            if raster_pos == 'top':    spike_y = max(axes.get_ylim())
            if raster_pos == 'botom':  spike_y = min(axes.get_ylim())
            if raster_pos == 'center': 
                spike_y = 0.0
                raster_height_factor = 1.0
            spike_ys = [spike_y for spike_index in spike_list]
            axes.plot(spike_list, spike_ys, color=lfs.SPIKE_RASTER_COLOR, 
                                 linewidth=0, 
                                 marker='|',
                                 markersize=lfs.SPIKE_RASTER_HEIGHT*
                                            raster_height_factor,
                                 label=SPIKES_GRAPH_LABEL_TEXT)

        # --- plot spike rate ---
        width = 50.0
        required_proportion = 0.75
        accepted_spike_list = get_accepted_spike_list(trial.spikes, 
                                                      trial.sampling_freq, 
                                                      width,
                                                      required_proportion)
        spike_rate = get_spike_rate(accepted_spike_list, width, 
                                    trial.sampling_freq, 
                                    len(trial.traces['extraction'][0]))
        spike_axes = self._spike_axes[fullpath]

        # remove old lines if present.
        while spike_axes.lines:
            del spike_axes.lines[0]
            
        spike_axes.plot(spike_rate, color=lfs.PLOT_COLOR_2, 
                                    linewidth=lfs.PLOT_LINEWIDTH_2)

        raster_height_factor = 2.0
        raster_pos = lfs.SPIKE_RASTER_ON_RATE_POSITION
        if raster_pos == 'top':    spike_y = max(spike_axes.get_ylim())
        if raster_pos == 'botom':  spike_y = min(spike_axes.get_ylim())
        if raster_pos == 'center': 
            spike_y = 0.0
            raster_height_factor = 1.0
            
        spike_ys = [spike_y for spike_index in accepted_spike_list]
        spike_axes.plot(accepted_spike_list, spike_ys, 
                                color=lfs.SPIKE_RASTER_COLOR,
                                linewidth=0.0,
                                marker='|',
                                markersize=lfs.SPIKE_RASTER_HEIGHT*
                                            raster_height_factor)


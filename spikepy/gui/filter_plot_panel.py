import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class FilterPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self.figsize   = (2.5, 1.0)
        self.facecolor = 'white'
        self.dpi       = 50.0
        self.name      = name
        MultiPlotPanel.__init__(self, parent, figsize=self.figsize,
                                              facecolor=self.facecolor,
                                              dpi=self.dpi)
        pub.subscribe(self._trial_added, topic='TRIAL_ADDED')
        pub.subscribe(self._trial_filtered, 
                      topic='TRIAL_%s_FILTERED' % name.upper())
        pub.subscribe(self._show_psd, topic='SHOW_PSD')

        self._psd_shown = True
        self._trials = {}
        self._trace_axes = {}
        self._psd_axes = {}

    def _show_psd(self, message=None):
        name = message.data
        if name == self.name:
            self._psd_shown = True
            trial = self._trials.values()
            for trial in trials:
                self._trial_added(trial=trial)

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        fullpath = trial.fullpath
        self._trials[fullpath] = trial
        traces = trial.traces['raw']

        if self._psd_shown: psd = 1
        else: psd = 0
        figsize = (self.figsize[0], self.figsize[1]*len(traces)+psd)
        self.add_plot(PlotPanel(self, figsize=figsize,
                                      facecolor=self.facecolor,
                                      dpi=self.dpi), fullpath)

        figure = self._plot_panels[fullpath].figure

        for i, trace in enumerate(traces):
            if i==0:
                self._trace_axes[fullpath] = [
                        figure.add_subplot(len(traces)+psd, 1, i+1+psd)]
                top_axes = self._trace_axes[fullpath][0]
            else:
                self._trace_axes[fullpath].append(
                        figure.add_subplot(len(traces)+psd, 
                                           1, i+1+psd,
                                           sharex=top_axes,
                                           sharey=top_axes))
            axes = self._trace_axes[fullpath][-1]
            axes.plot(trace, color='black', linewidth=1.3, label='Raw')
            axes.set_ylabel('Trace #%d' % (i+1))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel('Sample Number')
        figure.subplots_adjust(hspace=0.02)

        #add psd plot
        if self._psd_shown:
            # concat all traces
            traces = numpy.hstack(traces)
            self._psd_axes[fullpath] = figure.add_subplot(
                    len(self._trace_axes[fullpath])+psd, 1, 1)
            psd_axes = self._psd_axes[fullpath]
            psd_axes.psd(traces, Fs=trial.sampling_freq, label='Raw',
                               linewidth=2.0, color='black')
            # move psd plot's bottom edge up a bit
            box = psd_axes.get_position()
            box.p0 = (box.p0[0], box.p0[1]+0.05)
            psd_axes.set_position(box)

        if self.name.lower() in trial.traces.keys():
            self._trial_filtered(trial=trial)
            
    def _trial_filtered(self, message=None, trial=None):
        if message is not None:
            trial = message.data
        fullpath = trial.fullpath
        traces = trial.traces[self.name.lower()]
        figure = self._plot_panels[fullpath].figure
        for trace, axes in zip(traces, self._trace_axes[fullpath]):
            axes.set_autoscale_on(False)
            lines = axes.get_lines()
            if len(lines) == 2:
                filtered_line = lines[1]
                filtered_line.set_ydata(trace)
            else:
                axes.plot(trace, color='blue', linewidth=1.0, label='Filtered')

        #add psd plot
        if self._psd_shown:
            # concat all traces
            traces = numpy.hstack(traces)
            axes = self._psd_axes[fullpath]
            lines = axes.get_lines()
            if len(lines) == 2:
                del(axes.lines[1])
            axes.psd(traces, Fs=trial.sampling_freq, 
                                       label='Filtered', 
                                       linewidth=1.5, color='blue')
            axes.legend()
        else:
            self._trace_axes[fullpath][0].legend()

        figure.canvas.draw()

import os

from wx.lib.pubsub import Publisher as pub
from matplotlib.pyplot import psd
import numpy

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class FilterPSDPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self.figsize   = (6, 4.3)
        self.facecolor = 'white'
        self.dpi       = 72.0
        self.name      = name
        MultiPlotPanel.__init__(self, parent, figsize=self.figsize,
                                              facecolor=self.facecolor,
                                              dpi=self.dpi)
        pub.subscribe(self._trial_added, topic='TRIAL ADDED')
        pub.subscribe(self._trial_filtered, 
                      topic='TRIAL %s FILTERED' % name.upper())

    def _trial_added(self, message):
        trial = message.data
        fullpath = trial.filename
        filename = os.path.split(fullpath)[1]
        self._plot_panels[fullpath] = PlotPanel(self, figsize=self.figsize,
                                                      facecolor=self.facecolor,
                                                      dpi=self.dpi)

        figure = self._plot_panels[fullpath].figure

        traces = numpy.hstack(trial.traces) #all traces together
        axes = figure.add_subplot(1,1,1)
        axes.psd(traces, Fs=trial.sampling_freq, label='Raw', 
                             linewidth=2.0, color='black')

        if hasattr(trial, '%s_traces' % self.name.lower()):
            self._trial_filtered(trial=trial)
            
    def _trial_filtered(self, message=None, trial=None):
        if message is not None:
            trial = message.data
        fullpath = trial.filename
        traces = numpy.hstack(getattr(trial, '%s_traces' % self.name.lower()))

        figure = self._plot_panels[fullpath].figure
        for trace, axes in zip(traces, figure.get_axes()):
            lines = axes.get_lines()
            if len(lines) == 2:
                del(axes.lines[1])
            axes.psd(traces, Fs=trial.sampling_freq, label='Filtered', 
                             linewidth=1.5, color='blue')
        axes.legend()
        figure.canvas.draw()

import os

from wx.lib.pubsub import Publisher as pub
from matplotlib.pyplot import psd
import numpy

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class FilterPSDPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self.figsize   = (5, 2)
        self.facecolor = 'white'
        self.dpi       = 60.0
        self.name      = name
        MultiPlotPanel.__init__(self, parent, figsize=self.figsize,
                                              facecolor=self.facecolor,
                                              dpi=self.dpi)
        pub.subscribe(self._trial_added, topic='TRIAL_ADDED')
        pub.subscribe(self._trial_filtered, 
                      topic='TRIAL_%s_FILTERED' % name.upper())

    def _trial_added(self, message):
        trial = message.data
        fullpath = trial.fullpath
        filename = os.path.split(fullpath)[1]
        self.add_plot(PlotPanel(self, figsize=self.figsize,
                                      facecolor=self.facecolor,
                                      dpi=self.dpi), fullpath)

        figure = self._plot_panels[fullpath].figure

        traces = numpy.hstack(trial.traces['raw']) #all traces together
        axes = figure.add_subplot(1,1,1)
        axes.psd(traces, Fs=trial.sampling_freq, label='Raw', 
                             linewidth=2.0, color='black')

        if self.name.lower() in trial.traces.keys():
            self._trial_filtered(trial=trial)
            
    def _trial_filtered(self, message=None, trial=None):
        if message is not None:
            trial = message.data
        fullpath = trial.fullpath
        traces = numpy.hstack(trial.traces[self.name.lower()]) #all traces together

        figure = self._plot_panels[fullpath].figure
        for trace, axes in zip(traces, figure.get_axes()):
            axes.set_autoscale_on(False)
            lines = axes.get_lines()
            if len(lines) == 2:
                del(axes.lines[1])
            axes.psd(traces, Fs=trial.sampling_freq, label='Filtered', 
                             linewidth=1.5, color='blue')
        axes.legend()
        figure.canvas.draw()

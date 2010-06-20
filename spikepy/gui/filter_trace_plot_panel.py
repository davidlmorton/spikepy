import os

from wx.lib.pubsub import Publisher as pub

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class FilterTracePlotPanel(MultiPlotPanel):
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

        traces = trial.traces
        for i, trace in enumerate(traces):
            axes = figure.add_subplot(len(traces), 1, i+1)
            axes.plot(trace, color='black', linewidth=2.0, label='Raw')
            if i==0:
                axes.set_title('Trace: %s' % str(filename))
            if i+1 < len(traces):
                axes.set_xticks([])
                axes.set_yticks([])

        axes.set_xlabel('Sample Number')

        if hasattr(trial, '%s_traces' % self.name.lower()):
            self._trial_filtered(trial=trial)
            
    def _trial_filtered(self, message=None, trial=None):
        if message is not None:
            trial = message.data
        fullpath = trial.filename
        traces = getattr(trial, '%s_traces' % self.name.lower())
        figure = self._plot_panels[fullpath].figure
        for trace, axes in zip(traces, figure.get_axes()):
            lines = axes.get_lines()
            if len(lines) == 2:
                filtered_line = lines[1]
                filtered_line.set_ydata(trace)
            else:
                axes.plot(trace, color='blue', linewidth=1.5, label='Filtered')
        axes.legend()
        figure.canvas.draw()

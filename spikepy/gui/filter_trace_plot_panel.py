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
        fullpath = trial.fullpath
        self._plot_panels[fullpath] = PlotPanel(self, figsize=self.figsize,
                                                      facecolor=self.facecolor,
                                                      dpi=self.dpi)

        figure = self._plot_panels[fullpath].figure

        filename = os.path.split(fullpath)[1]
        traces = trial.traces['raw']
        for i, trace in enumerate(traces):
            if i==0:
                axes = first_axes = figure.add_subplot(len(traces), 1, i+1)
                axes.set_title('Trial:  %s' % str(filename))
            else:
                axes = figure.add_subplot(len(traces), 1, i+1,
                                          sharex=first_axes,
                                          sharey=first_axes)
            axes.plot(trace, color='black', linewidth=2.0, label='Raw')
            axes.set_ylabel('Trace #%d' % (i+1))
            if i+1 < len(traces): #all but the last trace
                # make the x/yticklabels dissapear
                axes.set_xticklabels([''],visible=False)
                axes.set_yticklabels([''],visible=False)

        axes.set_xlabel('Sample Number')
        figure.subplots_adjust(hspace=0.02)

        if self.name.lower() in trial.traces.keys():
            self._trial_filtered(trial=trial)
            
    def _trial_filtered(self, message=None, trial=None):
        if message is not None:
            trial = message.data
        fullpath = trial.fullpath
        traces = trial.traces[self.name.lower()]
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

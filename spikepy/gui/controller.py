import os 

import wx
from wx.lib.pubsub import Publisher as pub

from ..common.model import Model
from .view import View
from .utils import named_color

class Controller(object):
    def __init__(self):
        self.model = Model()
        self.model.setup_subscriptions()
        self.view = View()

    def setup_subscriptions(self):
        pub.subscribe(self._open_file, topic="OPEN FILE")
        pub.subscribe(self._file_selection_changed, 
                      topic='FILE SELECTION CHANGED')
        pub.subscribe(self._setup_new_trace_plot, 
                      topic='SETUP NEW TRACE PLOT')

    def _setup_new_trace_plot(self, message):
        fullpath, plot_panel, trace_plot_panel = message.data
        trial = self.model.trials[fullpath]
        traces = trial.traces
        colors = [named_color('blue'), 
                  named_color('red'), 
                  named_color('black')]
        while len(traces) > len(colors):
            colors.extend(colors)
        canvas = plot_panel.canvas
        figure = plot_panel.figure
        axes = figure.add_subplot(111)
        for trace, color in zip(traces,colors):
            axes.plot(trace, color=color, linewidth=1.5)
        trace_plot_panel.add_plot_panel(plot_panel, fullpath)
        sampling_freq = trial.sampling_freq
        trace_plot_panel.setup_dressings(axes, sampling_freq)

    def _file_selection_changed(self, message):
        fullpath = message.data
        pub.sendMessage(topic='SHOW TRACE PLOT', data=fullpath)
        """
        """

    def _open_file(self, message):
        frame = message.data

        paths = []
        dlg = wx.FileDialog(frame, message="Choose file(s) to open.",
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()
        for path in paths:
            pub.sendMessage(topic='OPENING DATA FILE', data=path)
            pub.sendMessage(topic='OPEN DATA FILE', data=path)




import matplotlib
import wx
from .wxPlotPanel import PlotPanel
from wx.lib.pubsub import Publisher as pub

class TracePlotPanel(PlotPanel):
    def __init__(self, parent, **kwargs):
        # initiate plotter
        PlotPanel.__init__(self, parent, **kwargs)
        pub.subscribe(self._update_trace_plot, topic="UPDATE TRACE PLOT")

    def _update_trace_plot(self, message):
        sampling_rate, traces, colors = message.data
        self.set_data(sampling_rate, traces, colors)

    def set_data(self, sampling_rate, traces, colors):
        self.traces = traces
        while len(colors) < len(traces):
            colors.append(colors[-1])
        self.colors = colors
        self.sampling_rate = sampling_rate
        self.draw()

    def draw(self):
        """Draw data."""
        if not hasattr(self, 'colors'):
            return

        if hasattr(self, 'subplot'):
            self.figure.clear()
        self.subplot = self.figure.add_subplot(111)

        for color, trace in zip(self.colors, self.traces):
            color = [float(channel)/255. for channel in color]
            self.subplot.plot(trace, color=color)
        current_axes = self.figure.gca()
        current_axes.set_xlabel("Sample Number (sample rate = %d Hz)" %
                                 self.sampling_rate)
        current_axes.set_ylabel("Y (data collection units, mV?)")
        current_axes.set_title("Voltage Trace")
        self.canvas.draw()

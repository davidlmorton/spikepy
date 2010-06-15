import matplotlib
import wx
from .wxPlotPanel import PlotPanel

matplotlib.interactive(True)
matplotlib.use('WXAgg')

class TracePlotPanel(PlotPanel):
    def __init__(self, parent, sampling_rate, traces, colors, **kwargs):
        self.parent = parent
        self.traces = traces
        self.colors = colors
        self.sampling_rate = sampling rate
        
        # initiate plotter
        PlotPanel.__init__(self, parent, **kwargs)
        self.SetColor((255,255,255))

    def draw(self):
        """Draw data."""
        if not hasattr(self, 'subplot'):
            self.subplot = self.figure.add_subplot(111)

        for color, trace in zip(self.colors, self.traces):
            color = [float(c)/255. for c in self.color_list[i]]
            self.subplot.plot(trace, color=color)
        self.subplot.xlabel("Sample Number (sample rate = %d Hz)" % 
                                                       self.sampling_rate)
        self.subplot.ylabel("Y (data collection units, mV?)")
        self.subplot.title("Voltage Trace")

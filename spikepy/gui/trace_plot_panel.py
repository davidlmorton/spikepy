from wx.lib.pubsub import Publisher as pub

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class TracePlotPanel(MultiPlotPanel):
    def __init__(self, parent):
        MultiPlotPanel.__init__(self, parent, figsize=(6,4.3),
                                              facecolor='white',
                                              dpi=72)
        self._new_plot_message = 'SETUP NEW TRACE PLOT'
        
    def setup_dressings(self, axes, sampling_freq):
        '''Sets up the xlabel/ylabel/title of this axis'''
        axes.set_xlabel("Sample Number (sample rate = %d Hz)" %
                        sampling_freq)
        axes.set_ylabel("(data collection units, mV?)")
        axes.set_title("Voltage Trace")

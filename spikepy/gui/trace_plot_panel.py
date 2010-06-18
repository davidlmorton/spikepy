from wx.lib.pubsub import Publisher as pub

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel

class TracePlotPanel(MultiPlotPanel):
    kwargs = {}
    kwargs['figsize']   = (7, 4.3)
    kwargs['facecolor'] = 'white'
    kwargs['dpi']       = 64
    def __init__(self, parent):
        MultiPlotPanel.__init__(self, parent, **TracePlotPanel.kwargs)

    def _setup_new_plot(self, new_panel_key): 
        # needs to be defined for MultiPlotPanel
        pub.sendMessage(topic='SETUP NEW TRACE PLOT', 
                        data=(new_panel_key, 
                              PlotPanel(self, **TracePlotPanel.kwargs), 
                              self))
        
    def setup_dressings(self, axes, sampling_freq):
        '''Sets up the xlabel/ylabel/title of this axis'''
        axes.set_xlabel("Sample Number (sample rate = %d Hz)" %
                        sampling_freq)
        axes.set_ylabel("(data collection units, mV?)")
        axes.set_title("Voltage Trace")

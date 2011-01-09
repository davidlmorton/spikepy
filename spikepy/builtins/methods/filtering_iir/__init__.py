from spikepy.developer_tools.filtering_method import FilteringMethod
from .control_panel import ControlPanel
from .run import run as runner

class FilteringIIR(FilteringMethod):
    '''
    This class implements an infinte impulse response filtering method.
    '''
    def __init__(self):
        self.name = 'Infinite Impulse Response'
        self.description = 'Butterworth and bessel filters.  Can be high/low/band pass types.'

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, signal_list, sampling_freq, **kwargs):
        return runner(signal_list, sampling_freq, **kwargs)
    

from spikepy.developer_tools.filtering_method import FilteringMethod
from .control_panel import ControlPanel
from .run import run as runner

class FilteringFIR(FilteringMethod):
    '''
    This class implements a finite impulse response filtering method.
    '''
    def __init__(self):
        self.name = 'Finite Impulse Response'
        self.description = 'Sinc type filters with a windowing function.'

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, signal_list, sampling_freq, **kwargs):
        return runner(signal_list, sampling_freq, **kwargs)

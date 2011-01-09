from spikepy.developer_tools.filtering_method import FilteringMethod
from .control_panel import ControlPanel
from .run import run as runner

class FilteringNone(FilteringMethod):
    '''
    This class implements a NULL filtering method.
    '''
    def __init__(self):
        self.name = 'None'
        self.description = 'No Filtering, will simply use the raw trace.'

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent **kwargs)

    def run(self, signal_list, sampling_freq, **kwargs):
        return runner(signal_list, sampling_freq, **kwargs)

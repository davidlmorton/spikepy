from spikepy.developer_tools.extraction_method import ExtractionMethod
from .control_panel import ControlPanel
from .run import run as runner

class ExtractionSpikeWindow(ExtractionMethod):
    '''
    This class implements a spike-window feature-extraction method.
    '''
    def __init__(self):
        self.name = "Spike Window"
        self.description = "Extract the waveform of spikes in a temporal window around the spike event."

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, signal_list, sampling_freq, spike_list, **kwargs):
        return runner(signal_list, sampling_freq, spike_list, **kwargs)

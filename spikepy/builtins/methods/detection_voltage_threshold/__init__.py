from spikepy.developer_tools.detection_method import DetectionMethod
from .control_panel import ControlPanel
from .run import run as runner

class VoltageThreshold(DetectionMethod):
    '''
    This class implements a voltage threshold spike detection method.
    '''
    def __init__(self):
        self.name = "Voltage Threshold"
        self.description = "Spike detection using voltage threshold(s)"

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, signal_list, sampling_freq, **kwargs):
        return runner(signal_list, sampling_freq, **kwargs)




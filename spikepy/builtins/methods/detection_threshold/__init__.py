

from spikepy.developer.methods import DetectionMethod
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption
from .threshold_detection import threshold_detection

class VoltageThreshold(DetectionMethod):
    '''
    This class implements a voltage threshold spike detection method.
    '''
    name = "Threshold"
    description = "Spike detection using one or two thresholds."

    requires = ['df_traces', 'df_sampling_freq']
    provides = ['event_times']

    # method settings (become kwargs for run)
    threshold_1 = ValidFloat(default=-6.0)
    threshold_2 = ValidFloat(default=-6.0)
    threshold_units = ValidOption('Standard Deviation', 'Median', 'Signal', 
            default='Standard Deviation')
    refractory_time = ValidFloat(min=0.0, default=0.50,
            description='Refractory time in ms.')
    max_spike_duration = ValidFloat(min=0.0, default=4.0,
            description='Spikes wider than this at threshold (in ms) are ignored.')

    def run(self, signal, sampling_freq, **kwargs):
        event_times = threshold_detection(signal, sampling_freq, **kwargs)
        return event_times







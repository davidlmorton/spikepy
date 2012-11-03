

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidInteger
from spikepy.utils.generate_spike_windows import generate_spike_windows

class DetectionSpikeWindow(AuxiliaryMethod):
    '''
    This class implements a spike-window method.
    '''
    group = 'Spike Window'
    name = "Detection Spike Window"
    description = "Extract the waveform of spikes in a temporal window around the spike event."
    runs_with_stage = 'detection'
    is_stochastic = False
    pooling = False
    requires = ['df_traces', 'df_sampling_freq', 'event_times']
    provides = ['df_spike_windows', 'df_spike_window_times']

    pre_padding = ValidFloat(min=0.0, default=2.0)
    post_padding = ValidFloat(min=0.0, default=4.0)
    exclude_overlappers = ValidBoolean(default=False)
    min_num_channels = ValidInteger(min=1, default=3)
    peak_drift = ValidFloat(min=0.01, default=0.3) # ms

    def run(self, signal, sampling_freq, event_times, **kwargs):
        return generate_spike_windows(signal, sampling_freq, event_times, 
                **kwargs)[:2]

class ExtractionSpikeWindow(DetectionSpikeWindow):
    group = 'Spike Window'
    name = 'Extraction Spike Window'
    runs_with_stage = 'extraction_filter'
    requires = ['ef_traces', 'ef_sampling_freq', 'event_times']
    provides = ['ef_spike_windows', 'ef_spike_window_times']



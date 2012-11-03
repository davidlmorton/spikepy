

from spikepy.developer.methods import ExtractionMethod
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidInteger
from spikepy.utils.generate_spike_windows import generate_spike_windows

class ExtractionSpikeWindow(ExtractionMethod):
    '''
    This class implements a spike-window feature-extraction method.
    '''
    name = "Spike Window"
    description = "Extract the waveform of spikes in a temporal window around the spike event."
    is_stochastic = False
    provides = ['features', 'feature_times', 'excluded_features', 
            'excluded_feature_times']

    pre_padding = ValidFloat(min=0.0, default=2.0,
            description='Determines the amount of time before the spike (in ms) to include in the windowed spike.')
    post_padding = ValidFloat(min=0.0, default=4.0,
            description='The amount of time after the spike (in ms) to include in the windowed spike.')
    exclude_overlappers = ValidBoolean(default=False,
            description="Throw out all spikes who's windows would overlap with another spike (both overlappers are thrown out.)")
    min_num_channels = ValidInteger(min=1, default=3,
            description="The lowest number of channels on which a spike must have been identified within 'peak drift' milliseconds.")
    peak_drift = ValidFloat(min=0.01, default=0.3,
            description='The greatest amount of time (in ms) between spikes on different channels while they still are considered part of a single spike event.') # ms

    def run(self, signal, sampling_freq, event_times, **kwargs):
        return generate_spike_windows(signal, sampling_freq, event_times, 
                **kwargs)


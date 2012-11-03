

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidInteger
from spikepy.utils.resample import resample

class ResampleAEF(AuxiliaryMethod):
    name = 'Resample after Extraction Filter'
    description = 'Resample the signal after running the Extraction Filter stage.'
    runs_with_stage = 'extraction_filter'
    requires = ['ef_traces', 'ef_sampling_freq']
    provides = ['ef_traces', 'ef_sampling_freq']
    is_stochastic = False

    new_sampling_frequency = ValidInteger(10, 100000, default=30000)

    def run(self, signal, sampling_freq, **kwargs):
        return [resample(signal, sampling_freq, 
                kwargs['new_sampling_frequency']), 
                kwargs['new_sampling_frequency']]

class ResampleADF(ResampleAEF):
    name = 'Resample after Detection Filter'
    description = 'Resample the signal after running the Detection Filter stage.'
    runs_with_stage = 'detection_filter'
    requires = ['df_traces', 'df_sampling_freq']
    provides = ['df_traces', 'df_sampling_freq']
    

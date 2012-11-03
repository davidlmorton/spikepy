
import numpy

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidFloat
from spikepy.utils.frequency_analysis import psd

class PSDPF(AuxiliaryMethod):
    group = 'PSD'
    name = 'Power Spectral Density (Pre-Filtering)'
    description = 'Spectral Density of the pre-filtered signal.'
    runs_with_stage = 'detection_filter'
    requires = ['pf_traces', 'pf_sampling_freq']
    provides = ['pf_psd', 'pf_freqs']
    is_stochastic = False

    frequency_resolution = ValidFloat(min=0.1, default=10,
            description="The minimal acceptable frequency resolution.  The actual frequency resolution may be better than this (but won't be worse).")

    def run(self, signal, sampling_freq, **kwargs):
        return psd(signal.flatten(), sampling_freq, 
                kwargs['frequency_resolution'])

class PSDDF(PSDPF):
    group = 'PSD'
    name = 'Power Spectral Density (Post-Detection-Filtering)'
    description = 'Spectral Density of the detection-filtered signal.'
    runs_with_stage = 'detection_filter'
    requires = ['df_traces', 'df_sampling_freq']
    provides = ['df_psd', 'df_freqs']

class PSDEF(PSDPF):
    group = 'PSD'
    name = 'Power Spectral Density (Post-Extraction-Filtering)'
    description = 'Spectral Density of the extraction-filtered signal.'
    runs_with_stage = 'extraction_filter'
    requires = ['ef_traces', 'ef_sampling_freq']
    provides = ['ef_psd', 'ef_freqs']
    


import pywt

from spikepy.developer.methods import FilteringMethod
from spikepy.common.valid_types import ValidOption, ValidInteger
from .wavelet import filt

class FilteringWavelets(FilteringMethod):
    '''
    This class implements a wavelet filtering method.
    '''
    name = 'Wavelets Filter'
    description = 'Filter based on wavelet decomposition.'
    is_stochastic = False

    # method parameters
    wavelet = ValidOption(*pywt.wavelist(), default='db20')
    min_level = ValidInteger(min=1, default=1, 
            description="Effectively sets the low-pass cutoff frequency (sampling_freq/2**<Min Level>)")
    max_level = ValidInteger(min=1, default=6, 
            description="Effectively sets the high-pass cutoff frequency (sampling_freq/2**(<Max Level>+1))")

    def run(self, signal, sampling_freq, wavelet='db20', 
            min_level=1, max_level=6):
        filtered_signal = filt(signal,
                wavelet=wavelet,
                minlevel=min_level, 
                maxlevel=max_level)
        return [filtered_signal, sampling_freq]

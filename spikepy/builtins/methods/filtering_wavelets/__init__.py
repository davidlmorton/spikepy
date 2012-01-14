"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import pywt
import numpy

from spikepy.developer_tools.methods import FilteringMethod
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
    min_level = ValidInteger(min=1, default=1, description="Effectively sets the low-pass cutoff frequency (sampling_freq/2**<Min Level>)")
    max_level = ValidInteger(min=1, default=6, description="Effectively sets the high-pass cutoff frequency (sampling_freq/2**(<Max Level>+1))")

    def run(self, signal, sampling_freq, wavelet='db20', 
            min_level=1, max_level=6):
        filtered_signal = numpy.empty(signal.shape, signal.dtype)
        for i in range(len(signal)):
            filtered_signal[i] = filt(signal[i],
                    wavelet=wavelet,
                    minlevel=min_level, 
                    maxlevel=max_level)
        return [filtered_signal, sampling_freq]

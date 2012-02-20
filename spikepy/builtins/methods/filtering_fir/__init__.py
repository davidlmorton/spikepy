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

from spikepy.developer.methods import FilteringMethod
from spikepy.common.valid_types import ValidOption, ValidInteger
from .simple_fir import fir_filter

class FilteringFIR(FilteringMethod):
    '''
    This class implements a finite impulse response filtering method.
    '''
    name = 'Finite Impulse Response'
    description = 'Sinc type filters with a windowing function.'
    is_stochastic = False

    # method parameters
    kernel_window = ValidOption('boxcar', 'triang', 'blackman', 'hamming', 
            'hanning', 'bartlett', 'parzen', 'bohman', 'blackmanharris', 
            'nuttal', 'barthann', default='hamming')
    low_cutoff_frequency = ValidInteger(min=10, default=300)
    high_cutoff_frequency = ValidInteger(min=10, default=3000)
    kind = ValidOption('low pass', 'high pass', 'band pass', 
            default='band pass')
    order = ValidInteger(min=31, default=100,
            description="The impulse response of an Nth-order FIR filter (i.e. with a Kronecker delta impulse input) lasts for N+1 samples, and then dies to zero." )

    def run(self, signal, sampling_freq, **kwargs):
        kind = kwargs['kind'] = kwargs['kind'].lower().split()[0]
        if kind == 'low':
            critical_freq = kwargs['low_cutoff_frequency']
        elif kind == 'high':
            critical_freq = kwargs['high_cutoff_frequency']
        else:
            critical_freq = (kwargs['low_cutoff_frequency'],
                    kwargs['high_cutoff_frequency'])
        del kwargs['low_cutoff_frequency']
        del kwargs['high_cutoff_frequency']
        kwargs['critical_freq'] = critical_freq
        kwargs['kernel_window'] = str(kwargs['kernel_window'])
        filtered_signal = fir_filter(signal, sampling_freq, **kwargs)
        return [filtered_signal, sampling_freq]


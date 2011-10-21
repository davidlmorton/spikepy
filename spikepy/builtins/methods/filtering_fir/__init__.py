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

from spikepy.developer_tools.methods import FilteringMethod
from spikepy.common.valid_types import ValidOption, ValidIntegerList, \
        ValidInteger
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
    critical_freq = ValidIntegerList(1, 2, default=[300, 3000])
    kind = ValidOption('low pass', 'high pass', 'band pass', 
            default='band pass')
    taps = ValidInteger(min=31, default=101)

    def run(self, signal, sampling_freq, **kwargs):
        kwargs['kind'] = kwargs['kind'].lower().split()[0]
        results = fir_filter(signal, sampling_freq, **kwargs)
        return results


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

import numpy
import scipy.signal as scisig

def resample(signal, prev_sample_rate, new_sample_rate):
    if prev_sample_rate == new_sample_rate:
        return signal

    rate_factor = new_sample_rate/float(prev_sample_rate)
    num_samples = int(len(signal.T)*rate_factor)
    if signal.ndim == 2:
        result = numpy.empty((len(signal), num_samples), dtype=signal.dtype)
        for si, s in enumerate(signal):
            result[si] = scisig.resample(s, num_samples)
        return result
    else:
        return scisig.resample(signal, num_samples)    

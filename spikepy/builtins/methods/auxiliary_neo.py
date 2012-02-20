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

from spikepy.developer.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidFloat
from spikepy.utils.frequency_analysis import psd

def nonlinear_energy_operator(signal):
    result = numpy.empty(signal.shape, dtype=signal.dtype)
    if signal.ndim == 2:
        for i in range(len(signal)):
            result[i][0] = 0.0
            result[i][-1] = 0.0
            result[i][1:-1] = signal[i][1:-1]*signal[i][1:-1] -\
                    signal[i][2:]*signal[i][:-2]
    elif signal.ndim == 1:
        result[0] = 0.0
        result[-1] = 0.0
        result[1:-1] = signal[1:-1]*signal[1:-1] - signal[2:]*signal[:-2]
    else:
        raise ValueError('Signal must be either 1D or 2D not %dD' % signal.ndim)
    return result

class NEODF(AuxiliaryMethod):
    name = 'Apply Nonlinear Energy Operator (Post-Detection-Filtering)'
    description = 'Applies a nonlinear energy operator to the detection-filtered signal.'
    runs_with_stage = 'detection_filter'
    requires = ['df_traces']
    provides = ['df_traces']
    is_stochastic = False

    def run(self, signal, **kwargs):
        return [nonlinear_energy_operator(signal)]

class NEOEF(NEODF):
    name = 'Apply Nonlinear Energy Operator (Post-Extraction-Filtering)'
    description = 'Applies a nonlinear energy operator to the extraction-filtered signal.'
    runs_with_stage = 'extraction_filter'
    requires = ['ef_traces']
    provides = ['ef_traces']

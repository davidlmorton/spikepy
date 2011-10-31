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

from spikepy.developer_tools.methods import AuxiliaryMethod
from spikepy.common.valid_types import ValidInteger
from spikepy.utils.resample import resample

class ResampleAEF(AuxiliaryMethod):
    group = 'Resample'
    optional_in_gui = True
    name = 'Resample after Extraction Filter'
    description = 'Resample the signal after running the Extraction Filter stage.'
    requires = ['ef_traces', 'ef_sampling_freq']
    provides = ['ef_traces', 'ef_sampling_freq']
    is_stochastic = False

    new_sampling_frequency = ValidInteger(10, 100000, default=30000)

    def run(self, signal, sampling_freq, **kwargs):
        return [resample(signal, sampling_freq, 
                kwargs['new_sampling_frequency']), 
                kwargs['new_sampling_frequency']]

class ResampleADF(ResampleAEF):
    group = 'Resample'
    optional_in_gui = True
    name = 'Resample after Detection Filter'
    description = 'Resample the signal after running the Detection Filter stage.'
    requires = ['df_traces', 'df_sampling_freq']
    provides = ['df_traces', 'df_sampling_freq']
    

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

class FilteringCopyDetection(FilteringMethod):
    '''
    This class represents using the results of detection filtering.
    '''
    name = 'Copy Detection Filtering'
    description = 'Copy the results of the detection filtering stage.'
    is_stochastic = False
    requires = ['df_traces', 'df_sampling_freq'] # different from defaults.
    provides = ['ef_traces', 'ef_sampling_freq']

    def run(self, signal, sampling_freq, **kwargs):
        return [signal, sampling_freq]


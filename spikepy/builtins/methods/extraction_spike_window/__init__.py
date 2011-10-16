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

from spikepy.developer_tools.methods import ExtractionMethod
from spikepy.common.valid_types import ValidFloat, ValidBoolean
from .run import run as runner

class ExtractionSpikeWindow(ExtractionMethod):
    '''
    This class implements a spike-window feature-extraction method.
    '''
    name = "Spike Window"
    description = "Extract the waveform of spikes in a temporal window around the spike event."
    is_stochastic = False

    pre_padding = ValidFloat(min=0.0, default=2.0)
    post_padding = ValidFloat(min=0.0, default=4.0)
    exclude_overlappers = ValidBoolean(default=False)

    def run(self, signal_list, sampling_freq, spike_list, **kwargs):
        return runner(signal_list, sampling_freq, spike_list, **kwargs)


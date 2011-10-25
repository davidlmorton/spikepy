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

from spikepy.developer_tools.methods import DetectionMethod
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption
from .run import run as runner

class VoltageThreshold(DetectionMethod):
    '''
    This class implements a voltage threshold spike detection method.
    '''
    name = "Voltage Threshold"
    description = "Spike detection using voltage threshold(s)"
    is_stochastic = False

    threshold_1 = ValidFloat(default=6.0)
    threshold_2 = ValidFloat(default=-6.0)
    refractory_time = ValidFloat(min=0.0, default=0.50)
    max_spike_duration = ValidFloat(min=0.0, default=4.0)
    threshold_units = ValidOption('Standard Deviation', 'Median', 'Signal', 
            default='Standard Deviation')

    def run(self, signal, sampling_freq, **kwargs):
        return runner(signal, sampling_freq, **kwargs)







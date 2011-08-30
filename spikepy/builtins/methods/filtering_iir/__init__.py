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

from spikepy.developer_tools.filtering_method import FilteringMethod
from .control_panel import ControlPanel
from .run import run as runner

class FilteringIIR(FilteringMethod):
    '''
    This class implements an infinte impulse response filtering method.
    '''
    name = 'Infinite Impulse Response'
    description = 'Butterworth and bessel filters.  Can be high/low/band pass types.'
    is_stochastic = False

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def get_run_defaults(self):
        kwargs = {}
        kwargs['function_name'] = 'Butterworth'
        kwargs['acausal'] = True
        kwargs['critical_freq'] = (300, 3000)
        kwargs['kind'] = 'band'
        kwargs['order'] = 3
        return kwargs

    def run(self, signal_list, sampling_freq, **kwargs):
        return runner(signal_list, sampling_freq, **kwargs)
    
del ControlPanel

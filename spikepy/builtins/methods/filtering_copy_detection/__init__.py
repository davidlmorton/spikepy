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

class FilteringCopyDetection(FilteringMethod):
    '''
    This class represents using the results of detection filtering.
    '''
    def __init__(self):
        self.name = 'Copy Detection Filtering'
        self.description = 'Copy the results of the detection filtering stage.'
        self._is_stochastic = True # always yields potentially novel results.

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, signal_list, sampling_freq, **kwargs):
        return None

del ControlPanel

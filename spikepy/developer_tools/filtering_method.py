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

from spikepy.developer_tools.registering_class import RegisteringClass

class FilteringMethod(object):
    '''
    This class should be subclassed in order for developers to add a new 
filtering method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new filtering method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(signal_list, sampling_freq, **kwargs)
        -- This method returns the filtered results.  It should return a list
           of filtered signals.  The filtered signals should have the same
           sampling_freq as the input signals.  kwargs are all the arguments
           to the filtering code.
    '''
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True
    _is_stochastic = False
    _requires = ['raw_data.traces', 'raw_data.sampling_freq']
    _provides = ['<stage_name>.traces'] 
    # <stage_name> is one of "detection_filter" or "extraction_filter"


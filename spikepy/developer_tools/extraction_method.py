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

class ExtractionMethod(object):
    '''
    This class should be subclassed in order for developers to add a new 
feature-extraction method to spikepy.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - make_control_panel(parent, **kwargs)
        -- This method returns a wx.Panel object (or a subclass) that acts as 
           the control panel for the new method.  kwargs should be 
           passed to the wx.Panel constructor.
    - run(signal_list, sampling_freq, events, **kwargs)
        -- This method returns the features.  kwargs are all the arguments
           to the feature-extraction code.
    '''
    # --- CAN OVERWRITE ---
    _is_stochastic = False

    # --- DO NOT ALTER ---
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True
    _requires = ['ef_traces', 'ef_sampling_freq', 'events']

    _provides = ['features', 'feature_locations']
    # features is 2D numpy array with shape = (n, m) where
    #    n == the total number of kept events
    #    m == the number of features describing each event
    #    features[k][l] == feature l of event k
    # feature_locations is a 1D numpy array of indexes.
    #    time of kth feature == feature_locations[k]/ef_sampling_freq

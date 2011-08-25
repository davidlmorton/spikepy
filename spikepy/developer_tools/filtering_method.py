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
    - run(raw_traces, sampling_freq, **kwargs)
        -- This method returns the filtered results and the new sampling_freq.
           It should return a list of filtered signals and the sampling_freq 
           of the new signals.  kwargs are all the arguments to the filtering 
           code.
    '''
    #     Is this method stochastic in nature (generally gives different results
    # with the same inputs)?
    is_stochastic = False

    # what resources or attributes (of Trial objects) does this method need 
    # in order to run?
    requires = ['raw_traces', 'sampling_freq']

    provides = ['<stage_name>_traces', '<stage_name>_sampling_freq'] 
    # <stage_name> is one of "df" or "ef" for detection and extraction.
    # <stage_name>_traces is a 2D numpy array where
    #    len(<stage_name>_traces) == num_channels

    def make_control_panel(parent, **kwargs):
        raise NotImplementedError

    def run(*args, **kwargs):
        raise NotImplementedError 

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
from spikepy.common.trial import Trial

class FileInterpreter(object):
    '''
    This class should be subclassed in order for developers to add a new file
interpreter to spikepy.  
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods AVAILABLE to subclasses:
    - make_trial_object(sampling_freq, raw_traces, fullpath)
        -- This method returns a new Trial object.  A list of Trial objects
           is the expected return value of the read_data_file method.
Methods that subclasses are REQUIRED to implement:
    - read_data_file(fullpath)
        -- This method recieves only a string representation of the
           fullpath to the data file.  It is required to return a list of 
           Trial objects, even if only one was created.  You should use the
           method make_trial_object to create these Trial objects.
    '''
    __metaclass__ = RegisteringClass
    _skips_registration = True
    _is_base_class = True

    def make_trial_object(self, sampling_freq, raw_traces, fullpath):
        return Trial(sampling_freq=sampling_freq, raw_traces=raw_traces,
                     fullpath=fullpath)


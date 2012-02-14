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

from spikepy.common.trial_manager import Trial
from spikepy.common.strategy_manager import Strategy

class FileInterpreter(object):
    '''
    This class should be subclassed in order for developers to add a new file
interpreter to spikepy.  
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Methods that subclasses are REQUIRED to implement:
    - read_data_file(fullpath)
        -- This method recieves only a string representation of the
           fullpath to the data file.  It is required to return a list of 
           Trial and or Strategy objects, even if only one was created.
    '''
    # A list of one or more file extentions this interpreter can open.
    extentions = [] 
    #     Higher priority means that this FileInterpreter will be tried first
    # if spikepy tries more than one FileInterpreter.
    priority = 10

    def read_data_file(fullpath):
        raise NotImplementedError



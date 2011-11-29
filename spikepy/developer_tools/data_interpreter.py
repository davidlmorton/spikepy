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

class DataInterpreter(object):
    '''
    This class should be subclassed in order for developers to add a new way to
export data from spikepy.  
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).
    '''
    name = 'Some Name'
    description = 'Some description.'

    file_extention = '.txt'
    requires = []

    def write_data_file(trials):
        """
        Should raise DataUnavailableError if trials do not have what is
        required.
        """
        raise NotImplementedError



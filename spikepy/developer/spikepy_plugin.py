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
from spikepy.common.valid_types import ValidType


class SpikepyPlugin(object):
    '''
        This is the base class for all spikepy plugins.  To create a plugin
    you should use one of the subclasses of this class, and not this class
    directly.
    '''
    def get_parameter_attributes(self):
        ''' Return a dictionary of ValidType attributes. '''
        attrs = {}
        attribute_names = dir(self)
        for name in attribute_names:
            value = getattr(self, name)
            if isinstance(value, ValidType):
                attrs[name] = value
        return attrs
    
    def get_parameter_defaults(self):
        ''' Return a dictionary containing the default parameter values.  '''
        kwargs = {}
        for attr_name, attr in self.get_parameter_attributes().items():
            kwargs[attr_name] = attr()
        return kwargs

    def validate_parameters(self, parameter_dict):
        '''
            Attempts to validate parameters in a dictionary.  If parameters are 
        invalid an exception is raised.  If parameters are valid, None is 
        returned.
        '''
        for key, value in parameter_dict.items():
            getattr(self, key)(value)

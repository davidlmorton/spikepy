
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

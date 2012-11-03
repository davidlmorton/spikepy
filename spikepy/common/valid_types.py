

from validate import Validator, VdtValueError
from spikepy.common.errors import *

v = Validator()

class ValidType(object):
    mytype = 'pass'
    def __init__(self, *args, **kwargs):
        self._are_args = False
        self._are_kwargs = False

        if 'default' in kwargs.keys():
            self._default = kwargs['default']
            del kwargs['default']

        self.description = kwargs.get('description', None)
        if 'description' in kwargs.keys():
            del kwargs['description']

        if args:
            self._are_args = True
            arg_string = ', '.join(map(str, args))
        if kwargs != {}:
            self._are_kwargs = True
            kwargs_strings = ['%s=%s' % (key, value) 
                    for key, value in kwargs.items()]
            kwargs_string = ', '.join(kwargs_strings)

        args = []
        if self._are_args:
            args.append(arg_string)
        if self._are_kwargs:
            args.append(kwargs_string)

        self.args = ', '.join(args)
        self.default = self(self._default)

    @property
    def passed_args(self):
        return self.args.split(', ')

    def __call__(self, value=None, **kwargs):
        check_string = '%s(%s)' % (self.mytype, self.args) 
        if value is None:
            return self.default
        else:
            try:
                return v.check(check_string, value, **kwargs)
            except:
                raise InvalidValueError('The value "%s" is invalid [%s]' % 
                        (value, check_string))

class ValidInteger(ValidType):
    mytype = 'integer'

class ValidIntegerList(ValidType):
    mytype = 'int_list'

class ValidFloat(ValidType):
    mytype = 'float'

class ValidString(ValidType):
    mytype = 'string'

class ValidBoolean(ValidType):
    mytype = 'boolean'

class ValidOption(ValidType):
    mytype = 'option'

    def __call__(self, value=None, **kwargs):
        check_string = '%s(%s)' % (self.mytype, self.args) 
        if value is None:
            return self.default
        try:
            return v.check(check_string, value, **kwargs)
        except VdtValueError:
            raise InvalidValueError(
                    'The value "%s" must be one of "%s"' % (value, self.args))

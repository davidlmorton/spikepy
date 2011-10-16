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

    def __call__(self, value=None, **kwargs):
        check_string = '%s(%s)' % (self.mytype, self.args) 
        if value is None:
            return self.default
        else:
            return v.check(check_string, value, **kwargs)

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
            raise InvalidOptionError(
                    'The value "%s" must be one of "%s"' % (value, self.args))

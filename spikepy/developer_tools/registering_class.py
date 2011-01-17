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

_class_registry = {}

force_unique_names = True

class unique_name_list(list):
    def __init__(self):
        list.__init__(self)

    def append(self, value):
        # get names of existing members
        existing_names = [cls().name for cls in self]
        if value().name not in existing_names:
            list.append(self, value)
        else:
            raise RuntimeError("A class with the name '%s' has already been registered." % value().name)

class RegisteringClass(type):
    def __init__(cls, name, bases, attrs):
        register = True
        if hasattr(cls, '_skips_registration'):
            register = not cls._skips_registration
            del cls._skips_registration
        if hasattr(cls, '_is_base_class'):
            if cls._is_base_class:
                if force_unique_names:
                    _class_registry[cls] = unique_name_list()
                else:
                    _class_registry[cls] = []
            del cls._is_base_class
        if register:
            for base_class in _class_registry.keys():
                if issubclass(cls, base_class) or base_class is cls:
                    _class_registry[base_class].append(cls)


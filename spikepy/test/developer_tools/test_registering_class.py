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

import unittest

from spikepy.developer_tools.registering_class import (RegisteringClass, 
                                                       _class_registry)

def ira(cls, base_class): # is registered as
    return cls in _class_registry[base_class]


class RegistrationBasics(unittest.TestCase):
    # -- COMMON SETUP --
    class Base(object):
        __metaclass__ = RegisteringClass
        _skips_registration = True
        _is_base_class = True
        def __init__(self):
            self.name = self.__class__.__name__

    class AnotherBase(object):
        __metaclass__ = RegisteringClass
        _skips_registration = True
        _is_base_class = True
        def __init__(self):
            self.name = self.__class__.__name__

    class SelfRegisteringBase(AnotherBase):
        _skips_registration = False
        _is_base_class = True
        def __init__(self):
            self.name = self.__class__.__name__

    class Sub(Base):
        _is_base_class = False
        def __init__(self):
            self.name = self.__class__.__name__

    class Sub2(Sub):
        def __init__(self):
            self.name = self.__class__.__name__

    class UnregisteredSub(Base):
        _skips_registration = True
        def __init__(self):
            self.name = self.__class__.__name__

    class RegisteredSub(Base):
        _skips_registration = False
        def __init__(self):
            self.name = self.__class__.__name__

    class AnotherSub(AnotherBase):
        def __init__(self):
            self.name = self.__class__.__name__

    all_classes = [Base, AnotherBase, SelfRegisteringBase, 
                   Sub, Sub2, UnregisteredSub, RegisteredSub, AnotherSub]

    def define_class(self):
        class AnotherDifferentSub(self.Sub):
            def __init__(self):
                self.name = 'Sub'

    # -- TESTS --
    def test_bases_registered_as_bases(self):
        self.assertTrue(self.Base in _class_registry.keys())
        self.assertTrue(self.AnotherBase in _class_registry.keys())
        self.assertTrue(self.SelfRegisteringBase in _class_registry.keys())

    def test_bases_not_registered_as_themselves(self):
        self.assertFalse(ira(self.Base, self.Base))
        self.assertFalse(ira(self.AnotherBase, self.AnotherBase))
        # SelfRegisteringBase SHOULD register itself.
        self.assertTrue(ira(self.SelfRegisteringBase, self.SelfRegisteringBase))

    def test_subs_not_registered_as_bases(self):
        self.assertFalse(self.Sub in _class_registry.keys())
        self.assertFalse(self.Sub2 in _class_registry.keys())
        self.assertFalse(self.UnregisteredSub in _class_registry.keys())
        self.assertFalse(self.RegisteredSub in _class_registry.keys())
        self.assertFalse(self.AnotherSub in _class_registry.keys())

    def test_unique_name(self):
        self.assertRaises(RuntimeError, self.define_class)

    def test_subclassing(self):
        self.assertTrue( ira(self.Sub, self.Base))
        self.assertFalse(ira(self.Sub, self.AnotherBase))

        self.assertTrue( ira(self.Sub2, self.Base))
        self.assertFalse(ira(self.Sub2, self.AnotherBase))

        self.assertFalse(ira(self.UnregisteredSub, self.Base))
        self.assertFalse(ira(self.UnregisteredSub, self.AnotherBase))

        self.assertTrue( ira(self.RegisteredSub, self.Base))
        self.assertFalse(ira(self.RegisteredSub, self.AnotherBase))

        self.assertTrue( ira(self.AnotherSub, self.AnotherBase))
        self.assertFalse(ira(self.AnotherSub, self.Base))

        self.assertTrue( ira(self.SelfRegisteringBase, self.AnotherBase))
        self.assertFalse(ira(self.SelfRegisteringBase, self.Base))

    def test_namespace_cleanup(self):
        for cls in self.all_classes:
            self.assertFalse(hasattr(cls, '_skips_registration'))
            self.assertFalse(hasattr(cls, '_is_base_class'))

if __name__ == '__main__':
    unittest.main()

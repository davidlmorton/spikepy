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

    class AnotherBase(object):
        __metaclass__ = RegisteringClass
        _skips_registration = True
        _is_base_class = True

    class SelfRegisteringBase(AnotherBase):
        __metaclass__ = RegisteringClass
        _skips_registration = False
        _is_base_class = True

    class Sub(Base):
        _is_base_class = False

    class Sub2(Sub):
        pass

    class UnregisteredSub(Base):
        _skips_registration = True

    class RegisteredSub(Base):
        _skips_registration = False

    class AnotherSub(AnotherBase):
        pass

    all_classes = [Base, AnotherBase, SelfRegisteringBase, 
                   Sub, Sub2, UnregisteredSub, RegisteredSub, AnotherSub]

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

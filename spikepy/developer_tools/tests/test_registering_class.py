import unittest

from spikepy.developer_tools.registering_class import (RegisteringClass, 
                                                       _class_registry,
                                                       _base_classes)

def ira(cls, base_class_name): # is registered as
    return cls in _class_registry[base_class_name]
        

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

    class SelfRegisteringBase(object):
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
        self.assertTrue('Base' in _class_registry.keys())
        self.assertTrue(_base_classes['Base'] == self.Base)

        self.assertTrue('AnotherBase' in _class_registry.keys())
        self.assertTrue(_base_classes['AnotherBase'] == self.AnotherBase)

        self.assertTrue('SelfRegisteringBase' in _class_registry.keys())
        self.assertTrue(_base_classes['SelfRegisteringBase'] == 
                        self.SelfRegisteringBase)

    def test_bases_not_registered_as_themselves(self):
        self.assertFalse(ira(self.Base, 'Base'))
        self.assertFalse(ira(self.AnotherBase, 'AnotherBase'))
        # SelfRegisteringBase SHOULD register itself.
        self.assertTrue(ira(self.SelfRegisteringBase, 'SelfRegisteringBase'))

    def test_subs_not_registered_as_bases(self):
        self.assertFalse('Sub' in _base_classes.keys())
        self.assertFalse('Sub2' in _base_classes.keys())
        self.assertFalse('UnregisteredSub' in _base_classes.keys())
        self.assertFalse('RegisteredSub' in _base_classes.keys())
        self.assertFalse('AnotherSub' in _base_classes.keys())

    def test_subclassing(self):
        self.assertTrue( ira(self.Sub, 'Base'))
        self.assertFalse(ira(self.Sub, 'AnotherBase'))

        self.assertTrue( ira(self.Sub2, 'Base'))
        self.assertFalse(ira(self.Sub2, 'AnotherBase'))

        self.assertFalse(ira(self.UnregisteredSub, 'Base'))
        self.assertFalse(ira(self.UnregisteredSub, 'AnotherBase'))

        self.assertTrue( ira(self.RegisteredSub, 'Base'))
        self.assertFalse(ira(self.RegisteredSub, 'AnotherBase'))

        self.assertTrue( ira(self.AnotherSub, 'AnotherBase'))
        self.assertFalse(ira(self.AnotherSub, 'Base'))

    def test_namespace_cleanup(self):
        for cls in self.all_classes:
            self.assertFalse(hasattr(cls, '_skips_registration'))
            self.assertFalse(hasattr(cls, '_is_base_class'))

if __name__ == '__main__':
    unittest.main()

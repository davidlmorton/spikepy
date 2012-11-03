

import unittest
import os

from spikepy.common.strategy_manager import Strategy
import spikepy.common.program_text as pt

class StrategyClassTests(unittest.TestCase):
    a = Strategy()

    b = Strategy()
    b.name='Save(me)'
    b.methods_used={'methods_used_key':'methods_used_value'}
    b.settings={'settings_key':42}

    def test_constructor(self):
        custom_name = "%s(%s)" % (pt.CUSTOM_SC, pt.CUSTOM_LC)
        self.assertTrue(self.a.name==custom_name)
        self.assertTrue(self.a.methods_used=={})
        self.assertTrue(self.a.settings=={})
        self.assertTrue(self.a.auxiliary_stages=={})
        
    def test_equality(self):
        c = Strategy()
        self.assertTrue(self.a==c)

        c.methods_used = None
        self.assertFalse(self.a==c)

        c.methods_used = {}
        self.assertTrue(self.a==c)

        c.settings = None
        self.assertFalse(self.a==c)

    def test_inequality(self):
        c = Strategy()
        self.assertFalse(self.a!=c)

        c.methods_used = None
        self.assertTrue(self.a!=c)

        c.methods_used = {}
        self.assertFalse(self.a!=c)

        c.settings = None
        self.assertTrue(self.a!=c)

    def test_as_dict(self):
        adict = self.a.as_dict
        self.assertTrue(len(adict.keys())==4)
        self.assertTrue('name' in adict.keys())
        self.assertTrue('methods_used' in adict.keys())
        self.assertTrue('settings' in adict.keys())
        self.assertTrue('auxiliary_stages' in adict.keys())

    def test_save_and_load(self):
        self.b.save('test.strategy')

        c = Strategy()
        c.load('test.strategy')
        self.assertTrue(c==self.b)
        self.assertFalse(c==self.a)

        os.remove('test.strategy')

    def test_from_file(self):
        self.b.save('test.strategy')

        c = Strategy.from_file('test.strategy')
        self.assertTrue(c==self.b)
        self.assertFalse(c==self.a)

        os.remove('test.strategy')
        

if __name__ == '__main__':
    unittest.main()

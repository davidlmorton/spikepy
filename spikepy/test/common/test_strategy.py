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
        self.assertTrue(self.a.methods_used==None)
        self.assertTrue(self.a.settings==None)
        
    def test_equality(self):
        c = Strategy()
        self.assertTrue(self.a==c)

        c.methods_used = {}
        self.assertFalse(self.a==c)

        c.methods_used = None
        self.assertTrue(self.a==c)

        c.settings = {}
        self.assertFalse(self.a==c)

    def test_inequality(self):
        c = Strategy()
        self.assertFalse(self.a!=c)

        c.methods_used = {}
        self.assertTrue(self.a!=c)

        c.methods_used = None
        self.assertFalse(self.a!=c)

        c.settings = {}
        self.assertTrue(self.a!=c)

    def test_as_dict(self):
        adict = self.a.as_dict
        self.assertTrue(len(adict.keys())==3)
        self.assertTrue('name' in adict.keys())
        self.assertTrue('methods_used' in adict.keys())
        self.assertTrue('settings' in adict.keys())

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

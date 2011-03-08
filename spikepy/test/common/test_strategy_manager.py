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

from spikepy.common.strategy import Strategy, make_strategy_name
from spikepy.common import program_text as pt
from spikepy.common.strategy_manager import StrategyManager

msn = make_strategy_name

class StrategyManagerTests(unittest.TestCase):
    a = {'s1':10, 's2':1}
    b = {'s1':10, 's2':2}
    c = {'s1':20, 's2':1}

    saa = Strategy(methods_used=a, settings=a)
    saa.name = msn('a','a')
    sab = Strategy(methods_used=a, settings=b)
    sab.name = msn('a','b')
    sba = Strategy(methods_used=b, settings=a)
    sba.name = msn('b','a')
    # sab -named- aa, ba, None(none)...
    sabnaa = Strategy(methods_used=a, settings=b)
    sabnaa.name = msn('a','a')
    sabnba = Strategy(methods_used=a, settings=b)
    sabnba.name = msn('b','a')
    sabnnn = Strategy(methods_used=a, settings=b)
    
    def test_constructor(self):
        sm = StrategyManager()
        self.assertTrue(sm.strategies=={})
        
    def test_add_1(self):
        sm = StrategyManager()
        self.assertTrue(len(sm.strategies.keys())==0)
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        self.assertRaises(RuntimeError, sm.add_strategy, self.saa)

    def test_add_2(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        sm.add_strategy(self.sab)
        self.assertTrue(len(sm.strategies.keys())==2)
        self.assertRaises(RuntimeError, sm.add_strategy, self.sab)

    def test_add_3(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        sm.add_strategy(self.sab)
        self.assertTrue(len(sm.strategies.keys())==2)
        sm.add_strategy(self.sba)
        self.assertTrue(len(sm.strategies.keys())==3)
        # because sba is alredy there
        self.assertRaises(RuntimeError, sm.add_strategy, self.sba)

    def test_add_4(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        sm.add_strategy(self.sabnnn)
        self.assertTrue(len(sm.strategies.keys())==2)
        # stored strategy is called A(none) and is same as sab
        smsabnnn = sm.get_strategy_by_name(msn('a','none'))
        self.assertTrue(smsabnnn == self.sab)
        # because ab is already there, but known as A(none)
        self.assertRaises(RuntimeError, sm.add_strategy, self.sab)

    def test_add_5(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        sm.add_strategy(self.sab)
        self.assertTrue(len(sm.strategies.keys())==2)
        # because abnba is already there, but known as A(b) not B(a)
        self.assertRaises(RuntimeError, sm.add_strategy, self.sabnba)

    def test_add_6(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertTrue(len(sm.strategies.keys())==1)
        # because sabnaa is has the same methods_used/methods_used_name and
        #   different settings AND the same settings_name.
        self.assertRaises(RuntimeError, sm.add_strategy, self.sabnaa)

    def test_get_strategy_by_strategy(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        sab_managed = sm.get_strategy_by_strategy(self.sab)

        self.assertTrue(sab_managed is not self.sab)
        self.assertTrue(sab_managed == self.sab)

    def test_get_strategy_by_strategy_2(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sba)
        self.assertRaises(ValueError, sm.get_strategy_by_strategy, self.sab)

    def test_get_strategy_by_name(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        sab_managed = sm.get_strategy_by_name(self.sab.name)

        self.assertTrue(sab_managed is not self.sab)
        self.assertTrue(sab_managed == self.sab)

    def test_get_strategy_by_name_2(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        self.assertRaises(ValueError, sm.get_strategy_by_name, 'Fail-lolz')

    def test_get_strategy_by_name_and_by_strategy(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)

        sab_by_name = sm.get_strategy_by_name(self.sab.name)
        sab_by_strategy = sm.get_strategy_by_strategy(self.sab)

        self.assertTrue(sab_by_name is not self.sab)
        self.assertTrue(sab_by_name is sab_by_strategy)

    def test_get_strategy_name(self):
        sm = StrategyManager()
        name = sm.get_strategy_name(self.saa)
        self.assertTrue(name==msn(pt.CUSTOM_SC, pt.CUSTOM_LC))

        # after adding saa, name should be same as saa
        sm.add_strategy(self.saa)
        name = sm.get_strategy_name(self.saa)
        self.assertTrue(name==self.saa.name)
        # name should be same methods_used part, but custom settings for sab
        name = sm.get_strategy_name(self.sab)
        self.assertTrue(name==msn(self.sab.methods_used_name, pt.CUSTOM_LC))

        name = sm.get_strategy_name(self.sba)
        self.assertTrue(name==msn(pt.CUSTOM_SC, pt.CUSTOM_LC))

    def test_remove_strategy(self):
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        self.assertTrue(len(sm.strategies.keys())==3)
        sm.remove_strategy(self.sab)
        self.assertTrue(len(sm.strategies.keys())==2)
        self.assertRaises(ValueError, sm.get_strategy_by_strategy, self.sab)

    def test_remove_strategy_2(self):
        sm = StrategyManager()
        self.assertRaises(ValueError, sm.remove_strategy, self.sab)
        
if __name__ == '__main__':
    unittest.main()

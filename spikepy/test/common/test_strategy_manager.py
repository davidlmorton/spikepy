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

from spikepy.common import program_text as pt
from spikepy.common.strategy_manager import StrategyManager, \
        Strategy, make_strategy_name

from spikepy.common.errors import *

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
    sabnnn.name = msn('none', 'none')
    
    def test_constructor(self):
        sm = StrategyManager()
        self.assertEquals(sm.strategies, {})
        
    def test_add_1(self):
        # can add one strategy, and adding it again raises error.
        sm = StrategyManager()
        self.assertEquals(len(sm.strategies.keys()), 0)
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.saa)

    def test_add_2(self):
        # can add two different strategies, adding either again raises error.
        # same methods used, different settings
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        sm.add_strategy(self.sab)
        self.assertEquals(len(sm.strategies.keys()), 2)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sab)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.saa)

    def test_add_3(self):
        # can add three different strategies, adding any again raises error.
        # same methods used, same settings
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        sm.add_strategy(self.sab)
        self.assertEquals(len(sm.strategies.keys()), 2)
        sm.add_strategy(self.sba)
        self.assertEquals(len(sm.strategies.keys()), 3)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.saa)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sab)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sba)

    def test_add_4(self):
        # adding strategy with a methods_used set that already has a name
        #   added strategy will adopt existing name.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        sm.add_strategy(self.sabnnn)
        self.assertEquals(len(sm.strategies.keys()), 2)
        # stored strategy is called A(none) and is same as sab
        smsabnnn = sm.get_strategy(msn('a','none'))
        self.assertEquals(smsabnnn ,  self.sab)
        # because ab is already there, but known as A(none)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sab)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, smsabnnn)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sabnnn)

    def test_add_5(self):
        # when adding a strategy, it doesn't matter what it's name is, if it
        # is already under management, it raises an error
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        sm.add_strategy(self.sab)
        self.assertEquals(len(sm.strategies.keys()), 2)
        # because abnba is already there, but known as A(b) not B(a)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sabnba)
        self.assertRaises(DuplicateStrategyError, sm.add_strategy, self.sabnnn)

    def test_add_6(self):
        # cannot resolve conflict on settings name if methods_used match.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        self.assertEquals(len(sm.strategies.keys()), 1)
        # because sabnaa is has the same methods_used/methods_used_name and
        #   different settings AND the same settings_name.
        self.assertRaises(SettingsNameForbiddenError, sm.add_strategy, 
                self.sabnaa)

    def test_add_7(self):
        # cannot resolve conflict on methods_used name.
        sm = StrategyManager()
        sm.add_strategy(self.sba)
        self.assertEquals(len(sm.strategies.keys()), 1)
        # because sabnba is has different methods_used
        # but the same methods_used_name as existing Strategy.
        self.assertRaises(MethodsUsedNameForbiddenError, sm.add_strategy, 
                self.sabnba)

    def test_get_strategy_by_strategy(self):
        # can get the strategy from manager if we have equivalent strategy,
        # regardless of names.
        # managed strategies are copies of strategies, not references.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        sab_managed = sm.get_strategy(self.sab)
        sabnnn_managed = sm.get_strategy(self.sabnnn)

        self.assertTrue(sab_managed is not self.sab)
        self.assertEquals(sab_managed ,  self.sab)

        self.assertTrue(sabnnn_managed is not self.sabnnn)
        self.assertEquals(sabnnn_managed ,  self.sab)

    def test_get_strategy_by_strategy_2(self):
        # asking for strategy not under management raises error
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sba)
        self.assertRaises(MissingStrategyError, sm.get_strategy, self.sab)

    def test_get_strategy_by_name(self):
        # can get strategy under management given its name as well.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        sab_managed = sm.get_strategy(self.sab.name)

        self.assertTrue(sab_managed is not self.sab)
        self.assertEquals(sab_managed ,  self.sab)

    def test_get_strategy_by_name_2(self):
        # raises error if name isn't one of strategies under management
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        self.assertRaises(MissingStrategyError, sm.get_strategy, 
                self.sabnnn.name)

    def test_get_strategy_by_name_and_by_strategy(self):
        # getting strategy by name or by strategy yields same result.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)

        sab_by_name = sm.get_strategy(self.sab.name)
        sab_by_strategy = sm.get_strategy(self.sab)

        self.assertTrue(sab_by_name is not self.sab)
        self.assertTrue(sab_by_name is sab_by_strategy)

        self.assertRaises(ArgumentTypeError, sm.get_strategy, True)

    def test_get_strategy_name(self):
        sm = StrategyManager()
        name = sm.get_strategy_name(self.saa)
        self.assertEquals(name, msn(pt.CUSTOM_SC, pt.CUSTOM_LC))

        # after adding saa, name should be same as saa
        sm.add_strategy(self.saa)
        name = sm.get_strategy_name(self.saa)
        self.assertEquals(name, self.saa.name)
        # name should be same methods_used part, but custom settings for sab
        name = sm.get_strategy_name(self.sab)
        self.assertEquals(name, msn(self.sab.methods_used_name, pt.CUSTOM_LC))

        name = sm.get_strategy_name(self.sba)
        self.assertEquals(name, msn(pt.CUSTOM_SC, pt.CUSTOM_LC))

    def test_remove_strategy(self):
        # can remove strategies by name or by strategy.
        sm = StrategyManager()
        sm.add_strategy(self.saa)
        sm.add_strategy(self.sab)
        sm.add_strategy(self.sba)
        self.assertEquals(len(sm.strategies.keys()), 3)
        sm.remove_strategy(self.sab)
        self.assertEquals(len(sm.strategies.keys()), 2)
        self.assertRaises(MissingStrategyError, sm.get_strategy, self.sab)

        sm.add_strategy(self.sab)
        self.assertEquals(len(sm.strategies.keys()), 3)
        sm.remove_strategy(self.sab.name)
        self.assertEquals(len(sm.strategies.keys()), 2)
        self.assertRaises(MissingStrategyError, sm.get_strategy, self.sab.name)

    def test_remove_strategy_2(self):
        # raises error if trying to remove something that isn't managed.
        sm = StrategyManager()
        self.assertRaises(MissingStrategyError, sm.remove_strategy, self.sab)
        self.assertRaises(MissingStrategyError, sm.remove_strategy, self.sab.name)
        
if __name__ == '__main__':
    unittest.main()

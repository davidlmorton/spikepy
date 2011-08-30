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

import os

from spikepy.common import program_text as pt
from strategy import (make_strategy_name, make_methods_used_name, 
                      make_settings_name)
from spikepy.common.path_utils import get_data_dirs
from spikepy.common.strategy import Strategy


class StrategyManager(object):
    def __init__(self, config_manager=None):
        self.config_manager = config_manager 
        self.strategies = {} # strategies under management
        self._current_strategy = None

    @property
    def current_strategy(self):
        '''Return the currently selected strategy.'''
        return self._current_strategy

    @current_strategy.setter
    def current_strategy(self, value):
        '''Set the current strategy with either a name or a Strategy object.'''
        if isinstance(value, Strategy):
            self._current_strategy = value
        elif isinstance(value, type('')):
            self._current_strategy = self.get_strategy_name(value)
        else:
            raise RuntimeError('Current Strategy must be set with either a string or a Strategy object, not %s' % type(value))

    def load_all_strategies(self):
        '''
        Load all the strategies "builtins", "application", and "user".
        '''
        # load strategies (first builtins, then application, then user)
        for level in ['builtins', 'application', 'user']:
            strategy_path = get_data_dirs()[level]['strategies']
            self.load_strategies(strategy_path)

    def load_strategies(self, path):
        if os.path.exists(path):
            files = os.listdir(path)
            for f in files:
                if f.endswith('.strategy'):
                    fullpath = os.path.join(path, f)
                    strategy = Strategy.from_file(fullpath)
                    self.add_strategy(strategy)

    def save_strategies(self):
        strategy_path = get_data_dirs()['user']['strategies']
        for strategy in self.strategies.values():
            if strategy.fullpath is None:
                fullpath = os.path.join(strategy_path, 
                                        '%s.strategy' % strategy.name)
                strategy.fullpath = fullpath
                strategy.save(fullpath)

    # --- ADD AND REMOVE STRATEGIES ---
    def add_strategy(self, strategy):
        strategy = strategy.copy() 
        proposed_name = self.get_strategy_name(strategy)
        proposed_methods_used_name = make_methods_used_name(proposed_name)
        proposed_settings_name = make_settings_name(proposed_name)

        # -- check for uniqueness --
        if strategy in self.strategies.values():
            raise RuntimeError("Strategy (%s/%s) already under management." % 
                               (strategy.name, 
                                self.get_strategy_by_strategy(strategy).name))

        # -- check methods_used_name -- (coherse if collision)
        if proposed_methods_used_name != pt.CUSTOM_LC:
            if proposed_methods_used_name != strategy.methods_used_name:
                strategy.methods_used_name = proposed_methods_used_name
        else:
            forbidden_methods_used_names = [s.methods_used_name
                                            for s in self.strategies.values()]
            forbidden_methods_used_names.append(pt.CUSTOM_LC)
            if strategy.methods_used_name in forbidden_methods_used_names:
                raise RuntimeError("Methods-used name '%s' forbidden." % 
                                   strategy.methods_used_name)

        # -- check settings_name -- (raise RuntimeError if collision)
        if proposed_settings_name != pt.CUSTOM_LC:
            if proposed_settings_name != strategy.settings_name:
                raise RuntimeError("Adding '%s': Settings already named '%s' NOT '%s'" % 
                                   (strategy.name,
                                    proposed_settings_name,
                                    strategy.settings_name))
        else:
            forbidden_settings_names = [s.settings_name
                                        for s in self.strategies.values()
                                        if s.methods_used_name == 
                                           strategy.methods_used_name]
            forbidden_settings_names.append(pt.CUSTOM_LC)
            if strategy.settings_name in forbidden_settings_names:
                raise RuntimeError("Settings name '%s' forbidden." % 
                                   strategy.settings_name)

        # -- checks passed, so add to manager --
        self.strategies[strategy.name] = strategy

    def remove_strategy(self, strategy):
        try:  
            del self.strategies[strategy.name]
        except KeyError:
            raise ValueError('This strategy (%s) is not under management.' %
                             strategy.name)

    # --- GET STRATEGIES UNDER MANAGEMENT ---
    def get_strategy_by_strategy(self, strategy):
        '''
        If argument 'strategy' is a currently managed strategy, return the
            managed strategy.  Otherwise raise a ValueError.
        '''
        for s_name, s in self.strategies.items():
            if s == strategy:
                return s
        raise ValueError('This strategy (%s) is not under management.' %
                             strategy.name)

    def get_strategy_by_name(self, strategy_name):
        for managed_strategy in self.strategies.values():
            if managed_strategy.name == strategy_name:
                return managed_strategy
        raise ValueError('No strategy named "%s" under management.' % 
                           strategy_name)

    def get_strategies_with_same_methods_used(self, strategy):
        return_strategies = []
        for managed_strategy in self.strategies.values():
            if managed_strategy.methods_used == strategy.methods_used:
                return_strategies.append(managed_strategy)
        return return_strategies

    # --- NAME STRATEGIES ---
    def get_strategy_name(self, strategy):
        '''
        See if this strategy already is under management, if so return 
            its name.  Otherwise give this strategy an appropriate name.
        '''
        if strategy in self.strategies.values():
            managed_strategy = self.get_strategy_by_strategy(strategy)
            return managed_strategy.name

        cousin_strategies = self.get_strategies_with_same_methods_used(strategy)
        if cousin_strategies:
            return make_strategy_name(cousin_strategies[0].methods_used_name,
                                      pt.CUSTOM_LC)

        return make_strategy_name(pt.CUSTOM_SC, pt.CUSTOM_LC)



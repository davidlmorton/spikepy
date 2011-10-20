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
import json
import copy

import os

from spikepy.common import program_text as pt
from spikepy.common.path_utils import get_data_dirs
from spikepy.common.stages import stages
from spikepy.common.errors import *


class Strategy(object):
    def __init__(self, methods_used={}, 
                methods_used_name=pt.CUSTOM_SC, 
                settings={}, 
                settings_name=pt.CUSTOM_LC,
                auxiliary_stages={}):
        self.methods_used = methods_used
        self.methods_used_name = methods_used_name
        self.settings = settings
        self.settings_name = settings_name
        self.auxiliary_stages = auxiliary_stages
            
        self.fullpath = None

    def __str__(self):
        return_str = [self.name]
        for stage in stages:
            method = self.methods_used[stage]
            return_str.append('    %s: %s' % (stage, repr(method)))
            settings = self.settings[stage]
            for setting_name, value in settings.items():
                return_str.append('        %s: %s' % 
                        (setting_name, repr(value)))

        for aux_plugin_name, aux_settings in self.auxiliary_stages.items():
            return_str.append('    %s: %s' % ('auxiliary_stage', 
                    repr(aux_plugin_name)))
            for setting_name, value in aux_settings.items():
                return_str.append('        %s: %s' % 
                        (setting_name, repr(value)))
            
        return '\n'.join(return_str)

    # NAME
    @property
    def name(self):
        return make_strategy_name(self.methods_used_name,
                                  self.settings_name)
    @name.setter
    def name(self, value):
        self.methods_used_name = make_methods_used_name(value)
        self.settings_name = make_settings_name(value)

    # METHODS USED NAME
    @property
    def methods_used_name(self):
        return self._methods_used_name.lower()

    @methods_used_name.setter
    def methods_used_name(self, value):
        self._methods_used_name = value.lower()

    # SETTINGS NAME
    @property
    def settings_name(self):
        return self._settings_name.lower()

    @settings_name.setter
    def settings_name(self, value):
        self._settings_name = value.lower()

    # --- COMPARISON OPERATORS ---
    def __eq__(self, other):
        return not self != other

    def __ne__(self, other):
        # ensure settings are different (most likely)
        if self.methods_used != other.methods_used:
            return True

        # ensure methods sets are different (less likely)
        if self.settings != other.settings:
            return True

        return False # least likely of all

    # --- ARCHIVING METHODS ---
    @property
    def as_dict(self):
        return {'name':self.name, 'methods_used':self.methods_used,
                'settings':self.settings}

    def save(self, fullpath):
        with open(fullpath, 'w') as ofile:
            json.dump(self.as_dict, ofile, indent=4)

    def load(self, fullpath):
        with open(fullpath, 'r') as infile:
            strategy_dict = json.load(infile)
        self.methods_used = strategy_dict['methods_used']
        self.settings     = strategy_dict['settings']
        self.name         = strategy_dict['name']
        self.fullpath     = fullpath

    @classmethod
    def from_file(cls, fullpath):
        return_strategy = cls()
        return_strategy.load(fullpath)
        return return_strategy

    def copy(self):
        return copy.deepcopy(self)


class StrategyManager(object):
    _managed_class = Strategy
    _managed_file_type = '.strategy'

    def __init__(self, config_manager=None):
        self.config_manager = config_manager 
        self.strategies = {} # strategies under management
        self._current_strategy = None

    def __str__(self):
        return_str = ['Strategy Manager with strategies:']
        for strategy_name in sorted(self.strategies.keys()):
            is_current = ''
            if self.current_strategy.name == strategy_name:
                is_current = ' (Currently Selected)'
            return_str.append('    %s%s' % (strategy_name, is_current))
        return '\n'.join(return_str)

    @property
    def current_strategy(self):
        '''Return the currently selected strategy.'''
        return self._current_strategy

    @current_strategy.setter
    def current_strategy(self, value):
        '''Set the current strategy with either a name or a Strategy object.'''
        if isinstance(value, self._managed_class):
            self._current_strategy = value
        elif isinstance(value, str):
            self._current_strategy = self.get_strategy_name(value)
        else:
            raise ArgumentTypeError('Current Strategy must be set with either a string or a Strategy object, not %s' % type(value))

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
                if f.endswith(self._managed_file_type):
                    fullpath = os.path.join(path, f)
                    strategy = self._managed_class.from_file(fullpath)
                    self.add_strategy(strategy)

    def save_strategies(self):
        strategy_path = get_data_dirs()['user']['strategies']
        for strategy in self.strategies.values():
            if strategy.fullpath is None:
                fullpath = os.path.join(strategy_path, 
                        '%s%s' % (strategy.name, self._managed_file_type))
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
            raise DuplicateStrategyError(
                    "Strategy (%s/%s) already under management." % 
                               (strategy.name, 
                                self._get_strategy_by_strategy(strategy).name))

        # -- check methods_used_name -- (coherse if collision)
        if proposed_methods_used_name != pt.CUSTOM_LC:
            if proposed_methods_used_name != strategy.methods_used_name:
                strategy.methods_used_name = proposed_methods_used_name
        else:
            forbidden_methods_used_names = [s.methods_used_name
                                            for s in self.strategies.values()]
            forbidden_methods_used_names.append(pt.CUSTOM_LC)
            if strategy.methods_used_name in forbidden_methods_used_names:
                raise MethodsUsedNameForbiddenError(
                        "Methods-used name '%s' forbidden." % 
                                   strategy.methods_used_name)

        # -- check settings_name -- (raise Error if collision)
        forbidden_settings_names = [s.settings_name
                                    for s in self.strategies.values()
                                    if s.methods_used_name == 
                                       strategy.methods_used_name]
        forbidden_settings_names.append(pt.CUSTOM_LC)
        if strategy.settings_name in forbidden_settings_names:
            raise SettingsNameForbiddenError(
                    "Settings name '%s' forbidden." % 
                               strategy.settings_name)

        # -- checks passed, so add to manager --
        self.strategies[strategy.name] = strategy

    def remove_strategy(self, strategy):
        managed_strategy = self.get_strategy(strategy)
        del self.strategies[managed_strategy.name]

    # --- GET STRATEGIES UNDER MANAGEMENT ---
    def _get_strategy_by_strategy(self, strategy):
        '''
        If argument 'strategy' is a currently managed strategy, return the
            managed strategy.  Otherwise raise a MissingStrategyError.
        '''
        for s_name, s in self.strategies.items():
            if s == strategy:
                return s
        raise MissingStrategyError(
                'This strategy (%s) is not under management.' %
                             strategy.name)

    def _get_strategy_by_name(self, strategy_name):
        for managed_strategy in self.strategies.values():
            if managed_strategy.name == strategy_name:
                return managed_strategy
        raise MissingStrategyError(
                'No strategy named "%s" under management.' % 
                           strategy_name)

    def get_strategy(self, strategy):
        if isinstance(strategy, str):
            return self._get_strategy_by_name(strategy)
        elif isinstance(strategy, self._managed_class):
            return self._get_strategy_by_strategy(strategy)
        else:
            raise ArgumentTypeError('get_strategy must be called with either a string or an instance/subclass of Strategy, not %s' % type(strategy))

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
            managed_strategy = self._get_strategy_by_strategy(strategy)
            return managed_strategy.name

        cousin_strategies = self.get_strategies_with_same_methods_used(strategy)
        if cousin_strategies:
            return make_strategy_name(cousin_strategies[0].methods_used_name,
                                      pt.CUSTOM_LC)

        return make_strategy_name(pt.CUSTOM_SC, pt.CUSTOM_LC)


def make_methods_used_name(strategy_name):
    '''From a full strategy-name return just the method-used-name.'''
    return strategy_name.split('(')[0].lower()


def make_settings_name(strategy_name):
    '''From a full strategy-name return just the settings-name.'''
    return strategy_name.split('(')[1][:-1].lower()


def make_strategy_name(methods_used_name, settings_name):
    '''
    From a methods-set-name and a settings-name, make a full strategy name.
    '''
    pre  = methods_used_name
    post = settings_name
    if len(pre) >= 1:
        new_name = pre[0].upper() + pre[1:].lower() + '(%s)' % post.lower()
        return new_name



    

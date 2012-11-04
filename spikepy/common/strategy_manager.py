#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import types
import copy

import os

try:
    from callbacks import supports_callbacks
except ImportError:
    from spikepy.other.callbacks.callbacks import supports_callbacks

from spikepy.common import program_text as pt
from spikepy.common.path_utils import get_data_dirs
from spikepy.common.stages import stages
from spikepy.common.errors import *
from spikepy.common.plugin_manager import plugin_manager
from spikepy.utils.substring_dict import SubstringDict 
from spikepy.common.strategy import Strategy, make_methods_used_name,\
        make_settings_name, make_strategy_name

def check_plugin_settings(stage_name, method_name, settings, result=None):
    if result is None:
        result = defaultdict(list)

    plugin = plugin_manager.find_plugin(stage_name, 
            method_name)
    default_settings = plugin.get_parameter_defaults()

    for needed_setting in default_settings.keys():
        if needed_setting not in settings.keys():
            result['missing_settings'].append(
                    (stage_name, method_name, needed_setting))

    for existing_setting, value in settings.items():
        if existing_setting not in default_settings.keys():
            result['non_existing_settings'].append(
                    (stage_name, method_name, existing_setting))
        else:
            try:
                getattr(plugin, existing_setting)(value)
            except:
                result['invalid_settings'].append(
                    (stage_name, method_name, existing_setting))
    return result


class StrategyManager(object):
    _managed_class = Strategy
    _managed_file_type = '.strategy'

    def __init__(self):
        self.strategies = SubstringDict() # strategies under management

    def __str__(self):
        return_str = ['Strategy Manager with strategies:']
        for strategy_name in sorted(self.strategies.keys()):
            return_str.append('    %s' % strategy_name)
        return '\n'.join(return_str)

    @property
    def managed_strategy_names(self):
        return self.strategies.keys()

    def load_all_strategies(self):
        '''
        Load all the strategies "builtins", "application", and "user".
        '''
        # load strategies (first builtins, then application, then user)
        for level in ['builtins', 'application', 'user']:
            strategy_path = get_data_dirs(app_name='spikepy')[
                    level]['strategies']
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
        strategy_path = get_data_dirs(app_name='spikepy')[
                'user']['strategies']
        for strategy in self.strategies.values():
            if strategy.fullpath is None:
                fullpath = os.path.join(strategy_path, 
                        '%s%s' % (strategy.name, self._managed_file_type))
                strategy.fullpath = fullpath
                strategy.save(fullpath)

    def check_strategy(self, strategy):
        '''
            Return what is wrong with a strategy as a dictionary.
        returns:
            'missing_methods': list of (stage_name,) tuples
                -- Stage has no specified method at all.
            'non_existing_methods': list of (stage_name, method_name) tuples
                -- Stage has method that isn't a plugin on this system.
            'non_existing_settings': list of 
                    (stage_name, method_name, settings_name) tuples
                -- Stage has setting that isn't one of the settings that is
                   supposed to be specified for this method.
            'missing_settings': list of 
                (stage_name, methods_name, settings_name) tuples
                -- Stage does not have a setting that is supposed to be
                   specified for this method.
            'invalid_settings': list of
                (stage_name, methods_name, settings_name, settings_value) tuples
                -- Stage has setting that is not valid 
                   (i.e. out of range or wrong type) for this method.
        '''
        result = defaultdict(list)
        for stage_name in stages.stages:
            try:
                method_name = strategy.methods_used[stage_name]
            except KeyError:
                result['missing_methods'].append((stage_name,))
                continue

            try:
                plugin = plugin_manager.find_plugin(stage_name, 
                        method_name)
            except MissingPluginError:
                result['non_existing_methods'].append((stage_name, method_name))
                continue

            default_settings = plugin.get_parameter_defaults()
            try:
                settings = strategy.settings[stage_name]
            except KeyError:
                # all settings are missing.
                for setting_name in default_settings.keys():
                    result['missing_settings'].append(
                            (stage_name, method_name, setting_name))
                continue

            result = check_plugin_settings(stage_name, method_name, settings)

        stage_name = 'auxiliary'
        for method_name, settings in strategy.auxiliary_stages.items():
            try:
                plugin = plugin_manager.find_plugin(stage_name, 
                        method_name)
            except MissingPluginError:
                result['non_existing_methods'].append((stage_name, method_name))
                continue
            
            result = check_plugin_settings(stage_name, method_name, settings)
        return result

    def fix_strategy(strategy, problems_dict):
        '''
            Return a fixed strategy given a broken strategy and the output of 
        self.check_strategy.
        '''
        strategy = strategy.copy()
        for stage_name, method_name in problems_dict['non_existing_methods']:
            del strategy.methods_used[stage_name]
            problems_dict['missing_methods'].append((stage_name,))

        for value in problems_dict['missing_methods']:
            stage_name = value[-1]
            plugin = plugin_manager.get_default_plugin(stage_name)
            strategy.methods_used[stage_name] = plugin.name
            strategy.settings[stage_name] = plugin.get_parameter_defaults()

        for stage_name, method_name, setting_name in problems_dict[
                'non_existing_settings']:
            if stage_name != 'auxiliary':
                del strategy.settings[stage_name][setting_name]
            else:
                del strategy.auxiliary_stages[method_name][setting_name]

        for stage_name, method_name, setting_name in problems_dict[
                'invalid_settings']:
            if stage_name != 'auxiliary':
                del strategy.settings[stage_name][setting_name]
            else:
                del strategy.auxiliary_stages[method_name][setting_name]
            problems_dict['missing_settings'].append(
                    (stage_name, method_name, setting_name))

        for stage_name, method_name, setting_name in problems_dict[
                'missing_settings']:
            plugin = plugin_manager.find_plugin(stage_name, method_name)
            default_settings = plugin.get_parameter_defaults()
            if stage_name != 'auxiliary':
                strategy.settings[stage_name][setting_name] =\
                        default_settings[setting_name]
            else:
                strategy.auxiliary_stages[method_name][setting_name] =\
                        default_settings[setting_name]
        #TODO change name?
        return strategy


    # --- ADD AND REMOVE STRATEGIES ---
    @supports_callbacks 
    def add_strategy(self, strategy, name=None):
        strategy = strategy.copy() 
        if name is not None:
            strategy.name = name
            
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
        return strategy

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
        try:
            return self.strategies[strategy_name]
        except KeyError:
            raise MissingStrategyError(
                    'No strategy named "%s" under management.' % strategy_name)

    def get_strategy(self, strategy):
        if isinstance(strategy, types.StringTypes):
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




    

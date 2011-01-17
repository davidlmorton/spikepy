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


def make_methods_used_name(strategy_name):
    '''
    From a full strategy-name return just the method-used-name
    '''
    return strategy_name.split('(')[0].lower()


def make_settings_name(strategy_name):
    '''
    From a full strategy-name return just the settings-name
    '''
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
        

class Strategy(object):
    def __init__(self, methods_used=None, methods_used_name="None", 
                       settings=None, settings_name="None"):
        self.methods_used = methods_used
        self.methods_used_name = methods_used_name
        self.settings = settings
        self.settings_name = settings_name

    @property
    def name(self):
        return make_strategy_name(self.methods_used_name,
                                  self.settings_name)

    @name.setter
    def name(self, value):
        self.methods_used_name = make_methods_used_name(value)
        self.settings_name = make_settings_name(value)

    @property
    def methods_used(self):
        return self._methods_used
    
    @methods_used.setter
    def methods_used(self, value):
        self._methods_used = value

    @property
    def methods_used_name(self):
        return self._methods_used_name.lower()

    @methods_used_name.setter
    def methods_used_name(self, value):
        self._methods_used_name = value

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, value):
        self._settings = value

    @property
    def settings_name(self):
        return self._settings_name.lower()

    @settings_name.setter
    def settings_name(self, value):
        self._settings_name = value

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
    def as_dict(self):
        return {'name':self.name, 'methods_used':self.methods_used,
                'settings':self.settings}

    def save(self, fullpath):
        with open(fullpath, 'w') as ofile:
            json.dump(self.as_dict(), ofile, indent=4)

    def load(self, fullpath):
        with open(fullpath, 'r') as infile:
            strategy_dict = json.load(infile)
        self.methods_used = strategy_dict['methods_used']
        self.settings     = strategy_dict['settings']
        self.name         = strategy_dict['name']

    @classmethod
    def from_file(cls, fullpath):
        return_strategy = cls()
        return_strategy.load(fullpath)
        return return_strategy

    def copy(self):
        return copy.deepcopy(self)



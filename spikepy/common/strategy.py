
import copy

import json
from spikepy.common import program_text as pt
from spikepy.common.stages import stages

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

        # ensure methods sets are different (less likely)
        if self.auxiliary_stages != other.auxiliary_stages:
            return True

        return False # least likely of all

    # --- ARCHIVING METHODS ---
    @property
    def as_dict(self):
        return {'name':self.name, 'methods_used':self.methods_used,
                'settings':self.settings, 
                'auxiliary_stages':self.auxiliary_stages}

    def save(self, fullpath):
        with open(fullpath, 'w') as ofile:
            json.dump(self.as_dict, ofile, indent=4)

    def load(self, fullpath):
        with open(fullpath, 'r') as infile:
            strategy_dict = json.load(infile)
        self.update(strategy_dict)
        self.fullpath     = fullpath

    def update(self, strategy_dict):
        self.methods_used = strategy_dict['methods_used']
        self.settings     = strategy_dict['settings']
        self.name         = strategy_dict['name']
        self.auxiliary_stages = strategy_dict['auxiliary_stages']

    @classmethod
    def from_dict(cls, strategy_dict):
        return_strategy = cls()
        return_strategy.update(strategy_dict)
        return return_strategy

    @classmethod
    def from_file(cls, fullpath):
        return_strategy = cls()
        return_strategy.load(fullpath)
        return return_strategy

    def copy(self):
        return copy.deepcopy(self)



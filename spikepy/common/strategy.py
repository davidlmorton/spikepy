import json

from . import program_text as pt


def make_methods_used_name(strategy_name):
    '''
    From a full strategy-name return just the method-used-name
    '''
    return strategy_name.split('(')[0]


def make_settings_name(strategy_name):
    '''
    From a full strategy-name return just the settings-name
    '''
    return strategy_name.split('(')[1][:-1]


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



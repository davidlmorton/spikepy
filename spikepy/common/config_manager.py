import os

import wx
import configobj
from validate import Validator

from spikepy.common import path_utils
from spikepy.common import config_utils

class ConfigManager(object):
    def __init__(self):
        self._builtin = None
        self._application = None
        self._user = None
        self._current = configobj.ConfigObj()

    def load_configs(self):
        self.load_builtin_config()
        self.load_application_config()
        self.load_user_config()

    def load_user_config(self):
        self._user = config_utils.load_config('user')
        config_utils.noneless_merge(self._current, self._user)

    def load_application_config(self):
        self._application = config_utils.load_config('application')
        config_utils.noneless_merge(self._current, self._application)

    def load_builtin_config(self):
        self._builtin = config_utils.load_config('builtins')
        config_utils.noneless_merge(self._current, self._builtin)
    
    @property
    def current(self):
        return self._current

config_manager = ConfigManager()



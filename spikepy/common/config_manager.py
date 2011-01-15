import os
import copy

import wx
import numpy
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
        self._status_markers = None

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

    def __getitem__(self, key):
        return self._current[key]

    def get_size(self, name):
        if name == 'main_frame':
            screen_height = wx.GetDisplaySize()[1]
            height = screen_height*self['gui']['main_frame']['fill_ratio']
            width  = height*self['gui']['main_frame']['aspect_ratio']
            return numpy.array([width, height])
        elif name == 'pyshell':
            size_ratio = self['gui']['menu_bar']['pyshell_size_ratio']
            return self.get_size('main_frame')*size_ratio
                   

    @property
    def unmarked_status(self):
        if self._status_markers is None:
            self._status_markers = self.get_status_markers()
        return self._status_markers[0]

    @property
    def marked_status(self):
        if self._status_markers is None:
            self._status_markers = self.get_status_markers()
        return self._status_markers[1]

    def get_status_markers(self):
        if path_utils.platform == 'mac':
            unmarked = self._current['gui']['trial_list']['unmarked_status_mac']
            marked = self._current['gui']['trial_list']['marked_status_mac']
        else:
            unmarked = self._current['gui']['trial_list']['unmarked_status']
            marked = self._current['gui']['trial_list']['marked_status']
        return (unichr(unmarked), unichr(marked))
    
    @property
    def current(self):
        return copy.copy(self._current)

config_manager = ConfigManager()



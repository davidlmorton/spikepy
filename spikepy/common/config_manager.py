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
        self._control_border = None

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
        elif name == 'results_frame':
            mfs = self.get_size('main_frame')
            height = mfs[1]-230 # pixels in menu and such.
            width = mfs[0]-self['gui']['strategy_pane']['min_width']-20
            return numpy.array([width, height])       
        elif name == 'figure':
            base = self.get_size('results_frame')/self['gui']['plotting']['dpi']
            width = base[0]
            height = width/self['gui']['plotting']['aspect_ratio']
            return numpy.array([width, height])

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
        if path_utils.platform() == 'mac':
            unmarked = self._current['gui']['trial_list']['unmarked_status_mac']
            marked = self._current['gui']['trial_list']['marked_status_mac']
        else:
            unmarked = self._current['gui']['trial_list']['unmarked_status']
            marked = self._current['gui']['trial_list']['marked_status']
        return (unichr(unmarked), unichr(marked))

    @property
    def control_border(self):
        if self._control_border is None:
            self._control_border = self.get_control_border()
        return self._control_border

    def get_control_border(self):
        if path_utils.platform() == 'mac':
            cb = self['gui']['strategy_pane']['control_border_mac']
        else:
            cb = self['gui']['strategy_pane']['control_border']
        return cb
    
    @property
    def current(self):
        return copy.copy(self._current)

    def default_adjust_subplots(self, figure, canvas_size_in_pixels):
        '''
        Adjust the figure's subplot parameters according to the settings
        in this config_manager
        '''
        psconfig = self['gui']['plotting']['spacing']
        left   = psconfig['left_border'] / canvas_size_in_pixels[0]
        right  = 1.0 - psconfig['right_border'] / canvas_size_in_pixels[0]
        top    = 1.0 - psconfig['top_border'] / canvas_size_in_pixels[1]
        bottom = psconfig['bottom_border'] / canvas_size_in_pixels[1]
        figure.subplots_adjust(hspace=0.03, wspace=0.03, 
                               left=left, right=right, 
                               bottom=bottom, top=top)

    def get_color_from_cycle(self, num):
        cycle = self['gui']['plotting']['clustering']['color_cycle']
        len_color_cycle = len(cycle)
        return cycle[num % len_color_cycle]
        

config_manager = ConfigManager()



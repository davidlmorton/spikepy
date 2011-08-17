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
import copy

import wx
from wx.lib.pubsub import Publisher as pub
import numpy
import configobj

from spikepy.common import path_utils
from spikepy.common import config_utils

def rgb_int_to_float(*args):
    return [arg/255.0 for arg in args]

class ConfigManager(object):
    def __init__(self):
        self._builtin = None
        self._application = None
        self._user = None
        self._current = configobj.ConfigObj()
        self._status_markers = None
        self._control_border = None
        self._results_frame_size = numpy.array([800, 600])
        pub.subscribe(self._set_results_frame_size, "SET_RESULTS_FRAME_SIZE")
        self.load_configs(app_name='spikepy')

    def load_configs(self, **kwargs):
        self.load_builtin_config(**kwargs)
        self.load_application_config(**kwargs)
        self.load_user_config(**kwargs)

    def load_user_config(self, **kwargs):
        self._user = config_utils.load_config('user', **kwargs)
        config_utils.noneless_merge(self._current, self._user)

    def load_application_config(self, **kwargs):
        self._application = config_utils.load_config('application', **kwargs)
        config_utils.noneless_merge(self._current, self._application)

    def load_builtin_config(self, **kwargs):
        self._builtin = config_utils.load_config('builtins', **kwargs)
        config_utils.noneless_merge(self._current, self._builtin)

    def __getitem__(self, key):
        return self._current[key]

    def _set_results_frame_size(self, message):
        size = numpy.array(message.data)
        if size[0] != 0 and size[1] != 0:
            self._results_frame_size = size

    @property
    def results_frame_size(self):
        return self._results_frame_size

    def get_size(self, name):
        if name == 'main_frame':
            height = self['gui']['main_frame']['height']
            width  = height*self['gui']['main_frame']['aspect_ratio']
            return numpy.array([width, height])
        elif name == 'pyshell':
            size_ratio = self['gui']['menu_bar']['pyshell_size_ratio']
            return self.get_size('main_frame')*size_ratio
        elif name == 'figure':
            rfs = copy.copy(self.results_frame_size)
            rfs[0] -= 25 # compensate for scroll bar
            rfs[1] -= 60 # compensate for tabs.
            base = rfs/self['gui']['plotting']['dpi']
            width = base[0]
            height = base[1]/2.0
            return numpy.array([width, height])

    # --- COLORS ---
    @property
    def red(self):
        return self.get_color('red')

    @property
    def blue(self):
        return self.get_color('blue')

    @property
    def orange(self):
        return self.get_color('orange')

    @property
    def green(self):
        return self.get_color('green')

    @property
    def brown(self):
        return self.get_color('brown')

    @property
    def lime(self):
        return self.get_color('lime')

    @property
    def pink(self):
        return self.get_color('pink')

    @property
    def purple(self):
        return self.get_color('purple')

    @property
    def detection_color(self):
        return self.get_color(self['gui']['plotting']['colors']['detection'])

    @property
    def extraction_color(self):
        return self.get_color(self['gui']['plotting']['colors']['extraction'])

    @property
    def pca_colors(self):
        color_list = self['gui']['plotting']['colors']['pca']
        return [self.get_color(color) for color in color_list]

    def get_color(self, color):
        return rgb_int_to_float(*self['gui']['plotting']['colors'][color])

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
        unmarked = '0'
        marked = '1' 
        return (unmarked, marked)

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
        figure.subplots_adjust(hspace=0.00, wspace=0.00, 
                               left=left, right=right, 
                               bottom=bottom, top=top)


    def get_color_from_cycle(self, num):
        cycle = self['gui']['plotting']['colors']['cycle']
        len_color_cycle = len(cycle)
        return self.get_color(cycle[num % len_color_cycle])
        

config_manager = ConfigManager()



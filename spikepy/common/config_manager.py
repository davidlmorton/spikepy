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

import copy
import os

import wx
import numpy
import configobj
from validate import Validator

from spikepy.common import path_utils
from spikepy.common.errors import *

def rgb_int_to_float(*args):
    '''Return the normalized rgb representation of integer rgb values.'''
    return [arg/255.0 for arg in args]

def get_default_configspec(**kwargs):
    '''Return the fullpath to the default configspec.'''
    data_dirs = path_utils.get_data_dirs(**kwargs)
    default_config_dir = data_dirs['builtins']['configuration']
    return os.path.join(default_config_dir, 'spikepy.configspec')

def load_config(level, **kwargs):
    '''Return the configuration if it passes validation.'''
    data_dirs = path_utils.get_data_dirs(**kwargs)
    config_dir = data_dirs[level]['configuration']
    fullpath = os.path.join(config_dir, 'spikepy.ini')
    config = configobj.ConfigObj(fullpath, 
                                 configspec=get_default_configspec(**kwargs))
    validator = Validator()
    result = config.validate(validator, preserve_errors=True)
    if result == True:
        return config
    else:
        raise ConfigError("Reading in configuration file at %s has failed!\nFailure status: %s" % (fullpath, configobj.flatten_errors(config, result)))

def noneless_merge(config1, config2):
    '''
        Merge config2 into config1 ignoring values that are None.  That is, 
    config2's values, if present and not None will overwrite the values 
    of config1.
    '''
    for key, value in config2.items():
        if (key in config1 and isinstance(config1[key], dict) and
            isinstance(value, dict)):
            noneless_merge(config1[key], value)
        elif value is not None:
            config1[key] = value

class ConfigManager(object):
    '''
        ConfigManager contains the configuration as well as the methods needed
    to load configuration options from config files.

        ConfigManager objects can be indexed just like dictionaries where the
    keys are the names of configuration options.
    '''
    def __init__(self):
        self._builtin = None
        self._application = None
        self._user = None
        self._current = configobj.ConfigObj()
        self._status_markers = None
        self._results_frame_size = numpy.array([800, 600])
        self.load_configs(app_name='spikepy')

    def load_configs(self, **kwargs):
        '''
            Load the configuration files for the three levels of plugin:
        builtin, application and user.
        **kwargs passed on to the load_config function.
        '''
        for level in ['builtins', 'application', 'user']:
            loaded_config = load_config(level, **kwargs)
            setattr(self, '_%s' % level, loaded_config)
            noneless_merge(self._current, loaded_config)


    def __getitem__(self, key):
        return self._current[key]

    def _set_results_frame_size(self, message):
        size = numpy.array(message.data)
        if size[0] != 0 and size[1] != 0:
            self._results_frame_size = size

    @property
    def results_frame_size(self):
        return self._results_frame_size

    def get_num_workers(self):
        '''
            Return the number of worker processes to spawn.  Number is
        determined based on cpu_count and the configuration variable:
        ['backend']['limit_num_processes']
        '''
        try:
            import multiprocessing
            num_process_workers = multiprocessing.cpu_count()
        except NotImplementedError:
            num_process_workers = 8

        processes_limit = self['backend']['limit_num_processes']
        num_process_workers = min(num_process_workers, processes_limit)
        return num_process_workers

    def get_size(self, name):
        if name == 'main_frame':
            height = self['gui']['main_frame']['height']
            width  = height*self['gui']['main_frame']['aspect_ratio']
            return numpy.array([width, height])
        elif name == 'pyshell':
            size_ratio = self['gui']['menu_bar']['pyshell_size_ratio']
            return self.get_size('main_frame')*size_ratio
        elif name == 'figure':
            width = self['gui']['plotting']['plot_width_inches']
            height = self['gui']['plotting']['plot_height_inches']
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



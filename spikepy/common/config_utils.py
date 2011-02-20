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

import wx
import configobj
from validate import Validator

from spikepy.common import path_utils
    
def get_default_configspec(**kwargs):
    '''
    Returns the fullpath to the default configspec
    '''
    data_dirs = path_utils.get_data_dirs(**kwargs)
    default_config_dir = data_dirs['builtins']['configuration']
    return os.path.join(default_config_dir, 'spikepy.configspec')

def load_config(level, **kwargs):
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
        raise RuntimeError("Reading in configuration file at %s has failed!\nFailure status: %s" % (fullpath, configobj.flatten_errors(config, result)))

def noneless_merge(config1, config2):
    '''
    merges config2 into config1 ignoring values 
    that are None.
    That is, config2's values, if present and not None will overwrite 
    the values of config1.
    '''
    for key, value in config2.items():
        if (key in config1 and isinstance(config1[key], dict) and
            isinstance(value, dict)):
            noneless_merge(config1[key], value)
        elif value is not None:
            config1[key] = value

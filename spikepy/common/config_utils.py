import os

import wx
import configobj
from validate import Validator

from spikepy.common import path_utils
    
def get_default_configspec():
    '''
    Returns the fullpath to the default configspec
    '''
    data_dirs = path_utils.get_data_dirs()
    default_config_dir = data_dirs['builtins']['configuration']
    return os.path.join(default_config_dir, 'spikepy.configspec')

def load_config(level):
    data_dirs = path_utils.get_data_dirs()
    config_dir = data_dirs[level]['configuration']
    fullpath = os.path.join(config_dir, 'spikepy.ini')
    config = configobj.ConfigObj(fullpath, configspec=get_default_configspec())
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

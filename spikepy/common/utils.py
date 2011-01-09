import traceback
import csv
import sys
import os
import imp
import uuid
from collections import defaultdict

import wx
import numpy
from numpy.linalg import svd
from scipy.signal import resample


def platform():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    return 'linux'

def is_package():
    return not sys.argv[0].endswith('.py')

def get_python_setup():
    if hasattr(sys, 'frozen'):
        return 'frozen'
    elif is_package():
        return 'package'
    return 'source'

def get_base_path():
    path = __file__
    common_path = os.path.split(path)[0]
    return os.path.split(common_path)[0]

def should_load(entry):
    if entry.startswith('.'):
        return False
    if entry.endswith('.py'):
        return True
    if os.path.isdir(entry):
        module_init = os.path.join(entry,'__init__.py')
        return os.path.exists(module_init)
    return False

def load_plugins(plugin_dir):
    loaded_modules = {}
    if os.path.exists(plugin_dir):
        entries = os.listdir(plugin_dir)
        for e in entries:
            fullpath_e = os.path.join(plugin_dir, e)
            if should_load(fullpath_e):
                unique_name = 'spikepy_' + (str(uuid.uuid4())).replace('-','_') 
                module_name = os.path.splitext(e)[0]
                fm_results = None
                try:
                    fm_results = imp.find_module(module_name, [plugin_dir]) 
                except ImportError:
                    pass
                if fm_results is not None:
                    loaded_modules[module_name]=imp.load_module(unique_name,
                                                                *fm_results)
                    loaded_modules[module_name+'_name'] = unique_name
    return loaded_modules

def load_all_plugins(data_dirs=None, **kwargs):
    if data_dirs is None:
        data_dirs = get_data_dirs(**kwargs)

    loaded_modules = defaultdict(dict)
    for level in data_dirs.keys():
        for plugin_type in ['file_interpreters', 'methods']:
            plugin_dir = data_dirs[level][plugin_type]
            loaded_modules[level][plugin_type] = load_plugins(plugin_dir)

    return loaded_modules

def get_data_dirs(app_name=None):
    '''
    This function returns the proper directory for storing application data.
    If a wx.App() is running, it pulls info from it to determine the
        proper directory for storing application data.
    If a wx.App() is not runnining, it creates one temporarily.
    '''
    file_interpreters_dir = 'file_interpreters'
    methods_dir = 'methods'
    strategies_dir = 'strategies'
    # see if an App() instance is running.
    app = wx.GetApp()
    # creat an App() instance if we don't already have one.
    created_app = False
    if app is None:
        app = wx.App()
        created_app = True

    old_app_name = app.GetAppName()
    if app_name is None:
        if created_app:
            app.SetAppName('DEFAULT_APP_NAME')
    else:
        app.SetAppName(app_name)
        
    sp = wx.StandardPaths.Get()
    data_dir = sp.GetDataDir()
    user_data_dir = sp.GetUserDataDir()
    builtins_data_dir = os.path.join(get_base_path(), 'builtins')

    data_dirs = {}
    for base_name, base_dir in [('application', data_dir), 
                                ('builtins', builtins_data_dir),
                                ('user', user_data_dir)]:
        data_dirs[base_name] = {}
        data_dirs[base_name]['configuration'] = base_dir
        data_dirs[base_name]['strategies'] = os.path.join(base_dir,
                                                        strategies_dir)
        data_dirs[base_name]['file_interpreters'] = os.path.join(base_dir, 
                                                    file_interpreters_dir)
        data_dirs[base_name]['methods'] = os.path.join(base_dir, 
                                                    methods_dir)

    # return app to former name
    app.SetAppName(old_app_name)
    if created_app:
        app.Destroy()

    return data_dirs

def pool_process(pool, function, args=tuple(), kwargs=dict()):
    if pool is not None:
        try:
            pool_result = pool.apply_async(function, args=args, kwds=kwargs)
            result = pool_result.get()
        except:
            traceback.print_exc()
            sys.exit(1)
    else:
        result = function(*args, **kwargs)
    return result

def upsample_trace_list(trace_list, prev_sample_rate, desired_sample_rate):
    '''
    Upsample voltage traces.
    Inputs:
        trace_list          : a list of voltage traces
        prev_sample_rate    : the sample rate in hz of the traces to be 
                              upsampled
        desired_sample_rate : the target sample rate of the traces
    Returns:
        a list of resampled traces
    '''
    rate_factor = desired_sample_rate/float(prev_sample_rate)
    return [resample(trace, len(trace)*rate_factor)
            for trace in trace_list]

def save_list_txt(filename, array_list, delimiter=' '):
    '''
    Save a list of 1D arrays (of potentially varying lengths) as a single text
    file.
    Inputs:
        array_list      : a list of 1D arrays of any length.
    Returns:
        None
    '''
    with open(filename, 'w') as ofile:
        writer = csv.writer(ofile, delimiter=delimiter)
        for array in array_list:
            writer.writerow(array)

def pca(P):
    """
    Use singular value decomposition to determine the optimal
    rotation of the basis to view data from.

    Input:
    P          : an m x n array of input data
                (m trials, n measurements)
                (m rows  , n columns)

    Return value are
    signals     : rotated view of the data.
    pc          : each row is a principal component
    var         : the variance associated with each pc
                   this is the bias corrected variance using 
                   m-1 instead of m.
    """
    # first we need to zero mean the data
    m,n = P.shape
    column_means = sum(P,0) / m
    zmP = P - column_means

    # generate the Y vector we will decompose
    Y = zmP / numpy.sqrt(m-1)

    # do the singular value decomposition
    u,s,pc = svd(Y)
    # find the variance along each principal axis
    var = s**2

    # The transformed data
    signals = numpy.dot(pc,P.T).T

    return signals, pc, var


import traceback
import csv
import sys
import os
import imp

import wx
import numpy
from numpy.linalg import svd
from scipy.signal import resample

def load_plugins(name, base_path):
    loaded_modules = []
    if os.path.exists(base_path):
        name_base = os.path.join(base_path, name)
        if os.path.exists(name_base):
            files = os.listdir(name_base)
            for f in files:
                if f.endswith('.py'):
                    full_path = os.path.join(name_base, f)
                    loaded_modules.append(imp.load_source(name, full_path))
    return loaded_modules

def load_app_and_user_plugins(**kwargs):
    application_data_dir, user_data_dir = get_data_dirs(**kwargs)
    application_file_interpreters = load_plugins('file_interpreters', 
                                                 application_data_dir)
    application_methods = load_plugins('methods', application_data_dir)

    user_file_interpreters = load_plugins('file_interpreters', user_data_dir)
    user_methods = load_plugins('methods', user_data_dir)
    return (application_file_interpreters, application_methods, 
            user_file_interpreters, user_methods)

def get_data_dirs(app_name=None):
    '''
    This function returns the proper directory for storing application data.
    If a wx.App() is running, it pulls info from it to determine the
        proper directory for storing application data.
    If a wx.App() is not runnining, it creates one temporarily.
    '''
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

    # return app to former name
    app.SetAppName(old_app_name)
    if created_app:
        app.Destroy()

    return data_dir, user_data_dir

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


import os
import sys

import wx

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

def setup_user_directories():
    data_dirs = get_data_dirs()
    for directory in data_dirs['user'].values():
        if not os.path.exists(directory):
            os.makedirs(directory)



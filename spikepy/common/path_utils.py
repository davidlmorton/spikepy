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
import sys

import wx

def platform():
    '''Return the platform 'windows/mac/linux' currently running.'''
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    return 'linux'

def get_base_path():
    '''Return the path to the spikepy source directory.'''
    path = __file__
    common_path = os.path.split(path)[0]
    return os.path.split(common_path)[0]

def get_data_dirs(app_name=None):
    '''
        Return the proper directory for storing spikepy data/plugins.
    If a wx.App() is running, it pulls info from it to determine the
    proper directory for storing application data. If a wx.App() is not 
    runnining, it creates one temporarily.
    '''
    file_interpreters_dir = 'file_interpreters'
    data_interpreters_dir = 'data_interpreters'
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
        data_dirs[base_name]['data_interpreters'] = os.path.join(base_dir,
                                                    data_interpreters_dir)
        data_dirs[base_name]['methods'] = os.path.join(base_dir, 
                                                    methods_dir)

    # return app to former name
    app.SetAppName(old_app_name)
    if created_app:
        app.Destroy()

    return data_dirs

def setup_user_directories(**kwargs):
    '''Create (if necessary) the spikepy user directories'''
    data_dirs = get_data_dirs(**kwargs)
    for directory in data_dirs['user'].values():
        if not os.path.exists(directory):
            os.makedirs(directory)



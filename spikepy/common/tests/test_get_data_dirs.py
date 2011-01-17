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

import unittest
import os
import pwd

import wx

from spikepy.common.utils import get_data_dirs

def get_username():
    return pwd.getpwuid(os.getuid())[0]

def destroy_app():
    # get rid of app if one exists.
    app = wx.GetApp()
    while app is not None:
        app.Destroy()
        app = wx.GetApp()


class GetLocalDataDir(unittest.TestCase):
    def data_dirs_correct_structure(self, data_dirs):
        data_dirs_keys = data_dirs.keys()
        for level in ['application', 'user', 'builtins']:
            print level, data_dirs_keys
            self.assertTrue(level in data_dirs_keys)
        for value in data_dirs.values():
            value_keys = value.keys()
            for kind in ['configuration', 'file_interpreters', 'methods', 
                         'strategies']:
                self.assertTrue(kind in value_keys)
        
    def test_no_app_no_name(self):
        destroy_app()

        data_dirs = get_data_dirs()
        self.data_dirs_correct_structure(data_dirs)
        self.assertTrue(wx.GetApp()==None)

    def test_no_app_w_name(self):
        destroy_app()
        name = 'tnawn'

        data_dirs = get_data_dirs(app_name=name)
        self.data_dirs_correct_structure(data_dirs)
        self.assertTrue(wx.GetApp()==None)

    def test_w_app_no_name(self):
        destroy_app()
        external_name = 'external'
        app = wx.App()
        app.SetAppName(external_name)

        data_dirs = get_data_dirs()
        self.data_dirs_correct_structure(data_dirs)
        self.assertFalse(wx.GetApp()==None)
        if app is not None:
            self.assertTrue(app.GetAppName()==external_name)

    def test_w_app_w_name(self):
        internal_name = 'internal'
        external_name = 'external'
        destroy_app()
        app = wx.App()
        app.SetAppName(external_name)

        data_dirs = get_data_dirs()
        self.data_dirs_correct_structure(data_dirs)
        self.assertFalse(wx.GetApp()==None)

        app = wx.GetApp()
        self.assertFalse(app==None)
        if app is not None:
            self.assertTrue(app.GetAppName()==external_name)

if __name__ == '__main__':
    unittest.main()

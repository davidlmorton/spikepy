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
        for level in ['application', 'user']:
            self.assertTrue(level in data_dirs_keys)
        self.assertTrue(data_dirs.keys()==['application', 'user'])
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

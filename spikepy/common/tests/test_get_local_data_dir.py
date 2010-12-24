import unittest
import os
import pwd

import wx

from spikepy.common.utils import get_local_data_dir

def get_username():
    return pwd.getpwuid(os.getuid())[0]

def destroy_app():
    # get rid of app if one exists.
    app = wx.GetApp()
    while app is not None:
        app.Destroy()
        app = wx.GetApp()

class GetLocalDataDir(unittest.TestCase):
    def test_no_app_no_name(self):
        if wx.Platform == '__WXGTK__':
            destroy_app()

            ldd = get_local_data_dir()
            self.assertTrue(ldd=='/home/%s/.DEFAULT_APP_NAME' % get_username())
            self.assertTrue(wx.GetApp()==None)

    def test_no_app_w_name(self):
        if wx.Platform == '__WXGTK__':
            name = 'tnawn'
            destroy_app()

            ldd = get_local_data_dir(app_name=name)
            self.assertTrue(ldd=='/home/%s/.%s' % (get_username(),name))
            self.assertTrue(wx.GetApp()==None)

    def test_w_app_no_name(self):
        if wx.Platform == '__WXGTK__':
            name = 'tano'
            destroy_app()
            app = wx.App()
            app.SetAppName(name)

            ldd = get_local_data_dir()
            self.assertTrue(ldd=='/home/%s/.%s' % (get_username(),name))
            self.assertFalse(wx.GetApp()==None)

    def test_w_app_w_name(self):
        if wx.Platform == '__WXGTK__':
            internal_name = 'internal'
            external_name = 'external'
            destroy_app()
            app = wx.App()
            app.SetAppName(external_name)

            ldd = get_local_data_dir(app_name=internal_name)
            self.assertTrue(ldd=='/home/%s/.%s' % 
                            (get_username(),internal_name))
            app = wx.GetApp()
            self.assertFalse(app==None)
            if app is not None:
                self.assertTrue(app.GetAppName()==external_name)

if __name__ == '__main__':
    unittest.main()

#! /usr/bin/python
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

import wx
from spikepy.gui.images import spikepy_splash_image as spi
import matplotlib
# breaks pep-8 to put code here, but matplotlib 
#     requires this before importing wxagg backend
matplotlib.use('WXAgg', warn=False) 

from spikepy.common import plugin_utils
from spikepy.common import path_utils
from spikepy.common.config_manager import config_manager

class MySplashScreen(wx.SplashScreen):
    def __init__(self, image=None, splash_style=None, timeout=None, 
                       parent=None, **kwargs):
        wx.SplashScreen.__init__(self, image, splash_style, timeout, 
                                 parent, **kwargs)

path_utils.setup_user_directories(app_name='spikepy')
plugin_utils.load_all_plugins(app_name='spikepy')

if __name__ == '__main__':
    def startup():
        ''' Run after splash screen has loaded '''
        from spikepy.gui.controller import Controller
        controller = Controller()
        wx.CallLater(1000, splash_screen.Destroy)
        wx.CallLater(2100, controller.warn_for_matplotlib_version)

    app = wx.App(redirect=False)
    app.SetAppName("spikepy")

    image = spi.spikepy_splash.Image.ConvertToBitmap()
    splash_screen = MySplashScreen(image=image, 
                                   splash_style=wx.SPLASH_CENTRE_ON_SCREEN, 
                                   timeout=1000, 
                                   parent=None)
    wx.CallLater(200, startup)
    app.MainLoop()

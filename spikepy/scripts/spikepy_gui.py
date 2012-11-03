#! /usr/bin/python

# PARSE COMMAND LINE ARGUMENTS
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Graphical interface for the spikepy spike-sorting package.")

    parser.add_argument('-p', '--print_messages', dest='print_messages', 
            action='store_true',
            help='print out all pub/sub messages')
    command_line_arguments = vars(parser.parse_args())
    print_messages = command_line_arguments['print_messages']

# create a spikepy session
from spikepy.session import Session
session = Session()

if __name__ == '__main__':
    import wx
    from spikepy.common.path_utils import get_image_path
    class MySplashScreen(wx.SplashScreen):
        def __init__(self, image=None, splash_style=None, timeout=None, 
                           parent=None, **kwargs):
            wx.SplashScreen.__init__(self, image, splash_style, timeout, 
                                     parent, **kwargs)

    def startup():
        ''' Run after splash screen has loaded '''
        from spikepy.gui.controller import Controller
        controller = Controller(session, print_messages=print_messages)
        wx.CallLater(1000, splash_screen.Destroy)

    app = wx.App(redirect=False)
    app.SetAppName("spikepy")

    image = wx.Image(get_image_path('spikepy_splash.png'), 
            wx.BITMAP_TYPE_PNG).ConvertToBitmap()
    splash_screen = MySplashScreen(image=image, 
                                   splash_style=wx.SPLASH_CENTRE_ON_SCREEN, 
                                   timeout=1000, 
                                   parent=None)
    wx.CallLater(200, startup)
    app.MainLoop()


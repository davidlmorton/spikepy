import wx

class MySplashScreen(wx.SplashScreen):
    def __init__(self, image=None, splash_style=None, timeout=None, 
                       parent=None, **kwargs):
        wx.SplashScreen.__init__(self, image, splash_style, timeout, 
                                 parent, **kwargs)

if __name__ == '__main__':
    def startup():
        from spikepy.gui.controller import Controller
        controller = Controller()
        controller.setup_subscriptions()
        splash_screen.Destroy()
    from spikepy.gui.utils import get_bitmap_icon

    app = wx.App()
    splash_screen = MySplashScreen(image=get_bitmap_icon('spikepy_splash'), 
                                   splash_style=wx.SPLASH_CENTRE_ON_SCREEN, 
                                   timeout=1000, 
                                   parent=None)
    wx.CallLater(200, startup)
    app.MainLoop()

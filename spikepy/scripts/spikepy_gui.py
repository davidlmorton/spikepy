import wx
from spikepy.gui.images import spikepy_splash_image as spi

class MySplashScreen(wx.SplashScreen):
    def __init__(self, image=None, splash_style=None, timeout=None, 
                       parent=None, **kwargs):
        wx.SplashScreen.__init__(self, image, splash_style, timeout, 
                                 parent, **kwargs)

if __name__ == '__main__':
    def startup():
        ''' Run after splash screen has loaded '''
        from spikepy.gui.controller import Controller
        controller = Controller()
        wx.CallLater(1000, splash_screen.Destroy)

    app = wx.App(redirect=False)
    app.SetAppName("spikepy")

    image = spi.spikepy_splash.Image.ConvertToBitmap()
    splash_screen = MySplashScreen(image=image, 
                                   splash_style=wx.SPLASH_CENTRE_ON_SCREEN, 
                                   timeout=1000, 
                                   parent=None)
    wx.CallLater(200, startup)
    app.MainLoop()

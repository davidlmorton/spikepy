import wx


if __name__ == '__main__':
    from spikepy.gui.utils import get_bitmap_icon 
    app = wx.App()

    splash_image = get_bitmap_icon('spikepy_splash')
    splash_screen = wx.SplashScreen(splash_image, 
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_NO_TIMEOUT, 0, None)
    wx.Yield()

    from spikepy.gui.controller import Controller
    controller = Controller()
    controller.setup_subscriptions()
    splash_screen.Destroy()

    app.MainLoop()

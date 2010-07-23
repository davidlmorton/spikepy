import wx


if __name__ == '__main__':
    app = wx.App()
    from spikepy.gui.utils import get_bitmap_icon 
    splash_screen = wx.SplashScreen(get_bitmap_icon('spikepy_splash'), 
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_NO_TIMEOUT, 8000, None)
    from spikepy.gui.controller import Controller

    controller = Controller()
    controller.setup_subscriptions()
    splash_screen.Destroy()

    app.MainLoop()

import wx
from spikepy.gui.controller import Controller

if __name__ == '__main__':
    app = wx.App()

    controller = Controller()
    controller.setup_subscriptions()

    app.MainLoop()

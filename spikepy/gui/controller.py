import os 

import wx
from wx.lib.pubsub import Publisher as pub

from ..common.model import Model
from .view import View

class Controller(object):
    def __init__(self):
        self.model = Model()
        self.model.setup_subscriptions()
        self.view = View()

    def setup_subscriptions(self):
        pub.subscribe(self._open_file, topic="OPEN FILE")

    def _open_file(self, message):
        frame = message.data

        paths = []
        dlg = wx.FileDialog(frame, message="Choose file(s) to open.",
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()
        for path in paths:
            pub.sendMessage(topic="OPEN DATA FILE", data=path)


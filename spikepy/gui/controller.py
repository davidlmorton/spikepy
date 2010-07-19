import os 

import wx
from wx.lib.pubsub import Publisher as pub

from ..common.model import Model
from .view import View
from .utils import named_color
from . import program_text as pt
from .pyshell import locals_dict

class Controller(object):
    def __init__(self):
        self.model = Model()
        self.model.setup_subscriptions()
        self.view = View()

        # save for locals in pyshell
        locals_dict['model']      = self.model
        locals_dict['view']       = self.view
        locals_dict['controller'] = self


    def setup_subscriptions(self):
        pub.subscribe(self._open_file, topic="OPEN_FILE")
        pub.subscribe(self._file_selection_changed, 
                      topic='FILE_SELECTION_CHANGED')
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._print_messages, topic='')

    def _print_messages(self, message):
        topic = message.topic
        print topic

    def _file_closed(self, message):
        fullpath = message.data
        pub.sendMessage(topic='REMOVE_PLOT', data=fullpath)


    def _file_selection_changed(self, message):
        # XXX will this do something more?
        fullpath = message.data
        pub.sendMessage(topic='SHOW_PLOT', data=fullpath)

    def _open_file(self, message):
        frame = message.data

        paths = []
        dlg = wx.FileDialog(frame, message=pt.OPEN_FILE_DLG_MESSAGE,
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()
        for path in paths:
            pub.sendMessage(topic='OPENING_DATA_FILE', data=path)
            pub.sendMessage(topic='OPEN_DATA_FILE', data=path)




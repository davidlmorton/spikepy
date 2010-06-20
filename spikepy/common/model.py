import thread

import wx
from wx.lib.pubsub import Publisher as pub

from .open_data_file import open_data_file
from ..filtering.simple_iir import butterworth, bessel
from ..filtering.simple_fir import fir_filter

class Model(object):
    def __init__(self):
        self.trials = {}

    def setup_subscriptions(self):
        pub.subscribe(self._open_data_file, "OPEN DATA FILE")
        pub.subscribe(self._close_data_file, "CLOSE DATA FILE")

    def _open_data_file(self, message):
        fullpath = message.data
        if fullpath not in self.trials.keys():
            thread.start_new_thread(self.open_file, (fullpath,))
        else:
            pub.sendMessage(topic='FILE ALREADY OPENED',data=fullpath)

    def open_file(self, fullpath):
        self.trials[fullpath] = open_data_file(fullpath)
        # call sendMessage after thread exits. (Publisher is NOT threadsafe)
        wx.CallAfter(pub.sendMessage, topic='TRIAL ADDED', 
                     data=self.trials[fullpath])
        wx.CallAfter(pub.sendMessage, topic='FILE OPENED', data=fullpath)

    def _close_data_file(self, message):
        fullpath = message.data
        if fullpath in self.trials.keys():
            del self.trials[fullpath]
            pub.sendMessage(topic='FILE CLOSED', data=fullpath)



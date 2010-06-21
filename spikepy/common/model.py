import thread

import wx
from wx.lib.pubsub import Publisher as pub

from .open_data_file import open_data_file
from ..stages import filtering, detection, extraction, clustering

class Model(object):
    def __init__(self):
        self.trials = {}

    def setup_subscriptions(self):
        pub.subscribe(self._open_data_file, "OPEN DATA FILE")
        pub.subscribe(self._close_data_file, "CLOSE DATA FILE")
        pub.subscribe(self._filter, "FILTER")

    def _open_data_file(self, message):
        fullpath = message.data
        if fullpath not in self.trials.keys():
            thread.start_new_thread(self.open_file, (fullpath,))
        else:
            pub.sendMessage(topic='FILE ALREADY OPENED',data=fullpath)

    def open_file(self, fullpath):
        self.trials[fullpath] = open_data_file(fullpath)
        # call sendMessage after thread exits. (Publisher is NOT threadsafe)
        wx.CallAfter(self._file_opened, fullpath)

    def _file_opened(self, fullpath):
        pub.sendMessage(topic='TRIAL ADDED', data=self.trials[fullpath])
        pub.sendMessage(topic='FILE OPENED', data=fullpath)

    def _close_data_file(self, message):
        fullpath = message.data
        if fullpath in self.trials.keys():
            del self.trials[fullpath]
            pub.sendMessage(topic='FILE CLOSED', data=fullpath)

    def _filter(self, message):
        stage_name, method_name, method_parameters = message.data
        trace_type = stage_name.split()[0]
        for trial in self.trials.values():
            raw_traces = trial.traces['raw']
            filtered_traces = []
            for raw_trace in raw_traces:
                method = get_method(method_name)
                filtered_trace = method(*method_parameters)
                filtered_traces.append(filtered_trace)
            trial.set_traces(filtered_traces, trace_type=trace_type)
            pub.sendMessage(topic='TRIAL %s FILTERED' % trace_type.upper(),
                            data=trial)


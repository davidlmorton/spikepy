
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from .open_data_file import open_data_file
from ..stages import filtering, detection, extraction, clustering


class Model(object):
    def __init__(self):
        self.trials = {}

    def setup_subscriptions(self):
        pub.subscribe(self._open_data_file, "OPEN_DATA_FILE")
        pub.subscribe(self._close_data_file, "CLOSE_DATA_FILE")
        pub.subscribe(self._filter, "FILTER")

    # ---- OPEN FILE ----
    def _open_data_file(self, message):
        fullpath = message.data
        if fullpath not in self.trials.keys():
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,))
        else:
            pub.sendMessage(topic='FILE_ALREADY_OPENED',data=fullpath)

    def _open_file_worker(self, fullpath):
        self.trials[fullpath] = open_data_file(fullpath)
        return fullpath

    def _open_file_consumer(self, delayed_result):
        fullpath = delayed_result.get()
        pub.sendMessage(topic='TRIAL_ADDED', data=self.trials[fullpath])
        pub.sendMessage(topic='FILE_OPENED', data=fullpath)

    # ---- CLOSE FILE ----
    def _close_data_file(self, message):
        fullpath = message.data
        if fullpath in self.trials.keys():
            del self.trials[fullpath]
            pub.sendMessage(topic='FILE_CLOSED', data=fullpath)

    # ---- FILTER ----
    def _filter(self, message):
        stage_name, method_name, method_parameters = message.data
        trace_type = stage_name.split()[0]
        for trial in self.trials.values():
            startWorker(self._filter_consumer, self._filter_worker,
                        wargs=(trial, method_name, method_parameters),
                        cargs=(trace_type,))

    def _filter_worker(self, trial, method_name, method_parameters, trace_type):
        raw_traces = trial.traces['raw']
        filtered_traces = []
        for raw_trace in raw_traces:
            method = get_method(method_name)
            filtered_trace = method(*method_parameters)
            filtered_traces.append(filtered_trace)
        trial.set_traces(filtered_traces, trace_type=trace_type)
        return trial

    def _filter_consumer(self, delayed_result):
        trial = delayed_result.get()
        pub.sendMessage(topic='TRIAL_%s_FILTERED' % trace_type.upper(),
                        data=trial)



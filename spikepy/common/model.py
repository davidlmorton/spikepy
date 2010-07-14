import traceback 
import sys
from multiprocessing import Pool

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
        pub.subscribe(self._detection, "DETECTION")
        pub.subscribe(self._extraction, "EXTRACTION")

    # ---- OPEN FILE ----
    def _open_data_file(self, message):
        fullpath = message.data
        if fullpath not in self.trials.keys():
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,))
        else:
            pub.sendMessage(topic='FILE_ALREADY_OPENED',data=fullpath)

    def _open_file_worker(self, fullpath):
        try:
            processing_pool = Pool()
            result = processing_pool.apply_async(open_data_file, 
                                                 args=(fullpath,))
            self.trials[fullpath] = result.get()
            processing_pool.close()
        except:
            traceback.print_exc()
            sys.exit(1)
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

    # ---- DETECTION ----
    def _detection(self, message):
        stage_name, method_name, method_parameters = message.data
        startWorker(self._detection_consumer, self._detection_worker,
                        wargs=(method_name, method_parameters),
                        cargs=(stage_name,))

    def _detection_worker(self, method_name, method_parameters):
        try:
#            processing_pool = Pool()
            for trial in self.trials.values():
                filtered_traces = trial.traces['detection']
                method = detection.get_method(method_name)
                method_parameters['sampling_freq'] = trial.sampling_freq
#                result = processing_pool.apply_async(method.run, 
#                                                     args=(filtered_traces,),
#                                                     kwds=method_parameters)
#                trial.spikes = result.get()
                trial.spikes = method.run(filtered_traces, **method_parameters)
        except:
            traceback.print_exc()
            sys.exit(1)

    def _detection_consumer(self, delayed_result, stage_name):
        for trial in self.trials.values():
            trial.initialize_data(last_stage_completed=stage_name)
            pub.sendMessage(topic='TRIAL_DETECTIONED', data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')
        

    # ---- filter ----
    def _filter(self, message):
        stage_name, method_name, method_parameters = message.data
        trace_type = stage_name.split()[0] # removes ' filter' from name
        startWorker(self._filter_consumer, self._filter_worker,
                        wargs=(method_name, method_parameters, 
                               trace_type),
                        cargs=(trace_type, stage_name))

    def _filter_worker(self, method_name, method_parameters, trace_type):
        try:
            processing_pool = Pool()
            for trial in self.trials.values():
                raw_traces = trial.traces['raw']
                filtered_traces = []
                method = filtering.get_method(method_name)
                method_parameters['sampling_freq'] = trial.sampling_freq
                result = processing_pool.apply_async(method.run, 
                                                     args=(raw_traces,),
                                                     kwds=method_parameters)
                filtered_traces = result.get()
                trial.set_traces(filtered_traces, trace_type=trace_type)
            processing_pool.close()
        except:
            traceback.print_exc()
            sys.exit(1)

    def _filter_consumer(self, delayed_result, trace_type, stage_name):
        for trial in self.trials.values():
            trial.initialize_data(last_stage_completed=stage_name)
            pub.sendMessage(topic='TRIAL_%s_FILTERED' % trace_type.upper(),
                            data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')

    # ---- EXTRACTION ----
    def _extraction(self, message):
        stage_name, method_name, method_parameters = message.data
        startWorker(self._extraction_consumer, self._extraction_worker,
                        wargs=(method_name, method_parameters),
                        cargs=(stage_name,))

    def _extraction_worker(self, method_name, method_parameters):
        try:
#            processing_pool = Pool()
            for trial in self.trials.values():
                filtered_traces = trial.traces['extraction']
                method = extraction.get_method(method_name)
                method_parameters['sampling_freq'] = trial.sampling_freq
                method_parameters['spike_list'] = trial.spikes[0]
#                result = processing_pool.apply_async(method.run, 
#                                                     args=(filtered_traces,),
#                                                     kwds=method_parameters)
#                trial.spikes = result.get()
                trial.features = method.run(filtered_traces, **method_parameters)
        except:
            traceback.print_exc()
            sys.exit(1)

    def _extraction_consumer(self, delayed_result, stage_name):
        for trial in self.trials.values():
            trial.initialize_data(last_stage_completed=stage_name)
            pub.sendMessage(topic='TRIAL_EXTRACTIONED', data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')


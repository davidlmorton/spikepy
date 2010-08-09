import traceback 
import sys
from multiprocessing import Pool
import copy

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from .open_data_file import open_data_file
from .utils import pool_process, upsample_trace_list
from ..stages import filtering, detection, extraction, clustering
from .trial import format_traces

class Model(object):
    def __init__(self):
        self.trials = {}

        if wx.Platform != '__WXMAC__':
            self._processing_pool = Pool()
        else:
            self._processing_pool = None

    def setup_subscriptions(self):
        """
        Subscribe to relevant pubsub topics.
        """
        pub.subscribe(self._open_data_file,   "OPEN_DATA_FILE")
        pub.subscribe(self._close_data_file,  "CLOSE_DATA_FILE")

        pub.subscribe(self._carry_out_action, "FILTER_ALL_TRIALS")
        pub.subscribe(self._carry_out_action, "DETECTION_ALL_TRIALS")
        pub.subscribe(self._carry_out_action, "EXTRACTION_ALL_TRIALS")
        pub.subscribe(self._cluster_all,      "CLUSTERING_ALL_TRIALS")

        pub.subscribe(self._carry_out_action, "FILTER_TRIAL")
        pub.subscribe(self._carry_out_action, "DETECTION_TRIAL")
        pub.subscribe(self._carry_out_action, "EXTRACTION_TRIAL")
        pub.subscribe(self._cluster_single,   "CLUSTERING_TRIAL")

    def _carry_out_action(self, message):
        action = message.topic[0].lower()
        handler_name = '_%s' % action.split('_')[0]
        handler = getattr(self, handler_name)
        if 'all' in action:
            for trial in self.trials.values():
                handler(trial, *message.data)
        else:
            handler(*message.data)
            
    # ---- OPEN FILE ----
    def _open_data_file(self, message):
        """
        Read in data from a file and create a Trial object from it.
        Inputs:
            message     : message.data should be the fullpath to the file.
        Alters:
            self.trials : a new entry with key=fullpath and value=Trial object
                          will be added to this dictionary.
        Publishes:
            'FILE_ALREADY_OPENED'    : if the file has previously been opened
                                       -- data = fullpath
            'TRIAL_ADDED'            : if the file was just opened successfully
                                       -- data = Trial object just created
            'FILE_OPENED'            : if the file was just opened successfully
                                       -- data = fullpath
        """
        fullpath = message.data
        if fullpath not in self.trials.keys():
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,))
        else:
            pub.sendMessage(topic='FILE_ALREADY_OPENED',data=fullpath)

    def _open_file_worker(self, fullpath):
        trial = pool_process(self._processing_pool, open_data_file, 
                             args=(fullpath,))
        return trial

    def _open_file_consumer(self, delayed_result):
        trial = delayed_result.get()
        fullpath = trial.fullpath
        self.trials[fullpath] = trial
        pub.sendMessage(topic='TRIAL_ADDED', data=trial)
        pub.sendMessage(topic='FILE_OPENED', data=fullpath)

    # ---- CLOSE FILE ----
    def _close_data_file(self, message):
        """
        Remove an existing Trial object.
        Inputs:
            message     : message.data should be the fullpath to the file.
        Alters:
            self.trials : the entry with key=fullpath will be removed.
        Publishes:
            'FILE_CLOSED'            : if the file was just closed successfully
                                       -- data = fullpath
        """
        fullpath = message.data
        if fullpath in self.trials.keys():
            del self.trials[fullpath]
            pub.sendMessage(topic='FILE_CLOSED', data=fullpath)

    # ---- FILTER ----
    def _filter(self, trial, stage_name, method_name, method_parameters):
        """
        Perform filtering on the raw_data of a Trial and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (one of 'Detection Filter' or 
                                               'Extraction Filter')
            method_name     : a string
            method_parameters   : a dictionary of keyword arguments that 
                                  are required by the method.run() function.
        Alters:
            self.trials[fullpath]    : stores results, method_used and settings
                                       in the appropriate StageData instance.
        Publishes:
            'TRIAL_%s_FILTERED'    : if the trial was filtered successfully,
                                     the %s will be one of DETECTION or 
                                                           EXTRACTION
                                     --data = trial
            'RUNNING_COMPLETED'    : if the trial was filtered successfully
                                     -- data = None
        """
        stage_data = trial.get_stage_data(stage_name)
        stage_data.reinitialize()
        stage_data.method   = method_name
        stage_data.settings = copy.deepcopy(method_parameters)

        trace_type = stage_name.split()[0] # removes ' Filter' from name
        startWorker(self._filter_consumer, self._filter_worker,
                        wargs=(trial, stage_name, method_name, 
                               method_parameters, trace_type),
                        cargs=(trial, trace_type, stage_name))

    def _filter_worker(self, trial, stage_name, method_name, 
                             method_parameters, trace_type):
        raw_traces = trial.raw_traces
        filtered_traces = []
        method = filtering.get_method(method_name)
        # XXX just pass sampling_freq as a standard argument
        method_parameters['sampling_freq'] = trial.sampling_freq
        filtered_traces = pool_process(self._processing_pool, method.run,
                                       args=(raw_traces,),
                                       kwargs=method_parameters)
        return filtered_traces

    def _filter_consumer(self, delayed_result, trial,trace_type, stage_name):
        filtered_traces = delayed_result.get()
        stage_data = trial.get_stage_data(stage_name)
        stage_data.results = format_traces(filtered_traces)
        pub.sendMessage(topic='TRIAL_%s_FILTERED' % trace_type.upper(),
                        data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')

    # ---- DETECTION ----
    def _detection(self, trial, stage_name, method_name, method_parameters):
        """
        Perform spike detection on the detection filtered traces of a Trial 
            and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            method_parameters   : a dictionary of keyword arguments that 
                                  are required by the method.run() function.
        Alters:
            self.trials[fullpath]   : stores results, method_used and settings
                                      in the appropriate StageData instance.
        Publishes:
            'TRIAL_DETECTIONED'     : if the trial was successfully spike 
                                      detected
                                     --data = trial
            'RUNNING_COMPLETED'    : if the trial was filtered successfully
                                     -- data = None
        """
        trial.detection.reinitialize()
        trial.detection.method   = method_name
        trial.detection.settings = copy.deepcopy(method_parameters)

        startWorker(self._detection_consumer, self._detection_worker,
                        wargs=(trial, method_name, method_parameters),
                        cargs=(trial,))

    def _detection_worker(self, trial, method_name, method_parameters):
        new_sample_rate = 30000
        filtered_traces = pool_process(self._processing_pool, 
                                       upsample_trace_list,
                                       args=(trial.detection_filter.results,
                                             trial.sampling_freq,
                                             new_sample_rate))
        method = detection.get_method(method_name)
        spikes = pool_process(self._processing_pool, method.run,
                              args=(filtered_traces, new_sample_rate), 
                              kwargs=method_parameters)
        return spikes

    def _detection_consumer(self, delayed_result, trial):
        spikes = delayed_result.get()
        print spikes
        # XXX carefully consider what to do if no spikes were detected.
        if len(spikes[0]) > 0:
            trial.detection.results = spikes
        pub.sendMessage(topic='TRIAL_DETECTIONED', data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')

    # ---- EXTRACTION ----
    def _extraction(self, trial, stage_name, method_name, method_parameters):
        """
        Perform feature extraction on the extraction filtered traces of a Trial 
            and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            method_parameters   : a dictionary of keyword arguments that 
                                  are required by the method.run() function.
        Alters:
            self.trials[fullpath]   : stores results, method_used and settings
                                      in the appropriate StageData instance.
        Publishes:
            'TRIAL_DETECTIONED'     : if the trial was successfully feature
                                      extracted
                                     --data = trial
            'RUNNING_COMPLETED'    : if the trial was filtered successfully
                                     -- data = None
        """
        trial.extraction.reinitialize()
        trial.extraction.method   = method_name
        trial.extraction.settings = copy.deepcopy(method_parameters)
        startWorker(self._extraction_consumer, self._extraction_worker,
                        wargs=(trial, method_name, method_parameters),
                        cargs=(trial,))

    def _extraction_worker(self, trial, method_name, method_parameters):
        # XXX
        method_parameters['spike_list'] = trial.detection.results[0]
        if len(method_parameters['spike_list']) == 0:
            return None # no spikes from detection = no extraction
        new_sample_rate = 30000
        filtered_traces = pool_process(self._processing_pool, 
                                       upsample_trace_list,
                                       args=(trial.extraction_filter.results,
                                             trial.sampling_freq,
                                             new_sample_rate))
        method = extraction.get_method(method_name)
        features_dict = pool_process(self._processing_pool,
                                     method.run,
                                     args=(filtered_traces, new_sample_rate),
                                     kwargs=method_parameters)
        return features_dict

    def _extraction_consumer(self, delayed_result, trial):
        features_dict = delayed_result.get()
        trial.extraction.results = features_dict
        pub.sendMessage(topic='TRIAL_EXTRACTIONED', data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')

    def _cluster_all(self, message):
        trial_list = self.trials.values()
        self._clustering(trial_list, *message.data)

    def _cluster_single(self, message):
        pass

    # ---- CLUSTERING ----
    def _clustering(self, trial_list, stage_name, method_name, 
                          method_parameters):
        """
        Perform clustering on the extracted features of all Trials in 
            trial_list and store the results.
        Inputs:
            trial_list      : a list of Trial objects
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            method_parameters   : a dictionary of keyword arguments that 
                                  are required by the method.run() function.
        Alters:
            self.trials[fullpath]   : stores results, method_used and settings
                                      in the appropriate StageData instance.
        Publishes:
            'TRIAL_CLUSTERINGED'    : if the trial was successfully clustered
                                     --data = trial
            'RUNNING_COMPLETED'    : if the trial was filtered successfully
                                     -- data = None
        """
        for trial in trial_list:
            trial.clustering.reinitialize()
            trial.clustering.method   = method_name
            trial.clustering.settings = copy.deepcopy(method_parameters)
        startWorker(self._clustering_consumer, self._clustering_worker,
                        wargs=(trial_list, method_name, method_parameters),
                        cargs=(trial_list,))

    def _clustering_worker(self, trial_list, method_name, method_parameters):
        # get all feature_sets from all trials in a single long list.
        master_key_list   = []
        feature_set_list  = []
        feature_time_list = []
        trial_keys = sorted([trial.fullpath for trial in trial_list])
        for key in trial_keys:
            features = self.trials[key].extraction.results['features']
            feature_times = (self.trials[key].extraction.
                             results['feature_times'])
            key_list = [key for i in xrange(len(features))]
            feature_set_list.extend(features)
            feature_time_list.extend(feature_times)
            master_key_list.extend(key_list)

        method = clustering.get_method(method_name)
        if len(feature_set_list) == 0:
            return None # no spikes = no clustering

        results = pool_process(self._processing_pool, method.run,
                               args=(feature_set_list,),
                               kwargs=(method_parameters))

        # initialize clustering results to empty_list_dictionaries
        cluster_identities = set(results)
        for trial in trial_list:
            empty_dict = {}
            for ci in cluster_identities:
                empty_dict[ci] = []
            trial.clustering.results = empty_dict 
        # unpack results from run back into trial results.
        for mkey, result, feature_time in \
                zip(master_key_list, results, feature_time_list):
            trial_results = self.trials[mkey].clustering.results[result]
            trial_results.append(feature_time)

    def _clustering_consumer(self, delayed_result, trial_list):
        for trial in trial_list:
            pub.sendMessage(topic='TRIAL_CLUSTERINGED', data=trial)
        pub.sendMessage(topic='RUNNING_COMPLETED')

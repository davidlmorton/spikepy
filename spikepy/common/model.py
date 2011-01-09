import traceback 
import sys
from multiprocessing import Pool
import copy
import os
from collections import defaultdict

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker
import numpy

from .open_data_file import open_data_file
from .utils import pool_process, upsample_trace_list
from spikepy.common import utils
from spikepy.common.path_utils import setup_user_directories
from ..stages import filtering, detection, extraction, clustering
from spikepy.common.plugin_utils import get_method, load_all_plugins
from .trial import format_traces
from spikepy.common.run_manager import RunManager

class Model(object):
    def __init__(self):
        self.trials = {}
        self.run_manager = RunManager()
        load_all_plugins()
        setup_user_directories()

        if wx.Platform != '__WXMAC__':
            #self._processing_pool = Pool()
            self._processing_pool = None #XXX Til we understand pool better.
        else:
            self._processing_pool = None
        
        self.handlers = {'detection_filter':self._filter,
                         'detection':self._detection,
                         'extraction_filter':self._filter,
                         'extraction':self._extraction,
                         'clustering':self._cluster_single}
        self._opening_files = []

    def setup_subscriptions(self):
        """
        Subscribe to relevant pubsub topics.
        """
        pub.subscribe(self._open_data_file, "OPEN_DATA_FILE")
        pub.subscribe(self._close_trial,    "CLOSE_TRIAL")
        pub.subscribe(self._execute_stage,  "EXECUTE_STAGE")

    def _execute_stage(self, message):
        """
        Carry out an action such as filtering, detection, extraction or 
        clustering.
        """
        stage_name = message.data['stage_name']
        trial_list = message.data['trial_list']
 
        del message.data['trial_list']
        handler = self.handlers[stage_name]

        # special case for clustering
        if stage_name == 'clustering':
            self._clustering(trial_list, **message.data)
        else:
            for trial in trial_list:
                handler(trial=trial, **message.data)
            
    # ---- OPEN FILE ----
    def _open_data_file(self, message):
        """
        Read in data from a file and create a Trial object from it.
        Inputs:
            message     : message.data should be the fullpath to the file.
        Alters:
            self.trials : a new entry with key=trial_id and value=Trial object
                          will be added to this dictionary.
        Publishes:
            'TRIAL_ADDED'            : if the file was just opened successfully
                                       -- data = Trial object just created
            'FILE_OPENED'            : if the file was just opened successfully
                                       -- data = fullpath
            'ALREADY_OPENING_FILE'   : if the file is still being opened
                                       -- data = fullpath
        """
        fullpath = message.data
        if fullpath not in self._opening_files:
            self._opening_files.append(fullpath)
            pub.sendMessage(topic="FILE_OPENING_STARTED")
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,), cargs=(fullpath,))
        else:
            pub.sendMessage(topic='ALREADY_OPENING_FILE', data=fullpath)

    def _open_file_worker(self, fullpath):
        trial_list = pool_process(self._processing_pool, open_data_file, 
                             args=(fullpath,))
        return trial_list

    def _open_file_consumer(self, delayed_result, fullpath):
        pub.sendMessage(topic="FILE_OPENING_ENDED")
        trial_list = delayed_result.get()
        for trial in trial_list:
            trial_id = trial.trial_id
            self.trials[trial_id] = trial
            pub.sendMessage(topic='TRIAL_ADDED', data=trial)
        self._opening_files.remove(fullpath)
        pub.sendMessage(topic='FILE_OPENED', data=fullpath)

    # ---- CLOSE FILE ----
    def _close_trial(self, message):
        """
        Remove an existing Trial object.
        Inputs:
            message     : message.data should be the trial_id of the trial.
        Alters:
            self.trials : the entry with key=trial_id will be removed.
        Publishes:
            'TRIAL_CLOSED'      : if the trial was just closed successfully
                                  -- data = trial_id
        """
        trial_id = message.data
        if trial_id in self.trials.keys():
            del self.trials[trial_id]
            pub.sendMessage(topic='TRIAL_CLOSED', data=trial_id)

    # ---- FILTER ----
    def _filter(self, trial=None, stage_name=None, method_name=None, 
                      settings=None):
        """
        Perform filtering on the raw_data of a Trial and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (one of 'Detection Filter' or 
                                               'Extraction Filter')
            method_name     : a string
            settings        : a dictionary of keyword arguments that 
                              are required by the method.run() function.
        Alters:
            trial           : stores results, method_used and settings
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
        stage_data.settings = copy.deepcopy(settings)

        pub.sendMessage(topic="PROCESS_STARTED", data=[trial])
        startWorker(self._filter_consumer, self._filter_worker,
                        wargs=(trial, stage_name, method_name, 
                               settings),
                        cargs=(trial, stage_name))

    def _filter_worker(self, trial, stage_name, method_name, settings):
        raw_traces = trial.raw_traces
        filtered_traces = []
        method = get_method(stage_name, method_name)
        filtered_traces = pool_process(self._processing_pool, method.run,
                                       args=(raw_traces, trial.sampling_freq),
                                       kwargs=settings)
        return filtered_traces

    def _filter_consumer(self, delayed_result, trial, stage_name):
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])
        filtered_traces = delayed_result.get()
        stage_data = trial.get_stage_data(stage_name)
        stage_data.results = format_traces(filtered_traces)
        pub.sendMessage(topic='TRIAL_FILTERED',
                        data=(trial, stage_name))
        pub.sendMessage(topic='RUNNING_COMPLETED')

    # ---- DETECTION ----
    def _detection(self, trial=None, stage_name=None, method_name=None, 
                         settings=None):
        """
        Perform spike detection on the detection filtered traces of a Trial 
            and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            settings   : a dictionary of keyword arguments that 
                                  are required by the method.run() function.
        Alters:
            trial           : stores results, method_used and settings
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
        trial.detection.settings = copy.deepcopy(settings)

        pub.sendMessage(topic="PROCESS_STARTED", data=[trial])
        startWorker(self._detection_consumer, self._detection_worker,
                        wargs=(trial, method_name, settings),
                        cargs=(trial,))

    def _detection_worker(self, trial, method_name, settings):
        new_sample_rate = 30000
        filtered_traces = pool_process(self._processing_pool, 
                                       upsample_trace_list,
                                       args=(trial.detection_filter.results,
                                             trial.sampling_freq,
                                             new_sample_rate))
        method = detection.get_method(method_name)
        spikes = pool_process(self._processing_pool, method.run,
                              args=(filtered_traces, new_sample_rate), 
                              kwargs=settings)
        return spikes

    def _detection_consumer(self, delayed_result, trial):
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])
        spikes = delayed_result.get()
        # XXX carefully consider what to do if no spikes were detected.
        if len(spikes[0]) > 0:
            trial.detection.results = spikes
        pub.sendMessage(topic='TRIAL_SPIKE_DETECTED', data=(trial, 'detection'))
        pub.sendMessage(topic='RUNNING_COMPLETED')

    # ---- EXTRACTION ----
    def _extraction(self, trial=None, stage_name=None, method_name=None, 
                          settings=None):
        """
        Perform feature extraction on the extraction filtered traces of a Trial 
            and store the results.
        Inputs:
            trial           : a Trial object
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            settings        : a dictionary of keyword arguments that 
                              are required by the method.run() function.
        Alters:
            trial           : stores results, method_used and settings
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
        trial.extraction.settings = copy.deepcopy(settings)
        pub.sendMessage(topic="PROCESS_STARTED", data=[trial])
        startWorker(self._extraction_consumer, self._extraction_worker,
                        wargs=(trial, method_name, settings),
                        cargs=(trial,))

    def _extraction_worker(self, trial, method_name, settings):
        spike_list = trial.detection.results[0]
        if len(spike_list) == 0:
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
                                     args=(filtered_traces, 
                                           new_sample_rate,
                                           spike_list),
                                     kwargs=settings)
        return features_dict

    def _extraction_consumer(self, delayed_result, trial):
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])
        features_dict = delayed_result.get()
        features_dict['features'] = numpy.array(features_dict['features'])
        trial.extraction.results = features_dict
        pub.sendMessage(topic='TRIAL_FEATURE_EXTRACTED', data=(trial,
                                                               'extraction'))
        pub.sendMessage(topic='RUNNING_COMPLETED')

    def _cluster_single(self, trial, **kwargs):
        return self._clustering([trial], **kwargs)

    # ---- CLUSTERING ----
    def _clustering(self, trial_list=[], stage_name=None, method_name=None, 
                          settings=None):
        """
        Perform clustering on the extracted features of all Trials in 
            trial_list and store the results.
        Inputs:
            trial_list      : a list of Trial objects
            stage_name      : a string (unused, kept to keep API consistent)
            method_name     : a string
            settings        : a dictionary of keyword arguments that 
                              are required by the method.run() function.
        Alters:
            trial_list      : stores results, method_used and settings
                              in the appropriate StageData instance(s).
        Publishes:
            'TRIAL_CLUSTERINGED'    : if the trial was successfully clustered
                                     --data = trial
            'RUNNING_COMPLETED'    : if the trial was filtered successfully
                                     -- data = None
        """
        for trial in trial_list:
            trial.clustering.reinitialize()
            trial.clustering.method   = method_name
            trial.clustering.settings = copy.deepcopy(settings)
        pub.sendMessage(topic="PROCESS_STARTED", data=trial_list)
        startWorker(self._clustering_consumer, self._clustering_worker,
                        wargs=(trial_list, method_name, settings),
                        cargs=(trial_list,))

    def _clustering_worker(self, trial_list, method_name, settings):
        # get all feature_sets from all trials in a single long list.
        master_key_list   = []
        feature_set_list  = []
        feature_time_list = []
        trial_keys = sorted([trial.trial_id for trial in trial_list])
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
                               kwargs=(settings))

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
        pub.sendMessage(topic="PROCESS_ENDED", data=trial_list)
        for trial in trial_list:
            pub.sendMessage(topic='TRIAL_CLUSTERED', data=(trial,'clustering'))
        pub.sendMessage(topic='RUNNING_COMPLETED')

"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
print "MODEL IS DEPRECATED, DO NOT LOAD"

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

from spikepy.common.open_data_file import open_data_file
from spikepy.common import utils
from spikepy.common import path_utils 
from spikepy.common import plugin_utils
from spikepy.common import config_utils
from spikepy.common.config_manager import config_manager
from spikepy.common.run_manager import RunManager

class Model(object):
    def __init__(self):
        self.trials = {}
        self.run_manager = RunManager()
        plugin_utils.load_all_plugins()
        path_utils.setup_user_directories()
        config_manager.load_configs()
        self.config_manager = config_manager

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

        # extra special case for copy detection filter method
        if message.data['method_name'] == 'Copy Detection Filtering':
            self._copy_detection_filter(trial_list)
            return # don't try to do a real filtering job.

        # special case for clustering
        if stage_name == 'clustering':
            self._clustering(trial_list, **message.data)
        else:
            for trial in trial_list:
                handler(trial=trial, **message.data)

    def _copy_detection_filter(self, trial_list):
        for trial in trial_list:
            e_stage_data = trial.get_stage_data('extraction_filter')
            e_stage_data.reinitialize()
            e_stage_data.method = 'Copy Detection Filtering'
            e_stage_data.settings = {}
            pub.sendMessage(topic="PROCESS_STARTED", data=[trial])

            d_stage_data = trial.get_stage_data('detection_filter')
            e_stage_data.results = d_stage_data.results
            
            pub.sendMessage(topic='TRIAL_ALTERED',
                            data=(trial.trial_id, 'extraction_filter'))
            pub.sendMessage(topic="PROCESS_ENDED", data=[trial])
            
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
        trial_list = utils.pool_process(self._processing_pool, open_data_file, 
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
        method = plugin_utils.get_method(stage_name, method_name)
        filtered_traces = utils.pool_process(self._processing_pool, method.run,
                                       args=(raw_traces, trial.sampling_freq),
                                       kwargs=settings)
        return filtered_traces

    def _filter_consumer(self, delayed_result, trial, stage_name):
        filtered_traces = utils.format_traces(delayed_result.get())

        resample_results = resample(filtered_traces, trial.sampling_freq,
                                    processing_pool=self._processing_pool)
        resampled_filtered_traces, new_sampling_freq = resample_results

        stage_data = trial.get_stage_data(stage_name)
        stage_data.results = {'traces':filtered_traces,
                              'resampled_traces':resampled_filtered_traces,
                              'new_sampling_freq':new_sampling_freq}
        pub.sendMessage(topic='TRIAL_ALTERED',
                        data=(trial.trial_id, stage_name))
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])

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
        """
        trial.detection.reinitialize()
        trial.detection.method   = method_name
        trial.detection.settings = copy.deepcopy(settings)

        pub.sendMessage(topic="PROCESS_STARTED", data=[trial])
        startWorker(self._detection_consumer, self._detection_worker,
                        wargs=(trial, method_name, settings),
                        cargs=(trial,))

    def _detection_worker(self, trial, method_name, settings):
        dfr = trial.detection_filter.results
        traces = dfr['resampled_traces']
        new_sampling_freq = dfr['new_sampling_freq']
        method = plugin_utils.get_method('detection', method_name)
        spikes = utils.pool_process(self._processing_pool, method.run,
                              args=(traces, new_sampling_freq), 
                              kwargs=settings)
        return spikes

    def _detection_consumer(self, delayed_result, trial):
        spikes = delayed_result.get()
        # XXX carefully consider what to do if no spikes were detected.
        if len(spikes) > 0:
            # make the spike windows here and store them.
            bc = config_manager['backend']
            pre_padding = bc['spike_window_prepad']
            post_padding = bc['spike_window_postpad']
            dfr = trial.detection_filter.results
            traces = dfr['resampled_traces']
            sampling_freq = dfr['new_sampling_freq']
            window_maker = plugin_utils.get_method('extraction', 'Spike Window')
            window_dict = window_maker.run(traces, sampling_freq, 
                                           spikes, pre_padding=pre_padding,
                                                   post_padding=post_padding,
                                                   exclude_overlappers=False)
            results_dict = {'spike_windows':window_dict['features'],
                            'spike_window_times': window_dict['feature_times'],
                            'spike_times': spikes}
            trial.detection.results = results_dict
            pub.sendMessage(topic='TRIAL_ALTERED', 
                            data=(trial.trial_id, 'detection'))
        else:
            pub.sendMessage(topic='NO_SPIKES_DETECTED', data=trial)
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])

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
        """
        trial.extraction.reinitialize()
        trial.extraction.method   = method_name
        trial.extraction.settings = copy.deepcopy(settings)
        pub.sendMessage(topic="PROCESS_STARTED", data=[trial])
        startWorker(self._extraction_consumer, self._extraction_worker,
                        wargs=(trial, method_name, settings),
                        cargs=(trial,))

    def _extraction_worker(self, trial, method_name, settings):
        spike_list = trial.detection.results['spike_times']
        if len(spike_list) == 0:
            return None # no spikes from detection = no extraction

        efr = trial.extraction_filter.results
        traces = efr['resampled_traces']
        new_sampling_freq = efr['new_sampling_freq']
        method = plugin_utils.get_method('extraction', method_name)
        features_dict = utils.pool_process(self._processing_pool, method.run,
                              args=(traces, new_sampling_freq, spike_list),
                              kwargs=settings)
        return features_dict

    def _extraction_consumer(self, delayed_result, trial):
        features_dict = delayed_result.get()
        trial.extraction.results = features_dict
        pub.sendMessage(topic='TRIAL_ALTERED', 
                        data=(trial.trial_id, 'extraction'))
        pub.sendMessage(topic="PROCESS_ENDED", data=[trial])

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

        method = plugin_utils.get_method('clustering', method_name)
        if len(feature_set_list) == 0:
            return None # no spikes = no clustering

        results = utils.pool_process(self._processing_pool, method.run,
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
        for trial in trial_list:
            pub.sendMessage(topic='TRIAL_ALTERED', 
                            data=(trial.trial_id,'clustering'))
        pub.sendMessage(topic="PROCESS_ENDED", data=trial_list)

def resample(trace_list, prev_sampling_freq, processing_pool=None):
    new_sampling_freq = config_manager['backend']['new_sampling_freq']
    resampled_trace_list = utils.pool_process(processing_pool, 
                                        utils.resample_signals,
                                        args=(trace_list,
                                              prev_sampling_freq,
                                              new_sampling_freq))
    return utils.format_traces(resampled_trace_list), new_sampling_freq


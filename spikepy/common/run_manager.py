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
import multiprocessing
import traceback 
import sys
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
import spikepy.common.program_text as pt

def filter_process_worker(run_queue, results_queue):
    for run_data in iter(run_queue.get, None):
        method_class, run_dict = run_data
        method_obj = method_class()
        filtered_traces = method_obj.run(*run_dict['args'], 
                                         **run_dict['kwargs'])

        # resample the filtered traces
        sampling_freq = run_dict['args'][1]
        new_sampling_freq = config_manager['backend']['new_sampling_freq']
        resampled_traces = []
        resampled_traces = utils.resample_signals(filtered_traces, 
                                                  sampling_freq, 
                                                  new_sampling_freq)
        resampled_filtered_traces = utils.format_traces(resampled_traces)

        result = {'traces':utils.format_traces(filtered_traces),
                  'resampled_traces':resampled_filtered_traces,
                  'new_sampling_freq':new_sampling_freq}
        
        results_queue.put({'trial_id':run_dict['trial_id'],
                           'data':result})

def detection_process_worker(run_queue, results_queue):
    for run_data in iter(run_queue.get, None):
        method_class, run_dict = run_data
        method_obj = method_class()
        spikes = method_obj.run(*run_dict['args'], **run_dict['kwargs'])

        # make spike windows and store them.
        window_maker_class = run_dict['window_maker_class']
        window_maker_obj = window_maker_class()

        if len(spikes > 0):
            traces, sampling_freq = run_dict['args']
            pre_padding = run_dict['pre_padding']
            post_padding = run_dict['post_padding']
            window_dict = window_maker_obj.run(traces, sampling_freq, spikes,
                                               pre_padding=pre_padding,
                                               post_padding=post_padding,
                                               exclude_overlappers=False)

            spike_window_ys = window_dict['features']
            dt_in_ms = 1000.0/sampling_freq
            spike_window_xs = numpy.arange(len(spike_window_ys[0]))*dt_in_ms
            spike_window_times = window_dict['feature_times']
        else:
            spike_window_xs = []
            spike_window_times = []
            spike_window_ys = []
        result = {'spike_times':spikes,
                  'spike_window_xs':spike_window_xs,
                  'spike_window_times':spike_window_times,
                  'spike_window_ys':spike_window_ys}
        
        results_queue.put({'trial_id':run_dict['trial_id'],
                           'data':result})

def extraction_process_worker(run_queue, results_queue):
    for run_data in iter(run_queue.get, None):
        method_class, run_dict = run_data
        method_obj = method_class()
        try:
            result = method_obj.run(*run_dict['args'], **run_dict['kwargs'])
        except:
            result = {'features': [], 'feature_times':[],
                      'excluded_features':[],
                      'excluded_feature_times':[]}
        
        results_queue.put({'trial_id':run_dict['trial_id'],
                           'data':result})

def clustering_process_worker(run_queue, results_queue):
    for run_data in iter(run_queue.get, None):
        method_class, run_dict = run_data
        method_obj = method_class()
        results = method_obj.run(*run_dict['args'], **run_dict['kwargs'])
        
        master_key_list   = run_dict['master_key_list']
        feature_time_list = run_dict['feature_time_list']
        trial_keys = set(master_key_list)
        # initialize clustering results to empty_list_dictionaries
        cluster_identities = set(results)
        trial_results = {}
        for key in trial_keys:
            trial_results[key] = []
            empty_dict = {}
            for ci in cluster_identities:
                empty_dict[ci] = []
            trial_results[key] = empty_dict

        # unpack results from run back into trial results.
        for mkey, result, feature_time in \
                zip(master_key_list, results, feature_time_list):
            trial_results[mkey][result].append(feature_time)

        for key in trial_keys:
            results_queue.put({'trial_id':key,
                               'data':trial_results[key]})

class RunManager(object):
    def __init__(self):
        self.trials = {}
        plugin_utils.load_all_plugins()
        path_utils.setup_user_directories()
        config_manager.load_configs()
        
        self.num_processes = 0
        self.num_files = 0

        pub.subscribe(self._open_data_file, "OPEN_DATA_FILE")
        pub.subscribe(self._close_trial,    "CLOSE_TRIAL")
        pub.subscribe(self._run_stage, "RUN_STAGE")
        pub.subscribe(self._run_stage, "RUN_STRATEGY")
        pub.subscribe(self._abort_strategy, "ABORT_STRATEGY")

        self._run_order = ['detection_filter',
                           'detection',
                           'extraction_filter',
                           'extraction',
                           'clustering']
                           
        self._running = False
        self._running_strategy = False
        self._aborting_strategy = False
        self._offending_trials = []
        self._abort_reasons = []

        # pre-handlers are in charge of formatting the arguments for the
        #     method.run() functions.  They return a dictionary with keys
        #     'trial_id', 'args', and 'kwargs'.
        self._pre_handlers = {'detection_filter':self._pre_filter,
                             'detection':self._pre_detection,
                             'extraction_filter':self._pre_filter,
                             'extraction':self._pre_extraction,
                             'clustering':self._pre_clustering}
        # post-handlers set the trial.stage_data.results and are in charge of
        #     publishing any messages about the processing  that just happened.
        self._post_handlers = {'detection_filter':self._post_filter,
                              'detection':self._post_detection,
                              'extraction_filter':self._post_filter,
                              'extraction':self._post_extraction,
                              'clustering':self._post_clustering}
        # process_workers do the actual calling of method.run() and are run
        #     in another process, so cannot communicate except through the
        #     multiprocessing.Queue objects they are passed.
        self._process_workers = {'detection_filter':filter_process_worker,
                                'detection':detection_process_worker,
                                'extraction_filter':filter_process_worker,
                                'extraction':extraction_process_worker,
                                'clustering':clustering_process_worker}
        self._opening_files = []

    def _register_running(self):
        if not self._running:
            self._running = True
            pub.sendMessage(topic="UPDATE_STATUS", 
                            data=pt.STATUS_RUNNING)
            wx.Yield()

    def _register_running_strategy(self, message):
        if not self._running_strategy:
            self._running_strategy = True
            self._strategy_message = message
            self._strategy_step = 0
            self._offending_trials = []
            self._abort_reasons = []
            self._aborting_strategy = False

    def _register_done_running(self):
        if self._running:
            self._running = False
            pub.sendMessage(topic="UPDATE_STATUS",
                            data=pt.STATUS_IDLE)
            pub.sendMessage(topic="PLOT_RESULTS")
            wx.Yield()

    def _register_done_running_strategy(self):
        if self._running_strategy:
            if self._aborting_strategy:
                last_stage_name_run = self._run_order[self._strategy_step-1]
                pub.sendMessage('ABORTING_STRATEGY', 
                                data=(self._offending_trials, 
                                      self._abort_reasons, 
                                      last_stage_name_run))
            self._running_strategy = False
            # the following two lines will crash system if things are broken.
            #   so think of them as asserts...
            self._strategy_message = None
            self._strategy_step = 1000

    def _get_next_stage_name(self):
        if self._aborting_strategy:
            return None
        if self._strategy_step < len(self._run_order):
            self._strategy_step += 1
            return self._run_order[self._strategy_step-1]

    def _abort_strategy(self, message=None, offending_trial=None, reason=None):
        if message is None:
            if offending_trial is not None:
                self._offending_trials.append(offending_trial)
            self._abort_reasons.append(reason)
        else:
            self._abort_reasons.append(message.data)
        if self._running_strategy:
            self._aborting_strategy = True

    def _copy_detection_filter(self, trial_list):
        self._register_running()
        for trial in trial_list:
            e_stage_data = trial.get_stage_data('extraction_filter')
            e_stage_data.reinitialize()
            e_stage_data.method = 'Copy Detection Filtering'
            e_stage_data.settings = {}

            d_stage_data = trial.get_stage_data('detection_filter')
            e_stage_data.results = d_stage_data.results
            
            pub.sendMessage(topic='TRIAL_ALTERED',
                            data=(trial.trial_id, 'extraction_filter'))

        self._register_done_running()
        if self._running_strategy:
            self._run_stage(self._strategy_message)


    def _run_stage(self, message):
        """
        Carry out an action such as filtering, detection, extraction or 
        clustering.
        """
        if 'stage_name' in message.data.keys():
            stage_name  = message.data['stage_name']
        else:
            self._register_running_strategy(message)
            stage_name = self._get_next_stage_name()
            if stage_name is None:
                self._register_done_running_strategy()
                return # we're done now.

        strategy    = message.data['strategy']
        method_name = strategy.methods_used[stage_name]
        settings    = strategy.settings[stage_name]
        trial_list  = message.data['trial_list']

        # make special case for 'Copy Detection Filtering'
        if stage_name == 'extraction_filter' and\
           method_name == 'Copy Detection Filtering':
           self._copy_detection_filter(trial_list)
           return
 
        pre_handler = self._pre_handlers[stage_name]
        process_worker = self._process_workers[stage_name]

        method_class = plugin_utils.get_method(stage_name, method_name,
                                               instantiate=False)
        run_dict_list = pre_handler(trial_list, stage_name, settings)

        self._register_running()
        startWorker(self._run_stage_consumer, self._run_stage_worker,
                    wargs=(trial_list, method_class, run_dict_list, 
                           process_worker),
                    cargs=(trial_list, stage_name, strategy))

    def _run_stage_worker(self, trial_list, method_class, run_dict_list, 
                          process_worker):
        try:
            num_process_workers = multiprocessing.cpu_count()
        except NotImplimentedError:
            num_process_workers = 8

        processes_limit = config_manager['backend']['limit_num_processes']
        num_process_workers = min(num_process_workers, processes_limit)

        # setup the run and return queues.
        run_data_queue = multiprocessing.Queue()
        for run_dict in run_dict_list:
            run_data_queue.put((method_class, run_dict))
        for i in xrange(num_process_workers):
            run_data_queue.put(None)
        results_queue = multiprocessing.Queue()

        jobs = []
        for i in xrange(num_process_workers):
            # jobs run on run_data_queue and put results into the results_queue
            job = multiprocessing.Process(target=process_worker, 
                                          args=(run_data_queue, results_queue))
            job.start()
            jobs.append(job)

        results_list = []
        for i in xrange(len(trial_list)):
            results_list.append(results_queue.get())

        for job in jobs:
            job.join() # halt this thread until processes are all complete.

        return results_list

    def _run_stage_consumer(self, delayed_result, trial_list, stage_name,
                            strategy):
        # get the results and put them into a list.
        results_list = delayed_result.get()

        for trial in trial_list:
            # ensure a result for this trial was processed and returned
            this_result = None
            for result in results_list:
                if result['trial_id'] == trial.trial_id:
                    this_result = result['data']

            post_handler = self._post_handlers[stage_name]
            # store this result into the trial object.
            if this_result is not None:
                post_handler(trial, this_result, stage_name, strategy)
            else:
                raise RuntimeError('No result was generated for trial:%s during the processing of stage:%s' % (trial.trial_id, stage_name))

        self._register_done_running()
        if self._running_strategy:
            self._run_stage(self._strategy_message)


                
    def _pre_filter(self, trial_list, stage_name, settings):
        run_dict_list = []
        for trial in trial_list:
            raw_traces = trial.raw_traces
            sampling_freq = trial.sampling_freq
            args = (raw_traces, sampling_freq)
            kwargs = settings
            run_dict_list.append({'trial_id':trial.trial_id,
                                  'args':args, 
                                  'kwargs':kwargs})
        return run_dict_list

    def _pre_detection(self, trial_list, stage_name, settings):
        run_dict_list = []
        for trial in trial_list:
            bc = config_manager['backend']
            pre_padding = bc['spike_window_prepad']
            post_padding = bc['spike_window_postpad']
            dfr = trial.detection_filter.results
            window_maker_class = plugin_utils.get_method('extraction',
                                                         'Spike Window',
                                                         instantiate=False)
            traces = dfr['resampled_traces']
            sampling_freq = dfr['new_sampling_freq']
            args = (traces, sampling_freq)
            kwargs = settings
            run_dict_list.append({'trial_id':trial.trial_id,
                                  'args':args, 
                                  'kwargs':kwargs,
                                  'window_maker_class':window_maker_class,
                                  'pre_padding':pre_padding,
                                  'post_padding':post_padding})
        return run_dict_list

    def _pre_extraction(self, trial_list, stage_name, settings):
        run_dict_list = []
        for trial in trial_list:
            efr = trial.extraction_filter.results
            traces = efr['resampled_traces']
            sampling_freq = efr['new_sampling_freq']
            spike_times = trial.detection.results['spike_times']
            args = (traces, sampling_freq, spike_times)
            kwargs = settings
            run_dict_list.append({'trial_id':trial.trial_id,
                                  'args':args, 
                                  'kwargs':kwargs})
        return run_dict_list

    def _pre_clustering(self, trial_list, stage_name, settings):
        # get all feature_sets from all trials in a single long list.
        master_key_list   = []
        feature_set_list  = []
        feature_time_list = []
        trial_keys = sorted([trial.trial_id for trial in trial_list])
        for key in trial_keys:
            er = self.trials[key].extraction.results
            features = er['features']
            feature_times = er['feature_times']
            key_list = [key for i in xrange(len(features))]
            feature_set_list.extend(features)
            feature_time_list.extend(feature_times)
            master_key_list.extend(key_list)

        run_dict = {'args':(feature_set_list,),
                    'kwargs':settings,
                    'feature_set_list':feature_set_list,
                    'master_key_list':master_key_list,
                    'feature_time_list':feature_time_list}
        run_dict_list = [run_dict]
        return run_dict_list

    def _post_filter(self, trial, result, stage_name, strategy):
        stage_data = trial.get_stage_data(stage_name)
        stage_data.reinitialize()
        stage_data.results  = result
        stage_data.method   = strategy.methods_used[stage_name]
        stage_data.settings = strategy.settings[stage_name]
        pub.sendMessage(topic='TRIAL_ALTERED',
                        data=(trial.trial_id, stage_name))

    def _post_detection(self, trial, result, stage_name, strategy):
        if len(result['spike_times']) < 1:
            self._abort_strategy(offending_trial=trial, reason='NO_SPIKES')
        else:
            stage_data = trial.get_stage_data(stage_name)
            stage_data.reinitialize()
            stage_data.results  = result
            stage_data.method   = strategy.methods_used[stage_name]
            stage_data.settings = strategy.settings[stage_name]
            pub.sendMessage(topic='TRIAL_ALTERED',
                            data=(trial.trial_id, stage_name))

    def _post_extraction(self, trial, result, stage_name, strategy):
        if len(result['feature_times']) < 1:
            self._abort_strategy(offending_trial=trial, reason='NO_FEATURES')
        else:
            stage_data = trial.get_stage_data(stage_name)
            stage_data.reinitialize()
            stage_data.results  = result
            stage_data.method   = strategy.methods_used[stage_name]
            stage_data.settings = strategy.settings[stage_name]
            pub.sendMessage(topic='TRIAL_ALTERED',
                            data=(trial.trial_id, stage_name))

    def _post_clustering(self, trial, result, stage_name, strategy):
        stage_data = trial.get_stage_data(stage_name)
        stage_data.reinitialize()
        stage_data.results  = result
        stage_data.method   = strategy.methods_used[stage_name]
        stage_data.settings = strategy.settings[stage_name]
        pub.sendMessage(topic='TRIAL_ALTERED',
                        data=(trial.trial_id, stage_name))

    def can_run(self, run_data):
        stage_name = run_data['stage_name']
        trial_list = run_data['trial_list']
        stage_settings = run_data['settings']
        stage_name = run_data['stage_name']
        stage_method = run_data['method_name']
        methods_used = {stage_name:stage_method}
        settings     = {stage_name:stage_settings}
        run_states = self.get_stage_run_states(methods_used, settings,
                                               trial_list)
        return run_states[stage_name]

    def get_stage_run_states(self, methods_used, settings, trial_list,
                                   force_novelty=False):
        stage_run_state = {}

        num_trials = len(trial_list)
        # initialize to False
        for stage_name in methods_used.keys():
            stage_run_state[stage_name] = False
        if num_trials < 1 or self._running:
            return stage_run_state

        if force_novelty:
            # ensure that novel results would result.
            # all stage states are False at this point.
            for trial in trial_list:
                for stage_name, method_used in methods_used.items():
                    novelty = trial.would_be_novel(stage_name, method_used, 
                                                   settings[stage_name])
                    # novelty in any file = able to run for all files.
                    if novelty:
                        stage_run_state[stage_name] = True
        else:
            for stage_name, method_used in methods_used.items():
                stage_run_state[stage_name] = True
            

        # ensure EVERY trial is ready for this stage.
        for trial in trial_list:
            readyness = trial.get_readyness()
            for stage_name in methods_used.keys():
                if not readyness[stage_name]:
                    stage_run_state[stage_name] = False

        # check that the settings are valid
        for stage_name in methods_used.keys():
            settings_valid = settings[stage_name] is not None
            if not settings_valid:
                stage_run_state[stage_name] = False

        return stage_run_state

    def _file_opening_started(self):
        self.num_files += 1
        pub.sendMessage(topic="UPDATE_STATUS", 
                        data=pt.STATUS_OPENING % self.num_files)
        wx.Yield()

    def _file_opening_ended(self):
        if self.num_files:
            self.num_files -= 1

        if self.num_files:
            pub.sendMessage(topic="UPDATE_STATUS", 
                            data=pt.STATUS_OPENING % self.num_files)
        else:
            pub.sendMessage(topic="UPDATE_STATUS",
                            data=pt.STATUS_IDLE)
        wx.Yield()
        
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
            self._file_opening_started()
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,), cargs=(fullpath,))
        else:
            pub.sendMessage(topic='ALREADY_OPENING_FILE', data=fullpath)

    def _open_file_worker(self, fullpath):
        trial_list = open_data_file(fullpath)
        return trial_list

    def _open_file_consumer(self, delayed_result, fullpath):
        trial_list = delayed_result.get()
        for trial in trial_list:
            trial_id = trial.trial_id
            self.trials[trial_id] = trial
            pub.sendMessage(topic='TRIAL_ADDED', data=trial)
        self._opening_files.remove(fullpath)
        pub.sendMessage(topic='FILE_OPENED', data=fullpath)

        pub.sendMessage(topic="FILE_OPENING_ENDED")
        self._file_opening_ended()

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

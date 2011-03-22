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

import time
import datetime
import json
import os
import uuid
from collections import defaultdict

import wx
from wx.lib.pubsub import Publisher as pub
import numpy
import scipy.io

from spikepy.common import program_text as pt
from spikepy.common import utils
from spikepy.common.config_manager import config_manager as config
from spikepy.common.strategy import Strategy

text_delimiters = {pt.PLAIN_TEXT_TABS: '\t',
                   pt.PLAIN_TEXT_SPACES: ' ',
                   pt.CSV: ','}
format_extentions = {pt.PLAIN_TEXT_SPACES:'txt',
                     pt.PLAIN_TEXT_TABS:'txt',
                     pt.CSV:'csv',
                     pt.MATLAB:'mat',
                     pt.NUMPY_BINARY:'npz'}

display_names = set()

def get_unique_display_name(proposed_display_name):
    count = 1
    new_display_name = proposed_display_name
    while new_display_name in display_names:
        new_display_name = '%s(%d)' % (proposed_display_name, count)
        count += 1
    return new_display_name

class Trial(object):
    """This class represents an individual trial consisting of (potentially)
    multiple electrodes recording simultaneously.
    """
    def __init__(self, sampling_freq=1.0, 
                       raw_traces=[[0.0]], 
                       fullpath='FULLPATH NOT SET'):
        self.fullpath      = fullpath
        filename = os.path.split(fullpath)[1]
        self.display_name = get_unique_display_name(filename)
        display_names.add(self.display_name)
        self.raw_traces    = utils.format_traces(raw_traces)
        self._id = uuid.uuid4() 

        # imports matplotlib, so can't be at top.
        from spikepy.common import signal_utils 

        # calculate the psds of the raw_traces
        self.psd = signal_utils.psd(self.raw_traces.flatten(), 
                                    sampling_freq, 
                                    config['backend']['psd_freq_resolution'])

        self.sampling_freq = sampling_freq
        self.dt            = (1.0/sampling_freq)*1000.0 # dt in ms
        if len(self.raw_traces):
            trace_length = len(self.raw_traces[0])
            self.times = numpy.arange(0, trace_length, 1)*self.dt
        else:
            self.times = None

        self.clustering        = StageData(name='clustering',       
                                           dependents=[])
        self.extraction        = StageData(name='extraction',       
                                           dependents=[self.clustering])
        self.detection         = StageData(name='detection',        
                                           dependents=[self.extraction])
        self.extraction_filter = StageData(name='extraction_filter',
                                           dependents=[self.extraction])
        self.detection_filter  = StageData(name='detection_filter', 
                                           dependents=[self.detection, 
                                                       self.extraction_filter])
        self.raw_data          = StageData(name='raw_data',
                                           dependents=[self.detection_filter])

        self.clustering.set_prereqs([self.extraction])
        self.extraction.set_prereqs([self.extraction_filter, self.detection])
        self.extraction_filter.set_prereqs([self.detection_filter])
        self.detection.set_prereqs([self.detection_filter])
        self.detection_filter.set_prereqs([self.raw_data])

        self.stages = [self.detection_filter,
                       self.detection,
                       self.extraction_filter,
                       self.extraction,
                       self.clustering]

    @property
    def trial_id(self):
        return self._id

    @property
    def methods_used(self):
        _methods_used = {}
        for stage in self.stages:
            _methods_used[stage.name] = stage.method
        return _methods_used

    @property
    def settings(self):
        _settings = {}
        for stage in self.stages:
            _settings[stage.name] = stage.settings
        return _settings

    def get_strategy(self):
        '''
        Return the strategy that describes the processing that has already been
            performed on this trial.  If any stage is incomplete return None.
        '''
        for s in self.settings.values():
            if s is None:
                return None

        for m in self.methods_used.values():
            if m is None:
                return None

        return Strategy(methods_used=self.methods_used, settings=self.settings)

    def get_archive(self, archive_name='archive'):
        '''
        Create and return a dictionary that includes all the data needed to
        recreate the trial object.
        '''
        return_dict = {}
        return_dict['raw_traces'] = self.raw_traces
        # obscure the fullpath in archives for security reasons.
        return_dict['fullpath'] = os.path.join(archive_name, self.display_name)
        return_dict['sampling_freq'] = self.sampling_freq
        for stage in self.stages:
            return_dict[stage.name] = self.get_data_from_stage(stage.name)
        return return_dict

    def set_data_for_stage(self, stage_name, method=None, settings=None, 
                                             results=None):
        stage_data = self.get_stage_data(stage_name)
        stage_data.method   = method
        stage_data.settings = settings
        stage_data.results  = results

    @classmethod
    def from_archive(cls, archive):
        return_trial = Trial(sampling_freq=archive['sampling_freq'],
                             raw_traces=archive['raw_traces'], 
                             fullpath=archive['fullpath'])
        for stage in return_trial.stages:
            if stage.name in archive.keys():
                data_for_stage = archive[stage.name]
                return_trial.set_data_for_stage(stage.name, **data_for_stage)
        return return_trial

    def get_data_from_stage(self, stage_name):
        stage_data = self.get_stage_data(stage_name)
        return_dict = {'method': stage_data.method,
                       'settings': stage_data.settings,
                       'results': stage_data.results}
        return return_dict

    def has_run_stage(self, stage_name):
        stage_data = self.get_stage_data(stage_name)
        return stage_data.results is not None

    def can_run_stage(self, stage_name):
        return self.get_readyness()[stage_name]

    def get_prereq_stage_names(self, stage_name):
        '''
        Return a set of stage names which are either direct or 
        remote prereqs of the given stage_name.
        '''
        prereq_set = set()
        self._get_prereq_stage_names(stage_name, prereq_set)
        return prereq_set

    def _get_prereq_stage_names(self, stage_name, prereq_set):
        '''
        Given 'prereq_set' as an empty set(), this will recursively add
        all prerequisite stages to 'stage_name'
        '''
        stage_data = self.get_stage_data(stage_name)
        for prereq in stage_data.prereqs:
            prereq_set.add(prereq.name)
            self._get_prereq_stage_names(prereq.name, prereq_set)

    def get_stage_data(self, stage_name):
        if stage_name == pt.DETECTION_FILTER:
            return self.detection_filter
        if stage_name == pt.DETECTION:
            return self.detection
        if stage_name == pt.EXTRACTION_FILTER:
            return self.extraction_filter
        if stage_name == pt.EXTRACTION:
            return self.extraction
        if stage_name == pt.CLUSTERING:
            return self.clustering

        formatted_stage_name = stage_name.lower().replace(' ', '_')
        if hasattr(self, formatted_stage_name):
            return getattr(self, formatted_stage_name)
        else:
            raise RuntimeError('Trial does not have a stage by the name of %s' %
                                formatted_stage_name)

    def get_readyness(self):
        '''
        Return a dictionary with keys=stage names and
            values=True->stage prereqs met
                  =False->one or more prereqs unmet
        '''
        readyness = {}
        for stage in self.stages:
            can_run = True
            for prereq in stage.prereqs:
                if prereq.results is None:
                    can_run = False
            readyness[stage.name] = can_run
        return readyness

    def would_be_novel(self, stage_name, method_class, settings_dict):
        '''
        Would running a given stage yield novel results?
        '''
        method = method_class()
        method_name = method.name
        if method._is_stochastic:
            return True
        else:
            stage_data = self.get_data_from_stage(stage_name)
            return not (method_name == stage_data['method'] and 
                        settings_dict == stage_data['settings'])

    def __hash__(self):
        return hash(self.trial_id)

    def get_clustered_spike_windows(self):
        if self.extraction.results is None or self.clustering.results is None:
            raise RuntimeError('Trial with trial_id:%s does not have extraction or clustering results, so cannot find clustered spike windows.' % self.trial_id)
        window_times = self.detection.results['spike_window_times']
        windows = self.detection.results['spike_window_ys']
        times = self.clustering.results['clustered_spike_times']
        clustered_windows = defaultdict(list)
        for cluster_num, time_list in times.items():
            for time in time_list:
                window_index = window_times.index(time)
                clustered_windows[cluster_num].append(windows[window_index])
            clustered_windows[cluster_num] =\
                    numpy.array(clustered_windows[cluster_num]) 
        return clustered_windows

    def get_num_clusters(self):
        if self.extraction.results is None or self.clustering.results is None:
            raise RuntimeError('Trial with trial_id:%s does not have extraction or clustering results, so cannot find clustered features.' % self.trial_id)
        return len(self.clustering.results['clustered_spike_times'].keys())

    def rename(self, new_display_name):
        display_names.remove(self.display_name)
        self.display_name = new_display_name
        display_names.add(self.display_name)
        pub.sendMessage(topic='TRIAL_RENAMED', data=self)

    def export(self, path=None, stages_selected=[], file_format=None):
        '''
        Store the results of the stages in <stage_list> to files in <path>.
        Inputs:
            path            : The export directory (must exist)
            stage_list      : A list of strings denoting the stages results to
                              export.
            rows_or_cols    : Should sequences be stored as rows or columns.
            format          : The file format
        Returns:
            None
        '''
        for stage_name in stages_selected:
            extention = format_extentions[file_format]
            base_name = '%s-%s' % (self.display_name, stage_name)
            filename = '%s.%s' % (base_name, extention)
            fullpath = os.path.join(path, filename)
            times = self.times
            if 'raw_traces' == stage_name:
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    results = [times]
                    for trace in self.raw_traces:
                        results.append(trace)
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, times=times, 
                                raw_traces=self.raw_traces)
                elif file_format == pt.MATLAB:
                    results = {'times': times,
                               'raw_traces': self.raw_traces}
                    scipy.io.savemat(fullpath, results)
                continue
            stage_data = self.get_stage_data(stage_name)
            if stage_data.results is None:
                continue # this stage hasn't been run.
            # EXPORT FILTER STAGE
            if 'filter' in stage_name:
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    results = [times]
                    for trace in stage_data.results['traces']:
                        results.append(trace)
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                        delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT DETECTION STAGE
            if stage_name == 'detection':
                spike_times        = stage_data.results['spike_times']
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    results = [spike_times]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT EXTRACTION STAGE
            if stage_name == 'extraction':
                features = numpy.array(stage_data.results['features'])
                feature_times = numpy.array(stage_data.results['feature_times'])
                feature_times = feature_times.reshape(1,-1)
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    for f, ft in zip(features, feature_times):
                        results.append([ft, f])
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **stage_data.results)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, stage_data.results)
            # EXPORT CLUSTERING STAGE
            if stage_name == 'clustering':
                sr = stage_data.results
                # store results the way you should for .mat files.
                results_dict = {}
                st_dict = sr['clustered_spike_times']
                for cluster_id, spike_times in st_dict.items():
                    key = 'cluster_%s_spike_times' % cluster_id
                    results_dict[key] = spike_times
                f_dict = sr['clustered_features']
                for cluster_id, features in f_dict.items():
                    key = 'cluster_%s_features' % cluster_id
                    results_dict[key] = features
                sw_dict = self.get_clustered_spike_windows()
                for cluster_id, sw in sw_dict.items():
                    key = 'cluster_%s_spike_windows'% cluster_id
                    results_dict[key] = sw
                # format results for .txt files.
                clustered_spike_times = sr['clustered_spike_times']
                cluster_keys = sorted(clustered_spike_times.keys())
                results = [clustered_spike_times[key] for key in cluster_keys]
                string_dict = {}
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    utils.save_list_txt(fullpath, results, 
                                        delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **sr)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, results_dict)

class StageData(object):
    def __init__(self, name=None, dependents=[], prereqs=[]):
        self.name = name
        self.dependents = dependents
        self.prereqs = prereqs

        self.settings    = None
        self.method_name = None
        self.results     = None

        self.reinitialize()

    def set_prereqs(self, prereqs):
        self.prereqs = prereqs
    
    def reinitialize(self):
        if self.settings is not None:
            self.settings    = None
            self.method_name = None
            self.results     = None
            for dependent in self.dependents:
                dependent.reinitialize()

class ExtractionFilterStageData(StageData):
    def reinitialize(self):
        if (self.settings is not None and
            self.method_name is 'Copy Detection Filtering'):
            self.settings    = None
            self.method_name = None
            self.results     = None
            for dependent in self.dependents:
                dependent.reinitialize()

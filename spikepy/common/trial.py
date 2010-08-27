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

from spikepy.gui.strategy_manager import make_strategy
import spikepy.gui.program_text as pt
from spikepy.common.utils import save_list_txt

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
                       raw_traces=[], 
                       fullpath='FULLPATH NOT SET'):
        self.fullpath      = fullpath
        filename = os.path.split(fullpath)[1]
        self.display_name = get_unique_display_name(filename)
        display_names.add(self.display_name)
        self.raw_traces    = format_traces(raw_traces)
        self._id = uuid.uuid4() 

        self.sampling_freq = sampling_freq
        self.dt            = (1.0/sampling_freq)*1000.0 # dt in ms
        if len(self.raw_traces):
            trace_length = len(self.raw_traces[0])
            self.times = numpy.arange(0, trace_length, 1)*self.dt
        else:
            self.times = None

        self.clustering        = StageData(self, name='clustering',       
                                           dependents=[])
        self.extraction        = StageData(self, name='extraction',       
                                           dependents=[self.clustering])
        self.detection         = StageData(self, name='detection',        
                                           dependents=[self.extraction])
        self.extraction_filter = StageData(self, name='extraction_filter',
                                           dependents=[self.extraction])
        self.detection_filter  = StageData(self, name='detection_filter', 
                                           dependents=[self.detection])

        self.clustering.set_prereqs([self.extraction])
        self.extraction.set_prereqs([self.extraction_filter, self.detection])
        self.detection.set_prereqs([self.detection_filter])

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

    def get_archive(self, archive_name='archive'):
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

    def get_data_from_stage(self, stage_name):
        stage_data = self.get_stage_data(stage_name)
        return_dict = {'method': stage_data.method,
                       'settings': stage_data.settings,
                       'results': stage_data.results}
        return return_dict

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

    def get_stages_that_are_ready_to_run(self):
        can_run_list = []
        for stage in self.stages:
            can_run = True
            for prereq in stage.prereqs:
                if prereq.results is None:
                    can_run = False
            if can_run:
                can_run_list.append(stage.name)
        return can_run_list

    def rename(self, new_display_name):
        display_names.remove(self.display_name)
        self.display_name = new_display_name
        display_names.remove(new_display_name)
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
                    save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, times = times, 
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
                    for trace in stage_data.results:
                        results.append(trace)
                    delimiter = text_delimiters[file_format]
                    save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, times=times,
                                detection_filtered_traces=stage_data.results)
                elif file_format == pt.MATLAB:
                    results = {'times': times,
                               'filtered_traces': stage_data.results}
                    scipy.io.savemat(fullpath, results)
            # EXPORT DETECTION STAGE
            if stage_name == 'detection':
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    save_list_txt(fullpath, stage_data.results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, 
                                spikes_detected=stage_data.results)
                elif file_format == pt.MATLAB:
                    results = {'spikes_detected': stage_data.results}
                    scipy.io.savemat(fullpath, results)
            # EXPORT EXTRACTION STAGE
            if stage_name == 'extraction':
                features = numpy.array(stage_data.results['features'])
                ft = numpy.array(stage_data.results['feature_times'])
                feature_times = ft.reshape(1,-1)
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    results = [ft]
                    for feature_set in features:
                        results.append(feature_set)
                    delimiter = text_delimiters[file_format]
                    save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, feature_sets=features,
                                          feature_times=feature_times)
                elif file_format == pt.MATLAB:
                    results = {'feature_sets': features,
                               'feature_times': feature_times}
                    scipy.io.savemat(fullpath, results)
            # EXPORT CLUSTERING STAGE
            if stage_name == 'clustering':
                clusters_keys = sorted(stage_data.results.keys())
                results = [stage_data.results[key] for key in clusters_keys]
                string_dict = {}
                for key in clusters_keys:
                    string_dict['cluster %d' % key] = stage_data.results[key]
                if (file_format == pt.PLAIN_TEXT_TABS or
                    file_format == pt.PLAIN_TEXT_SPACES or
                    file_format == pt.CSV ):
                    delimiter = text_delimiters[file_format]
                    save_list_txt(fullpath, results, 
                                  delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, **string_dict)
                elif file_format == pt.MATLAB:
                    scipy.io.savemat(fullpath, string_dict)


def zero_mean(trace_array):
    return trace_array - numpy.average(trace_array)


def format_traces(trace_list):
    array_trace_list = [zero_mean(numpy.array(trace,dtype=numpy.float64))
                        for trace in trace_list]
    traces = numpy.vstack(array_trace_list)
    return traces


class StageData(object):
    def __init__(self, trial, name=None, dependents=[], prereqs=[]):
        self.trial = trial
        self.name = name
        self.dependents = dependents
        self.prereqs = prereqs

        self.settings   = None
        self.method     = None
        self.results    = None

        self.reinitialize()

    def set_prereqs(self, prereqs):
        self.prereqs = prereqs
    
    def publish_reinitialized(self):
        pub.sendMessage(topic='STAGE_REINITIALIZED', 
                        data=(self.trial, self.name))

    def reinitialize(self):
        if self.results is not None:
            self.results  = None
            self.settings = None
            self.method   = None
            self.publish_reinitialized()
            for dependent in self.dependents:
                dependent.reinitialize()



import time
import datetime
import json
import os

import wx
from wx.lib.pubsub import Publisher as pub
import numpy

from spikepy.gui.strategy_manager import make_strategy
import spikepy.gui.program_text as pt

class Trial(object):
    """This class represents an individual trial consisting of (potentially)
    multiple electrodes recording simultaneously.
    """
    def __init__(self, sampling_freq=1.0, 
                       raw_traces=[], 
                       fullpath='FULLPATH NOT SET'):
        self.fullpath      = fullpath
        filename = os.path.split(fullpath)[1]
        self.display_name = filename
        self.raw_traces    = format_traces(raw_traces)

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

    def reset_stage_results(self, message=None):
        if message is not None:
            stage_data = getattr(self, message.data)
            stage_data.reset_results()

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
        self.display_name = new_display_name
        pub.sendMessage(topic='TRIAL_RENAMED', data=self)

    def export(self, path=None, stages_selected=[], 
                     store_arrays_as=None, file_format=None):
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
        fmt = '%1.10e'
        for stage_name in stages_selected:
            stage_data = self.get_stage_data(stage_name)
            extention = get_format_extention(file_format)
            filename = '%s-%s-results.%s' % (self.display_name, stage_name,
                                             extention)
            fullpath = os.path.join(path, filename)
            # filtering
            if 'filter' in stage_name:
                if file_format == pt.PLAIN_TEXT_SPACES:
                    delimiter = ' '
                    numpy.savetxt(fullpath, stage_data.results, 
                                  fmt=fmt, delimiter=delimiter)
                elif file_format == pt.PLAIN_TEXT_TABS:
                    delimiter = '\t'
                    numpy.savetxt(fullpath, stage_data.results, 
                                  fmt=fmt, delimiter=delimiter)
                elif file_format == pt.CSV:
                    delimiter = ','
                    numpy.savetxt(fullpath, stage_data.results, 
                                  fmt=fmt, delimiter=delimiter)
                elif file_format == pt.NUMPY_BINARY:
                    numpy.savez(fullpath, results=stage_data.results)
                elif file_format == pt.MATLAB:
                    pass
        pass

def get_format_extention(format):
    if (format == pt.PLAIN_TEXT_SPACES or
        format == pt.PLAIN_TEXT_TABS):
        return 'txt'
    if format == pt.CSV:
        return 'csv'
    if format == pt.MATLAB:
        return 'mat'
    if format == pt.NUMPY_BINARY:
        return 'npz'

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
            wx.CallLater(20, self.publish_reinitialized)
            self.results  = None
            self.settings = None
            self.method   = None
            for dependent in self.dependents:
                dependent.reinitialize()



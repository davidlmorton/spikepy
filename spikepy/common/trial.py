import time
import datetime
import json

from wx.lib.pubsub import Publisher as pub
import numpy

from spikepy.gui.strategy_manager import make_strategy


class Trial(object):
    """This class represents an individual trial consisting of (potentially)
    multiple electrodes recording simultaneously.
    """
    def __init__(self, sampling_freq=1.0, 
                       raw_traces=[], 
                       fullpath='FULLPATH NOT SET'):
        self.fullpath      = fullpath
        self.raw_traces    = format_traces(raw_traces)

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
        self.detection         = StageData(name='spike_detection',        
                                           dependents=[self.extraction])
        self.extraction_filter = StageData(name='extraction_filter',
                                           dependents=[self.extraction])
        self.detection_filter  = StageData(name='detection_filter', 
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

def zero_mean(trace_array):
    return trace_array - numpy.average(trace_array)


def format_traces(trace_list):
    array_trace_list = [zero_mean(numpy.array(trace,dtype=numpy.float64))
                        for trace in trace_list]
    traces = numpy.vstack(array_trace_list)
    return traces


class StageData(object):
    def __init__(self, name, dependents=[], prereqs=[]):
        self.name = name
        self.dependents = dependents
        self.prereqs = prereqs

        self.settings   = None
        self.method     = None
        self.results    = None

        self.reset_results()

    def set_prereqs(self, prereqs):
        self.prereqs = prereqs

    def reset_results(self, message=None):
        if self.results is not None:
            self.results  = None
            self.settings = None
            self.method   = None
            for dependent in self.dependents:
                dependent.reset_results()



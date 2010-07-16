import time
import datetime

from wx.lib.pubsub import Publisher as pub
import numpy


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

        self.detection_filter  = StageData(name='detection_filter', 
                                           dependents=['detection'])
        self.detection         = StageData(name='detection',        
                                           dependents=['extraction'])
        self.extraction_filter = StageData(name='extraction_filter',
                                           dependents=['extraction'])
        self.extraction        = StageData(name='extraction',       
                                           dependents=['clustering'])
        self.clustering        = StageData(name='clustering',       
                                           dependents=None)


def zero_mean(trace_array):
    return trace_array - numpy.average(trace_array)


def format_traces(trace_list):
    array_trace_list = [zero_mean(numpy.array(trace,dtype=numpy.float64))
                        for trace in trace_list]
    traces = numpy.vstack(array_trace_list)
    return traces


class StageData(object):
    def __init__(self, name, dependents):
        self.name = name
        self.dependents = dependents

        self.settings   = None
        self.method     = None
        self.results    = None

        self.reinitialize_results()
        pub.subscribe(self.reinitialize_results, 
                      topic='REINITIALIZE_%s' % name.upper())

    def reinitialize_results(self, message=None):
        if self.results is not None:
            self.results = None
            for dependent in self.dependents:
                pub.sendMessage(topic='REINITIALIZE_%s' % dependent.upper())



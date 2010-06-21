import time
import datetime

import numpy


class Trial(object):
    """This class represents an individual trial consisting of (potentially)
    multiple electrodes recording simultaneously.
    """
    def __init__(self):
        self.sampling_freq = 1.0
        self.time_collected = time.time() # right now
        self.fullpath = 'FULLPATH NOT SET'
        self.traces = {} # keys = 'raw', 'detection', 'extraction', 'others?'
        self.spikes = []
        self.features = []
        self.units = {} # XXX Flesh out later

    def set_traces(self, trace_list, 
                   sampling_freq=1.0, 
                   time_collected=time.time(), 
                   fullpath='FULLPATH NOT SET', 
                   trace_type='raw'):
        "Make this trace_list the trace set for this trial."
        self.traces[trace_type] = numpy.array(trace_list, dtype=numpy.float64)
        self.sampling_freq = sampling_freq
        self.time_collected = time_collected
        self.fullpath = fullpath

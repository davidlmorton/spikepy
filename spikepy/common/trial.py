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
        self.initialize_data()

    def set_traces(self, trace_list, 
                   sampling_freq=None, 
                   time_collected=None, 
                   fullpath=None, 
                   trace_type='raw'):
        "Make this trace_list the trace set for this trial."
        array_trace_list = [zero_mean(numpy.array(trace,dtype=numpy.float64))
                            for trace in trace_list]
        self.traces[trace_type.lower()] = numpy.vstack(
                                                     array_trace_list)

        if sampling_freq is not None:
            self.sampling_freq = sampling_freq
        if time_collected is not None:
            self.time_collected = time_collected
        if fullpath is not None:
            self.fullpath = fullpath

    def initialize_data(self, last_stage_completed=None):
        if last_stage_completed is not None:
            last_stage_completed = last_stage_completed.lower()
        if last_stage_completed is None:
            # keys = 'raw', 'detection', 'extraction', 'others?'
            self.traces = {} 
            # a list of (lists of spikes) equal in len to num electrodes
            self.spikes = []
            self.features = []
            self.units = {} 
        elif last_stage_completed == "detection filter":
            self.spikes = []
            self.features = []
            self.units = {}
        elif last_stage_completed == "detection":
            self.features = []
            self.units = {}
        elif last_stage_completed == "extraction filter":
            self.features = []
            self.units = {}
        elif last_stage_completed == "extraction":
            self.units = {}
        elif last_stage_completed == 'clustring':
            pass


def zero_mean(trace_array):
    return trace_array - numpy.average(trace_array)


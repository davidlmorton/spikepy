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

    def add_trace(self, trace):
        "Add a voltage trace which was recorded simultaneously with the others."
        if hasattr(self, 'traces'):
            self.traces = numpy.vstack([self.traces, trace])
        else:
            self.traces = numpy.array(trace, dtype=numpy.float64)

    def set_traces(self, trace_list, sampling_freq, time_collected, filename):
        "Make the trace_list given the voltage trace set for this trial."
        self.traces = numpy.array(trace_list, dtype=numpy.float64)
        self.sampling_freq = sampling_freq
        self.time_collected = time_collected
        self.filename = filename

    def __str__(self):
        if hasattr(self, 'traces'):
            str = "Trial collected at %s\n" %\
                  datetime.datetime.utcfromtimestamp(self.time_collected)
            str += "  with %d traces, %3.3f s sampled at %d Hz,\n" %\
                    (self.traces.shape[0], 
                     self.traces.shape[1]/float(self.sampling_freq),
                     self.sampling_freq)
            str += "  read in from file: %s" % self.filename
        else:
            str = "Trial with no traces... add traces with add_trace method."
        return str

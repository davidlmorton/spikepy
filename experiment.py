import os

import numpy

class Trial(object):
    """This class represents an individual trial consisting of (potentially)
    multiple electrodes recording simultaneously.
    """
    def __init__(self):
        self._voltage_traces = []

    def add_trace(self, trace):
        "Add a voltage trace which was recorded simultaneously with the others."
        self._voltage_traces.append(trace)
        self.traces = numpy.array(self._voltage_traces, dtype=numpy.float64)

    def set_traces(self, trace_list):
        "Make the trace_list given the voltage trace set for this trial."
        self._voltage_traces = trace_list
        self.traces = numpy.array(self._voltage_traces, dtype=numpy.float64)

    def __str__(self):
        str = "Trial with %d traces, %3.3f s sampled at %d Hz" %\
                (self.traces.shape[0], 
                 self.traces.shape[1]/float(self.sample_rate),
                 self.sample_rate)
        return str


class Experiment(list):
    """This class holds information about a single experiment consisting
    of multiple trials each with multiple electrodes.
    """
    def __init__(self):
        '''Tries to figure out what kind of data format is used and loads
        data.
        '''
        list.__init__(self)
        self.read_in_file = self.read_wessel_formatted_file

    def add_trial(self, filename):
        time_collected = os.stat(filename).st_ctime
        voltage_traces, sample_rate = self.read_in_file(filename)

        trial = Trial()
        trial.set_traces(voltage_traces)
        trial.time_collected = time_collected
        trial.sample_rate    = sample_rate
        trial.filename       = filename

        self.append( trial )

    def read_wessel_formatted_file(self, filename, 
                                   time_column=3, voltage_column=0):
        voltage_trace = []
        times = []
        with open(filename) as infile:
            for line in infile.readlines():
                tokens = line.split()
                voltage_trace.append( float(tokens[voltage_column]) )
                times.append( float(tokens[time_column]) )
        sample_rate = int(len(times)/times[-1]*1000) # 1000 because times in ms.

        return [voltage_trace], sample_rate

    def __str__(self):
        trials_string = ''.join([('    %d) ' % i) + str(t) + '\n' 
                                 for i,t in enumerate(self)])
        return "Experiment with %d trial(s):\n%s" % (len(self), trials_string)

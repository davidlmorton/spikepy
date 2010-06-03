import os

class Experiment(object):
    """This class holds information about a single experiment consisting
    of multiple trials each with multiple electrodes.
    """
    def __init__(self):
        '''Tries to figure out what kind of data format is used and loads
        data.
        '''
        self.trials = []
        self.read_in_file = self.read_wessel_formatted_file

    def add_trial(self, filename):
        voltage_traces, sample_rate, time_collected = self.read_in_file(
                                                                     filename)
        self.trials.append( {'electrodes':voltage_traces, 
                             'sample_rate':sample_rate,
                             'time_collected':time_collected} )

    def read_wessel_formatted_file(self, filename, 
                                   time_column=3, voltage_column=0):
        voltage_trace = []
        times = []
        with open(filename) as infile:
            for line in infile.readlines():
                tokens = line.split()
                voltage_trace.append( float(tokens[voltage_column]) )
                times.append( float(tokens[time_column]) )
        sample_rate = len(times)/times[-1]
        time_collected = os.stat(filename).st_ctime

        return [voltage_trace], sample_rate, time_collected


import gzip
import cPickle
import os

from spikepy.developer.file_interpreter import FileInterpreter, Trial

SHANK_CHANNEL_INDEX = [9,   8, 10,  7, 13,  4, 12,  5, 
                       15,  2, 16,  1, 14,  3, 11,  6]

class TurtleElectrophysiologyProject(FileInterpreter):
    def __init__(self):
        self.name = 'Archived TEP file'
        self.extentions = ['.gz', '.cPickle']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''An archived Turtle Electrophysiology Project file.'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.gz'):
            infile = gzip.open(fullpath, 'rb')
        else:
            infile = open(fullpath, 'rb')
        data = cPickle.load(infile)
        voltage_traces = data['voltage_traces']
        sampling_freq = data['sampling_freq']

        if len(voltage_traces) == 16:
            voltage_traces = voltage_traces[[i-1 for i in SHANK_CHANNEL_INDEX]]

        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]
        trials = [Trial.from_raw_traces(sampling_freq, voltage_traces, 
                                        origin=fullpath, 
                                        display_name=display_name)]
        return trials

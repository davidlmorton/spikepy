
import gzip
import cPickle
import os

import numpy

from spikepy.developer.file_interpreter import FileInterpreter, Trial

class WesselLabViewText(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView Pickle'
        self.extentions = ['.pgz', '.cPickle']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A pickled version of data acquired in the Wessel lab.'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.pgz'):
            infile = gzip.open(fullpath)
        else:
            infile = open(fullpath)
        data = cPickle.load(infile)
        voltage_trace = data['voltage_trace']
        sampling_freq = data['sampling_freq']

        display_name = os.path.splitext(os.path.split(fullpath)[-1])[0]
        trial = Trial.from_raw_traces(sampling_freq, [voltage_trace], 
                origin=fullpath, display_name=display_name)
        return [trial]

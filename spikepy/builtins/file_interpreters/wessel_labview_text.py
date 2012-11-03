
import gzip

import numpy

from spikepy.developer.file_interpreter import FileInterpreter

class Wessel_LabView_text(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView plain text'
        self.extentions = ['.wpt', '', '.gz']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A plain text file containing one trial.  Data are organized in columns.  Columns: 0=data(mV) 1=pulse_1 2=pulse_2 3=time(ms).'''

    def read_data_file(self, fullpath):
        if fullpath.endswith('.gz'):
            infile = gzip.open(fullpath)
        else:
            infile = open(fullpath)
        data = numpy.loadtxt(infile)
        raw_trace = data.T[0]
        times = data.T[3]
        sampling_freq = int((len(times)-1)/
                            (times[-1]-times[0])*1000) # 1000 kHz->Hz

        trials = [self.make_trial_object(sampling_freq, [raw_trace], fullpath)]
        return trials

import numpy

from spikepy.developer_tools.file_interpreter import FileInterpreter

class Wessel_LabView_text(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView plain text'
        self.extention = 'wpt'
        self.description = '''A plain text file containing one trial.  Data are organized in columns.  Columns: 0=data(mV) 1=pulse_1 2=pulse_2 3=time(ms).'''

    def read_data_file(self, fullpath):
        print "reading in data file"
        data = numpy.loadtxt(fullpath)
        raw_trace = data.T[0]
        times = data.T[3]
        sampling_freq = int(len(times)/(times[-1]-times[0])*1000) # 1000 kHz->Hz

        print "making trial objects"
        trials = [self.make_trial_object(sampling_freq, [raw_trace], fullpath)]
        print "made trial objects (%d)" % len(trials)
        return trials

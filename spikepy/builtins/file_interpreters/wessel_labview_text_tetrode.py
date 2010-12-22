import numpy

from spikepy.developer_tools.file_interpreter import FileInterpreter

class Wessel_LabView_text_tetrode(FileInterpreter):
    def __init__(self):
        self.name = 'Wessel LabView plain text tetrode'
        self.extention = 'tet'
        self.description = '''A plain text file containing one trial.  Data are organized in columns.  Columns: 0,1,2,3=data(mV) 4=pulse_1 5=pulse_2 6=time(ms).'''

    def read_data_file(self, fullpath):
        print "reading in data file"
        data = numpy.loadtxt(fullpath)
        raw_traces = data.T[:4]
        times = data.T[-1]
        sampling_freq = int(len(times)/(times[-1]-times[0])*1000) # 1000 kHz->Hz

        print "making trial objects"
        trials = [self.make_trial_object(sampling_freq, raw_traces, fullpath)]
        print "made trial objects (%d)" % len(trials)
        return trials

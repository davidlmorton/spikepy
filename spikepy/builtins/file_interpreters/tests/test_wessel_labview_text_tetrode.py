import unittest
import os

from spikepy.builtins.file_interpreters.wessel_labview_text_tetrode import \
    Wessel_LabView_text_tetrode
from spikepy.common.trial import Trial

base_directory = os.path.split(__file__)[0]
sample_data_fullpath = os.path.join(base_directory, 'sample_data_file.tet')

class ReadingSampleDataFile(unittest.TestCase):
    file_interpreter = Wessel_LabView_text_tetrode()
    trial_list = file_interpreter.read_data_file(sample_data_fullpath)
    trial = trial_list[0]

    def test_list_of_trial_objects(self):
        self.assertTrue(isinstance(self.trial_list, list))
        for trial in self.trial_list:
            self.assertTrue(isinstance(trial, Trial))

    def test_num_traces(self):
        self.assertTrue(len(self.trial.raw_traces)==4)

    def test_len_of_raw_traces(self):
        self.assertTrue(len(self.trial.raw_traces[0])==9)

    def test_sampling_freq(self):
        self.assertTrue(self.trial.sampling_freq==10000)

    def test_fullpath(self):
        self.assertTrue(self.trial.fullpath==sample_data_fullpath)

if __name__ == '__main__':
    unittest.main()

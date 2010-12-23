import unittest

from spikepy.builtins.file_interpreters.wessel_labview_text import \
    Wessel_LabView_text
from spikepy.common.trial import Trial

class ReadingSampleDataFile(unittest.TestCase):
    file_interpreter = Wessel_LabView_text()
    trial_list = file_interpreter.read_data_file('sample_data_file.wpt')
    trial = trial_list[0]

    def test_list_of_trial_objects(self):
        self.assertTrue(isinstance(self.trial_list, list))
        for trial in self.trial_list:
            self.assertTrue(isinstance(trial, Trial))

    def test_trial_properly_constructed(self):
        self.assertTrue(len(self.trial.raw_traces)==1)
        self.assertTrue(len(self.trial.raw_traces[0])==9)
        self.assertTrue(self.trial.sampling_freq==10000)
        self.assertTrue(self.trial.fullpath=='sample_data_file.wpt')

if __name__ == '__main__':
    unittest.main()

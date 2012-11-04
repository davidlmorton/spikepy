#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
import os

from spikepy.builtins.file_interpreters.wessel_labview_text import \
    Wessel_LabView_text
from spikepy.common.trial import Trial

base_directory = os.path.split(__file__)[0]
sample_data_fullpath = os.path.join(base_directory, 'sample_data_file.tet')

class ReadingSampleDataFile(unittest.TestCase):
    file_interpreter = Wessel_LabView_text()
    trial_list = file_interpreter.read_data_file(sample_data_fullpath)
    trial = trial_list[0]

    def test_list_of_trial_objects(self):
        self.assertTrue(isinstance(self.trial_list, list))
        for trial in self.trial_list:
            self.assertTrue(isinstance(trial, Trial))

    def test_num_traces(self):
        self.assertTrue(len(self.trial.raw_traces)==1)

    def test_len_of_raw_traces(self):
        self.assertTrue(len(self.trial.raw_traces[0])==9)

    def test_sampling_freq(self):
        self.assertTrue(self.trial.sampling_freq==10000)

    def test_fullpath(self):
        self.assertTrue(self.trial.fullpath==sample_data_fullpath)

if __name__ == '__main__':
    unittest.main()

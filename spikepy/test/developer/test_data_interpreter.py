
import os
import unittest

from spikepy.developer.data_interpreter import DataInterpreter
from spikepy.common.valid_types import ValidInteger

class DummyTrial(object):
    def __init__(self, display_name, trial_id):
        self.display_name = display_name
        self.trial_id = trial_id

class DummyResource(object):
    def __init__(self, data):
        self.data = data

class TestDataInterpreter(unittest.TestCase):
    def test_write_data_file(self):
        di = DataInterpreter()
        self.assertRaises(NotImplementedError, di.write_data_file, None)

    def test_construct_filenames(self):
        di = DataInterpreter()
        di.name = 'Some Name'
        trials = [DummyTrial('t1', 1), DummyTrial('t2', 2)]
        base_path = 'BASEPATH'
        f1 = 't1__Some_Name'
        f2 = 't2__Some_Name'
        expected = {1:os.path.join(base_path, f1), 
                    2:os.path.join(base_path, f2)}
        self.assertEquals(di.construct_filenames(trials, base_path), expected)

    def test_is_available(self):
        di = DataInterpreter()
        di.requires = ['a', 'b']
            
        t1 = DummyTrial('t1', 1)
        t1.a = DummyResource('data')
        t1.b = DummyResource('data')

        t2 = DummyTrial('t2', 2)
        t2.a = DummyResource('data')
        t2.b = DummyResource(None)

        t3 = DummyTrial('t3', 3)
        t3.a = DummyResource('data')

        ok_trials = [t1]
        bad_trials_1 = [t2]
        bad_trials_2 = [t3]
        bad_trials_3 = [t2, t3]
        bad_trials_4 = [t1, t2, t3]

        self.assertEquals(di.is_available(ok_trials), True)
        self.assertEquals(di.is_available(bad_trials_1), False)
        self.assertEquals(di.is_available(bad_trials_2), False)
        self.assertEquals(di.is_available(bad_trials_3), False)
        self.assertEquals(di.is_available(bad_trials_4), False)


if __name__ == '__main__':
    unittest.main()

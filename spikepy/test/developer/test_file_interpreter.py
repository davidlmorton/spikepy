
import unittest

from spikepy.developer.file_interpreter import FileInterpreter

class TestDataInterpreter(unittest.TestCase):
    def test_class_variables(self):
        fi = FileInterpreter()
        self.assertTrue(hasattr(fi, 'extentions'))
        self.assertTrue(hasattr(fi.extentions, '__iter__'))
        self.assertTrue(hasattr(fi, 'priority'))

    def test_read_data_file(self):
        fi = FileInterpreter()
        self.assertRaises(NotImplementedError, fi.read_data_file, None)


if __name__ == '__main__':
    unittest.main()

from spikepy.gui import utils

import unittest

class KnownColors(unittest.TestCase):
    known_colors = ( ("red",   [1,0,0]),
                     ("green", [0,1,0]),
                     ("blue",  [0,0,1])
                   )

    def test_named_color(self):
        '''
        named_color should give known rgb values given known color names.
        '''
        for name, rgb_val in self.known_colors:
            result = utils.named_color(name)
            self.assertEqual(rgb_val, result)

class BadInput(unittest.TestCase):
    def test_not_a_color(self):
        '''
        named_color should fail if given anything but a color name.
        '''
        self.assertRaises(ValueError, utils.named_color, 
                          "owl exterminators")


if __name__ == "__main__":
    unittest.main()

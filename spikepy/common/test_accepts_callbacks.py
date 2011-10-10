from accepts_callbacks import accepts_callbacks

def refoo(blah):
    print 'refoo %s' % blah
    return blah
import unittest

from accepts_callbacks import accepts_callbacks

class TestAcceptsCallbacksDecorator(unittest.TestCase):
    def test_register_pre_single_function(self):
        called_with = []
        def callback(*args, **kwargs):
            called_with.append((args, kwargs))

        @accepts_callbacks
        def foo(bar, baz='bone'):
            return (bar, baz)

        result = foo(10, 20)
        self.assertEquals(result, (10, 20))
        self.assertEquals(len(called_with), 0)

        foo.register_pre(callback)

        result = foo(10, 20)
        self.assertEquals(result, (10, 20))
        self.assertEquals(len(called_with), 1)
        self.assertEquals(called_with[0], ((10, 20), {}))

        result = foo(10, baz=20)
        self.assertEquals(result, (10, 20))
        self.assertEquals(len(called_with), 2)
        self.assertEquals(called_with[1], ((10,), {'baz':20}))

        



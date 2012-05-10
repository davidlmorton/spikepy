import unittest
import uuid

from spikepy.common.scheduler import Scheduler, Operation, OperationError
from spikepy.common import scheduler

class OperationTests(unittest.TestCase):
    def setUp(self):
        self.test_op = Operation([1,2,3,4], [3,4,5,6])
        
    def test_categories(self):
        finalizes = set([1,2])
        self.assertEqual(finalizes, self.test_op.finalizes)
        modifies = set([3,4])
        self.assertEqual(modifies, self.test_op.modifies)
        originates = set([5,6])
        self.assertEqual(originates, self.test_op.originates)

    def test_name(self):
        self.assertTrue(isinstance(self.test_op.name, uuid.UUID))
        op = Operation([],[],'test_name')
        self.assertEqual('test_name', op.name)

    def test_points(self):
        a = Operation([],[],'a')
        b = Operation([],[],'b')
        c = Operation([],[],'c')

        self.assertEqual(a.points_at, set())
        self.assertEqual(a.is_pointed_at_by, set())

        a.point_at(b)
        self.assertEqual(a.points_at, set([b]))
        self.assertEqual(a.is_pointed_at_by, set())
        self.assertEqual(b.points_at, set())
        self.assertEqual(b.is_pointed_at_by, set([a]))

        a.point_at(c)
        self.assertEqual(a.points_at, set([b,c]))
        self.assertEqual(a.is_pointed_at_by, set())
        self.assertEqual(b.points_at, set())
        self.assertEqual(b.is_pointed_at_by, set([a]))
        self.assertEqual(c.points_at, set())
        self.assertEqual(c.is_pointed_at_by, set([a]))

        c.point_at(a)
        self.assertEqual(a.points_at, set([b,c]))
        self.assertEqual(a.is_pointed_at_by, set([c]))
        self.assertEqual(b.points_at, set())
        self.assertEqual(b.is_pointed_at_by, set([a]))
        self.assertEqual(c.points_at, set([a]))
        self.assertEqual(c.is_pointed_at_by, set([a]))

        a.unpoint()
        self.assertEqual(a.points_at, set())
        self.assertEqual(a.is_pointed_at_by, set())
        self.assertEqual(b.points_at, set())
        self.assertEqual(b.is_pointed_at_by, set())
        self.assertEqual(c.points_at, set())
        self.assertEqual(c.is_pointed_at_by, set())

        self.assertRaises(OperationError, a.point_at, a)

class OperationFunctionsTests(unittest.TestCase):
    def setUp(self):
        a = Operation([],    [1],   'a')
        b = Operation([1,2], [2,3], 'b')
        c = Operation([2,3], [3,4], 'c')
        d = Operation([1], [5],   'd')
        e = Operation([3,4,5], [],    'e')

        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.operations = set([a,b,c,d,e])

    def test_find_xputs(self):
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        e = self.e

        desired_output = {
                1:{'originated_by':set([a]),
                   'modified_by':set(),
                   'finalized_by':set([b,d]) }, 
                2:{'originated_by':set(),
                   'modified_by':set([b]),
                   'finalized_by':set([c]) }, 
                3:{'originated_by':set([b]),
                   'modified_by':set([c]),
                   'finalized_by':set([e]) }, 
                4:{'originated_by':set([c]),
                   'modified_by':set(),
                   'finalized_by':set([e]) }, 
                5:{'originated_by':set([d]),
                   'modified_by':set(),
                   'finalized_by':set([e]) }}

        output = scheduler.find_xputs(self.operations)
        for key, value in desired_output.items():
            self.assertEqual(output[key], value)
        self.assertEqual(output, desired_output)

    def test_find_dependencies(self):
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        e = self.e

        desired_output = set([(a, b), (a, d), (b, c), (b, c), (c, e), 
                (d, e)])
        xputs = scheduler.find_xputs(self.operations)
        output = scheduler.find_dependencies(xputs)
        self.assertEqual(output, desired_output)

    def test_point_operations(self):
        scheduler.point_operations(self.operations)
        self.assertEqual(self.a.points_at, set([self.b,self.d]))
        self.assertEqual(self.b.points_at, set([self.c]))
        self.assertEqual(self.c.points_at, set([self.e]))
        self.assertEqual(self.d.points_at, set([self.e]))
        self.assertEqual(self.e.points_at, set())

    def test_find_impossible_operations(self):
        desired_output = set([self.b, self.c]) 
        self.assertEqual(scheduler.find_impossible_operations(self.operations), 
                desired_output)

    def test_clear_impossible_operations(self):
        desired_output = set([self.b, self.c, self.e])
        cleared_input = set([self.a, self.d])
        output = scheduler.clear_impossible_operations(self.operations)
        self.assertEqual(output, desired_output)
        self.assertEqual(self.operations, cleared_input)

    def test_find_ready_operations(self):
        fn = scheduler.find_ready_operations
        self.assertEqual(fn(self.operations), self.operations)

        self.a.point_at(self.b)
        self.assertEqual(set(fn(self.operations)), 
                self.operations-set([self.b]))

        self.a.point_at(self.c)
        self.a.point_at(self.d)
        self.a.point_at(self.e)
        self.b.point_at(self.a)
        self.assertEqual(fn(self.operations), set())

    def test_find_ready_lists(self):
        desired_output = [list(self.operations)]
        output = scheduler.find_ready_sets(self.operations)
        for i in range(len(desired_output)):
            d = desired_output[i]
            o = output[i]
            self.assertEqual(o, set(d))

        scheduler.point_operations(self.operations)
        desired_output = [[self.a], [self.b, self.d], [self.c],
                [self.e]]
        output = scheduler.find_ready_sets(self.operations)
        self.assertEqual(len(output), len(desired_output))
        for i in range(len(desired_output)):
            d = desired_output[i]
            o = output[i]
            self.assertEqual(o, set(d))
        


        

        


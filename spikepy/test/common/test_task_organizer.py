"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest

from spikepy.common.process_manager import Task, TaskOrganizer
from spikepy.common.trial_manager import Trial, Resource
from spikepy.test.common.test_task import FauxPlugin

class TaskOrganizerTests(unittest.TestCase):
    def setUp(self):
        trial_1 = Trial()
        trial_1.a = 'some_data'
        trial_1.b = 'some_other_data'
        trial_1.add_resource(Resource('c'))
        trial_1.add_resource(Resource('d'))

        plugin_1 = FauxPlugin(requires=['a', 'b'], provides=['c'])
        plugin_2 = FauxPlugin(requires=['a', 'c'], provides=['d'])
        plugin_bad_1 = FauxPlugin(requires=['a', 'b'], provides=['d'])
        plugin_bad_2 = FauxPlugin(requires=['a'], provides=['c', 'd', 'e'])

        t1_task = Task(trial_1, plugin_1)
        t2_task = Task(trial_1, plugin_2)
        bad_task_1 = Task(trial_1, plugin_bad_1)
        bad_task_2 = Task(trial_1, plugin_bad_2)

        self.trial_1 = trial_1 
        self.plugin_1 = plugin_1
        self.plugin_2 = plugin_2 
        self.t1_task = t1_task
        self.t2_task = t2_task
        self.bad_task_1 = bad_task_1
        self.bad_task_2 = bad_task_2

    def test_add_task_1(self):
        '''Add one task, then adding it again raises RuntimeError'''
        to = TaskOrganizer()
        self.assertEquals(len(to._task_index.keys()), 0)

        to.add_task(self.t1_task)
        self.assertTrue(self.t1_task in to._task_index.values())
        
        self.assertRaises(RuntimeError, to.add_task, self.t1_task)

    def test_add_task_2(self):
        '''Add multiple tasks, then adding bad tasks raises RuntimeError'''
        to = TaskOrganizer()
        to.add_task(self.t1_task)
        to.add_task(self.t2_task)
        self.assertTrue(self.t1_task in to._task_index.values())
        self.assertTrue(self.t2_task in to._task_index.values())
        self.assertEquals(len(to._task_index.values()), 2)
        
        self.assertRaises(RuntimeError, to.add_task, self.bad_task_1)
        self.assertRaises(RuntimeError, to.add_task, self.bad_task_2)

    def test_all_provided_items(self):
        "all_provided_items returns a list of all the items plugins provide."
        to = TaskOrganizer()
        self.assertEqual(len(to.all_provided_items), 0)

        to.add_task(self.t1_task)
        self.assertEqual(len(to.all_provided_items), 1)
        self.assertTrue(self.trial_1.c in to.all_provided_items)

        to.add_task(self.t2_task)
        self.assertEqual(len(to.all_provided_items), 2)
        self.assertTrue(self.trial_1.d in to.all_provided_items)

    def test_get_runnable_tasks_1(self):
        '''If no tasks left, get_runnable_tasks returns None'''
        to = TaskOrganizer()
        self.assertEqual(to.get_runnable_tasks(), None)

    def test_get_runnable_tasks_2(self):
        '''Returns only tasks who don't require what is provided later.'''
        to = TaskOrganizer()
        to.add_task(self.t1_task)
        to.add_task(self.t2_task)

        result1 = to.get_runnable_tasks()
        self.assertEqual(len(result1), 1)
        self.assertEqual(result1[0][1]['plugin'], self.plugin_1)

        # cannot get more runnable_tasks since haven't checked in results yet.
        result2 = to.get_runnable_tasks()
        self.assertEqual(len(result2), 0)

        # checkin results and requirements
        self.assertEqual(result1[0][0], self.t1_task)
        for item in self.t1_task.provides:
            item.checkin(key=self.t1_task._results_locking_keys[item])

        # still cannot get other task out, because we didn't check in any DATA.
        self.assertRaises(RuntimeError, to.get_runnable_tasks)

        # update the data in trial_1.c
        self.trial_1.c._data = 'something'

        # now can get other task out
        result3 = to.get_runnable_tasks()
        self.assertEqual(len(result3), 1)
        self.assertEqual(result3[0][1]['plugin'], self.plugin_2)


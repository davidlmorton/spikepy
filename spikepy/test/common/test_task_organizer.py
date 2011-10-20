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
from spikepy.common.errors import *

class TaskOrganizerTests(unittest.TestCase):
    def setUp(self):
        trial_1 = Trial()
        trial_1.a = 'some_data'
        trial_1.b = 'some_other_data'
        trial_1.add_resource(Resource('c'))
        trial_1.add_resource(Resource('d'))

        plugin_1 = FauxPlugin(requires=['a', 'b'], provides=['c'])
        plugin_2 = FauxPlugin(requires=['a', 'c'], provides=['d'])

        t1_task = Task(trial_1, plugin_1)
        t2_task = Task(trial_1, plugin_2)

        self.trial_1 = trial_1 
        self.plugin_1 = plugin_1
        self.plugin_2 = plugin_2 
        self.t1_task = t1_task
        self.t2_task = t2_task

    def test_add_task_1(self):
        '''Add one task'''
        to = TaskOrganizer()
        self.assertEquals(len(to._task_index.keys()), 0)

        to.add_task(self.t1_task)
        self.assertTrue(self.t1_task in to._task_index.values())

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
        self.assertEqual(result1[0].plugin, self.plugin_1)

        # cannot get more runnable_tasks since haven't checked in results yet.
        result2 = to.get_runnable_tasks()
        self.assertEqual(len(result2), 1)

        # TODO WRITE TESTS FOR PULL RUNNABLE TASKS 

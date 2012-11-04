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
import uuid

from spikepy.common.process_manager import Task
from spikepy.common.trial_manager import Trial, Resource
from spikepy.common.errors import *

class FauxPlugin(object):
    def __init__(self, requires, provides):
        self.name = 'Faux Plugin'
        self.requires = requires
        self.provides = provides
        self.is_stochastic = False
        self.is_pooling = False
        self.unpool_as = None
        self.silent_pooling = False

plugin_1 = FauxPlugin(requires=['ra', 'rb'],
                      provides=['pb', 'pa'])
plugin_2 = FauxPlugin(requires=['rb'],
                      provides=['ra', 'pa'])

trial_1 = Trial()
trial_1.add_resource(Resource('ra', data='some_data'))
trial_1.add_resource(Resource('rb'))

class TaskTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_constructor_1(self):
        '''Resources created on trial by task if plugin produces them.'''
        trial = Trial()
        self.assertFalse(hasattr(trial, 'pa'))
        self.assertFalse(hasattr(trial, 'pb'))

        task_1 = Task([trial], plugin_1, 'plugin_category')
        self.assertTrue(hasattr(trial, 'pa'))
        self.assertTrue(isinstance(trial.pa, Resource))
        self.assertTrue(hasattr(trial, 'pb'))
        self.assertTrue(isinstance(trial.pb, Resource))

    def test_constructor_2(self):
        '''task_id is constructed correctly.'''
        task_1 = Task([trial_1], plugin_1, 'plugin_category')
        self.assertTrue(isinstance(task_1.task_id, type(uuid.uuid4())))

    def test_provides(self):
        '''task.provides returns trial attributes in a list.'''
        task_1 = Task([trial_1], plugin_1, 'plugin_category')
        provides = task_1.provides
        self.assertTrue(trial_1.pb in provides)
        self.assertTrue(trial_1.pa in provides)
        self.assertEqual(len(provides), 2)

    def test_requires(self):
        '''task.requires returns trial attributes in a list.'''
        task_1 = Task([trial_1], plugin_1, 'plugin_category')
        requires = task_1.requires
        self.assertTrue(trial_1.rb in requires)
        self.assertTrue(trial_1.ra in requires)
        self.assertEqual(len(requires), 2)
        
    def test_get_args(self):
        '''_get_args checks out 'requirements' and returns them in a list.'''
        trial = Trial()
        trial.add_resource(Resource('ra', data='some_data'))
        trial.add_resource(Resource('rb'))
        task_1 = Task([trial], plugin_1, 'plugin_category')

        self.assertTrue(task_1.is_ready)

        result = task_1._get_args()

        self.assertTrue(task_1.is_ready)
        
        self.assertTrue('some_data' in result)
        self.assertTrue(trial.rb.data in result)
        self.assertEqual(len(result), 2)

    def test_get_run_info(self):
        trial = Trial()
        trial.add_resource(Resource('ra', data='some_data'))
        trial.add_resource(Resource('rb'))
        task_1 = Task([trial], plugin_1, 'plugin_category')

        self.assertTrue(task_1.is_ready)
        result = task_1.get_run_info()
        self.assertFalse(task_1.is_ready)

        self.assertEqual(len(task_1.locking_keys.keys()), 2)
        self.assertTrue(task_1.provides[0] in 
                task_1.locking_keys.keys())
        self.assertTrue(task_1.provides[1] in 
                task_1.locking_keys.keys())


        
        
        
        



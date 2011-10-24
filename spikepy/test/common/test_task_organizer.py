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

from spikepy.common.process_manager import Task, PoolingTask, TaskOrganizer
from spikepy.common.trial_manager import Trial, Resource
from spikepy.test.common.test_task import FauxPlugin
from spikepy.common.errors import *

def return_fake_results(to, task):
    fake_results = [1 for i in task.plugin.provides]
    to.complete_task(task, fake_results)
    

class TaskOrganizerTests(unittest.TestCase):
    def setUp(self):
        trials = [Trial() for i in range(2)]
        for trial in trials:
            trial.add_resource(Resource('pf', 1))
        dfp = FauxPlugin(requires=['pf'],       provides=['df'])
        dfp.name = 'dfp'
        sdp = FauxPlugin(requires=['df'],       provides=['ev'])
        sdp.name = 'sdp'
        efp = FauxPlugin(requires=['pf'],       provides=['ef'])
        efp.name = 'efp'
        fep = FauxPlugin(requires=['ef', 'ev'], provides=['f'])
        fep.name = 'fep'
        cp  = FauxPlugin(requires=['f'],        provides=['c'])
        cp.name = 'cp'
        cp.pooling = True

        crp  = FauxPlugin(requires=['ev', 'ef', 'c'],  provides=['c', 'cr'])
        crp.name = 'crp'
        crp.pooling = True
        esrp = FauxPlugin(requires=['ef'],             provides=['ef'])
        esrp.name = 'esrp'
        esrp2 = FauxPlugin(requires=['ef'],             provides=['ef'])
        esrp2.name = 'esrp2'
        spp  = FauxPlugin(requires=['ef', 'ev' , 'c'], provides=['sp'])
        spp.name = 'spp'

        plugins = [dfp, sdp, efp, fep, cp, crp, esrp, esrp2, spp]
        
        tasks = []
        for plugin in plugins:
            if not hasattr(plugin, 'pooling'):
                for trial in trials:
                    tasks.append(Task(trial, plugin))
            else:
                tasks.append(PoolingTask(trials, plugin))
                
                    
        self.dfp = dfp
        self.sdp = sdp
        self.efp = efp
        self.fep = fep
        self.cp = cp
        self.crp = crp
        self.esrp = esrp
        self.esrp2 = esrp2
        self.spp = spp
        self.trials = trials
        self.plugins = plugins
        self.tasks = tasks

    def test_add_task_1(self):
        '''Add tasks'''
        to = TaskOrganizer()
        for i, task in enumerate(self.tasks):
            self.assertEquals(len(to.tasks), i)

            to.add_task(task)
            self.assertTrue(task in to.tasks)
            self.assertEquals(len(to.tasks), i+1)

        # adding same task doesn't do anything.
        self.assertEquals(len(to.tasks), len(self.tasks))
        to.add_task(self.tasks[0])
        self.assertEquals(len(to.tasks), len(self.tasks))

    def test_pull_runnable_tasks(self):
        to = TaskOrganizer()
        for task in self.tasks:
            to.add_task(task)

        # batch one should be filtering and nothing else
        results = to.pull_runnable_tasks()
        pp = [task.plugin for task, info in results]
        print '1', [p.name for p in pp]
        self.assertTrue(self.dfp in pp)
        self.assertTrue(self.efp in pp)
        self.assertEquals(len(pp), 4) # 2 for each trial.

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])

        for task, info in results:
            return_fake_results(to, task)

        # batch 2 should be detection and upsampling.
        results = to.pull_runnable_tasks()

        pp = [task.plugin for task, info in results]
        print '2', [p.name for p in pp]
        self.assertTrue(self.esrp in pp or self.esrp2 in pp)
        self.assertTrue(self.sdp in pp)
        self.assertEquals(len(pp), 4) # 2 for each trial.

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])

        for task, info in results:
            return_fake_results(to, task)

        # batch 3 should more upsampling.
        results = to.pull_runnable_tasks()

        pp = [task.plugin for task, info in results]
        print '3', [p.name for p in pp]
        self.assertTrue(self.esrp in pp or self.esrp2 in pp)
        self.assertEquals(len(pp), 2) # 2 for each trial.

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])

        for task, info in results:
            return_fake_results(to, task)

        # batch 4 should be feature extraction.
        results = to.pull_runnable_tasks()

        pp = [task.plugin for task, info in results]
        print '4', [p.name for p in pp]
        self.assertTrue(self.fep in pp)
        self.assertEquals(len(pp), 2) # 2 for each trial.

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])
        
        for task, info in results:
            return_fake_results(to, task)

        # batch 5 should be clustering.
        results = to.pull_runnable_tasks()

        pp = [task.plugin for task, info in results]
        print '5', [p.name for p in pp]
        self.assertTrue(self.cp in pp)
        self.assertEquals(len(pp), 1) # 1 for each trial. (pooling)

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])

        for task, info in results:
            return_fake_results(to, task)

        # batch 6 should be clustering revision.
        results = to.pull_runnable_tasks()

        pp = [task.plugin for task, info in results]
        print '6', [p.name for p in pp]
        self.assertTrue(self.crp in pp)
        self.assertEquals(len(pp), 1) # 1 for each trial. (pooling)

        no_results = to.pull_runnable_tasks()
        self.assertEquals(no_results, [])

        for task, info in results:
            return_fake_results(to, task)


        


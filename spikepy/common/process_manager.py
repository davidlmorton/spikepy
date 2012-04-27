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
import uuid
import multiprocessing
import traceback
import time
from collections import defaultdict

import numpy

try:
    from callbacks import supports_callbacks
except ImportError:
    from spikepy.other.callbacks.callbacks import supports_callbacks

from spikepy.common.open_data_file import open_data_file
from spikepy.common.config_manager import config_manager
from spikepy.common.plugin_manager import plugin_manager
from spikepy.common.errors import *

def build_tasks(marked_trials, plugin, plugin_category, plugin_kwargs):
    tasks = []
    if not marked_trials:
        return tasks

    if plugin.is_pooling:
        tasks.append(Task(marked_trials, plugin, plugin_category, 
                plugin_kwargs))
    else:
        for trial in marked_trials:
            tasks.append(Task([trial], plugin, plugin_category, plugin_kwargs)) 
    return tasks 

def get_num_workers():
    '''
        Return the number of worker processes to spawn.  Number is
    determined based on cpu_count and the configuration variable:
    ['backend']['limit_num_processes']
    '''
    try:
        num_process_workers = multiprocessing.cpu_count()
    except NotImplimentedError:
        num_process_workers = 8

    processes_limit = config_manager['backend']['limit_num_processes']
    num_process_workers = min(num_process_workers, processes_limit)
    return num_process_workers

def open_file_worker(input_queue, results_queue):
    '''Worker process to handle open_file operations.'''
    for fullpath in iter(input_queue.get, None):
        file_interpreters = plugin_manager.file_interpreters
        try:
            results = open_data_file(fullpath, file_interpreters)
        except:
            results = []
            traceback.print_exc()
        results_queue.put(results)

def task_worker(input_queue, results_queue):
    '''Worker process to handle task operations.'''
    for task_info in iter(input_queue.get, None):
        args = task_info['args']
        kwargs = task_info['kwargs']
        stage_name = task_info['plugin_info']['stage']
        plugin_name = task_info['plugin_info']['name']
        plugin = plugin_manager.find_plugin(stage_name, plugin_name)

        results_dict = {}
        begin_time = time.time()
        try:
            results_dict['result'] = plugin.run(*args, **kwargs)
        except:
            results_dict['result'] = None
            results_dict['traceback'] = traceback.format_exc()
            traceback.print_exc()
        end_time = time.time()
        results_dict['task_id'] = task_info['task_id']
        results_dict['runtime'] = end_time - begin_time

        results_queue.put(results_dict)
    
class ProcessManager(object):
    '''
        ProcessManager handles all the multi-processing and task
    creation and management.
    '''
    def __init__(self, trial_manager):
        self.trial_manager  = trial_manager
        self._task_organizer = TaskOrganizer()

    def build_tasks_from_strategy(self, strategy, stage_name=None):
        '''Create a task for each stage of the strategy.'''
        tasks = []
        marked_trials = self.trial_manager.marked_trials

        if stage_name == 'auxiliary':
            for plugin_name, plugin_kwargs in strategy.auxiliary_stages.items():
                plugin = plugin_manager.find_plugin('auxiliary', 
                        plugin_name)
                if plugin.runs_with_stage == 'auxiliary':
                    tasks.extend(build_tasks(marked_trials, plugin, 
                            stage_name, plugin_kwargs))

        if stage_name is not None: 
            if stage_name != 'auxiliary':
                plugin_name = strategy.methods_used[stage_name]
                plugin = plugin_manager.find_plugin(stage_name,
                        plugin_name)
                plugin_kwargs = strategy.settings[stage_name]
                tasks.extend(build_tasks(marked_trials, plugin, 
                        stage_name, plugin_kwargs))
                    
                # get auxiliary stages that should run with this stage.
                for plugin_name, plugin_kwargs in \
                        strategy.auxiliary_stages.items():
                    plugin = plugin_manager.find_plugin('auxiliary', 
                            plugin_name)
                    if plugin.runs_with_stage == stage_name:
                        tasks.extend(build_tasks(marked_trials, plugin, 
                                'auxiliary', plugin_kwargs))
        else: # do for all stages
            for stage_name, plugin_name in strategy.methods_used.items():
                plugin = plugin_manager.find_plugin(stage_name, 
                        plugin_name)
                plugin_kwargs = strategy.settings[stage_name]
                tasks.extend(build_tasks(marked_trials, plugin, stage_name,
                        plugin_kwargs))

            for plugin_name, plugin_kwargs in strategy.auxiliary_stages.items():
                plugin = plugin_manager.find_plugin('auxiliary', 
                        plugin_name)
                tasks.extend(build_tasks(marked_trials, plugin, 
                        'auxiliary', plugin_kwargs))
        return tasks 

    def prepare_to_run_strategy(self, strategy, stage_name=None):
        '''
            Validate strategy, build tasks for it and put them in a 
        TaskOrganizer self._task_organizer. (see self.run_tasks()).
        '''
        plugin_manager.validate_strategy(strategy)
        tasks = self.build_tasks_from_strategy(strategy, stage_name=stage_name)
        for task in tasks:
            self._task_organizer.add_task(task)

    def run_tasks(self, message_queue=multiprocessing.Queue()):
        '''
            Run all the tasks in self._task_organizer 
        (see self.prepare_to_run_strategy()).
        '''
        num_process_workers = get_num_workers()
        num_tasks = self._task_organizer.num_tasks
        if num_tasks == 0:
            raise NoTasksError('There are no tasks to run')
        if num_tasks < num_process_workers:
            num_process_workers = num_tasks

        input_queue = multiprocessing.Queue()
        results_queue = multiprocessing.Queue()

        # start the jobs
        jobs = []
        results_list = []
        for i in xrange(num_process_workers):
            job = multiprocessing.Process(target=task_worker, 
                                          args=(input_queue, 
                                                results_queue))
            job.start()
            jobs.append(job)

        task_index = {}
        for task in self._task_organizer.tasks:
            task_index[task.task_id] = task
        message_queue.put(('TASKS', [str(t) for t in task_index.values()]))
            
        results_index = {}
        queued_tasks = 0
        while True:
            # queue up ready tasks
            pulled, skipped, impossible =\
                    self._task_organizer.pull_runnable_tasks()
            for task in impossible:
                message_queue.put(('IMPOSSIBLE_TASK', str(task)))
            for task in skipped:
                message_queue.put(('SKIPPED_TASK', str(task)))

            for task, task_info in pulled:
                message_queue.put(('RUNNING_TASK', str(task)))
                input_queue.put(task_info)
                queued_tasks += 1
            

            # wait for one result
            if queued_tasks > 0:
                result = results_queue.get()
                finished_task_id = result['task_id']
                finished_task = task_index[finished_task_id]
                results_index[finished_task_id] = result['result']
                if result['result'] is None:
                    message_queue.put(('TASK_ERROR', 
                            {'task':str(finished_task),
                             'traceback':result['traceback'],
                             'runtime':result['runtime']}))
                    finished_task.skip()
                    self._task_organizer.remove_tasks()
                else:
                    message_queue.put(('FINISHED_TASK', 
                            {'task':str(finished_task), 
                             'runtime':result['runtime']}))
                    finished_task.complete(result['result'])

            # are we done queueing up tasks? then add in the sentinals.
            if self._task_organizer.num_tasks == 0:
                for i in xrange(num_process_workers):
                    input_queue.put(None)
            
                # are we done getting results? then exit.
                if len(results_index.keys()) == queued_tasks:
                    break

        for job in jobs:
            job.join() # halt this thread until processes are all complete.
        message_queue.put(('FINISHED_RUN', None))

        return task_index, results_index

    def open_file(self, fullpath):
        '''
            Open a single data file. Returns the list of trials created.
        '''
        return self.open_files([fullpath])[0]

    @supports_callbacks
    def open_files(self, fullpaths):
        '''
            Open a multiple data files. Returns a list of 
        'list of trials created'.
        '''
        file_interpreters = plugin_manager.file_interpreters
        if len(fullpaths) == 1:
            try:
                results = open_data_file(fullpaths[0], file_interpreters)
            except:
                results = []
                traceback.print_exc()
            return results

        num_process_workers = get_num_workers()
        if len(fullpaths) < num_process_workers:
            num_process_workers = len(fullpaths)

        # setup the input and return queues.
        input_queue = multiprocessing.Queue()
        for fullpath in fullpaths:
            input_queue.put(fullpath)
        for i in xrange(num_process_workers):
            input_queue.put(None)
        results_queue = multiprocessing.Queue()

        # start the jobs
        jobs = []
        for i in xrange(num_process_workers):
            job = multiprocessing.Process(target=open_file_worker, 
                                          args=(input_queue, 
                                                results_queue))
            job.start()
            jobs.append(job)

        # collect the results, waiting for all the jobs to complete
        results_list = []
        for i in xrange(len(fullpaths)):
            # file_interpreters return list of trial objects.
            results_list.extend(results_queue.get())

        for job in jobs:
            job.join() # halt this thread until processes are all complete.

        return results_list


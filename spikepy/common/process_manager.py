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
import time

from callbacks import supports_callbacks

from spikepy.common.open_data_file import open_data_file
from spikepy.common.trial_manager import Resource 
from spikepy.common.errors import *

def build_tasks(marked_trials, plugin, plugin_kwargs):
    tasks = []
    if not marked_trials:
        return tasks

    if plugin.pooling:
        tasks.append(Task(marked_trials, plugin, plugin_kwargs))
    else:
        for trial in marked_trials:
            tasks.append(Task([trial], plugin, plugin_kwargs)) 
    return tasks 

def get_num_workers(config_manager):
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
    for run_data in iter(input_queue.get, None):
        fullpath, file_interpreters = run_data
        results_queue.put(open_data_file(fullpath, file_interpreters))

def task_worker(input_queue, results_queue):
    '''Worker process to handle task operations.'''
    for task_info in iter(input_queue.get, None):
        args = task_info['args']
        kwargs = task_info['kwargs']
        plugin = task_info['plugin']

        results_dict = {}
        results_dict['result'] = plugin.run(*args, **kwargs)
        #results_dict['result'] = [time.time() for i in plugin.provides]
        results_dict['task_id'] = task_info['task_id']

        results_queue.put(results_dict)
    
class ProcessManager(object):
    '''
        ProcessManager handles all the multi-processing and task
    creation and management.
    '''
    def __init__(self, config_manager, trial_manager, plugin_manager):
        self.config_manager = config_manager
        self.trial_manager  = trial_manager
        self.plugin_manager = plugin_manager
        self._task_organizer = TaskOrganizer()

    def build_tasks_from_strategy(self, strategy, stage_name=None):
        '''Create a task for each stage of the strategy.'''
        tasks = []
        marked_trials = self.trial_manager.marked_trials

        if stage_name == 'auxiliary' or stage_name is None:
            for plugin_name, plugin_kwargs in strategy.auxiliary_stages.items():
                plugin = self.plugin_manager.find_plugin('auxiliary', 
                        plugin_name)
                tasks.extend(build_tasks(marked_trials, plugin, plugin_kwargs))

        if stage_name is not None: 
            if stage_name != 'auxiliary':
                plugin_name = strategy.methods_used[stage_name]
                plugin = self.plugin_manager.find_plugin(stage_name,
                        plugin_name)
                plugin_kwargs = strategy.settings[stage_name]
                tasks.extend(build_tasks(marked_trials, plugin, plugin_kwargs))
        else: # do for all stages
            for stage_name, plugin_name in strategy.methods_used.items():
                plugin = self.plugin_manager.find_plugin(stage_name, 
                        plugin_name)
                plugin_kwargs = strategy.settings[stage_name]
                tasks.extend(build_tasks(marked_trials, plugin, plugin_kwargs))
        return tasks 

    def prepare_to_run_strategy(self, strategy, stage_name=None):
        '''
            Validate strategy, build tasks for it and put them in a 
        TaskOrganizer self._task_organizer. (see self.run_tasks()).
        '''
        self.plugin_manager.validate_strategy(strategy)
        tasks = self.build_tasks_from_strategy(strategy, stage_name=stage_name)
        for task in tasks:
            self._task_organizer.add_task(task)

    def run_tasks(self, message_queue=multiprocessing.Queue()):
        '''
            Run all the tasks in self._task_organizer 
        (see self.prepare_to_run_strategy()).
        '''
        num_process_workers = get_num_workers(self.config_manager)
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
            
        results_index = {}
        queued_tasks = 0
        while True:
            # queue up ready tasks
            for task, task_info in self._task_organizer.pull_runnable_tasks():
                message_queue.put(('Added task to input_queue.', task))
                print "RUNNING: %s on %s" % (task.plugin.name,
                        [t.display_name for t in task.trials])
                input_queue.put(task_info)
                queued_tasks += 1

            # wait for one result
            if queued_tasks > 0:
                result = results_queue.get()
                finished_task_id = result['task_id']
                finished_task = task_index[finished_task_id]
                results_index[finished_task_id] = result['result']
                message_queue.put(('Recieved task results', finished_task))
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
        num_process_workers = get_num_workers(self.config_manager)
        if len(fullpaths) < num_process_workers:
            num_process_workers = len(fullpaths)

        file_interpreters = self.plugin_manager.file_interpreters

        # setup the input and return queues.
        input_queue = multiprocessing.Queue()
        for fullpath in fullpaths:
            input_queue.put((fullpath, file_interpreters))
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

class TaskOrganizer(object):
    '''
        TaskOrganizers take a number of Tasks and allow you to get the ones
    ready to run.
    '''
    def __init__(self):
        self._non_stationary_tasks = {}
        self._stationary_tasks = {}

    @property
    def num_tasks(self):
        num_ns = len(self._non_stationary_tasks.keys())
        num_s = len(self._stationary_tasks.keys())
        return num_ns + num_s

    @property
    def tasks(self):
        return (self._non_stationary_tasks.values() + 
                self._stationary_tasks.values())

    def __str__(self):
        str_list = ['TaskOrganizer:']
        for task in self.tasks:
            str_list.append('    %s' % str(task))
        return '\n'.join(str_list)

    def pull_runnable_tasks(self):
        '''
            Return a list of (task, task_info) tuples for each runnable task 
        and remove those tasks from the organizer.
        '''
        results = []

        task_list = [task for task in self._stationary_tasks.values()]
        task_list += [task for task in self._non_stationary_tasks.values()]
        for task in task_list:
            all_provided_items = []
            for ttask in self._non_stationary_tasks.values():
                all_provided_items.extend(ttask.provides)
            can_run = True

            # do you require something that someone here will later provide?
            for req in task.requires:
                if req in all_provided_items:
                    can_run = False
                    break

            # do you require or provide something that is locked?
            if not task.is_ready:
                can_run = False

            # do you require something never set?
            if can_run:
                for item in task.requires:
                    if item.data is None:
                        raise ImpossibleTaskError('Cannot execute %s because it requires something that will not be set by any task in this set.' % task)

            if can_run:
                (co_task, co_task_info) = self.checkout_task(task)
                if co_task.would_generate_unique_results:
                    results.append((co_task, co_task_info))
                else:
                    co_task.skip()
                
        return results

    def checkout_task(self, task):
        task_id = task.task_id
        if task_id in self._stationary_tasks.keys():
            del self._stationary_tasks[task_id]
        if task_id in self._non_stationary_tasks.keys():
            del self._non_stationary_tasks[task_id]
        return (task, task.get_run_info())

    def add_task(self, new_task):
        ''' Add a task to the TaskOrganizer.  '''
        if set(new_task.provides).intersection(set(new_task.requires)):
            self._stationary_tasks[new_task.task_id] = new_task
        else:
            self._non_stationary_tasks[new_task.task_id] = new_task


class Task(object):
    '''
        Task objects combine a list of trials with a plugin and
    the kwargs that the plugin needs to run.
    '''
    def __init__(self, trials, plugin, plugin_kwargs={}):
        self.trials = trials
        trial_ids = [t.trial_id for t in trials]
        self.task_id = uuid.uuid4()
        self.plugin = plugin
        self.plugin_kwargs = plugin_kwargs
        self.locking_keys = {}
        self._prepare_trials_for_task()

    def __str__(self):
        str_list = ['Task: plugin="%s"' % self.plugin.name]
        for trial in self.trials:
            str_list.append('        trial="%s"' % trial.display_name)
        return '\n'.join(str_list)

    def _prepare_trials_for_task(self):
        '''
            If the trials do not have one of the resources that the plugin
        provides, create it.
        '''
        for trial in self.trials:
            for item in self.plugin.provides:
                if not hasattr(trial, item):
                    trial.add_resource(Resource(item))
                elif not isinstance(getattr(trial, item), Resource):
                    raise TaskCreationError('This plugin provides %s, but that is a read-only attribute on trial %s.' % (item, trial.trial_id))

    @property
    def would_generate_unique_results(self):
        if self.plugin.is_stochastic:
            return True
        else:
            old_results = self.provides
            # if by is different, return True
            for old_result in old_results:
                if old_result.change_info['by'] != self.plugin.name:
                    return True

            # if kwargs are different, return True
            for old_result in old_results:
                w = old_result.change_info['with']
                if self.change_info['with'] != w:
                    return True

            # if any of the args are different, return True
            for old_result in old_results:
                using = old_result.change_info['using']
                for arg_name in self.plugin.requires:
                    arg_info = []
                    for trial in self.trials:
                        arg = getattr(trial, arg_name)
                        arg_info.append((trial.trial_id, arg_name, 
                                arg.change_info['change_id']))

                    if arg_info not in using:
                        return True
            return False

    @property
    def change_info(self):
        return_dict = {}
        return_dict['by'] = self.plugin.name
        return_dict['with'] = self.plugin_kwargs
        u = []
        for rname in self.plugin.requires:
            pu = []
            for trial in self.trials:
                r = getattr(trial, rname)
                if not hasattr(r, 'change_info'):
                    pu.append((trial.trial_id, rname))
                else:
                    rchange_id = r.change_info['change_id']
                    pu.append((trial.trial_id, rname, rchange_id))
            u.append(pu)
        return_dict['using'] = u
        return return_dict

    @property
    def is_ready(self):
        '''
            Return True if this task's requirements and resources it provides
        are all unlocked.
        '''
        # once all the plugin's requirements are ready, we're ready.
        items = self.requires + self.provides
        for item in items:
            if (hasattr(item, 'is_locked') and item.is_locked):
                return False
        return True

    @property
    def provides(self):
        '''Return the trial attributes we provide after running.'''
        result = []
        for trial in self.trials:
            for item in self.plugin.provides:
                result.append(getattr(trial, item))
        return result

    @property
    def requires(self):
        '''Return the trial attributes we require to run.'''
        result = []
        for trial in self.trials:
            for item in self.plugin.requires:
                result.append(getattr(trial, item))
        return result

    def skip(self):
        for pname in self.plugin.provides:
            for trial in self.trials:
                item = getattr(trial, pname)
                key = self.locking_keys[item]
                item.checkin(key=key)

    def complete(self, result):
        change_info = self.change_info
        for pname, presult in zip(self.plugin.provides, result):
            if len(self.trials) == 1 and not self.plugin.pooling:
                presult = [presult]
            for trial, tresult in zip(self.trials, presult):
                item = getattr(trial, pname)
                key = self.locking_keys[item]
                data_dict = {'data':tresult,
                             'change_info':change_info}
                item.checkin(data_dict, key=key) 

    def get_run_info(self):
        '''
        Return a dictionary with the stuff needed to run.
        '''
        run_info = {}
        run_info['task_id'] = self.task_id
        run_info['plugin'] = self.plugin
        run_info['args'] = self._get_args()
        run_info['kwargs'] = self.plugin_kwargs

        # check out and keep track of locking keys for what task provides.
        for item in self.provides:
            co = item.checkout()
            self.locking_keys[item] = co['locking_key']
        return run_info

    def _get_args(self):
        '''Return the data we require as arguments to run.'''
        arg_list = []
        for requirement_name in self.plugin.requires:
            if not self.plugin.pooling:
                trial = self.trials[0]
                requirement = getattr(trial, requirement_name)
                if isinstance(requirement, Resource):
                    arg = requirement.data
                else:
                    arg = requirement
                arg_list.append(arg)
            else:
                args = []
                for trial in self.trials:
                    requirement = getattr(trial, requirement_name)
                    if isinstance(requirement, Resource):
                        arg = requirement.data
                    else:
                        arg = requirement
                    args.append(arg)
                arg_list.append(args)
        return arg_list
        
    

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
import multiprocessing

from spikepy.common.open_data_file import open_data_file
from spikepy.common.trial_manager import Resource 

def get_num_workers(config_manager):
    try:
        num_process_workers = multiprocessing.cpu_count()
    except NotImplimentedError:
        num_process_workers = 8

    processes_limit = config_manager['backend']['limit_num_processes']
    num_process_workers = min(num_process_workers, processes_limit)
    return num_process_workers

def open_file_worker(input_queue, results_queue):
    for run_data in iter(input_queue.get, None):
        fullpath, file_interpreters = run_data
        results_queue.put(open_data_file(fullpath, file_interpreters))
    
class ProcessManager(object):
    def __init__(self, config_manager, trial_manager, plugin_manager):
        self.config_manager = config_manager
        self.trial_manager  = trial_manager
        self.plugin_manager = plugin_manager

    def open_file(self, fullpath, created_trials_callback):
        return self.open_files([fullpath], created_trials_callback)[0]

    def open_files(self, fullpaths, created_trials_callback):
        num_process_workers = get_num_workers(self.config_manager)
        if len(fullpaths) < num_process_workers:
            num_process_workers = len(fullpaths)

        file_interpreters = self.plugin_manager.file_interpreters

        # setup the run and return queues.
        input_queue = multiprocessing.Queue()
        for fullpath in fullpaths:
            input_queue.put((fullpath, file_interpreters))
        for i in xrange(num_process_workers):
            input_queue.put(None)
        results_queue = multiprocessing.Queue()

        jobs = []
        for i in xrange(num_process_workers):
            job = multiprocessing.Process(target=open_file_worker, 
                                          args=(input_queue, 
                                                results_queue))
            job.start()
            jobs.append(job)

        results_list = []
        for i in xrange(len(fullpaths)):
            results_list.append(results_queue.get())

        for job in jobs:
            job.join() # halt this thread until processes are all complete.

        for result in results_list:
            created_trials_callback(result)

        return results_list

class TaskOrganizer(object):
    def __init__(self):
        self._task_index = {}

    @property
    def all_provided_items(self):
        result = []
        for task in self._task_index.values():
            result.extend(task.provides)
        return result

    def get_runnable_tasks(self):
        if not self._task_index.keys():
            return None # No tasks left.
        # begin with all tasks, then eliminate ineligible tasks.
        available_tasks = self._task_index.values()
        results = []
        for task in available_tasks:
            can_run = True

            # do you require something that someone here will later provide?
            if set(task.requires).intersection(set(self.all_provided_items)):
                can_run = False

            # do you require something that is locked?
            if not task.is_ready:
                can_run = False

            # do you require something not provided and never set?
            if can_run:
                for item in task.requires:
                    if hasattr(item, 'data') and item.data is None:
                        raise RuntimeError('Cannot execute task %s because it requires something that will not be set by any task in this set.' % task)

            # all tests have passed, so get ready to run.
            if can_run:
                del self._task_index[task.task_id]
                results.append((task, task.get_run_info()))
            
        return results

    def add_task(self, new_task):
        if self.all_provided_items:
            intersection = set(new_task.provides).intersection(
                    set(self.all_provided_items))
        else:
            intersection = False

        if intersection:
            raise RuntimeError('Cannot add task %s as it provides (%s) which is(are) already provided.' % (new_task, intersection))
        else:
            self._task_index[new_task.task_id] = new_task


class Task(object):
    '''
        Task objects combine a trial with a plugin and the kwargs that the 
    plugin needs to run.
    '''
    def __init__(self, trial, plugin, plugin_kwargs={}):
        self.trial = trial
        self.task_id = (trial.trial_id, tuple(sorted(plugin.provides)))
        self.plugin = plugin
        self.plugin_kwargs = plugin_kwargs
        self._arg_locking_keys = {}
        self._results_locking_keys = {}
        self._prepare_trial_for_task()

    def _prepare_trial_for_task(self):
        '''
            If the trial does not have one of the resources that the plugin
        provides, create it.
        '''
        for item in self.plugin.provides:
            if not hasattr(self.trial, item):
                self.trial.add_resource(Resource(item))
            elif not isinstance(getattr(self.trial, item), Resource):
                raise RuntimeError('This plugin provides %s, but that is a read-only attribute on trial %s.' % (item, self.trial.trial_id))

    @property
    def is_ready(self):
        '''Return True if this task's requirements are all unlocked'''
        # once all the plugin's requirements are ready, we're ready.
        for requirement_name in self.plugin.requires:
            requirement = getattr(self.trial, requirement_name)
            if (hasattr(requirement, 'is_locked') and
                requirement.is_locked):
                return False
        return True

    @property
    def provides(self):
        '''Return the trial attributes we provide after running.'''
        result = []
        for item in self.plugin.provides:
            result.append(getattr(self.trial, item))
        return result

    @property
    def requires(self):
        '''Return the trial attributes we require to run.'''
        result = []
        for item in self.plugin.requires:
            result.append(getattr(self.trial, item))
        return result

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
            self._results_locking_keys[item.name] = co['locking_key']
        return run_info

    def _get_args(self):
        '''
            Return the data we require as arguments to run.  Check out
        data from the trial if it is a resource.
        '''
        args = []
        for requirement_name in self.plugin.requires:
            requirement = getattr(self.trial, requirement_name)
            if hasattr(requirement, 'checkout'):
                co = requirement.checkout()
                self._arg_locking_keys[requirement_name] = co['locking_key']
                arg = co['data']
            else:
                arg = requirement
            args.append(arg)
        return args

    def release_args(self):
        '''Check in the requirements we checked out from the trial.'''
        for requirement_name in self._arg_locking_keys.keys():
            key = self._arg_locking_keys[requirement_name]
            del self._arg_locking_keys[requirement_name]
            requirement = getattr(self.trial, requirement_name)
            requirement.checkin(key=key)
        
        
            
        
    

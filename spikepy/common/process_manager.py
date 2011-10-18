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
import time

from callbacks import supports_callbacks

from spikepy.common.open_data_file import open_data_file
from spikepy.common.trial_manager import Resource 

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
        #results_dict['result'] = plugin.run(*args, **kwargs)
        results_dict['result'] = [time.time() for i in plugin.provides]
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

    def build_tasks_from_strategy(self, strategy):
        '''Create a task for each stage of the strategy.'''
        tasks = []
        marked_trials = self.trial_manager.get_marked_trials()
        for stage_name, plugin_name in strategy.methods_used.items():
            plugin = self.plugin_manager.find_plugin(stage_name, 
                    plugin_name)
            plugin_kwargs = strategy.settings[stage_name]
            if stage_name == 'clustering':
                tasks.append(PoolingTask(marked_trials, plugin, plugin_kwargs))
            else:
                for trial in marked_trials:
                    tasks.append(Task(trial, plugin, plugin_kwargs)) 
        return tasks 

    def prepare_to_run_strategy(self, strategy):
        '''
            Validate strategy, build tasks for it and put them in a 
        TaskOrganizer self._task_organizer. (see self.run_tasks()).
        '''
        self.plugin_manager.validate_strategy(strategy)
        tasks = self.build_tasks_from_strategy(strategy)
        for task in tasks:
            self._task_organizer.add_task(task)

    def run_tasks(self, message_queue=multiprocessing.Queue()):
        '''
            Run all the tasks in self._task_organizer 
        (see self.prepare_to_run_strategy()).
        '''
        num_process_workers = get_num_workers(self.config_manager)
        num_tasks = self._task_organizer.num_tasks
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
        while True:
            # queue up ready tasks
            for task, task_info in self._task_organizer.pull_runnable_tasks():
                message_queue.put(('Added task to input_queue.', task))
                input_queue.put(task_info)

            # wait for one result
            result = results_queue.get()
            finished_task_id = result['task_id']
            finished_task = task_index[finished_task_id]
            results_index[finished_task_id] = result['result']
            message_queue.put(('Recieved task results', finished_task))
            self._recieve_result(result['result'], finished_task)

            # are we done queueing up tasks? then add in the sentinals.
            if self._task_organizer.num_tasks == 0:
                for i in xrange(num_process_workers):
                    input_queue.put(None)
            
            # are we done getting results? then exit.
            if len(results_index.keys()) == num_tasks:
                break

        for job in jobs:
            job.join() # halt this thread until processes are all complete.

        return task_index, results_index

    def _recieve_result(self, result, task):
        if isinstance(task, PoolingTask):
            pass
        else:
            change_info = task.change_info
            if len(task.plugin.provides) == 1:
                result = [result]
            for pname, presult in zip(task.plugin.provides, result):
                key = task.locking_keys[pname]
                data_dict = {'data':presult,
                             'change_info':change_info}
                resource = getattr(task.trial, pname)
                resource.checkin(data_dict, key=key) 


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
        self._task_index = {}

    @property
    def num_tasks(self):
        return len(self._task_index.keys())

    @property
    def tasks(self):
        return self._task_index.values()

    def __str__(self):
        str_list = ['TaskOrganizer:']
        for task in self._task_index.values():
            str_list.append('    %s' % str(task))
        return '\n'.join(str_list)

    @property
    def all_provided_items(self):
        '''All the items provided by all the tasks.'''
        result = []
        for task in self._task_index.values():
            result.extend(task.provides)
        return result

    def get_runnable_tasks(self):
        ''' Return a list of tasks that are ready to be run.  '''
        if not self._task_index.keys():
            return None # No tasks left.
        # begin with all tasks, then eliminate ineligible tasks.
        available_tasks = self._task_index.values()
        results = []
        for task in available_tasks:
            can_run = True

            # do you require something that someone here will later provide?
            for pi in self.all_provided_items:
                for req in task.requires:
                    if req is pi:
                        can_run = False

            # do you require something that is locked?
            if not task.is_ready:
                can_run = False

            # do you require something not provided and never set?
            if can_run:
                for item in task.requires:
                    if hasattr(item, 'data') and item.data is None:
                        raise ImpossibleTaskError('Cannot execute %s because it requires something that will not be set by any task in this set.' % task)

            if can_run:
                results.append(task)
        return results

    def pull_runnable_tasks(self):
        '''
            Return a list of (task, task_info) tuples for each runnable task 
        and remove those tasks from the organizer.
        '''
        results = []
        for task in self.get_runnable_tasks():
            del self._task_index[task.task_id]
            results.append((task, task.get_run_info()))
        return results

    def add_task(self, new_task):
        '''
            Add a task to the TaskOrganizer.  Tasks must not provide anything
        that other tasks already provide.
        '''
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
        self.locking_keys = {}
        self._prepare_trial_for_task()

    def __str__(self):
        return 'Task: plugin="%s" trial="%s"' % (self.plugin.name,
                self.trial.display_name)

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
    def change_info(self):
        return_dict = {}
        return_dict['by'] = self.plugin.name
        return_dict['with'] = self.plugin_kwargs
        u = []
        for rname in self.plugin.requires:
            r = getattr(self.trial, rname)
            if not hasattr(r, 'change_info'):
                u.append((self.trial.trial_id, rname))
            else:
                rchange_id = r.change_info['change_id']
                u.append((self.trial.trial_id, rname, rchange_id))
        return_dict['using'] = u
        return return_dict

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
            self.locking_keys[item.name] = co['locking_key']
        return run_info

    def _get_args(self):
        '''Return the data we require as arguments to run.'''
        args = []
        for requirement_name in self.plugin.requires:
            requirement = getattr(self.trial, requirement_name)
            if isinstance(requirement, Resource):
                arg = requirement.data
            else:
                arg = requirement
            args.append(arg)
        return args


class PoolingTask(object):
    '''
        PoolingTask objects combine a list of trials with a plugin and
    the kwargs that the plugin needs to run.
    '''
    def __init__(self, trials, plugin, plugin_kwargs={}):
        self.trials = trials
        trial_ids = [t.trial_id for t in trials]
        self.task_id = (tuple(trial_ids), tuple(sorted(plugin.provides)))
        self.plugin = plugin
        self.plugin_kwargs = plugin_kwargs
        self.locking_keys = {}
        self._prepare_trials_for_task()

    def __str__(self):
        str_list = ['PoolingTask: plugin="%s"' % self.plugin.name]
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
                    raise RuntimeError('This plugin provides %s, but that is a read-only attribute on trial %s.' % (item, trial.trial_id))

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
            self.locking_keys[item.name] = co['locking_key']
        return run_info

    def _get_args(self):
        '''Return the data we require as arguments to run.'''
        arg_list = []
        for requirement_name in self.plugin.requires:
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
        
    

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

class ProcessOrganizer(object):
    def __init__(self):
        self.process_index = {}

    def add_process(self, )
        # TODO finish

class Process(object):
    def __init__(self, trial, plugin, plugin_kwargs={}):
        self.trial = trial
        self.plugin = plugin
        self.plugin_kwargs = plugin_kwargs
        self._arg_locking_keys = {}

    def is_ready(self):
        # once all the plugin's requirements are ready, we're ready.
        for requirement_name in self.plugin.requires:
            requirement = getattr(self.trial, requirement_name)
            if (hasattr(requirement, 'is_locked') and
                requirement.is_locked):
                return False

    def get_run_info(self):
        run_info = {}
        run_info['plugin'] = self.plugin
        run_info['args'] = self._get_args()
        run_info['kwargs'] = self.plugin_kwargs
        return run_info

    def _get_args(self):
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
        for requirement_name, key in self._arg_locking_keys.items():
            requirement = getattr(self.trial, requirement_name)
            requirement.checkin(key=key)
        
        
            
        
    

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
from collections import defaultdict
import time

class NonPluginJob(Job):
        
class PluginJob(Job):

class Job(object):
    def __init__(self, stage_name=None, trial_ids=[], requires=[],
                       run_dict={}, job_name=None, job_id=None):
        self.stage_name = stage_name
        self.trial_ids = trial_ids
        self.requires = requires
        self.provides = provides
        self.job_name = job_name
        self.job_id = job_id
        self._start_time = None
        self._end_time = None
        self.run_dict = run_dict

    def set_start_time(self):
        self._start_time = time.time()

    def set_end_time(self):
        self._end_time = time.time()

    def get_run_time(self):
        if self._start_time is None:
            return None
        if self._end_time is not None:
            return self._end_time - self._start_time
        else:
            return time.time() - self._start_time

    def get_run_time_as_string(self):
        run_time = self.get_run_time()
        if run_time is None:
            return ''
        else:
            ss = int(run_time * 100) % 100
            s = int(run_time) % 60
            m = int(run_time/60) % 60
            h = int(run_time/3600)
            return "%2d:%02d:%02d:%02d" % (h, m, s, ss)

    def check_dependencies(self, trial_list):
        trial_dict = {}
        for trial in trial_list:
            trial_dict[trial.trial_id] = trial

        dependencies_left = defaultdict(list)
        for dependency in self.depends_on:
            all_trials_satisfy = True
            for trial_id in trial_ids:
                trial = trial_dict[trial_id]
                if '.' in dependency:
                    stage_name, result_name = dependency.split('.')
                    stage_data = trial.get_stage_data(stage_name)
                    results = stage_data.results
                    if (result_name in results.keys() and 
                        results[result_name] is not None):
                        satisfied = True
                    else:
                        satisfied = False
                else:
                    if (hasattr(trial, dependency) and 
                        trial.get_stage_data(dependency).results is not None):
                        satisfied = True
                    else:
                        satisfied = False
                if not satisfied:
                    dependencies_left[trial_id].append(dependency)
        return dependencies_left

    def is_ready_to_run(self, trial_list):
        '''
        Checks to see if this job is ready to be run.
        Returns:
            status          : True/False
        '''
        dependencies_left = self.check_dependencies(trial_list)
        for dl in dependencies_left.values():
            if dl:
                return False
        return True
        

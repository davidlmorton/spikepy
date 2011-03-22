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

class Job(object):
    def __init__(self, kind='standard', stage_name=None, 
                       trial_ids=[], depends_on=[],
                       method_name=None, run_dict={}):
        self._id = uuid.uuid4()
        self.kind = kind
        self.stage_name = stage_name
        self.trial_ids = trial_ids
        self.depends_on = depends_on
        self.method_name = method_name
        self.run_dict = run_dict

    @property
    def job_id(self):
        return self._id

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
                        getattr(trial, dependency) is not None):
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
        

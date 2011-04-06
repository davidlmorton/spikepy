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

from spikepy.common.job import Job
from spikepy.common.plugin_utils import get_method

def make_jobs_for_stage(trial_list, stage_name, strategy):
    all_jobs = []
    if stage_name != 'clustering':
        for trial in trial_list:
            method_name = strategy.methods_used[stage_name]
            method_class = get_method(stage_name, method_name)
            depends_on = method_class._requires

            run_dict = {'args':map(trial.get_result, depends_on),
                        'kwargs':strategy.settings[stage_name]}

            new_job = Job(kind='plugin', 
                          stage_name=stage_name,
                          trial_ids=[trial.trial_id], 
                          depends_on=depends_on,
                          method_name=method_name, 
                          run_dict=run_dict,
                          job_name=stage_name,
                          job_id=uuid.uuid4())

            all_jobs.append(new_job)
    else:
        pass #FIXME add clustering job
    return all_jobs
            

            
        

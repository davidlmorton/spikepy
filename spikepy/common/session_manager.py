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
import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from spikepy.common.open_data_file import open_data_file
from spikepy.common import job_utils
import spikepy.common.program_text as pt

class SessionManager(object):
    def __init__(self):
        self.trials = {}
        self.num_files = 0     # number of files being opened
        self._opening_files = []
        self._process_running = False

        pub.subscribe(self._open_data_file, "OPEN_DATA_FILE")
        pub.subscribe(self._close_trial,    "CLOSE_TRIAL")
        pub.subscribe(self._run_stage, "RUN_STAGE")
        #pub.subscribe(self._run_strategy, "RUN_STRATEGY")

    def _run_stage(self, message):
        self.run_stage(**message.data)

    def run_stage(self, trial_list, stage_name, strategy, 
                  message_queue, abort_queue):
        jobs = job_utils.make_jobs_for_stage(trial_list, stage_name, strategy)
        for job in jobs:
            message_queue.put(('JOB_CREATED', job))
        # DEBUG
        self.jobs = jobs
        self.message_queue = message_queue
        self._job_count = 0
        for i, job in enumerate(jobs):
            # debugging...
            wx.CallLater(3321*(i+1), self.start_job)
        pass

    def start_job(self):
        # DEBUG
        self.jobs[self._job_count].set_start_time()
        self.message_queue.put(('JOB_STARTED', self.jobs[self._job_count]))
        self._job_count += 1
        
    def can_run(self, run_data):
        stage_name = run_data['stage_name']
        trial_list = run_data['trial_list']
        stage_settings = run_data['settings']
        stage_name = run_data['stage_name']
        stage_method = run_data['method_name']
        methods_used = {stage_name:stage_method}
        settings     = {stage_name:stage_settings}
        run_states = self.get_stage_run_states(methods_used, settings,
                                               trial_list)
        return run_states[stage_name]

    def get_stage_run_states(self, methods_used, settings, trial_list,
                                   force_novelty=False):
        stage_run_state = {}

        num_trials = len(trial_list)
        # initialize to False
        for stage_name in methods_used.keys():
            stage_run_state[stage_name] = False
            stage_run_state[stage_name] = True # DEBUGGING
        if num_trials < 1 or self._process_running:
            return stage_run_state

        if force_novelty:
            # ensure that novel results would result.
            # all stage states are False at this point.
            for trial in trial_list:
                for stage_name, method_used in methods_used.items():
                    novelty = trial.would_be_novel(stage_name, method_used, 
                                                   settings[stage_name])
                    # novelty in any file = able to run for all files.
                    if novelty:
                        stage_run_state[stage_name] = True
        else:
            for stage_name, method_used in methods_used.items():
                stage_run_state[stage_name] = True
            

        # ensure EVERY trial is ready for this stage.
        for trial in trial_list:
            readyness = trial.get_readyness()
            for stage_name in methods_used.keys():
                if not readyness[stage_name]:
                    stage_run_state[stage_name] = False

        # check that the settings are valid
        for stage_name in methods_used.keys():
            settings_valid = settings[stage_name] is not None
            if not settings_valid:
                stage_run_state[stage_name] = False

        return stage_run_state

    # ---- OPEN FILE ----
    def _file_opening_started(self):
        self.num_files += 1
        pub.sendMessage(topic="UPDATE_STATUS", 
                        data=pt.STATUS_OPENING % self.num_files)
        wx.Yield()

    def _file_opening_ended(self):
        if self.num_files:
            self.num_files -= 1

        if self.num_files:
            pub.sendMessage(topic="UPDATE_STATUS", 
                            data=pt.STATUS_OPENING % self.num_files)
        else:
            pub.sendMessage(topic="UPDATE_STATUS",
                            data=pt.STATUS_IDLE)
        wx.Yield()
        
    def _open_data_file(self, message):
        """
        Read in data from a file and create a Trial object from it.
        Inputs:
            message     : message.data should be the fullpath to the file.
        Alters:
            self.trials : a new entry with key=trial_id and value=Trial object
                          will be added to this dictionary.
        Publishes:
            'TRIAL_ADDED'            : if the file was just opened successfully
                                       -- data = Trial object just created
            'FILE_OPENED'            : if the file was just opened successfully
                                       -- data = fullpath
            'ALREADY_OPENING_FILE'   : if the file is still being opened
                                       -- data = fullpath
        """
        fullpath = message.data
        if fullpath not in self._opening_files:
            self._opening_files.append(fullpath)
            pub.sendMessage(topic="FILE_OPENING_STARTED")
            self._file_opening_started()
            startWorker(self._open_file_consumer, self._open_file_worker, 
                        wargs=(fullpath,), cargs=(fullpath,))
        else:
            pub.sendMessage(topic='ALREADY_OPENING_FILE', data=fullpath)

    def _open_file_worker(self, fullpath):
        trial_list = open_data_file(fullpath)
        return trial_list

    def _open_file_consumer(self, delayed_result, fullpath):
        trial_list = delayed_result.get()
        for trial in trial_list:
            trial_id = trial.trial_id
            self.trials[trial_id] = trial
            pub.sendMessage(topic='TRIAL_ADDED', data=trial)
        self._opening_files.remove(fullpath)
        pub.sendMessage(topic='FILE_OPENED', data=fullpath)

        trial_strategy = trial.get_strategy()
        if trial_strategy is not None:
            pub.sendMessage(topic='ENACT_STRATEGY', data=trial_strategy)

        pub.sendMessage(topic="FILE_OPENING_ENDED")
        self._file_opening_ended()

    # ---- CLOSE FILE ----
    def _close_trial(self, message):
        """
        Remove an existing Trial object.
        Inputs:
            message     : message.data should be the trial_id of the trial.
        Alters:
            self.trials : the entry with key=trial_id will be removed.
        Publishes:
            'TRIAL_CLOSED'      : if the trial was just closed successfully
                                  -- data = trial_id
        """
        trial_id = message.data
        if trial_id in self.trials.keys():
            del self.trials[trial_id]
            pub.sendMessage(topic='TRIAL_CLOSED', data=trial_id)

    

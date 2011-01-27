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

from spikepy.common import program_text as pt

class RunManager(object):
    def __init__(self):
        self.num_processes = 0
        self.num_files = 0
        self.locked_trials = set()
        self._to_be_run_list = []

        pub.subscribe(self._process_started, "PROCESS_STARTED")
        pub.subscribe(self._process_ended, "PROCESS_ENDED")

        pub.subscribe(self._file_opening_started, "FILE_OPENING_STARTED")
        pub.subscribe(self._file_opening_ended, "FILE_OPENING_ENDED")
        pub.subscribe(self._run_stage, "RUN_STAGE")

        self._run_order = ['detection_filter',
                           'detection',
                           'extraction_filter',
                           'extraction',
                           'clustering']
        self._running = False

    def _get_next_to_run(self):
        if self._to_be_run_list:
            for stage_name in self._run_order:
                for run_data in self._to_be_run_list:
                    if run_data['stage_name'] == stage_name:
                        return run_data
            raise RuntimeError("Stage to be run doesn't exist. %s" %
                                self._to_be_run_list)

    def _run_stage(self, message):
        self._to_be_run_list.append(message.data)
        self._complete_run()

    def _complete_run(self):
        if self._running:
            return

        self._running = True
        while self._get_next_to_run() is not None:
            next_to_run = self._get_next_to_run() 
            while not self.can_run(next_to_run):
                wx.Yield()
                wx.MilliSleep(100)
                wx.Yield()
            self._to_be_run_list.remove(next_to_run)
            pub.sendMessage("EXECUTE_STAGE", next_to_run)
        self._running = False

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
        if num_trials < 1 or not self.trials_available(trial_list):
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

    def trials_available(self, trial_list):
        if set(trial_list).intersection(self.locked_trials):
            return False
        else:
            return True

    def _process_started(self, message=None):
        self.locked_trials.update(message.data)
        self.num_processes += 1
        pub.sendMessage(topic="UPDATE_STATUS", 
                        data=pt.STATUS_RUNNING % self.num_processes)
        wx.Yield()

    def _process_ended(self, message=None):
        self.locked_trials -= set(message.data)
        if self.num_processes:
            self.num_processes -= 1

        if self.num_processes:
            pub.sendMessage(topic="UPDATE_STATUS", 
                            data=pt.STATUS_RUNNING % self.num_processes)
        else:
            pub.sendMessage(topic="UPDATE_STATUS",
                            data=pt.STATUS_IDLE)
            pub.sendMessage(topic="PLOT_RESULTS")
        wx.Yield()

    def _file_opening_started(self, message=None):
        self.num_files += 1
        pub.sendMessage(topic="UPDATE_STATUS", 
                        data=pt.STATUS_OPENING % self.num_files)
        wx.Yield()

    def _file_opening_ended(self, message=None):
        if self.num_files:
            self.num_files -= 1

        if self.num_files:
            pub.sendMessage(topic="UPDATE_STATUS", 
                            data=pt.STATUS_OPENING % self.num_files)
        else:
            pub.sendMessage(topic="UPDATE_STATUS",
                            data=pt.STATUS_IDLE)
        wx.Yield()
        

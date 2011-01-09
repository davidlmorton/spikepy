
import wx
from wx.lib.pubsub import Publisher as pub

from spikepy.common import program_text as pt

class RunManager(object):
    def __init__(self):
        self.num_processes = 0
        self.num_files = 0
        self.locked_trials = set()

        pub.subscribe(self._process_started, "PROCESS_STARTED")
        pub.subscribe(self._process_ended, "PROCESS_ENDED")

        pub.subscribe(self._file_opening_started, "FILE_OPENING_STARTED")
        pub.subscribe(self._file_opening_ended, "FILE_OPENING_ENDED")

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
        

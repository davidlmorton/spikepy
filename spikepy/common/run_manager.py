
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
            pub.sendMessage(topic="ABLE_TO_RUN_AGAIN")
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
        

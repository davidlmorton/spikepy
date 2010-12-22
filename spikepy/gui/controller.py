import os 
import traceback 
import sys
import cPickle
from multiprocessing import Pool

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from ..common.model import Model
from ..common.trial import Trial
from ..common.utils import pool_process
from .view import View
from .utils import named_color, load_pickle
from . import program_text as pt
from .trial_rename_dialog import TrialRenameDialog
from .pyshell import locals_dict
from .export_dialog import ExportDialog


class Controller(object):
    def __init__(self):
        self.model = Model()
        self.model.setup_subscriptions()
        self.view = View()

        # save for locals in pyshell
        locals_dict['model']      = self.model
        locals_dict['view']       = self.view
        locals_dict['controller'] = self


    def setup_subscriptions(self):
        pub.subscribe(self._open_open_file_dialog, 
                      topic="OPEN_OPEN_FILE_DIALOG")
        pub.subscribe(self._trial_selection_changed, 
                      topic='TRIAL_SELECTION_CHANGED')
        pub.subscribe(self._calculate_run_buttons_state,
                      topic='CALCULATE_RUN_BUTTONS_STATE')
        pub.subscribe(self._trial_closed, topic='TRIAL_CLOSED')
        pub.subscribe(self._save_session, topic='SAVE_SESSION')
        pub.subscribe(self._load_session, topic='LOAD_SESSION')
        pub.subscribe(self._close_application,  topic="CLOSE_APPLICATION")
        pub.subscribe(self._open_rename_trial_dialog,
                      topic='OPEN_RENAME_TRIAL_DIALOG')
        pub.subscribe(self._export_trials,  topic="EXPORT_TRIALS")
        pub.subscribe(self._run_all,  topic="RUN_ALL")
        pub.subscribe(self._run_marked,  topic="RUN_MARKED")
        pub.subscribe(self._print_messages, topic='')

    def _run_all(self, message):
        message.data['trial'] = 'all' 
        pub.sendMessage(topic='EXECUTE_STAGE', data=message.data) 

    def _run_marked(self, message):
        message.data['trial'] = self.get_marked_trials()
        pub.sendMessage(topic='EXECUTE_STAGE', data=message.data) 

    def _export_trials(self, message):
        export_type = message.data
        fullpaths = []
        if export_type == "all":
            trial_list = self.model.trials.values()
            caption=pt.EXPORT_ALL
        else:
            trial_list = self.get_marked_trials()
            caption=pt.EXPORT_MARKED

        dlg = ExportDialog(self.view.frame, title=caption)
        if dlg.ShowModal() == wx.ID_OK:
            settings = dlg.get_settings()
            print settings
            for trial in trial_list:
                trial.export(**settings)
        dlg.Destroy()

    def _open_rename_trial_dialog(self, message):
        trial_id = message.data
        this_trial = self.model.trials[trial_id]
        this_trial_name = this_trial.display_name
        other_trials = [trial for trial in 
                       self.model.trials.values()
                       if trial is not this_trial]
        fullpath = this_trial.fullpath
        dlg = TrialRenameDialog(self.view.frame, this_trial_name, 
                                fullpath, other_trials)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg._text_ctrl.GetValue()
            if new_name != this_trial_name:
                this_trial.rename(new_name)
        dlg.Destroy()

    def get_marked_trials(self):
        trial_grid_ctrl = self.view.frame.trial_list
        trial_ids = trial_grid_ctrl.marked_trial_ids
        return [self.model.trials[trial_id] for trial_id in trial_ids]

    def _calculate_run_buttons_state(self, message):
        methods_used, settings = message.data
        trial_list = self.model.trials.values()
        run_all_button_states = self._get_stage_run_states(methods_used, 
                                                           settings, 
                                                           trial_list)
        trial_list = self.get_marked_trials()
        run_marked_button_states = self._get_stage_run_states(methods_used, 
                                                              settings, 
                                                              trial_list)
        pub.sendMessage(topic='SET_RUN_BUTTONS_STATE', 
                        data=(run_all_button_states, run_marked_button_states))

    def _get_stage_run_states(self, methods_used, settings, trial_list):
        # find out if we should enable/disable run buttons.
        stage_run_state = {}

        num_trials = len(trial_list)
        for stage_name in methods_used.keys():
            stage_run_state[stage_name] = False
        if num_trials < 1:
            return stage_run_state

        # all stage states are False at this point.
        for trial in trial_list:
            tmethods_used = trial.methods_used
            tsettings     = trial.settings
            for stage_name in methods_used.keys():
                tmu = tmethods_used[stage_name]
                mu  = methods_used[stage_name]
                ts = tsettings[stage_name]
                s  = settings[stage_name]
                if tmu is not None and tmu == mu:
                    novelty = (ts != s)
                else:
                    novelty = True
                # novelty in any file = able to run for all files.
                if novelty:
                    stage_run_state[stage_name] = True

        # ensure EVERY trial is ready for this stage.
        for trial in trial_list:
            can_run_list = trial.get_stages_that_are_ready_to_run()
            for stage_name in methods_used.keys():
                if stage_name not in can_run_list:
                    stage_run_state[stage_name] = False

        # check that the settings are valid
        for stage_name in methods_used.keys():
            settings_valid = settings[stage_name] is not None
            if not settings_valid:
                stage_run_state[stage_name] = False

        return stage_run_state

    def _close_application(self, message):
        pub.sendMessage(topic='SAVE_ALL_STRATEGIES')
        pub.unsubAll()
        # deinitialize the frame manager
        self.view.frame.Destroy()
        if self.model._processing_pool is not None:
            self.model._processing_pool.close()

    def _save_session(self, message):
        save_path = message.data
        trials = self.model.trials.values()
        save_filename = os.path.split(save_path)[1]
        trial_archives = [trial.get_archive(archive_name=save_filename) 
                          for trial in trials]
        with open(save_path, 'w') as ofile:
            cPickle.dump(trial_archives, ofile, protocol=-1)
        
    def _load_session(self, message):
        session_fullpath = message.data
        session_filename = os.path.split(session_fullpath)[1]
        session_name = os.path.splitext(session_filename)[0]
        startWorker(self._load_session_consumer, self._load_session_worker, 
                    wargs=(session_fullpath,), cargs=(session_filename, 
                                                      session_name))

    def _load_session_worker(self, session_fullpath):
        pool = self.model._processing_pool
        trial_archives = pool_process(pool, load_pickle, 
                                      args=(session_fullpath,))
        return trial_archives


    def _load_session_consumer(self, delayed_result, session_filename, 
                               session_name):
        # change the fullpath so it corresponds to the session file
        trial_archives = delayed_result.get()
        trials = []
        for archive in trial_archives:
            trial = Trial(sampling_freq=archive['sampling_freq'],
                          raw_traces=archive['raw_traces'], 
                          fullpath=archive['fullpath'])
            trials.append(trial)
            for stage in trial.stages:
                if stage.name in archive.keys():
                    data_for_stage = archive[stage.name]
                    trial.set_data_for_stage(stage.name, **data_for_stage)

        # simulate opening the files
        for trial in trials:
            self.model.trials[trial.trial_id] = trial
            pub.sendMessage(topic='OPENING_DATA_FILE', data=trial.fullpath)
            pub.sendMessage(topic='TRIAL_ADDED',       data=trial)
            pub.sendMessage(topic='FILE_OPENED',       data=trial.fullpath)
            pub.sendMessage(topic='SET_STRATEGY', 
                            data=(trial.methods_used, trial.settings))
            
    def _print_messages(self, message):
        topic = message.topic
        data = message.data
        print topic,data

    def _trial_closed(self, message):
        trial_id = message.data
        pub.sendMessage(topic='REMOVE_PLOT', data=trial_id)


    def _trial_selection_changed(self, message):
        # XXX will this do something more?
        trial_id = message.data
        pub.sendMessage(topic='SHOW_PLOT', data=trial_id)

    def _open_open_file_dialog(self, message):
        frame = message.data

        paths = []
        dlg = wx.FileDialog(frame, message=pt.OPEN_FILE_DLG_MESSAGE,
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()
        for path in paths:
            pub.sendMessage(topic='OPENING_DATA_FILE', data=path)
            pub.sendMessage(topic='OPEN_DATA_FILE', data=path)

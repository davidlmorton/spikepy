import os 
import traceback 
import sys
import cPickle
from multiprocessing import Pool

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from ..common.model import Model
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
        pub.subscribe(self._open_file, topic="OPEN_FILE")
        pub.subscribe(self._file_selection_changed, 
                      topic='FILE_SELECTION_CHANGED')
        pub.subscribe(self._calculate_stage_run_state,
                      topic='CALCULATE_STAGE_RUN_STATE')
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._save_session, topic='SAVE_SESSION')
        pub.subscribe(self._load_session, topic='LOAD_SESSION')
        pub.subscribe(self._close_application,  topic="CLOSE_APPLICATION")
        pub.subscribe(self._open_rename_trial_dialog,
                      topic='OPEN_RENAME_TRIAL_DIALOG')
        pub.subscribe(self._export_trials,  topic="EXPORT_TRIALS")
        #pub.subscribe(self._print_messages, topic='')

    def _export_trials(self, message):
        export_type = message.data
        fullpaths = []
        if export_type == "all":
            trials = self.model.trials
            fullpaths = trials.keys()
            trial_list = [self.model.trials[fullpath] for fullpath in fullpaths]
            caption=pt.EXPORT_ALL
        else:
            file_grid_ctrl = self.view.frame.file_list
            fullpaths = file_grid_ctrl.marked_fullpaths
            trial_list = [self.model.trials[fullpath] for fullpath in fullpaths]
            caption=pt.EXPORT_MARKED

        dlg = ExportDialog(self.view.frame, title=caption)
        if dlg.ShowModal() == wx.ID_OK:
            settings = dlg.get_settings()
            print settings
            for trial in trial_list:
                trial.export(**settings)
        dlg.Destroy()

    def _open_rename_trial_dialog(self, message):
        fullpath = message.data
        this_trial = self.model.trials[fullpath]
        this_trial_name = this_trial.display_name
        other_trials = [trial for trial in 
                       self.model.trials.values()
                       if trial is not this_trial]
        dlg = TrialRenameDialog(self.view.frame, this_trial_name, 
                                fullpath, other_trials)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg._text_ctrl.GetValue()
            if new_name != this_trial_name:
                this_trial.rename(new_name)
        dlg.Destroy()

    def _calculate_stage_run_state(self, message):
        methods_used, settings = message.data
        # find out if we should enable/disable run buttons.
        stage_run_state = {}

        num_trials = len(self.model.trials.keys())
        for stage_name in methods_used.keys():
            stage_run_state[stage_name] = False
        if num_trials < 1:
            pub.sendMessage(topic='SET_RUN_STATE',data=stage_run_state)
            return

        # all stage states are False at this point.
        for trial in self.model.trials.values():
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
        for trial in self.model.trials.values():
            can_run_list = trial.get_stages_that_are_ready_to_run()
            for stage_name in methods_used.keys():
                if stage_name not in can_run_list:
                    stage_run_state[stage_name] = False

        # check that the settings are valid
        for stage_name in methods_used.keys():
            settings_valid = settings[stage_name] is not None
            if not settings_valid:
                stage_run_state[stage_name] = False

        pub.sendMessage(topic='SET_RUN_STATE',data=stage_run_state)

    def _save_session(self, message):
        save_path = message.data
        trials = self.model.trials
        with open(save_path, 'w') as ofile:
            cPickle.dump(trials, ofile, protocol=-1)
        
    def _load_session(self, message):
        session_fullpath = message.data
        session_filename = os.path.split(session_fullpath)[1]
        session_name = os.path.splitext(session_filename)[0]
        startWorker(self._load_session_consumer, self._load_session_worker, 
                    wargs=(session_fullpath,), cargs=(session_filename, 
                                                      session_name))

    def _close_application(self, message):
        pub.sendMessage(topic='SAVE_ALL_STRATEGIES')
        pub.unsubAll()
        # deinitialize the frame manager
        self.view.frame.Destroy()
        if wx.Platform != '__WXMAC__':
            self.model._processing_pool.close()


    def _load_session_worker(self, session_fullpath):
        try:
            if wx.Platform == '__WXMAC__':
                trials = load_pickle(session_fullpath)
            else:
                processing_pool = self.model._processing_pool
                result = processing_pool.apply_async(load_pickle, 
                                                     args=(session_fullpath,))
                trials = result.get()
        except:
            traceback.print_exc()
            sys.exit(1)
        return trials


    def _load_session_consumer(self, delayed_result, session_filename, 
                               session_name):
        # change the fullpath so it corresponds to the session file
        trials = delayed_result.get()
        new_filename = ''
        new_filenames = set()
        new_filenames.add(new_filename)
        for trial in trials.values():
            old_fullpath = trial.fullpath
            old_dir = os.path.split(old_fullpath)[0]
            old_filename = os.path.split(old_fullpath)[1]
            count = 0
            original_session_name = session_name
            while new_filename in new_filenames:
                tokens = old_filename.split('--')
                if count != 0:
                    this_session_name = original_session_name + '(%d)' % count
                else:
                    this_session_name = original_session_name
                if len(tokens) > 1:
                    new_filename = old_filename.replace(tokens[0], 
                            this_session_name)
                else:
                    new_filename = this_session_name + '--' + old_filename
                count += 1
            new_filenames.add(new_filename)
            trial.fullpath = os.path.join(old_dir, new_filename)

        # close opened files
        for fullpath in self.model.trials.keys():
            pub.sendMessage(topic='CLOSE_DATA_FILE', data=fullpath)

        # simulate opening the files
        for trial in trials.values():
            self.model.trials[trial.fullpath] = trial
            pub.sendMessage(topic='OPENING_DATA_FILE', data=trial.fullpath)
            pub.sendMessage(topic='TRIAL_ADDED',       data=trial)
            pub.sendMessage(topic='FILE_OPENED',       data=(trial.fullpath,
                                                            trial.display_name))
            pub.sendMessage(topic='SET_STRATEGY', 
                            data=(trial.methods_used, trial.settings))
            
            
    def _print_messages(self, message):
        topic = message.topic
        data = message.data
        print topic,data

    def _file_closed(self, message):
        fullpath = message.data
        pub.sendMessage(topic='REMOVE_PLOT', data=fullpath)


    def _file_selection_changed(self, message):
        # XXX will this do something more?
        fullpath = message.data
        pub.sendMessage(topic='SHOW_PLOT', data=fullpath)

    def _open_file(self, message):
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

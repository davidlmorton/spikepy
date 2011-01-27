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
from spikepy.common.utils import pool_process
from .view import View
from .utils import named_color, load_pickle
from spikepy.common import program_text as pt
from .trial_rename_dialog import TrialRenameDialog
from .pyshell import locals_dict
from .export_dialog import ExportDialog

def make_version_float(version_number_string):
    nums = version_number_string.split('.')
    result = 0.0
    for i, num in enumerate(nums):
        result += float(num)*10**(-3*i)
    return result

class Controller(object):
    def __init__(self):
        self.model = Model()
        self.model.setup_subscriptions()
        self.view = View()
        self.results_notebook = self.view.frame.results_notebook
        self._selected_trial = None

        # save for locals in pyshell
        locals_dict['model']      = self.model
        locals_dict['view']       = self.view
        locals_dict['controller'] = self
        self.setup_subscriptions()

    def warn_for_matplotlib_version(self):
        import matplotlib
        version = matplotlib.__version__
        min_version = '0.99.1.1'

        if make_version_float(version) < make_version_float(min_version):
            msg = pt.MATPLOTLIB_VERSION % (min_version, version)
            dlg = wx.MessageDialog(self.view.frame, msg, 
                                   style=wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def setup_subscriptions(self):
        pub.subscribe(self._open_open_file_dialog, 
                      topic="OPEN_OPEN_FILE_DIALOG")
        pub.subscribe(self._trial_selection_changed, 
                      topic='TRIAL_SELECTION_CHANGED')
        pub.subscribe(self._results_notebook_page_changed,
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGED')
        pub.subscribe(self._plot_results, topic='PLOT_RESULTS')
        pub.subscribe(self._hide_results, topic='HIDE_RESULTS')
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

    def start_debug_subscriptions(self):
        pub.subscribe(self._print_messages) # subscribes to all topics

    def stop_debug_subscriptions(self):
        pub.unsubscribe(self._print_messages) # unsubscribes from all

    def get_marked_trials(self):
        trial_grid_ctrl = self.view.frame.trial_list
        trial_ids = trial_grid_ctrl.marked_trial_ids
        return [self.model.trials[trial_id] for trial_id in trial_ids]

    def get_all_trials(self):
        return self.model.trials.values()

    def _run_all(self, message):
        message.data['trial_list'] = self.get_all_trials()
        pub.sendMessage(topic='RUN_STAGE', data=message.data) 

    def _run_marked(self, message):
        message.data['trial_list'] = self.get_marked_trials()
        pub.sendMessage(topic='RUN_STAGE', data=message.data) 

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

    def _calculate_run_buttons_state(self, message):
        methods_used, settings = message.data

        checker = self.model.run_manager.get_stage_run_states
        marked_trials = self.get_marked_trials()
        run_state = {}
        run_state.update(checker(methods_used, settings, marked_trials))
        run_state['strategy'] = any(run_state.values())

        pub.sendMessage(topic='SET_RUN_BUTTONS_STATE', data=run_state)

    def _close_application(self, message):
        pub.sendMessage(topic='SAVE_ALL_STRATEGIES')
        pub.unsubAll()
        wx.Yield()
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
        self._selected_trial = None
        pub.sendMessage(topic='REMOVE_PLOT', data=trial_id)

    def _plot_results(self, message):
        trial_id = self._selected_trial
        stage_name = self.results_notebook.get_current_stage_name()
        should_plot = self.results_notebook.should_plot(stage_name)
        
        if trial_id is not None and should_plot:
            pub.sendMessage(topic='DISPLAY_RESULT', 
                            data=(trial_id, stage_name))

    def _hide_results(self, message):
        stage_name = message.data
        if stage_name != 'all':
            pub.sendMessage(topic='CLEAR_RESULTS', data=stage_name)
        else:
            for stage_name in ['detection_filter', 'detection', 
                               'extraction_filter', 'extraction', 
                               'clustering', 'summary']:
                pub.sendMessage(topic='CLEAR_RESULTS', data=stage_name)

    def _results_notebook_page_changed(self, message):
        trial_id = self._selected_trial
        stage_name = self.results_notebook.get_current_stage_name()
        should_plot = self.results_notebook.should_plot(stage_name)

        if trial_id is not None and should_plot:
            pub.sendMessage(topic='DISPLAY_RESULT', 
                            data=(trial_id, stage_name))

    def _trial_selection_changed(self, message):
        trial_id = message.data
        # clear all plots when changing trial selections.
        message.data = 'all'
        self._hide_results(message)

        self._selected_trial = trial_id
        stage_name = self.results_notebook.get_current_stage_name()
        should_plot = self.results_notebook.should_plot(stage_name)
        if trial_id is not None and should_plot:
            pub.sendMessage(topic='DISPLAY_RESULT', data=(trial_id, stage_name))

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

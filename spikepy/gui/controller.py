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
import gzip
import os 
import traceback 
import sys
import cPickle
import multiprocessing

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker

from spikepy import session

from spikepy.common.errors import *
from spikepy.common import program_text as pt
from spikepy.gui.view import View
from spikepy.gui.utils import named_color, load_pickle
from spikepy.gui.process_progress_dialog import ProcessProgressDialog
from spikepy.gui.trial_rename_dialog import TrialRenameDialog
from spikepy.gui.pyshell import locals_dict
from spikepy.gui.export_dialog import ExportDialog

all_stages = ['detection_filter', 'detection', 'extraction_filter', 
              'extraction', 'clustering']

def make_version_float(version_number_string):
    nums = version_number_string.split('.')
    result = 0.0
    for i, num in enumerate(nums):
        result += float(num)*10**(-3*i)
    return result

class Controller(object):
    def __init__(self):
        self.session = session.Session()
        self.session.open_files.add_callback(self._files_opened, 
                takes_target_results=True)
        self.session.trial_manager.remove_trial.add_callback(
                self._trial_closed, 
                takes_target_results=True)
        self.session.rename_trial.add_callback(self._trial_renamed,
                takes_target_results=True)
        self.session.trial_manager.mark_trial.add_callback(self._trial_marked,
                takes_target_results=True)

        self.view = View(plugin_manager=self.session.plugin_manager, 
                strategy_manager=self.session.strategy_manager)
        self.results_notebook = self.view.frame.results_notebook
        self._selected_trial = None
        self._process_progress_dlg = None

        # save for locals in pyshell
        locals_dict['session']      = self.session
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
        pub.subscribe(self._close_trial, topic='CLOSE_TRIAL')
        pub.subscribe(self._mark_trial, topic='MARK_TRIAL')
        pub.subscribe(self._trial_selection_changed, 
                      topic='TRIAL_SELECTION_CHANGED')
        pub.subscribe(self._results_notebook_page_changed,
                      topic='RESULTS_NOTEBOOK_PAGE_CHANGED')
        pub.subscribe(self._plot_results, topic='PLOT_RESULTS')
        pub.subscribe(self._hide_results, topic='HIDE_RESULTS')
        pub.subscribe(self._save_session, topic='SAVE_SESSION')
        pub.subscribe(self._close_application,  topic="CLOSE_APPLICATION")
        pub.subscribe(self._open_rename_trial_dialog,
                      topic='OPEN_RENAME_TRIAL_DIALOG')
        pub.subscribe(self._export_trials,  topic="EXPORT_TRIALS")
        #pub.subscribe(self._run_strategy, topic="RUN_STRATEGY")
        #pub.subscribe(self._run_stage, topic="RUN_STAGE")
        pub.subscribe(self._aborting_processing, topic='ABORTING_PROCESSING')
        pub.subscribe(self._processing_finished, topic='PROCESSING_FINISHED')

    def start_debug_subscriptions(self):
        pub.subscribe(self._print_messages) # subscribes to all topics

    def stop_debug_subscriptions(self):
        pub.unsubscribe(self._print_messages) # unsubscribes from all

    def _close_trial(self, message):
        self.session.remove_trial(message.data)

    def _mark_trial(self, message):
        try:
            self.session.mark_trial(*message.data)
        except CannotMarkTrialError as e:
            msg = e.args[0]
            dlg = wx.MessageDialog(self.view.frame, msg, 
                                   style=wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def _trial_marked(self, args):
        trial_id, status = args
        pub.sendMessage(topic='TRIAL_MARKED', data=(trial_id, status))

    def _run_stage(self, message):
        message_queue = multiprocessing.Queue()
        abort_queue = multiprocessing.Queue()
        locals_dict['mq'] = message_queue
        self._open_process_progress_dialog(trial_list, message_queue,
                                           abort_queue)

        message.data['trial_list'] = trial_list
        message.data['message_queue'] = message_queue
        message.data['abort_queue'] = abort_queue
        if 'STRATEGY' in message.topic:
            pub.sendMessage(topic='RUN_STRATEGY', data=message.data) 
        else:
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
        this_trial = self.session.get_trial(trial_id)
        this_trial_name = this_trial.display_name
        origin = this_trial.origin
        all_display_names = self.session.trial_manager.all_display_names
        dlg = TrialRenameDialog(self.view.frame, this_trial_name, origin,
                all_display_names)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg._text_ctrl.GetValue()
            if new_name != this_trial_name:
                self.session.rename_trial(this_trial_name, new_name)
        dlg.Destroy()

    def _trial_renamed(self, trial):
        pub.sendMessage(topic='TRIAL_RENAMED', data=trial)

    def _calculate_run_buttons_state(self, message):
        methods_used, settings = message.data

        checker = self.model.get_stage_run_states
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

    def _save_session(self, message):
        save_path = message.data
        trials = self.model.trials.values()
        save_filename = os.path.split(save_path)[1]
        trial_archives = [trial.get_archive(archive_name=save_filename) 
                          for trial in trials]

        ofile = gzip.open(save_path, 'wb')
        cPickle.dump(trial_archives, ofile, protocol=-1)
        ofile.close()
        
    def _print_messages(self, message):
        topic = message.topic
        data = message.data
        print topic, data

    def _trial_closed(self, trial_id):
        self._selected_trial = None
        pub.sendMessage(topic='REMOVE_PLOT', data=trial_id)
        pub.sendMessage(topic='TRIAL_CLOSED', data=trial_id)

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

    def _processing_finished(self, message):
        stage_name = message.data
        if self._process_progress_dlg is not None:
            done = self._process_progress_dlg.is_done
            if done:
                self._process_progress_dlg = None

    def _aborting_processing(self, message):
        self._process_progress_dlg.abort()
        self._process_progress_dlg = None
        offending_trials, abort_reasons, last_stage_name_run = message.data
        if 'USER_PRESSED_ABORT' in abort_reasons:
            info = pt.USER_ABORT_MESSAGE % last_stage_name_run
        else:
            info = pt.ABORT_MESSAGE
            for ot, ar in zip(offending_trials, abort_reasons):
                info += pt.ABORT_TRIALS % (ot.display_name, ar)
        msg_dlg = wx.MessageDialog(self.view.frame, info, style=wx.OK|wx.CENTRE)
        msg_dlg.ShowModal()
        msg_dlg.Destroy()
        
    def _open_process_progress_dialog(self, trial_list, message_queue, 
                                       abort_queue):
        main_frame_pos = self.view.frame.GetPosition()
        main_frame_size = self.view.frame.GetSize()
        dlg_pos = (main_frame_pos[0]+main_frame_size[0]/2,
                   main_frame_pos[1]+main_frame_size[1]/2)
        self._process_progress_dlg = ProcessProgressDialog(self.view.frame,
                                                           trial_list, 
                                                           message_queue, 
                                                           abort_queue,
                                                           pos=dlg_pos)
        self._process_progress_dlg.Show()

    def _open_open_file_dialog(self, message):
        frame = message.data

        paths = []
        dlg = wx.FileDialog(frame, message=pt.OPEN_FILE_DLG_MESSAGE,
                            defaultDir=os.getcwd(),
                            style=wx.OPEN|wx.MULTIPLE) 
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
        dlg.Destroy()

        self.session.open_files(paths)

    def _files_opened(self, trials):
        for trial in trials:
            pub.sendMessage(topic='TRIAL_ADDED', data=trial)
        

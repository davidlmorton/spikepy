import os 
import cPickle

import wx
from wx.lib.pubsub import Publisher as pub

from ..common.model import Model
from .view import View
from .utils import named_color
from . import program_text as pt
from .pyshell import locals_dict


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
        pub.subscribe(self._file_closed, topic='FILE_CLOSED')
        pub.subscribe(self._save_session, topic='SAVE_SESSION')
        pub.subscribe(self._load_session, topic='LOAD_SESSION')
        pub.subscribe(self._print_messages, topic='')

    def _save_session(self, message):
        save_path = message.data
        trials = self.model.trials
        with open(save_path, 'w') as ofile:
            cPickle.dump(trials, ofile, protocol=-1)

    def _load_session(self, message):
        session_fullpath = message.data
        session_name = os.path.split(session_fullpath)[1]
        with open(session_fullpath) as ifile:
            trials = cPickle.load(ifile)
        # change the fullpath so it corresponds to the session file
        for trial in trials.values():
            old_fullpath = trial.fullpath
            old_dir = os.path.split(old_fullpath)[0]
            old_filename = os.path.split(old_fullpath)[1]
            new_filename = session_name + '-' + old_filename
            trial.fullpath = os.path.join(old_dir, new_filename)

        # close opened files
        for fullpath in self.model.trials.keys():
            pub.sendMessage(topic='CLOSE_DATA_FILE', data=fullpath)

        # simulate opening the files
        for trial in trials.values():
            self.model.trials[trial.fullpath] = trial
            pub.sendMessage(topic='OPENING_DATA_FILE', data=trial.fullpath)
            pub.sendMessage(topic='TRIAL_ADDED', data=trial)
            pub.sendMessage(topic='FILE_OPENED', data=trial.fullpath)
            
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




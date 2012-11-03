
import os

import wx

from spikepy.developer.file_interpreter import FileInterpreter, Trial

SHANK_CHANNEL_INDEX = [9,   8, 10,  7, 13,  4, 12,  5, 
                       15,  2, 16,  1, 14,  3, 11,  6]


class TEPDatabaseFile(FileInterpreter):
    def __init__(self):
        self.name = 'TEP database file'
        self.extentions = ['.sqlite']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A Turtle Electrophysiology Project database.'''

    def read_data_file(self, fullpath):
        #   I don't want this plugin to fail (if TEP is not installed on the system)
        # until it is tried.
        from tep.utils.file_io.read_data_file import read_data_file as rdf
        self.db_path = fullpath
        app = wx.GetApp()
        start_loop = False
        if app is None:
            start_loop = True
            app = wx.PySimpleApp()

        if start_loop:
            # if we're not already in the MainLoop, we have to have to start it
            # up and then have it call the startup_search.
            wx.CallLater(300, self._startup_search)
            app.MainLoop()
        else:
            self._startup_search()

        # make trial objects and return them.
        trials = []
        for path, display_name in self.data_paths:
            data = rdf(path, determine_pulse_onset=False)
            voltage_traces = data['voltage_traces']
            sampling_freq = data['sampling_freq']

            if len(voltage_traces) == 16:
                voltage_traces = voltage_traces[[i-1 
                        for i in SHANK_CHANNEL_INDEX]]

            trial = Trial.from_raw_traces(sampling_freq, voltage_traces,
                    origin=path, display_name=display_name)
            trials.append(trial)
        return trials

    def _startup_search(self):
        msg = "Open the search program on the database:\n\n%s\n\n    The recordings or collection you have selected\nwhen you close the search program will be opened in Spikepy." % self.db_path
        dlg = wx.MessageDialog(None, msg, style=wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            # open up the database
            from tep.acquire.database.open_utils import open_database
            db_dir = os.path.split(self.db_path)[0]
            open_database(db_dir, readonly=True, 
                    backup_suffix='search_data__via__spikepy')
            from tep.acquire.database.alchemy_database_manager import adbm
            
            # start up search program
            # have to import this after opening database.
            from tep.search.search import MainFrame
            main_frame = MainFrame(None, size=(1100, 800), 
                    close_callback=self.close_callback)
            main_frame.ShowModal()

            # figure out what files to open and open them.
            recordings = main_frame.results_notebook.get_selected_recordings() 
            self.data_paths = [(r.data_path, repr(r))  for r in recordings]
        else:
            # open nothing and return an empty list.
            self.data_paths = []

    def close_callback(self, main_frame):
        # figure out what files to open and open them.
        recordings = main_frame.results_notebook.get_selected_recordings() 

        msg = "This will load %d recordings into Spikepy:\n\nVisualRecordings:%s\n\nSearchingRecordings:%s\n" %\
                (len(recordings), [r.vr_id for r in recordings if hasattr(r, 'vr_id')], [r.sr_id for r in recordings if hasattr(r, 'sr_id')])
        dlg = wx.MessageDialog(None, msg, style=wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            confirmation = True
        else:
            confirmation = False
        return confirmation

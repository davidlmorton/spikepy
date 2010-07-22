import os

import cPickle
import wx
import wx.aui
from wx.lib.pubsub import Publisher as pub

import spikepy
from .menu_bar import SpikepyMenuBar
from .strategy_pane import StrategyPane
from .file_list_ctrl import FileListCtrl
from .results_notebook import ResultsNotebook
from .look_and_feel_settings import lfs
from . import program_text as pt

class View(object):
    def __init__(self, *args, **kwargs):
        self.frame = MyFrame(None, *args, **kwargs)
        self.frame.Show()
        

class MyFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, 
                 title=lfs.MAIN_FRAME_TITLE,
                 size=None,
                 style=lfs.MAIN_FRAME_STYLE):
        # MAIN_FRAME_SIZE needs the wx.App() instance so can't be put 
        #   in declaration
        if size is None: size = lfs.MAIN_FRAME_SIZE
        wx.Frame.__init__(self, parent, title=title, size=size, style=style)

        self._mgr = wx.aui.AuiManager(self)

        # --- STRATEGY PANE ---
        self.strategy_pane = strategy_pane  = StrategyPane(self)        
        strategy_pane_info = wx.aui.AuiPaneInfo()
        strategy_pane_info.Right()
        strategy_pane_info.CloseButton(   visible=False)
        strategy_pane_info.MinimizeButton(visible=False)
        strategy_pane_info.MaximizeButton(visible=False)
        strategy_pane_info.MinSize(lfs.STRATEGY_PANE_MIN_SIZE)
        strategy_pane_info.FloatingSize(lfs.STRATEGY_PANE_MIN_SIZE)
        strategy_pane_info.Caption(pt.STRATEGY)

        # --- FILE LIST PANE ---
        self.file_list = file_list = FileListCtrl(self, 
                style=lfs.FILE_LISTCTRL_STYLE)
        file_list_pane_info = wx.aui.AuiPaneInfo()
        file_list_pane_info.Left()
        file_list_pane_info.CloseButton(   visible=False)
        file_list_pane_info.MinimizeButton(visible=False)
        file_list_pane_info.MaximizeButton(visible=False)
        file_list_pane_info.MinSize(lfs.FILE_LISTCTRL_MIN_SIZE)
        file_list_pane_info.FloatingSize(lfs.FILE_LISTCTRL_MIN_SIZE)
        file_list_pane_info.Caption(pt.FILE_LISTCTRL_TITLE)
        
        # ---  RESULTS PANE ---
        self.results_notebook = results_notebook = ResultsNotebook(self)

        # add the panes to the manager
        self._mgr.AddPane(file_list, info=file_list_pane_info)
        self._mgr.AddPane(strategy_pane, info=strategy_pane_info)
        self._mgr.AddPane(results_notebook, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self._close_application)

        # create status bar (I'm not sure if we'll use this or not)
        self.CreateStatusBar()
        self.SetStatusText("We can put status updates here if we want")

        # create menu bar
        self.menubar = SpikepyMenuBar(self)
        self.SetMenuBar(self.menubar)

        pub.subscribe(self._close_application,  topic="CLOSE_APPLICATION")
        pub.subscribe(self._save_perspective,   topic="SAVE_PERSPECTIVE")
        pub.subscribe(self._load_perspective,   topic="LOAD_PERSPECTIVE")
        
        self.perspectives = read_in_perspectives()
        self.menubar._update_perspectives(self.perspectives)

    def _save_perspective(self, message):
        dlg = wx.TextEntryDialog(self, pt.ENTER_NEW_WORKSPACE,
                                 caption=pt.NEW_WORKSPACE_DLG)
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        perspective_data = self._mgr.SavePerspective()
        perspective_name = dlg.GetValue()
        dlg.Destroy()
        self.perspectives[perspective_name] = perspective_data
        self.menubar._update_perspectives(self.perspectives)

        #TODO add warning if overwriting file
        perspectives_file = open(self.perspectives_file_path, 'w')

        cPickle.dump(self.perspectives, perspectives_file, protocol=-1)
        perspectives_file.close()
        
    def _load_perspective(self, message):
        perspective_name = message.data
        perspective = self.perspectives[perspective_name]
        perspective = update_with_current_names(perspective, self._mgr)
        self._mgr.LoadPerspective(perspective)

    def _close_application(self, message):
        pub.unsubAll()
        # deinitialize the frame manager
        self._mgr.UnInit()
        self.Destroy()


def read_in_perspectives():
    # find and load perspectives
    spikepy_location = spikepy.__file__
    spikepy_directory = os.path.split(spikepy_location)[0]
    perspectives_file_path = os.path.join(spikepy_directory, 
                                          "perspectives",
                                          "perspectives.cPickle")
    with open(perspectives_file_path, 'r') as perspectives_file:
        perspectives = cPickle.load(perspectives_file)
    return perspectives


def update_with_current_names(perspective, mgr):
    # get names from this instance and replace them in the perspective
    old_perspective = mgr.SavePerspective()
    old_names = get_perspective_names(old_perspective)
    new_names = get_perspective_names(perspective)
    for old, new in zip(old_names, new_names):
        perspective = perspective.replace(new, old)
    return perspective
    

def get_perspective_names(perspective_string):
    tokens = perspective_string.split(';')
    names = []
    for token in tokens:
        if 'name=' in token:
            names.append(token.split('name=')[-1])
    return names

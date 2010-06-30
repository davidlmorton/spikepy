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

class View(object):
    def __init__(self, *args, **kwargs):
        self.frame = MyFrame(None, *args, **kwargs)
        self.frame.Show()
        
class MyFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, 
                 title='Spikepy - A spike sorting framework.',
                 pos=wx.DefaultPosition, size=(1200, 700),
                 style=wx.DEFAULT_FRAME_STYLE|wx.SUNKEN_BORDER):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)

        # --- STRATEGY PANE ---
        strategy_pane  = StrategyPane(self)        
        strategy_pane_info = wx.aui.AuiPaneInfo()
        strategy_pane_info.Right()
        strategy_pane_info.CloseButton(   visible=False)
        strategy_pane_info.MinimizeButton(visible=False)
        strategy_pane_info.MaximizeButton(visible=False)
        strategy_pane_info.MinSize((310, 500))
        strategy_pane_info.FloatingSize((310,500))
        strategy_pane_info.Caption("Strategy")

        # --- FILE LIST PANE ---
        file_list = FileListCtrl(self, style=wx.LC_REPORT|wx.LC_VRULES)
        file_list_pane_info = wx.aui.AuiPaneInfo()
        file_list_pane_info.Left()
        file_list_pane_info.CloseButton(   visible=False)
        file_list_pane_info.MinimizeButton(visible=False)
        file_list_pane_info.MaximizeButton(visible=False)
        file_list_pane_info.MinSize((200,250))
        file_list_pane_info.FloatingSize((200,250))
        file_list_pane_info.Caption("Opened Files List")
        
        # ---  RESULTS PANE ---
        results_notebook = ResultsNotebook(self)

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

        self.panes = [file_list, strategy_pane, results_notebook]
        pub.subscribe(self._close_application, topic="CLOSE_APPLICATION")
        pub.subscribe(self._save_perspective, topic="SAVE_PERSPECTIVE")
        pub.subscribe(self._load_perspective, topic="LOAD_PERSPECTIVE")
        
        # find and load perspectives
        spikepy_location = spikepy.__file__
        spikepy_directory = os.path.split(spikepy_location)[0]
        self.perspectives_file_path = os.path.join(spikepy_directory, 
                                              "perspectives",
                                              "perspectives.cPickle")
        perspectives_file = open(self.perspectives_file_path, 'r')
        self.perspectives = cPickle.load(perspectives_file)
        perspectives_file.close()
        self.menubar._update_perspectives(self.perspectives)

    def _close_application(self, message):
        # deinitialize the frame manager
        self._mgr.UnInit()
        self.Destroy()

    def _save_perspective(self, message):
        dlg = wx.TextEntryDialog(self, "Enter a name for the new workspace:",
                                 caption="Save current workspace")
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        perspective_data = self._mgr.SavePerspective()
        perspective_name = dlg.GetValue()
        dlg.Destroy()
        self.perspectives[perspective_name] = perspective_data
        self.menubar._update_perspectives(self.perspectives)

        perspectives_file = open(self.perspectives_file_path, 'w')

        cPickle.dump(self.perspectives, perspectives_file, protocol=-1)
        perspectives_file.close()
        
        #TODO add warning if overwriting file
        
    def _load_perspective(self, message):
        perspective_name = message.data
        perspective = self.perspectives[perspective_name]
        perspective = update_with_current_names(perspective, self._mgr)
        self._mgr.LoadPerspective(perspective)

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

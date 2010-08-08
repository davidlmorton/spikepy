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
                 title=pt.MAIN_FRAME_TITLE,
                 size=None,
                 style=lfs.MAIN_FRAME_STYLE):
        # MAIN_FRAME_SIZE needs the wx.App() instance so can't be put 
        #   in declaration
        if size is None: size = lfs.MAIN_FRAME_SIZE
        wx.Frame.__init__(self, parent, title=title, size=size, style=style)

        # --- STRATEGY PANE ---
        vsplit = wx.SplitterWindow(self, style=wx.SP_3D)
        hsplit = wx.SplitterWindow(vsplit, style=wx.SP_3D)


        strategy_holder = BorderPanel(hsplit, style=wx.BORDER_SUNKEN)
        self.strategy_pane = StrategyPane(strategy_holder)
        strategy_holder.add_content(self.strategy_pane, 2)

        file_list_holder = BorderPanel(hsplit, style=wx.BORDER_SUNKEN)
        self.file_list = FileListCtrl(hsplit, style=lfs.FILE_LISTCTRL_STYLE)
        file_list_holder.add_content(self.file_list, 2)

        self.results_notebook = results_notebook = ResultsNotebook(
                                                    vsplit)

        vsplit.SplitVertically(hsplit, self.results_notebook, 400)
        hsplit.SplitHorizontally(file_list_holder, strategy_holder, 200)

        hsplit.SetMinimumPaneSize(lfs.FILE_LISTCTRL_MIN_SIZE[1])
        vsplit.SetMinimumPaneSize(lfs.STRATEGY_PANE_MIN_SIZE[0])
        hsplit.SetSashPosition(lfs.FILE_LISTCTRL_MIN_SIZE[1])
        vsplit.SetSashPosition(lfs.STRATEGY_PANE_MIN_SIZE[0])

        self.Bind(wx.EVT_CLOSE, self._close_application)

        # create status bar (I'm not sure if we'll use this or not)
        self.CreateStatusBar()
        self.SetStatusText("We can put status updates here if we want")

        # create menu bar
        self.menubar = SpikepyMenuBar(self)
        self.SetMenuBar(self.menubar)

    def _close_application(self, event=None):
        pub.sendMessage(topic='CLOSE_APPLICATION')

class BorderPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(sizer)

    def add_content(self, content, border):
        sizer = self.GetSizer()
        sizer.Add(content, proportion=1, flag=wx.EXPAND|wx.ALL, border=border)

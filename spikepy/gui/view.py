

import os

import cPickle
import wx
import wx.aui
from wx.lib.pubsub import Publisher as pub

import spikepy
from .menu_bar import SpikepyMenuBar
from .strategy_pane import StrategyPane
from .trial_grid_ctrl import TrialGridCtrl
from .results_notebook import ResultsNotebook
from spikepy.common.config_manager import config_manager as config
from spikepy.common import program_text as pt
from spikepy.gui import pyshell

class View(object):
    def __init__(self, *args, **kwargs):
        self.frame = MyFrame(None, *args, **kwargs)
        self.frame.Show()
        
class MyFrame(wx.Frame):
    def __init__(self, parent, session, id=wx.ID_ANY, 
                 title=pt.MAIN_FRAME_TITLE,
                 size=None,
                 style=wx.DEFAULT_FRAME_STYLE):
        plugin_manager = session.plugin_manager
        strategy_manager = session.strategy_manager
        # MAIN_FRAME_SIZE needs the wx.App() instance so can't be put 
        #   in declaration
        if size is None: 
            size = config.get_size('main_frame')
        wx.Frame.__init__(self, parent, title=title, size=size, style=style)

        # --- STRATEGY PANE ---
        vsplit = wx.SplitterWindow(self, style=wx.SP_3D)
        hsplit = wx.SplitterWindow(vsplit, style=wx.SP_3D)

        strategy_holder = BorderPanel(hsplit, style=wx.BORDER_SUNKEN)
        self.strategy_pane = StrategyPane(strategy_holder, 
                plugin_manager=plugin_manager, 
                strategy_manager=strategy_manager)
        strategy_holder.add_content(self.strategy_pane, 0)

        trial_list_holder = BorderPanel(hsplit, style=wx.BORDER_SUNKEN)
        self.trial_list = TrialGridCtrl(trial_list_holder)
        trial_list_holder.add_content(self.trial_list, 0)

        self.results_notebook = results_notebook = ResultsNotebook(
                                                    vsplit, session)
        pyshell.locals_dict['results_notebook'] = self.results_notebook

        vsplit.SplitVertically(hsplit, self.results_notebook, 400)
        hsplit.SplitHorizontally(trial_list_holder, strategy_holder, 200)

        hsplit.SetMinimumPaneSize(config['gui']['strategy_pane']['min_height'])
        vsplit.SetMinimumPaneSize(config['gui']['strategy_pane']['min_width'])
        hsplit.SetSashPosition(config['gui']['strategy_pane']['min_height'])
        vsplit.SetSashPosition(config['gui']['strategy_pane']['min_width'])

        self.Bind(wx.EVT_CLOSE, self._close_application)

        # create status bar (I'm not sure if we'll use this or not)
        self.CreateStatusBar()
        self.SetStatusText(pt.STATUS_IDLE)

        # create menu bar
        self.menubar = SpikepyMenuBar(self)
        self.SetMenuBar(self.menubar)

        pub.subscribe(self._update_status_bar, 
                      topic='UPDATE_STATUS')

    def wiggle(self):
        '''
        Resize main frame up one pixel in each direction then back down... so
        as to fix osX related drawing bugs.
        '''
        if wx.Platform in ['__WXMAC__', '__WXMSW__']:
            s = self.GetSize()
            self.SetSize((s[0]+1, s[1]+1))
            self.SendSizeEvent()
            self.SetSize(s)
            self.SendSizeEvent()
        else:
            pass

    def _update_status_bar(self, message=None):
        new_text = message.data
        self.SetStatusText(new_text)

    def _close_application(self, event=None):
        event.Skip()
        pub.sendMessage(topic='CLOSE_APPLICATION')

class BorderPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.SetSizer(sizer)

    def add_content(self, content, border):
        sizer = self.GetSizer()
        sizer.Add(content, proportion=1, flag=wx.EXPAND|wx.ALL, border=border)

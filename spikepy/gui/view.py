import os

import wx
import wx.aui
from wx.lib.pubsub import Publisher as pub

from .file_list_ctrl import FileListCtrl
from .menu_bar import SpikepyMenuBar
from .trace_plot_panel import TracePlotPanel

class View(object):
    def __init__(self, *args, **kwargs):
        self.frame = MyFrame(None, *args, **kwargs)
        self.frame.Show()
        
class MyFrame(wx.Frame):

    def __init__(self, parent, id=-1, 
                 title='Spikepy - A spike sorting framework.',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE|wx.SUNKEN_BORDER):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)

        # --- STRATEGY PANE ---
        text1 = wx.TextCtrl(self, -1, 'Pane 1 - sample text',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        strategy_pane_info = wx.aui.AuiPaneInfo()
        strategy_pane_info.CloseButton(   visible=False)
        strategy_pane_info.MinimizeButton(visible=False)
        strategy_pane_info.MaximizeButton(visible=False)
        strategy_pane_info.FloatingSize((300,500))
        strategy_pane_info.Caption("Strategy")

        # --- FILE LIST PANE ---
        file_list = FileListCtrl(self, style=wx.LC_REPORT|wx.LC_VRULES)
        file_list_pane_info = wx.aui.AuiPaneInfo()
        file_list_pane_info.CloseButton(   visible=False)
        file_list_pane_info.MinimizeButton(visible=False)
        file_list_pane_info.MaximizeButton(visible=False)
        file_list_pane_info.FloatingSize((450,200))
        file_list_pane_info.Caption("Opened Files List")
        
        # --- TRACE PLOT PANEL PANE ---
        holding_panel = wx.Panel(self)
        trace_plot_panel = TracePlotPanel(holding_panel)

        # add the panes to the manager
        self._mgr.AddPane(file_list, info=file_list_pane_info)
        self._mgr.AddPane(text1, info=strategy_pane_info)
        self._mgr.AddPane(holding_panel, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self._close_application)

        # create status bar (I'm not sure if we'll use this or not)
        self.CreateStatusBar()
        self.SetStatusText("We can put status updates here if we want")
        
        # create menu bar
        menubar = SpikepyMenuBar(self)
        self.SetMenuBar(menubar)

        pub.subscribe(self._close_application, topic="CLOSE APPLICATION")

    def _close_application(self, message):
        # deinitialize the frame manager
        self._mgr.UnInit()
        self.Destroy()



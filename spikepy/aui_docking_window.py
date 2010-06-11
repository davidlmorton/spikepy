import os

import wx
import wx.aui
from spikepy.gui import file_list_ctrl

class MyFrame(wx.Frame):

    def __init__(self, parent, id=-1, title='wx.aui Test',
                 pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)

        # create several text controls
        text1 = wx.TextCtrl(self, -1, 'Pane 1 - sample text',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        file_list = file_list_ctrl.FileListCtrl(self, 
                                                style=wx.LC_REPORT|wx.LC_VRULES)
        file_list.add_file('a', 'b')

        text3 = wx.TextCtrl(self, -1, 'Main content window',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)
        # add the panes to the manager
        self._mgr.AddPane(file_list, wx.LEFT, 'Opened Files List')
        self._mgr.AddPane(text1, wx.LEFT, 'Pane Number One')
        self._mgr.AddPane(text3, wx.CENTER)

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()

app = wx.App()
frame = MyFrame(None)
frame.Show()
app.MainLoop()


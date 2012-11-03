

import wx
from spikepy.gui.stage_ctrl import StageCtrl

app = wx.PySimpleApp()
frame = wx.Frame(None, title='StageCtrl Demo', size=(400, 300))

ctrl = StageCtrl(frame, 'stage name', 'Stage Name', ['a', 'b', 'c'])

frame.Show()
app.MainLoop()




import wx

from .look_and_feel_settings import lfs
from . import program_text as pt

class PreferencesFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title=pt.PREFERENCES_FRAME_TITLE,
                 size=None, style=lfs.MAIN_FRAME_STYLE):
                 
        if size is None: size = lfs.PREFERENCES_FRAME_SIZE             
        wx.Frame.__init__(self, parent, title=title, size=size, style=style)

class PreferencesNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)

        workspaces_panel = WorkSpacesPanel(self)

        self.AddPage(workspaces_panel, pt.WORKSPACES_MANAGER)

class WorkspacesPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        

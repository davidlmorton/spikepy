"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import wx

from spikepy.common import program_text as pt

class PreferencesFrame(wx.Frame):
    def __init__(self, parent, id=wx.ID_ANY, title=pt.PREFERENCES_FRAME_TITLE,
                 size=None):
        pass
                 

class PreferencesNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)

        workspaces_panel = WorkSpacesPanel(self)

        self.AddPage(workspaces_panel, pt.WORKSPACES_MANAGER)

class WorkspacesPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        

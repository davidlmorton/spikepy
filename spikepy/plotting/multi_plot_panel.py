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

import weakref

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.common import program_text as pt
from spikepy.plotting.plot_panel import PlotPanel

class MultiPlotPanel(ScrolledPanel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        """
        A panel which holds multiple similar PlotPanels. Right-click will
            toggle showing a toolbar with PlotPanels.
        Subscribes to pubsub message: 
            'SHOW_PLOT' to alter which PlotPanel
                is visible.  (data=new_panel_key)
            'REMOVE_PLOT' to destroy PlotPanels after the file they are
                associated with is closed.
        """
        ScrolledPanel.__init__(self, parent)

        kwargs['toolbar_visible'] = toolbar_visible
        self._plot_kwargs = kwargs
        self._plot_panels = {}
        self._currently_shown = 'DEFAULT'
        self._toolbar_visible = toolbar_visible 

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.add_plot('DEFAULT')
        self._plot_panels['DEFAULT'].Show(True)
        self.SetupScrolling(scrollToTop=False)

        pub.subscribe(self._show_plot, topic='SHOW_PLOT')
        pub.subscribe(self._remove_plot, topic='REMOVE_PLOT')

    def OnChildFocus(self, event=None):
        """Overwrites ScrolledPanel's OnChildFocus to NOT scroll the
            child into view."""
        pass

    def add_plot(self, key, **kwargs):
        ''' 
        Add new plot, if key already exists, overwrite silently.
        '''
        if key in self._plot_panels.keys():
            raise RuntimeError("Plot with key '%s' already in this MultiPlotPanel." % key)

        self._plot_kwargs.update(kwargs)
        self._plot_panels[key] = PlotPanel(self, **self._plot_kwargs)
        self.GetSizer().Add(self._plot_panels[key], proportion=1, 
                                                    flag=wx.EXPAND)

        self._plot_panels[key].Show(False)
        self.Layout()

    def draw_canvas(self, key):
        # hide -> draw -> unhide   to avoid display bugs with canvas
        old_shown_state = self._plot_panels[key].IsShown()
        self._plot_panels[key].Show(False)
        figure = self._plot_panels[key].figure
        figure.canvas.draw()
        self._plot_panels[key].Show(old_shown_state)
        self.SetupScrolling()
        self.Layout()

    def clear_plot(self, key=None):
        self._plot_panels[key].clear()

    def _remove_plot(self, message):
        removed_panel_key = message.data
        if removed_panel_key == self._currently_shown:
            self._show_plot(new_panel_key='DEFAULT')
        self._plot_panels[removed_panel_key].Destroy()

    def _show_plot(self, message=None, new_panel_key=None):
        if new_panel_key is None:
            new_panel_key = message.data
        if new_panel_key not in self._plot_panels.keys():
            raise RuntimeError(pt.MISSING_PLOT_ERROR %
                                new_panel_key)

        # --- Hide what's shown now first.
        shown_plot_panel = self._plot_panels[self._currently_shown]
        shown_plot_panel.Show(False)

        # --- Swap what should be shown.
        self._currently_shown = new_panel_key
        showing_plot_panel = self._plot_panels[new_panel_key]

        # --- Show what should be shown.
        showing_plot_panel.Show(True)
        self.Layout()
        self.SetupScrolling()


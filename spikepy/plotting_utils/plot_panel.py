#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import copy
import gc

try:
    from spikepy.plotting_utils.import_matplotlib import *
except ImportError:
    import matplotlib
    # breaks pep-8 to put code here, but matplotlib 
    #     requires this before importing wxagg backend
    matplotlib.use('WXAgg', warn=False) 
    from matplotlib.backends.backend_wxagg import \
            FigureCanvasWxAgg as Canvas, \
            NavigationToolbar2WxAgg as Toolbar
    from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub


class CustomToolbar(Toolbar):
    """
    A toolbar which has the stupid adjust subplots button removed.
    """
    def __init__(self, canvas, plot_panel, **kwargs):
        Toolbar.__init__(self, canvas, **kwargs)
        self.DeleteToolByPos(6) # subplots adjust tool is worse than useless.

class PlotPanel(wx.Panel):
    def __init__(self, parent, toolbar_visible=False, **kwargs):
        """
        A panel which contains a matplotlib figure with (optionally) a 
            toolbar to zoom/pan/ect.
        Inputs:
            parent              : the parent frame/panel
            toolbar_visible     : the initial state of the toolbar
            **kwargs            : arguments passed on to 
                                  matplotlib.figure.Figure
        Introduces:
            figure              : a matplotlib figure
            canvas              : a FigureCanvasWxAgg from matplotlib's
                                  backends
            toggle_toolbar()    : to toggle the visible state of the toolbar
            show_toolbar()      : to show the toolbar
            hide_toolbar()      : to hide the toolbar
        Subscribes to:
            'TOGGLE_TOOLBAR'    : if data=None or data=self will toggle the
                                  visible state of the toolbar
            'SHOW_TOOLBAR'      : if data=None or data=self will show the
                                  toolbar
            'HIDE_TOOLBAR'      : if data=None or data=self will hide the
                                  toolbar
        """
        wx.Panel.__init__(self, parent)

        self.figure = Figure(**kwargs)
        self.canvas = Canvas(self, wx.ID_ANY, self.figure)
        self.toolbar = CustomToolbar(self.canvas, self)
        self.toolbar.Show(False)
        self.toolbar.Realize()

        toolbar_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.x_coord = wx.StaticText(self, label='x:')
        self.y_coord = wx.StaticText(self, label='y:')
        toolbar_sizer.Add(self.toolbar, proportion=2)
        toolbar_sizer.Add(self.x_coord, proportion=1, 
                flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.LEFT, border=5)
        toolbar_sizer.Add(self.y_coord, proportion=1,
                flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.LEFT, border=5)


        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(toolbar_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(self.canvas,  proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        figheight = self.figure.get_figheight()
        figwidth  = self.figure.get_figwidth()
        min_size = self.set_minsize(figwidth ,figheight)

        self._toolbar_visible = toolbar_visible
        if toolbar_visible:
            self.show_toolbar()
        else:
            self.hide_toolbar()

        self.canvas.Bind(wx.EVT_LEFT_DCLICK, self.toggle_toolbar)

        self._last_time_coordinates_updated = 0.0
        self._coordinates_blank = True
        self.canvas.mpl_connect('motion_notify_event', self._update_coordinates)
        
        # ---- Setup Subscriptions
        pub.subscribe(self._toggle_toolbar, topic="TOGGLE_TOOLBAR")
        pub.subscribe(self._show_toolbar,   topic="SHOW_TOOLBAR")
        pub.subscribe(self._hide_toolbar,   topic="HIDE_TOOLBAR")

        self.axes = {}

    def _save_history(self):
        if (hasattr(self.toolbar, '_views') and 
                hasattr(self.toolbar, '_positions')):
            self._old_history = {}
            self._old_history['views'] = copy.copy(self.toolbar._views)
            self._old_history['positions'] = copy.copy(self.toolbar._positions)

    def _restore_history(self):
        if hasattr(self, '_old_history'):
            self.toolbar._views = self._old_history['views']
            self.toolbar._positions = self._old_history['positions']
            self.toolbar.set_history_buttons()
            if hasattr(self.toolbar, '_update_view'):
                self.toolbar._update_view()

    def clear(self, keep_history=False):
        self._save_history()
        self.axes = {}
        self.figure.clear()
        gc.collect()

    def set_minsize(self, figwidth, figheight):
        dpi = self.figure.get_dpi()
        # compensate for toolbar height, even if not visible, to keep
        #   it from riding up on the plot when it is visible and the
        #   panel is shrunk down.
        toolbar_height = self.toolbar.GetSize()[1]
        min_size_x = dpi*figwidth
        min_size_y = dpi*figheight+toolbar_height
        min_size = (min_size_x, min_size_y)
        self.SetMinSize(min_size)
        return min_size

    # --- TOGGLE TOOLBAR ----
    def _toggle_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.toggle_toolbar()

    def toggle_toolbar(self, event=None):
        '''
        Toggle the visible state of the toolbar.
        '''
        if self._toolbar_visible:
            self.hide_toolbar()
        else:
            self.show_toolbar()

    # --- SHOW TOOLBAR ----
    def _show_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.show_toolbar()

    def show_toolbar(self):
        '''
        Make the toolbar visible.
        '''
        self.toolbar.Show(True)
        self.x_coord.Show(True)
        self.y_coord.Show(True)
        self._toolbar_visible = True
        self.Layout()

    # --- HIDE TOOLBAR ----
    def _hide_toolbar(self, message):
        if (message.data is None or 
            self is message.data):
            self.hide_toolbar()

    def hide_toolbar(self):
        '''
        Make toolbar invisible.
        '''
        self.toolbar.Show(False)
        self.x_coord.Show(False)
        self.y_coord.Show(False)
        self._toolbar_visible = False
        self.Layout()

    def _update_coordinates(self, event=None):
        if event.inaxes:
            now = time.time()
            # only once every 100 ms.
            if now-self._last_time_coordinates_updated > 0.100:
                self._last_time_coordinates_updated = now
                x, y = event.xdata, event.ydata
                self._coordinates_blank = False
                self.x_coord.SetLabel('x: %e' % x)
                self.y_coord.SetLabel('y: %e' % y)
        elif not self._coordinates_blank:
            # make the coordinates blank
            self._coordinates_not_blank = True
            self.x_coord.SetLabel('x: ')
            self.y_coord.SetLabel('y: ')



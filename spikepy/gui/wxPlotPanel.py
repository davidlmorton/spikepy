import matplotlib
matplotlib.use( 'WXAgg' )
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx as Toolbar
from matplotlib.figure import Figure
import wx
from wx.lib.pubsub import Publisher as pub
import utils

WHITE = (255,255,255)

class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
    flag, and the actual resizing of the figure triggered by an Idle event."""
    def __init__(self, parent, surround_color=WHITE, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = Figure(dpi=dpi, figsize=(0.5,0.5))
        self.canvas = FigureCanvasWxAgg(self, -1, self.figure)
        self._set_surround_color(surround_color)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND)
        self.SetSizer(sizer)
        pub.subscribe(self._toggle_toolbar, topic="TOGGLE TOOLBAR")
        self._toolbar_visible = False

        self.Bind(wx.EVT_CONTEXT_MENU, self._context_menu)

    def _context_menu(self, event):
        if not hasattr(self, '_cmid_show_or_hide_toolbar'):
            self._cmid_show_or_hide_toolbar  = wx.NewId()

            self.Bind(wx.EVT_MENU, self._show_or_hide_toolbar, 
                      id=self._cmid_show_or_hide_toolbar)

        cm = wx.Menu()
        # toggle toolbar item
        item = wx.MenuItem(cm, self._cmid_show_or_hide_toolbar, 
                           'Show/Hide Toolbar')
        bmp = utils.get_bitmap_icon('image_new')
        item.SetBitmap(bmp)
        cm.AppendItem(item)
        self.PopupMenu(cm)
        cm.Destroy()

    def _do_toolbar_toggling(self):
        sizer = self.GetSizer()
        if self._toolbar_visible:
            sizer.Detach(self.toolbar)
            self.toolbar.Disable()
            self.toolbar.Show(False)
            self._toolbar_visible = False
        else:
            if not hasattr(self, 'toolbar'):
                self.toolbar = Toolbar(self.canvas)
                self.toolbar.Realize()
            else:
                self.toolbar.Enable()
                self.toolbar.Show()
            sizer.Add(self.toolbar, 0 , wx.LEFT | wx.EXPAND)
            self._toolbar_visible = True
        sizer.Layout()

    def _show_or_hide_toolbar(self, event):
        self._do_toolbar_toggling()
        
    def _toggle_toolbar(self, message):
        if message.data is not None and self is not message.data:
            return
        self._do_toolbar_toggling()

    def _set_surround_color(self, rgb):
        """Set figure and canvas colours to be the same."""
        if rgb is None:
            rgb = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        self.canvas.SetBackgroundColour(rgb)
        self.figure.set_facecolor(norm_rgb(rgb))

    def plot(self): 
        pass

def norm_rgb(rgb, num_shades=256):
    return_rgb = [channel/float(num_shades-1) for channel in rgb]
    return return_rgb

import wx
from wx.lib.pubsub import Publisher as pub

from .filter_plot_panel import FilterPlotPanel

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = FilterResultsPanel(self, "detection")
        detection_panel = wx.Panel(self)
        extraction_filter_panel = FilterResultsPanel(self, "extraction")
        extraction_panel = wx.Panel(self)
        clustering_panel = wx.Panel(self)
        
        self.AddPage(detection_filter_panel, "Detection Filter")
        self.AddPage(detection_panel, "Detection")
        self.AddPage(extraction_filter_panel, "Extraction Filter")
        self.AddPage(extraction_panel, "Extraction")
        self.AddPage(clustering_panel, "Clustering")

class FilterResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name

        filter_buttons = FilterButtons(self)
        filter_plot_panel = FilterPlotPanel(self, name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(filter_buttons, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(filter_plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self._show_psd, filter_buttons.show_psd_button)
        self.Bind(wx.EVT_BUTTON, self._zoom_in, filter_buttons.zoom_in_button)
        self.Bind(wx.EVT_BUTTON, self._zoom_out, filter_buttons.zoom_out_button)
        self.filter_buttons = filter_buttons

    def _show_psd(self, event=None):
        pub.sendMessage(topic='SHOW_PSD', data=self.name)
        self.filter_buttons.show_psd_button.Disable()

    def _zoom_in(self, event=None):
        pub.sendMessage(topic='ZOOM_PLOT', data=(self.name, 1.5) )

    def _zoom_out(self, event=None):
        pub.sendMessage(topic='ZOOM_PLOT', data=(self.name, 1/1.5) )
        
class FilterButtons(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.show_psd_button = wx.Button(self, label='Show Power Spectrum')
        self.zoom_in_button = wx.Button(self, label='Enlarge Figure')
        self.zoom_out_button = wx.Button(self, label='Shrink Figure')

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALL
        sizer.Add(self.show_psd_button, proportion=0, flag=flag, border=4)
        sizer.Add(self.zoom_in_button,  proportion=0, flag=flag, border=4)
        sizer.Add(self.zoom_out_button, proportion=0, flag=flag, border=4)
        self.SetSizer(sizer)


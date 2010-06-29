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

        filter_plot_panel = FilterPlotPanel(self, name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(filter_plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)


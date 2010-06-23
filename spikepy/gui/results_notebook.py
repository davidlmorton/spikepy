import wx
from wx.lib.pubsub import Publisher as pub

from .filter_trace_plot_panel import FilterTracePlotPanel
from .filter_psd_plot_panel import FilterPSDPlotPanel

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

        filter_trace_plot_panel = FilterTracePlotPanel(self, name)
        filter_psd_plot_panel   = FilterPSDPlotPanel(self, name)

        sizer = wx.GridBagSizer()
        sizer.Add(filter_psd_plot_panel,   (0,0), span=(1,1), 
                flag=wx.ALL|wx.EXPAND, border=10)
        sizer.Add(filter_trace_plot_panel, (0,1), span=(2,1), 
                flag= wx.ALL|wx.EXPAND, border=10)
        sizer.AddGrowableRow(0, proportion=1)
        sizer.AddGrowableRow(1, proportion=2)
        sizer.AddGrowableCol(0, proportion=1)
        sizer.AddGrowableCol(1, proportion=2)
        self.SetSizer(sizer)


import wx
from wx.lib.pubsub import Publisher as pub

from .filter_plot_panel import FilterPlotPanel
from .detection_plot_panel import DetectionPlotPanel
from .extraction_plot_panel import ExtractionPlotPanel
from .look_and_feel_settings import lfs
from . import program_text as pt

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = FilterResultsPanel(self, "detection")
        detection_panel = DetectionResultsPanel(self, 'detection')
        extraction_filter_panel = FilterResultsPanel(self, "extraction")
        extraction_panel = ExtractionResultsPanel(self, "extraction")
        clustering_panel = wx.Panel(self)
        
        self.AddPage(detection_filter_panel,  pt.DETECTION_FILTER)
        self.AddPage(detection_panel,         pt.DETECTION)
        self.AddPage(extraction_filter_panel, pt.EXTRACTION_FILTER)
        self.AddPage(extraction_panel,        pt.EXTRACTION)
        self.AddPage(clustering_panel,        pt.CLUSTERING)

        self.page_names = ['Detection Filter',
                            'Detection', 
                            'Extraction Filter',
                            'Extraction',
                            'Clustering']

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._page_changing)

    def _page_changing(self, event=None):
        old = event.GetOldSelection()
        new = event.GetSelection()
        pub.sendMessage(topic='RESULTS_NOTEBOOK_PAGE_CHANGING', 
                        data=(self.page_names[old],self.page_names[new]))
        event.Skip()

class FilterResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name

        cursor_position_bar = CursorPositionBar(self)
        self.filter_plot_panel = FilterPlotPanel(self, name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(cursor_position_bar, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(self.filter_plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.filter_plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates


class ExtractionResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name

        cursor_position_bar = CursorPositionBar(self)
        self.extraction_plot_panel = ExtractionPlotPanel(self, name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(cursor_position_bar, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(self.extraction_plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.detection_plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates

class DetectionResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name

        cursor_position_bar = CursorPositionBar(self)
        self.detection_plot_panel = DetectionPlotPanel(self, name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(cursor_position_bar, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(self.detection_plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.detection_plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates


class CursorPositionBar(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.x_text = wx.StaticText(self, label='', size=(150,-1), 
                style=wx.ST_NO_AUTORESIZE)
        self.y_text = wx.StaticText(self, label='', size=(150,-1),
                style=wx.ST_NO_AUTORESIZE)
        self.show_cursor_position_checkbox = wx.CheckBox(self, 
                label=pt.SHOW_CURSOR_POSITION)
        self.scientific_notation_checkbox = wx.CheckBox(self, 
                label=pt.USE_SCIENTIFIC_NOTATION)
        self.scientific_notation_checkbox.Disable()
        self.Bind(wx.EVT_CHECKBOX, self._show_position, 
                  self.show_cursor_position_checkbox)

        # ---- SUBSCRIPTIONS ----
        pub.subscribe(self._update_cursor_display, 
                      topic='UPDATE_CURSOR_DISPLAY')

        # ---- SIZERS ----
        checkbox_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.ALIGN_CENTER_VERTICAL
        checkbox_sizer.Add(self.show_cursor_position_checkbox, proportion=0,
                           flag=flag,
                           border=2)
        checkbox_sizer.Add(self.scientific_notation_checkbox, proportion=0,
                           flag=flag,
                           border=2)

        position_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        position_sizer.Add(self.x_text, proportion=0, flag=flag, border=2)
        position_sizer.Add(self.y_text, proportion=0, flag=flag, border=2)

        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(position_sizer,  proportion=0, flag=flag, border=10)
        sizer.Add(checkbox_sizer,  proportion=0, flag=flag, border=10)
        self.SetSizer(sizer)

    def _show_position(self, event=None):
        # tell the plots shown in this window to report their coordinates or no.
        self.GetParent()._tell_report_coordinates(event.IsChecked())
        self.scientific_notation_checkbox.Enable(event.IsChecked())

    def _update_cursor_display(self, message=None):
        if self.show_cursor_position_checkbox.IsChecked():
            x, y = message.data
            if x is not None:
                if self.scientific_notation_checkbox.IsChecked():
                    self.x_text.SetLabel('X = %1.8e' % x)
                    self.y_text.SetLabel('Y = %1.8e' % y)
                else:
                    self.x_text.SetLabel('X = %8.8f' % x)
                    self.y_text.SetLabel('Y = %8.8f' % y)
            else:
                self.x_text.SetLabel('')
                self.y_text.SetLabel('')


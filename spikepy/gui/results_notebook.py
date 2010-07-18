import wx
from wx.lib.pubsub import Publisher as pub

from .filter_plot_panel import FilterPlotPanel
from .detection_plot_panel import DetectionPlotPanel
from .extraction_plot_panel import ExtractionPlotPanel
from .look_and_feel_settings import lfs
from . import program_text as pt
from ..stages import filtering, detection, extraction

plot_panels = {"detection filter" : FilterPlotPanel,
               "detection"        : DetectionPlotPanel,
               "extraction filter": FilterPlotPanel,
               "extraction"       : ExtractionPlotPanel}

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = ResultsPanel(self,  "detection filter")
        detection_panel = ResultsPanel(self,         "detection")
        extraction_filter_panel = ResultsPanel(self, "extraction filter")
        extraction_panel = ResultsPanel(self,        "extraction")
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
        pub.subscribe(self._change_page, 
                      topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED')

    def _page_changing(self, event=None):
        old_page_num  = event.GetOldSelection()
        new_page_num  = event.GetSelection()
        old_page_name = self.page_names[old_page_num]
        new_page_name = self.page_names[new_page_num]
        pub.sendMessage(topic='RESULTS_NOTEBOOK_PAGE_CHANGING', 
                        data=(old_page_num, new_page_num))
        event.Skip()

    def _change_page(self, message=None):
        new_page_num = message.data
        self.SetSelection(new_page_num)

class ResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name
        cursor_position_bar = CursorPositionBar(self)
        self.plot_panel = plot_panels[self.name](self, self.name.split()[0])

        method_extras_button = wx.Button(self, label=pt.METHOD_EXTRAS)

        top_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        top_sizer.Add(cursor_position_bar, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        top_sizer.Add(method_extras_button, proportion=0, 
                flag=wx.ALL, border=0)
        
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(top_sizer, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(self.plot_panel, proportion=1, 
                flag=wx.ALL|wx.EXPAND, border=10)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self._show_method_extras)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates

    def _show_method_extras(self, event=None):
        results_stage = self.name
        fullpath = self.plot_panel._currently_shown
        pub.sendMessage(topic="SHOW_METHOD_EXTRAS", data=(results_stage, 
                                                          fullpath))
        
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
        sizer.Add(checkbox_sizer,  proportion=0, flag=flag, border=10)
        sizer.Add(position_sizer,  proportion=0, flag=flag, border=10)
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


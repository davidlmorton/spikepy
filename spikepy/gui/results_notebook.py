import wx
from wx.lib.pubsub import Publisher as pub

from spikepy.plotting.filter_plot_panel import FilterPlotPanel
from spikepy.plotting.detection_plot_panel import DetectionPlotPanel
from spikepy.plotting.extraction_plot_panel import ExtractionPlotPanel
from spikepy.plotting.clustering_plot_panel import ClusteringPlotPanel
from spikepy.plotting.summary_plot_panel import SummaryPlotPanel
from spikepy.gui.look_and_feel_settings import lfs
from spikepy.common import program_text as pt
from spikepy.stages import filtering, detection, extraction, clustering
from spikepy.gui.utils import SinglePanelFrame

plot_panels = {"detection_filter" : FilterPlotPanel,
               "detection"        : DetectionPlotPanel,
               "extraction_filter": FilterPlotPanel,
               "extraction"       : ExtractionPlotPanel,
               "clustering"       : ClusteringPlotPanel,
               "summary"          : SummaryPlotPanel}

# FIXME only used by details panel, which needs to be delegated.
stage_modules = {"detection_filter"  : filtering,
                 "detection"         : detection,
                 "extraction_filter" : filtering,
                 "extraction"        : extraction,
                 "clustering"        : clustering,
                 "summary"           : clustering}

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = ResultsPanel(self,  "detection_filter")
        detection_panel = ResultsPanel(self,         "detection")
        extraction_filter_panel = ResultsPanel(self, "extraction_filter")
        extraction_panel = ResultsPanel(self,        "extraction")
        clustering_panel = ResultsPanel(self,        "clustering")
        summary_panel = ResultsPanel(self,           "summary")
        
        self.AddPage(detection_filter_panel,  pt.DETECTION_FILTER)
        self.AddPage(detection_panel,         pt.DETECTION)
        self.AddPage(extraction_filter_panel, pt.EXTRACTION_FILTER)
        self.AddPage(extraction_panel,        pt.EXTRACTION)
        self.AddPage(clustering_panel,        pt.CLUSTERING)
        self.AddPage(summary_panel,           pt.SUMMARY)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_changed)

        # ---- Setup Subscriptions
        pub.subscribe(self._change_page, 
                      topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED')
        pub.subscribe(self._print,          topic="PRINT")
        pub.subscribe(self._page_setup,     topic="PAGE_SETUP")
        pub.subscribe(self._print_preview,  topic="PRINT_PREVIEW")

        # this is here for debugging in the pyflake shell
        self.results_panels = {'detection_filter':detection_filter_panel,
                               'detection':detection_panel,
                               'extraction_filter':extraction_filter_panel,
                               'extraction':extraction_panel,
                               'clustering':clustering_panel,
                               'summary':summary_panel}

    def get_currently_shown_plot_panel(self):
        # the following code relies heavily on existing structure, maybe this
        # isn't a good idea
        current_multi_plot_panel = self.GetCurrentPage().plot_panel
        plot_panels = current_multi_plot_panel._plot_panels
        current_plot_panel_key = current_multi_plot_panel._currently_shown
        return plot_panels[current_plot_panel_key]
        

    def _print(self, data=None):
        current_plot_panel = self.get_currently_shown_plot_panel()
        current_plot_panel.do_print()

    def _print_preview(self, event=None):
        current_plot_panel = self.get_currently_shown_plot_panel()
        current_plot_panel.print_preview()
    
    def _page_setup(self, event=None):
        current_plot_panel = self.get_currently_shown_plot_panel()
        current_plot_panel.page_setup()

    def _page_changed(self, event=None):
        old_page_num  = event.GetOldSelection()
        new_page_num  = event.GetSelection()
        pub.sendMessage(topic='RESULTS_NOTEBOOK_PAGE_CHANGING', 
                        data=(old_page_num, new_page_num))
        event.Skip()

    def _change_page(self, message=None):
        new_page_num = message.data
        self.ChangeSelection(new_page_num)

class ResultsPanel(wx.Panel):
    def __init__(self, parent, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name
        cursor_position_bar = CursorPositionBar(self)
        self.plot_panel = plot_panels[self.name](self, self.name)

        method_details_button = wx.Button(self, label=pt.METHOD_DETAILS)

        top_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        top_sizer.Add(cursor_position_bar, proportion=0, 
                flag=wx.ALL|wx.EXPAND, border=0)
        top_sizer.Add(method_details_button, proportion=0, 
                flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=4)
        
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(top_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(self.plot_panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self._show_method_details)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates

    def _show_method_details(self, event=None):
        # FIXME should be delegated via pubsub
        stage_name = self.name
        trial_id = self.plot_panel._currently_shown
        if trial_id == 'DEFAULT':
            return
        trial = self.plot_panel._trials[trial_id]
        stage_data = trial.get_stage_data(stage_name)
        method_name = stage_data.method
        if method_name is None:
            return
        stage_module = stage_modules[stage_name]
        method_index = stage_module.method_names.index(method_name)
        method_module = stage_module.method_modules[method_index]
        if hasattr(method_module, 'DetailsPanel'):
            title = pt.METHOD_DETAILS_FRAME_TITLE % method_name
            size = lfs.METHOD_DETAILS_FRAME_SIZE
            style = lfs.METHOD_DETAILS_FRAME_STYLE
            frame = SinglePanelFrame(self, title=title, size=size, style=style)
            details_panel = method_module.DetailsPanel(frame, trial, stage_name)
            frame.Show()


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


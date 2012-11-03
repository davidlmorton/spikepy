

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.gui.control_panels import VisualizationControlPanel
from spikepy.common import program_text as pt
from spikepy.gui import pyshell
from spikepy.common.config_manager import config_manager as config
from spikepy.plotting_utils.plot_panel import PlotPanel


class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, session, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = ResultsPanel(self, session, "detection_filter")
        detection_panel = ResultsPanel(self, session, "detection")
        extraction_filter_panel = ResultsPanel(self, session, 
                "extraction_filter")
        extraction_panel = ResultsPanel(self, session, "extraction")
        clustering_panel = ResultsPanel(self, session, "clustering")

        self.AddPage(detection_filter_panel,  pt.DETECTION_FILTER)
        self.AddPage(detection_panel,         pt.DETECTION)
        self.AddPage(extraction_filter_panel, pt.EXTRACTION_FILTER)
        self.AddPage(extraction_panel,        pt.EXTRACTION)
        self.AddPage(clustering_panel,        pt.CLUSTERING)

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_changed)
        self.Bind(wx.EVT_SIZE, self._on_size)

        # ---- Setup Subscriptions
        pub.subscribe(self._change_page, 
                      topic='STRATEGY_CHOICEBOOK_PAGE_CHANGED')

        # this is here for debugging in the pyflake shell
        self.results_panels = {'detection_filter':detection_filter_panel,
                               'detection':detection_panel,
                               'extraction_filter':extraction_filter_panel,
                               'extraction':extraction_panel,
                               'clustering':clustering_panel}
        pyshell.locals_dict['results_panels'] = self.results_panels
        self._selected_page_num = 0

    def _on_size(self, event):
        event.Skip()
        current_results_panel_size = self.GetCurrentPage().GetSize()
        pub.sendMessage("SET_RESULTS_FRAME_SIZE", 
                        data=current_results_panel_size)

    def get_current_stage_name(self):
        return self.GetPage(self._selected_page_num).name

    def _page_changed(self, event=None):
        old_page_num  = event.GetOldSelection()
        new_page_num  = event.GetSelection()
        self._selected_page_num = new_page_num
        try:
            old_page = self.GetPage(old_page_num)
            new_page = self.GetPage(new_page_num)
        except ValueError:
            # we're catching an odd behavior of wx on application close.
            event.Skip()
            return
        pub.sendMessage(topic='RESULTS_NOTEBOOK_PAGE_CHANGED', 
                        data=new_page.name)
        pub.sendMessage(topic="HIDE_RESULTS", data=old_page.name)
        event.Skip()

    def _change_page(self, message=None):
        new_page_num, old_page_num = message.data
        self.ChangeSelection(new_page_num)
        pub.sendMessage(topic='RESULTS_NOTEBOOK_PAGE_CHANGED', 
                        data=(old_page_num, new_page_num))

        old_page = self.GetPage(old_page_num)
        pub.sendMessage(topic="HIDE_RESULTS", data=old_page.name)


class ResultsPanel(ScrolledPanel):
    def __init__(self, parent, session, name, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        self.name = name

        sizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.visualizations = {}
        for visualization in session.plugin_manager.visualizations.values():
            if visualization.found_under_tab == name:
                self.visualizations[visualization.name] = visualization

        self.ctrls = {}
        for v_name in sorted(self.visualizations.keys()): 
            visualization = self.visualizations[v_name]
            self.ctrls[v_name] = VisualizationControlPanel(self, visualization)
            sizer.Add(self.ctrls[v_name], proportion=0, 
                    flag=wx.EXPAND|wx.ALL, border=2)
        
        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=False)

    def plot(self, trial):
        for ctrl in self.ctrls.values():
            ctrl.plot(trial)



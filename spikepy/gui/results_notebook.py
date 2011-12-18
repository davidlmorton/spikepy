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

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel

from spikepy.gui.strategy_pane import OptionalControlPanel
from spikepy.common import program_text as pt
from spikepy.gui import pyshell
from spikepy.common.config_manager import config_manager as config
from spikepy.plotting_utils.plot_panel import PlotPanel


class VisualizationControlPanel(OptionalControlPanel):
    num_columns = 3

    def layout_ui(self):
        active_checkbox = wx.CheckBox(self, label=self.plugin.name)
        self.Bind(wx.EVT_CHECKBOX, self._activate, active_checkbox)
        f = active_checkbox.GetFont()
        f.SetWeight(wx.BOLD)
        active_checkbox.SetFont(f)

        show_hide_button = wx.Button(self, label='+', size=(26, 26))
        self.Bind(wx.EVT_BUTTON, self._show_hide, show_hide_button)
        show_hide_button.SetToolTip(wx.ToolTip(pt.SHOW_HIDE_OPTIONS))

        top_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        top_sizer.Add(active_checkbox, flag=wx.ALIGN_CENTER_VERTICAL)
        top_sizer.Add(show_hide_button, flag=wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 
                border=5)

        main_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        main_sizer.Add(top_sizer, flag=wx.ALIGN_LEFT)

        control_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        col_sizers = []
        hidden_items = []
        for i in range(self.num_columns):
            col_sizers.append(wx.BoxSizer(orient=wx.VERTICAL))
            for ctrl_name in sorted(self.ctrls.keys())[i::self.num_columns]:
                hidden_items.append(self.ctrls[ctrl_name])
                col_sizers[-1].Add(self.ctrls[ctrl_name], 
                        flag=wx.EXPAND|wx.ALIGN_RIGHT)
                self.ctrls[ctrl_name].register_valid_entry_callback(
                        self._something_changed)
            control_sizer.Add(col_sizers[-1], proportion=1)
            if i != self.num_columns-1:
                static_line = wx.StaticText(self, style=wx.LI_VERTICAL)
                hidden_items.append(static_line)
                control_sizer.Add(static_line,
                        flag=wx.EXPAND|wx.ALL, border=3)

        main_sizer.Add(control_sizer, flag=wx.EXPAND)

        plot_panel = PlotPanel(self, figsize=config.get_size('figure'))
        main_sizer.Add(plot_panel, flag=wx.EXPAND|wx.ALL, border=5) 
        main_sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(main_sizer)

        self.active_checkbox = active_checkbox
        self.plot_panel = plot_panel
        self.hidden_items = hidden_items
        self.show_hide_button = show_hide_button
        self._hidden = True
        self.active = False

    def _show_hide(self, event):
        event.Skip()
        self._hidden = not self._hidden
        labels = {True:'+', False:'-'}
        self.show_hide_button.SetLabel(labels[self._hidden])
        for item in self.hidden_items:
            item.Show(not self._hidden)
        self.Layout()
        self.GetParent().Layout()
        self.GetParent().SetupScrolling(scroll_x=False, scrollToTop=False)

    def setup_active_state(self):
        OptionalControlPanel.setup_active_state(self)
        self.plot_panel.Show(self.active)
        if self.active:
            pub.sendMessage(topic='VISUALIZATION_PANEL_CHANGED', data=self)
        for item in self.hidden_items:
            item.Show(self.active and not self._hidden)
        self.show_hide_button.Enable(self.active)
        self.Layout()
        self.GetParent().Layout()
        self.GetParent().SetupScrolling(scroll_x=False, scrollToTop=False)

    def _something_changed(self, new_value):
        pub.sendMessage(topic='VISUALIZATION_PANEL_CHANGED', data=self)

    def plot(self, trial):
        if self.active:
            self.plugin.draw(trial, parent_panel=self, **self.pull())
        else:
            return

    def push(self, value_dict=None):
        if value_dict is not None:
            for name, value in value_dict.items():
                self.ctrls[name].SetValue(value)
        

class ResultsNotebook(wx.Notebook):
    def __init__(self, parent, session, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = ResultsPanel(self, session, "detection_filter")
        detection_panel = ResultsPanel(self, session, "detection")
        extraction_filter_panel = ResultsPanel(self, session, 
                "extraction_filter")
        extraction_panel = ResultsPanel(self, session, "extraction")
        clustering_panel = ResultsPanel(self, session, "clustering")
        summary_panel = ResultsPanel(self, session, "summary")

        self.AddPage(detection_filter_panel,  pt.DETECTION_FILTER)
        self.AddPage(detection_panel,         pt.DETECTION)
        self.AddPage(extraction_filter_panel, pt.EXTRACTION_FILTER)
        self.AddPage(extraction_panel,        pt.EXTRACTION)
        self.AddPage(clustering_panel,        pt.CLUSTERING)
        self.AddPage(summary_panel,           pt.SUMMARY)

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
                               'clustering':clustering_panel,
                               'summary':summary_panel}
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



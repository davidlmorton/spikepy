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

from spikepy.plotting.filter_plot_panel import FilterPlotPanel
from spikepy.plotting.detection_plot_panel import DetectionPlotPanel
from spikepy.plotting.extraction_plot_panel import ExtractionPlotPanel
from spikepy.plotting.clustering_plot_panel import ClusteringPlotPanel
from spikepy.plotting.summary_plot_panel import SummaryPlotPanel
from spikepy.common import program_text as pt
from spikepy.gui.utils import SinglePanelFrame
from spikepy.gui import pyshell

plot_panels = {"detection_filter" : FilterPlotPanel,
               "detection"        : DetectionPlotPanel,
               "extraction_filter": FilterPlotPanel,
               "extraction"       : ExtractionPlotPanel,
               "clustering"       : ClusteringPlotPanel,
               "summary"          : SummaryPlotPanel}

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
        pyshell.locals_dict['results_panels'] = self.results_panels
        self._selected_page_num = 0

    def _on_size(self, event):
        event.Skip()
        current_results_panel_size = self.GetCurrentPage().GetSize()
        pub.sendMessage("SET_RESULTS_FRAME_SIZE", 
                        data=current_results_panel_size)

    def should_plot(self, stage_name):
        return self.results_panels[stage_name].plot_checkbox.IsChecked()

    def get_current_stage_name(self):
        return self.GetPage(self._selected_page_num).name

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


class ResultsPanel(wx.Panel):
    def __init__(self, parent, session, name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.name = name
        self.plot_panel = plot_panels[self.name](self, session, self.name)
        self.plot_checkbox = wx.CheckBox(self, 
                                         label=pt.PLOT_RESULTS)
        self.plot_checkbox.SetValue(True)
        self.plot_checkbox.Show(False)

        top_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        top_sizer.Add(self.plot_checkbox, proportion=0, 
                flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM, border=4)
        
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(top_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(self.plot_panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

        pub.subscribe(self._set_plot_results_checkbox, 
                       "SET_PLOT_RESULTS_CHECKBOX")

        self.Bind(wx.EVT_BUTTON, self._show_method_details)
        self.Bind(wx.EVT_CHECKBOX, self._plot_results)

    def _set_plot_results_checkbox(self, message):
        state, name = message.data
        if name == self.name or name == 'all':
            self.plot_checkbox.SetValue(state)

    def _plot_results(self, event):
        if self.plot_checkbox.IsChecked():
            pub.sendMessage("PLOT_RESULTS", data=self.name)
        else:
            pub.sendMessage("HIDE_RESULTS", data=self.name)

    def _tell_report_coordinates(self, report_coordinates):
        for plot_panel in self.plot_panel._plot_panels.values():
            plot_panel._report_coordinates = report_coordinates

    def _show_method_details(self, event=None):
        pass

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


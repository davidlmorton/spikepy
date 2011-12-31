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

import spikepy.common.program_text as pt
from spikepy.utils.string_formatting import start_case
from spikepy.utils.wrap import wrap
from spikepy.gui.valid_controls import make_control
from spikepy.plotting_utils.plot_panel import PlotPanel
from spikepy.common.config_manager import config_manager as config

class ControlPanel(wx.Panel):
    '''
        A ControlPanel allows the user to set the parameters of a single
    method.
    '''
    def __init__(self, parent, plugin, valid_entry_callback=None, 
            background_color=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.plugin = plugin
        self.valid_entry_callback = valid_entry_callback
        self.background_color = background_color 

        if background_color is not None:
            self.SetBackgroundColour(background_color)

        self.build_controls()
        self.layout_ui()
        self.push(plugin.get_parameter_defaults())

    def layout_ui(self):
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        title = wx.StaticText(self, label=self.plugin.name)
        f = title.GetFont()
        f.SetWeight(wx.BOLD)
        title.SetFont(f)
        sizer.Add(title, flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        for ctrl_name in sorted(self.ctrls.keys()):
            sizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)
            self.ctrls[ctrl_name].register_valid_entry_callback(
                    self.valid_entry_callback)
        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(sizer)

    def build_controls(self):
        self.ctrls = {}
        for pname, valid_type in self.plugin.get_parameter_attributes().items():
            display_name = start_case(pname)
            self.ctrls[pname] = make_control(self, display_name, valid_type,
                    background_color=self.background_color)

    def pull(self):
        return_dict = {}
        for name, ctrl in self.ctrls.items():
            return_dict[name] = ctrl.GetValue()
        return return_dict

    def push(self, value_dict):
        for name, value in value_dict.items():
            self.ctrls[name].SetValue(value)

class OptionalControlPanel(ControlPanel):
    '''
        A ControlPanel that is optional and has a checkbox to turn
    on/off.
    '''
    def __init__(self, parent, plugin, valid_entry_callback=None, 
            background_color=None, 
            **kwargs):
        ControlPanel.__init__(self, parent, plugin, valid_entry_callback,
                background_color, **kwargs)

    def layout_ui(self):
        active_checkbox = wx.CheckBox(self, label=wrap(self.plugin.name, 40))
        f = active_checkbox.GetFont()
        f.SetWeight(wx.BOLD)
        active_checkbox.SetFont(f)

        active_checkbox.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self._activate, active_checkbox)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        sizer.Add(active_checkbox, flag=wx.ALIGN_LEFT)
        for ctrl_name in sorted(self.ctrls.keys()):
            sizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)
            self.ctrls[ctrl_name].register_valid_entry_callback(
                    self.valid_entry_callback)
        sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(sizer)
        self.active_checkbox = active_checkbox

    def _activate(self, event):
        event.Skip()
        if self.valid_entry_callback is not None:
            self.valid_entry_callback(self.active)
        self.setup_active_state()

    @property
    def active(self):
        return self.active_checkbox.GetValue()

    @active.setter
    def active(self, value):
        self.active_checkbox.SetValue(value)
        self.setup_active_state()

    def setup_active_state(self):
        for ctrl in self.ctrls.values():
            ctrl.Show(self.active)
        self.Layout()
        self.GetParent().Layout()
        self.GetParent().SetupScrolling(scrollToTop=False)

    def pull(self):
        if self.active:
            return_dict = {}
            for name, ctrl in self.ctrls.items():
                return_dict[name] = ctrl.GetValue()
            return return_dict
        else:
            return None

    def push(self, value_dict=None):
        if value_dict is None:
            self.active = False
        else:
            self.active = True
            for name, value in value_dict.items():
                self.ctrls[name].SetValue(value)


class ExportControlPanel(OptionalControlPanel):
    def layout_ui(self):
        vsizer = wx.BoxSizer(orient=wx.VERTICAL)
        hsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        tsizer = wx.BoxSizer(orient=wx.VERTICAL)

        active_checkbox = wx.CheckBox(self, label=self.plugin.name)
        f = active_checkbox.GetFont()
        f.SetWeight(wx.BOLD)
        active_checkbox.SetFont(f)
        self.Bind(wx.EVT_CHECKBOX, self._activate, active_checkbox)

        vsizer.Add(active_checkbox, flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        for ctrl_name in sorted(self.ctrls.keys()):
            vsizer.Add(self.ctrls[ctrl_name], flag=wx.EXPAND|wx.ALIGN_RIGHT)

        description = wx.StaticText(self, label=self.plugin.description)
        hsizer.Add(vsizer)
        hsizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 
                flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=8)
        hsizer.Add(description, proportion=1, flag=wx.ALL, border=5)

        tsizer.Add(hsizer)
        tsizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL, border=3)
        self.SetSizer(tsizer)

        self.active_checkbox = active_checkbox


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

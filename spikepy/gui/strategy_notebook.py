import wx

from .utils import NamedChoiceCtrl

class StrategyNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = FilterPanel(self, 1, "Detection Filter")
        detection_panel = wx.Panel(self)
        extraction_filter_panel = wx.Panel(self)
        extraction_panel = wx.Panel(self)
        clustering_panel = wx.Panel(self)
        
        self.AddPage(detection_filter_panel, "DF")
        self.AddPage(detection_panel, "D")
        self.AddPage(extraction_filter_panel, "EF")
        self.AddPage(extraction_panel, "E")
        self.AddPage(clustering_panel, "C")

class FilterPanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        title_panel = TitlePanel(self, stage_num, stage_name)
        method_chooser = NamedChoiceCtrl(self, name="Filter method:",
                                 choices=["Infinite impulse response",
                                          "Finite impulse response"])
        self.method_description = wx.StaticText(self, 
                                  label="Description: Choose a filter method.") 
        method_controls = ControlsPanel(self)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel, proportion=1, flag=ea_flag, border=5)
        sizer.Add(method_chooser, proportion=1, flag=ea_flag|wx.ALIGN_CENTER, 
                  border=5)
        sizer.Add(self.method_description, proportion=1, flag=ea_flag, 
                  border=5)
        sizer.Add(method_controls, proportion=1, flag=ea_flag, border=5)
        
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  method_chooser.choice)

    def _method_choice_made(self, event):
        method_chosen = event.GetString()
        self.method_description.SetLabel(
           "Description: Description for %s filtering method." % method_chosen)

class TitlePanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        stage_num_text = wx.StaticText(self, label="Stage\n%d" % stage_num,
                                       style=wx.ALIGN_CENTER)
        stage_num_font = stage_num_text.GetFont()
        stage_num_font.SetWeight(wx.FONTWEIGHT_BOLD)
        stage_num_text.SetFont(stage_num_font)
        stage_name_text = wx.StaticText(self, label=stage_name)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(stage_num_text, proportion=1, flag=wx.EXPAND|wx.ALL, 
                                                                    border=5)
        sizer.Add(stage_name_text, proportion=1, 
                  flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(sizer)

class DescriptionPanel(wx.Panel):
    def __init__(self, parent, description="Choose a filter method.", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.description = description
        description_text = wx.StaticText(self, 
                                    label="Description: %s" % self.description)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(description_text, proportion=1)
        
        self.SetSizer(sizer)

class ControlsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

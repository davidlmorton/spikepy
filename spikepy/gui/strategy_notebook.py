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
        category_chooser = NamedChoiceCtrl(self, name="Filter category:",
                                 choices=["Filter 1", "Filter 2", "Filter 3"])
        category_description = wx.Panel(self)
        category_controls = wx.Panel(self)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel, proportion=1, flag=ea_flag, border=5)
        sizer.Add(category_chooser, proportion=1, flag=ea_flag, border=5)
        sizer.Add(category_description, proportion=1, flag=ea_flag, border=5)
        sizer.Add(category_controls, proportion=1, flag=ea_flag, border=5)
        
        self.SetSizer(sizer)

class TitlePanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        stage_num_text = wx.StaticText(self, label="Stage \n%d" % stage_num,
                                                         style=wx.ALIGN_CENTER)
        stage_num_font = stage_num_text.GetFont()
        stage_num_font.SetWeight(wx.FONTWEIGHT_BOLD)
        stage_num_text.SetFont(stage_num_font)
        stage_name_text = wx.StaticText(self, label=stage_name)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(stage_num_text, proportion=1, flag=wx.EXPAND|wx.RIGHT, 
                                                                    border=5)
        sizer.Add(stage_name_text, proportion=1, flag=wx.EXPAND)

        self.SetSizer(sizer)



import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.scrolledpanel import ScrolledPanel
from wx.lib.buttons import GenButton

from .utils import NamedChoiceCtrl, recursive_layout
from ..stages import filtering

class StrategyPane(ScrolledPanel):
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, **kwargs)
        
        self.strategy_summary = StrategySummary(self)
        line = wx.StaticLine(self)
        stage_choicebook = wx.Choicebook(self, wx.ID_ANY)

        detection_filter_panel = FilterPanel(stage_choicebook, 
                                             1, "Detection Filter")
        detection_panel = DetectionPanel(stage_choicebook, 
                                         2, "Spike Detection")
        extraction_filter_panel = FilterPanel(stage_choicebook, 
                                              3, "Extraction Filter")
        extraction_panel = wx.Panel(stage_choicebook)
        clustering_panel = wx.Panel(stage_choicebook)

        stage_choicebook.AddPage(detection_filter_panel, 
                                 "Detection Filter Strategy")
        stage_choicebook.AddPage(detection_panel, "Detection Strategy")
        stage_choicebook.AddPage(extraction_filter_panel, 
                                 "Extraction Filter Strategy")
        stage_choicebook.AddPage(extraction_panel, "Extraction Strategy")
        stage_choicebook.AddPage(clustering_panel, "Clustering Strategy")
        
        # setup the sizer
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.EXPAND|wx.ALL
        border = 5
        sizer.Add(self.strategy_summary,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(line,  proportion=0, 
                                          flag=flag|wx.ALIGN_CENTER_HORIZONTAL, 
                                          border=border)
        sizer.Add(stage_choicebook,  proportion=1, flag=flag, border=border)
        self.strategy_summary.select_stage(1)
        self.SetSizer(sizer)
        self.do_layout()

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self._page_changed)

    def _page_changed(self, event=None):
        if event is not None:
            new_page_num = event.GetSelection()
            self.strategy_summary.select_stage(new_page_num+1)

    def do_layout(self):
        self.SetupScrolling(scroll_x = False)
        self.Layout()

class StrategySummary(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        
        title = wx.StaticText(self, label='Stage)  Method')
        s = []
        s.append(wx.StaticText(self, label=' 1)  Custom'))
        s.append(wx.StaticText(self, label=' 2)  Custom'))
        s.append(wx.StaticText(self, label=' 3)  Custom'))
        s.append(wx.StaticText(self, label=' 4)  Custom'))
        s.append(wx.StaticText(self, label=' 5)  Custom'))

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL | wx.ALIGN_CENTER_HORIZONTAL
        sizer.Add(title, proportion=0, flag=flag, border=3)
        for stage_text in s:
            sizer.Add(stage_text, proportion=0, flag=flag, 
                                  border=4)
        self.SetSizer(sizer)
        self.stage_text_list = s
        self._selected_stage = 1

    def select_stage(self, stage_num):
        old_stage_text = self.stage_text_list[self._selected_stage-1]
        stage_font = old_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_NORMAL)
        old_stage_text.SetFont(stage_font)

        new_stage_text = self.stage_text_list[stage_num-1]
        stage_font = new_stage_text.GetFont()
        stage_font.SetWeight(wx.FONTWEIGHT_BOLD)
        new_stage_text.SetFont(stage_font)
        self._selected_stage = stage_num


class FilterPanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.stage_num = stage_num
        self.stage_name = stage_name

        title_panel = TitlePanel(self, stage_num, stage_name)

        # --- setup methods ---
        self.methods = {}
        self.method_names = filtering.method_names
        for method_module, method_name in zip(filtering.method_modules, 
                                              self.method_names):
            self.methods[method_name] = {}
            self.methods[method_name]['control_panel'] = \
                    method_module.ControlPanel(self)
            self.methods[method_name]['control_panel'].Show(False)
            self.methods[method_name]['description'] = method_module.description
        self._method_name_chosen = self.method_names[0]

        # --- setup other panel elements ---
        self.method_chooser = NamedChoiceCtrl(self, name="Filter method:",
                                 choices=self.method_names)
#        self.method_description_text = StaticBoxText(self, label='Description') 
        self.filter_button = wx.Button(self, label="Run filter")
        self.filter_button.Show(False)

        # --- sizer config ---
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel,                  proportion=0, 
                      flag=ea_flag,                        border=3)
        sizer.Add(self.method_chooser,          proportion=0, 
                      flag=ea_flag,                        border=3)
 #       sizer.Add(self.method_description_text, proportion=0, 
 #                     flag=ea_flag,                        border=3)
        for method in self.methods.values():
            sizer.Add(method['control_panel'],  proportion=0,
                      flag=ea_flag,                        border=3)
        sizer.Add(self.filter_button,           proportion=0, 
                      flag=wx.ALL,                         border=1)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._run_filter, self.filter_button)
#        self._method_choice_made(method_name=self._method_name_chosen)
        
        pub.subscribe(self._filtering_completed, topic='FILTERING_COMPLETED')
        self._method_choice_made(method_name=self.method_names[0])

    def _filtering_completed(self, message=None):
        self.filter_button.SetLabel('Run filter')
        self.filter_button.Enable()

    
    def _method_choice_made(self, event=None, method_name=None):
        self.methods[self._method_name_chosen]['control_panel'].Show(False)

        if method_name is not None:
            self._method_name_chosen = method_name
            self.method_chooser.SetStringSelection(method_name)
        else:
            self._method_name_chosen = self.method_chooser.GetStringSelection()

        #self.method_description_text.SetText( 
        #        self.methods[self._method_name_chosen]['description'])

        self.methods[self._method_name_chosen]['control_panel'].Show(True)
        self.filter_button.Show(True)
        self.Layout()
    

    def _run_filter(self, event=None):
        control_panel = self.methods[self._method_name_chosen]['control_panel']
        settings = control_panel.get_control_settings()
        self.filter_button.SetLabel('Filtering...')
        self.filter_button.Disable()
        wx.Yield() # about to let scipy hog cpu, so process all wx events.
        pub.sendMessage(topic='FILTER', data=(self.stage_name, 
                                              self._method_name_chosen,
                                              settings))

        

class DetectionPanel(wx.Panel):
    def __init__(self, parent, stage_num, stage_name, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        title_panel = TitlePanel(self, stage_num, stage_name)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel, proportion=0, flag=ea_flag, border=5)

        self.SetSizer(sizer)
    

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
        sizer.Add(stage_num_text, proportion=0, flag=wx.EXPAND|wx.ALL, 
                                                                    border=5)
        sizer.Add(stage_name_text, proportion=0, 
                  flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(sizer)

class DescriptionPanel(wx.Panel):
    def __init__(self, parent, description="Choose a filter method.", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.description = description
        description_text = wx.StaticText(self, 
                                    label="Description: %s" % self.description)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        sizer.Add(description_text, proportion=0)
        
        self.SetSizer(sizer)

class ControlsPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

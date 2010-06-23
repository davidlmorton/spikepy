import wx
from wx.lib.pubsub import Publisher as pub

from .utils import NamedChoiceCtrl, StaticBoxText
from ..stages import filtering

class StrategyNotebook(wx.Notebook):
    def __init__(self, parent, **kwargs):
        wx.Notebook.__init__(self, parent, **kwargs)
        
        detection_filter_panel = FilterPanel(self, 1, "Detection Filter")
        detection_panel = DetectionPanel(self, 2, "Spike Detection")
        extraction_filter_panel = FilterPanel(self, 3, "Extraction Filter")
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
        self.method_description_text = StaticBoxText(self, label='Description') 
        self.filter_button = wx.Button(self, label="Run filter")
        self.filter_button.Show(False)

        # --- sizer config ---
        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        ea_flag = wx.EXPAND|wx.ALL
        sizer.Add(title_panel,                  proportion=0, 
                      flag=ea_flag,                        border=5)
        sizer.Add(self.method_chooser,          proportion=0, 
                      flag=wx.ALL|wx.ALIGN_LEFT|wx.EXPAND, border=5)
        sizer.Add(self.method_description_text, proportion=0, 
                      flag=ea_flag,                        border=5)
        for method in self.methods.values():
            sizer.Add(method['control_panel'],  proportion=0,
                      flag=ea_flag,  border=5)
        sizer.Add(self.filter_button,           proportion=0, 
                      flag=wx.ALL,                         border=3)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CHOICE, self._method_choice_made,
                  self.method_chooser.choice)
        self.Bind(wx.EVT_BUTTON, self._run_filter, self.filter_button)
        self._method_choice_made(method_name=self._method_name_chosen)
        
        pub.subscribe(self._filtering_completed, topic='FILTERING_COMPLETED')

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

        self.method_description_text.SetText( 
                self.methods[self._method_name_chosen]['description'])

        self.methods[self._method_name_chosen]['control_panel'].Show(True)
        self.filter_button.Show(True)
        wx.CallLater(10,self.Layout)

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

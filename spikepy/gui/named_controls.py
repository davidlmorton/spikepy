import wx

from .look_and_feel_settings import lfs

class NamedChoiceCtrl(wx.Panel):
    def __init__(self, parent, name="", choices=[], bar_width=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        if bar_width == None and len(choices) > 0:
            bar_width_in_characters = max(map(len, choices))
            bar_width = bar_width_in_characters*8
            self.choice = wx.Choice(self, choices=choices) 
        elif bar_width == None and len(choices) == 0:
            self.choice = wx.Choice(self, choices=choices)
        else:
            self.choice = wx.Choice(self, choices=choices)
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        border = lfs.CHOICE_BORDER
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        sizer.Add(self.name, proportion=0, flag=flag, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.choice, proportion=1, flag=flag, border=border)
        
        self.SetSizer(sizer)

    def GetStringSelection(self):
        return self.choice.GetStringSelection()

    def SetStringSelection(self, string):
        self.choice.SetStringSelection(string)

    def SetItems(self, item_list):
        self.choice.SetItems(item_list)

    def GetItems(self):
        return self.choice.GetItems()

class NamedSpinCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent)

        self.name = wx.StaticText(self, label=name)
        if 'style' in kwargs.keys():
            kwargs['style'] = kwargs['style']|wx.SP_ARROW_KEYS
        else:
            kwargs['style'] = wx.SP_ARROW_KEYS
        self.spin_ctrl = wx.SpinCtrl(self, size=(50,-1), **kwargs)
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border=lfs.TEXT_CTRL_BORDER
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.spin_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)

    def SetRange(self, range_tuple):
        self.spin_ctrl.SetRange(range_tuple)

    def GetValue(self):
        return self.spin_ctrl.GetValue()

    def SetValue(self, value):
        return self.spin_ctrl.SetValue(value)

class NamedTextCtrl(wx.Panel):
    def __init__(self, parent, name="", **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        self.name = wx.StaticText(self, label=name)
        self.text_ctrl = wx.TextCtrl(self, size=(50,-1))
        
        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALIGN_CENTER_VERTICAL|wx.ALL
        border=lfs.TEXT_CTRL_BORDER
        sizer.Add(self.name, proportion=0, 
                  flag=flag|wx.ALIGN_RIGHT, border=border)
        sizer.Add((10,5), proportion=0)
        sizer.Add(self.text_ctrl, proportion=1, 
                  flag=flag|wx.ALIGN_LEFT, border=border)

        self.SetSizer(sizer)

    def GetValue(self):
        return self.text_ctrl.GetValue()

    def SetValue(self, value):
        self.text_ctrl.SetValue(value)

class OptionalNamedTextCtrl(NamedTextCtrl):
    def __init__(self, parent, name, enabled=False, **kwargs):
        NamedTextCtrl.__init__(self, parent, name='', **kwargs)
        
        self.checkbox = wx.CheckBox(self, label=name)
        self.GetSizer().Insert(0, self.checkbox, proportion=0, flag=wx.ALL,
                                                 border=3)
        self.Bind(wx.EVT_CHECKBOX, self._enable, self.checkbox)
        self._enabled = enabled
        self._enable(state=enabled)

    def _enable(self, event=None, state=None):
        if event is not None:
            state = event.IsChecked()
        self._enabled = state
        self.name.Enable(state)
        self.checkbox.SetValue(state)
        self.text_ctrl.Enable(state)

    def GetValue(self):
        return self.text_ctrl.GetValue()

    def SetValue(self, value):
        self.text_ctrl.SetValue(value)

import wx

from spikepy.gui.utils import NamedTextCtrl, OptionalNamedTextCtrl


class ControlPanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)

        sd_units_checkbox = wx.CheckBox(self,
                label='Thresholds as multiple\nof standard deviation.')
        threshold_1_sd = NamedTextCtrl(self, name='Threshold (SDs):')
        threshold_1    = NamedTextCtrl(self, name='Threshold:')

        threshold_2_sd = OptionalNamedTextCtrl(self, 
                                               name='Second Threshold (SDs):')
        threshold_2    = OptionalNamedTextCtrl(self, 
                                                        name='Second Threshold:')
        refractory_time = NamedTextCtrl(self, name='Refractory period (ms):')
        max_spike_width = NamedTextCtrl(self, 
                                      name='Max spike width at threshold (ms):')

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALIGN_LEFT|wx.ALL|wx.EXPAND
        border = 3
        sizer.Add(sd_units_checkbox, proportion=0, flag=flag, border=border)
        sizer.Add(threshold_1_sd,    proportion=0, flag=flag, border=border)
        sizer.Add(threshold_1,       proportion=0, flag=flag, border=border)
        sizer.Add(threshold_2_sd,    proportion=0, flag=flag, border=border)
        sizer.Add(threshold_2,       proportion=0, flag=flag, border=border)
        sizer.Add(refractory_time,   proportion=0, flag=flag, border=border)
        sizer.Add(max_spike_width,   proportion=0, flag=flag, border=border)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CHECKBOX, self._units_check, sd_units_checkbox)

        self.sd_units_checkbox = sd_units_checkbox
        self.threshold_1_sd = threshold_1_sd
        self.threshold_1 = threshold_1
        self.threshold_2_sd = threshold_2_sd
        self.threshold_2 = threshold_2
        self.refractory_time = refractory_time
        self.max_spike_width = max_spike_width

        self._using_sd_units = False
        self._units_check(state=self._using_sd_units)

    def _units_check(self, event=None, state=None):
        if state is None:
            state = event.IsChecked()
        self._using_sd_units = state
        self.threshold_1_sd.Show(state)
        self.threshold_1.Show(not state)
        self.threshold_2_sd.Show(state)
        self.threshold_2.Show(not state)

        self.Layout()

    def get_parameters(self):
        parameters = {}
        if self._using_sd_units:
            thresholds = [self.threshold_1_sd]
            if self.threshold_2_sd._enabled:
                thresholds.append(self.threshold_2_sd)
        else:
            thresholds = [self.threshold_1]
            if self.threshold_2._enabled:
                thresholds.append(self.threshold_2)
        parameters['threshold_1'] = float(thresholds[0].GetValue())
        if len(thresholds) > 1:
            parameters['threshold_2'] = float(thresholds[1].GetValue())
        else:
            parameters['threshold_2'] = parameters['threshold_1']
        parameters['refractory_time'] = float(self.refractory_time.GetValue())
        parameters['max_spike_duration'] = float(
                                                self.max_spike_width.GetValue())
        parameters['using_sd_units'] = self._using_sd_units
        return parameters

        

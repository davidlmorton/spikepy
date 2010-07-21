import wx

from spikepy.gui.named_controls import NamedTextCtrl, OptionalNamedTextCtrl
from spikepy.gui.look_and_feel_settings import lfs


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
        border = lfs.CONTROL_PANEL_BORDER
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

        # --- SET DEFAULTS ---
        threshold_1_sd.SetValue('4.0')
        threshold_2_sd.SetValue('-4.0')
        threshold_2_sd._enable(state=False)
        threshold_1.SetValue('0.01')
        threshold_2.SetValue('-0.01')
        threshold_2._enable(state=False)
        refractory_time.SetValue('0.0')
        max_spike_width.SetValue('2.0')
        self._units_check(state=True)

    def _units_check(self, event=None, state=None):
        if state is None:
            state = event.IsChecked()
        self.sd_units_checkbox.SetValue(state)
        self._using_sd_units = state
        self.threshold_1_sd.Show(state)
        self.threshold_1.Show(not state)
        self.threshold_2_sd.Show(state)
        self.threshold_2.Show(not state)

        self.Layout()

    def set_parameters(self, threshold_1="4.0", threshold_2="-4.0", 
                       refractory_time="0.0", max_spike_duration="2.0", 
                       using_sd_units=True):
        threshold_1 = str(threshold_1)
        threshold_2 = str(threshold_2)
        refractory_time = str(refractory_time)
        max_spike_duration = str(max_spike_duration)
        enable_second_threshold = (threshold_1 != threshold_2)
        self.threshold_2_sd._enable(state=enable_second_threshold)
        self.threshold_2._enable(   state=enable_second_threshold)
            
        if using_sd_units:
            threshold_ctrl_1 = self.threshold_1_sd
            threshold_ctrl_2 = self.threshold_2_sd
        else:  
            threshold_ctrl_1 = self.threshold_1
            threshold_ctrl_2 = self.threshold_2
        threshold_ctrl_1.SetValue(threshold_1)
        threshold_ctrl_2.SetValue(threshold_2)

        self.refractory_time.SetValue(refractory_time)
        self.max_spike_width.SetValue(max_spike_duration)
        self._units_check(state=using_sd_units)
        

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

        

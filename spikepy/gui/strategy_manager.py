import json

import wx
from wx.lib.pubsub import Publisher as pub

from . import program_text as pt
from .utils import strip_unicode
from .look_and_feel_settings import lfs
from .named_controls import NamedTextCtrl 

STRATEGIES_ARCHIVE_FILE= 'strategies_archive.txt'

class StrategyManager(object):
    def __init__(self, strategy_pane):
        self.strategy_pane    = strategy_pane
        self.strategy_chooser = self.strategy_pane.strategy_chooser
        self.save_button = self.strategy_pane.save_button
        # dictionaries are named by their values.
        self.methods        = {}
        self.settings       = {}
        self.load_archived_strategies()

        self._should_sync = True
        self.strategy_pane.Bind(wx.EVT_IDLE, self._sync)
        self.strategy_pane.Bind(wx.EVT_CHOICE, self._strategy_choice_made, 
                                self.strategy_chooser.choice) 
        pub.subscribe(self.save_all_strategies, topic='SAVE_ALL_STRATEGIES')
        self.strategy_pane.Bind(wx.EVT_BUTTON, self.save_button_pressed, 
                                self.save_button)

    @property
    def strategy_names(self):
        return sorted(self.settings.keys())

    def load_archived_strategies(self, 
            strategy_archive_file=STRATEGIES_ARCHIVE_FILE):
        with open(strategy_archive_file) as infile:
            saved_strategies = json.load(infile)
            del saved_strategies['__comment']
        self._add_strategy(saved_strategies)

    def save_all_strategies(self, message=None):
        strategy_list = []
        for strategy_name in self.strategy_names:
            methods_set_name = get_methods_set_name(strategy_name)
            methods_dict  = self.methods[methods_set_name]
            settings_dict = self.settings[strategy_name]
            this_strategy_dict = make_strategy(strategy_name, 
                                               methods_dict, 
                                               settings_dict)
            strategy_list.append(this_strategy_dict)
        self.save_strategies(strategy_list)
        
    def save_strategies(self, strategy_list, filename=STRATEGIES_ARCHIVE_FILE):
        all_strategies_dict = {}
        for strategy in strategy_list:
            all_strategies_dict.update(strategy)

        comment = "DO NOT EDIT THIS DOCUMENT (BAD THINGS WILL HAPPEN)" 
        all_strategies_dict['__comment'] = comment
        with open(filename, 'w') as ofile:
            json.dump(all_strategies_dict, ofile, indent=4)
        
    def _strategy_choice_made(self, event=None):
        'Update The Strategy Pane based on the choice made.'
        strategy_name = self.strategy_chooser.GetStringSelection()
        methods_set_name = get_methods_set_name(strategy_name)
        methods_used = self.methods[methods_set_name]
        settings     = self.settings[strategy_name]
        for stage in self.strategy_pane.stages:
            stage_name = stage.stage_name.lower().replace(" ","_")
            method_name = methods_used[stage_name]        
            stage._method_choice_made(method_name=method_name)

            control_panel = stage.methods[method_name]['control_panel'] 
            stage_settings = settings[stage_name]
            non_unicode_stage_settings = strip_unicode(stage_settings)
            control_panel.set_parameters(**non_unicode_stage_settings)

    def _sync(self, event=None):
        if self._should_sync:
            self._should_sync = False
            wx.CallLater(lfs.STRATEGY_WAIT_TIME, self._toggle_should_sync)
            current_strategy      = self.get_current_strategy()
            current_strategy_name = current_strategy.keys()[0]

            if (not self.settings.has_key(current_strategy_name) or
                'custom' in current_strategy_name.lower()):
                self._add_strategy(current_strategy)
            strategy_chooser = self.strategy_chooser
            if current_strategy_name != strategy_chooser.GetStringSelection():
                strategy_chooser.SetStringSelection(current_strategy_name)

            button_state = 'custom' in current_strategy_name.lower()
            self.strategy_pane.save_button.Enable(button_state)

    def save_button_pressed(self, event=None):
        current_strategy = self.get_current_strategy() 
        current_strategy_name = current_strategy.keys()[0]
        dlg = SaveStrategyDialog(self.strategy_pane, current_strategy_name,
                                 self.strategy_names,
                                 title=pt.SAVE_STRATEGY_DIALOG_TITLE,
                                 style=wx.DEFAULT_DIALOG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            new_name = dlg.get_strategy_name()
            dlg.Destroy()
            if new_name in self.strategy_names:
                confirm_dlg = wx.MessageDialog(self.strategy_pane,
                        new_name + pt.ALREADY_EXISTS_LINE,
                        caption=pt.CONFIRM_OVERWRITE,
                        style=wx.YES_NO|wx.ICON_WARNING)
                if confirm_dlg.ShowModal() == wx.ID_NO:
                    confirm_dlg.Destroy()
                    self.save_strategy()
                    return
                confirm_dlg.Destroy()

            self._remove_strategy(current_strategy)
            renamed_strategy = self._get_renamed_strategy(current_strategy, 
                                                          new_name)
            self._add_strategy(renamed_strategy)

    def _get_renamed_strategy(self, strategy, new_name):
        new_strategy = {}
        old_name = strategy.keys()[0]
        methods_used = strategy[old_name]['methods_used']
        settings     = strategy[old_name]['settings']
        new_strategy[new_name] = {'methods_used':methods_used,
                                  'settings':settings}
        return new_strategy
        
    def _add_strategy(self, strategy):
        for strategy_name, value in strategy.items():
            method_name = get_methods_set_name(strategy_name)
            method_dict = value['methods_used']
            self.methods[method_name]       = method_dict

            settings_name = strategy_name
            settings_dict = value['settings'] 
            self.settings[settings_name]       = settings_dict
        self._update_strategy_choices()

    def _remove_strategy(self, strategy):
        strategy_name = strategy.keys()[0]
        method_name   = get_methods_set_name(strategy_name)
        settings_name = strategy_name
        method_dict    = strategy[strategy_name]['methods_used']
        settings_dict  = strategy[strategy_name]['settings']
        del self.methods[method_name]
        del self.settings[settings_name]

        self._update_strategy_choices()
        
    def _update_strategy_choices(self):
        old_items = self.strategy_chooser.GetItems()
        if old_items != self.strategy_names:
            self.strategy_chooser.SetItems(self.strategy_names)

    def _toggle_should_sync(self):
        self._should_sync = not self._should_sync 

    def get_strategy_name(self, methods_used, settings):
        for strategy_name, settings_dict in self.settings.items():
            if settings == settings_dict:
                # potential match
                name = strategy_name
                method_set_name = get_methods_set_name(name)
                if self.methods[method_set_name] == methods_used:
                    return name

        for method_set_name, methods_dict in self.methods.items():
            if methods_dict == methods_used:
                return method_set_name + '(custom)'

        return 'Custom(custom)'

    def get_current_strategy(self):
        methods_used = {}
        settings     = {}
        for stage in self.strategy_pane.stages:
            method_chosen = stage._method_name_chosen
            control_panel = stage.methods[method_chosen]['control_panel']
            hashable_settings = control_panel.get_parameters()

            stage_name = stage.stage_name.lower().replace(' ', '_')
            methods_used[stage_name] = method_chosen
            settings[stage_name]     = hashable_settings

        strategy_name = self.get_strategy_name(methods_used, settings)
        return make_strategy(strategy_name, methods_used, settings)


def make_strategy(strategy_name, methods_used_dict, settings_dict):
    return_dict = {}
    return_dict[strategy_name] = {'methods_used':methods_used_dict, 
                                      'settings':settings_dict}
    return return_dict
    
def get_methods_set_name(strategy_name):
    return strategy_name.split('(')[0]

def get_settings_name(strategy_name):
    return strategy_name.split('(')[1][:-1]

def get_strategy_name(methods_set_name, settings_name):
    pre  = methods_set_name
    post = settings_name
    if len(pre) >= 1:
        new_name = pre[0].upper() + pre[1:].lower() + '(%s)' % post.lower()
    else:
        new_name = "*Invalid*"
    return new_name

class SaveStrategyDialog(wx.Dialog):
    def __init__(self, parent, old_name, all_names, **kwargs):
        wx.Dialog.__init__(self, parent, **kwargs)

        self.all_names = all_names
        self.old_name  = old_name
        self.all_methods_set_names = list(set([str(get_methods_set_name(name))
                                               for name in all_names]))
        self.contraban_list = {'(':pt.PARENTHESES, 
                               ')':pt.PARENTHESES, 
                               '"':pt.QUOTES, 
                               "'":pt.APOSTROPHES, 
                               'custom':pt.CUSTOM,
                               ' ':pt.SPACES}
        self.save_as_text = wx.StaticText(self, 
                            label='Save as: ')
        save_as_font = self.save_as_text.GetFont()
        save_as_font.SetWeight(wx.FONTWEIGHT_BOLD)
        save_as_font.SetPointSize(16)
        self.save_as_text.SetFont(save_as_font)

        methods_set_name = get_methods_set_name(old_name)
        self.methods_set_textctrl = NamedTextCtrl(self, name=pt.METHOD_SET_NAME)
        self.methods_set_textctrl.SetTextctrlSize((200,-1))
        self.methods_set_textctrl.SetValue(methods_set_name)

        settings_name   = get_settings_name(old_name)
        self.settings_textctrl   = NamedTextCtrl(self, name=pt.SETTINGS_NAME)
        self.settings_textctrl.SetTextctrlSize((200,-1))
        self.settings_textctrl.SetValue(settings_name)

        self.warning_text = wx.StaticText(self, 
                            label='Choose a set of names for the strategy.')

        self.ok_button = wx.Button(self, id=wx.ID_OK)
        cancel_button  = wx.Button(self, id=wx.ID_CANCEL)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        flag = wx.ALL|wx.EXPAND
        border = 5
        button_sizer.Add(cancel_button,  proportion=0, flag=flag, border=border)
        button_sizer.Add(self.ok_button, proportion=0, flag=flag, border=border)

        sizer = wx.BoxSizer(orient=wx.VERTICAL)
        flag = wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND
        sizer.Add(self.save_as_text,        proportion=0, flag=flag, border=15)
        sizer.Add(self.methods_set_textctrl, proportion=0, flag=flag, border=5)
        sizer.Add(self.settings_textctrl,   proportion=0, flag=flag, border=5)
        sizer.Add(button_sizer,             proportion=0, flag=wx.ALIGN_RIGHT)
        sizer.Add(self.warning_text,        proportion=0, flag=flag, border=5)
        self.SetSizerAndFit(sizer)
        # add space for long warning text.
        size = self.GetSize()
        self.SetSize((size[0]+10, size[1]+100))

        if not old_name.lower().startswith('custom'):
            self.methods_set_textctrl.Enable(False)

        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.methods_set_textctrl.text_ctrl)
        self.Bind(wx.EVT_TEXT, self._check_inputs, 
                  self.settings_textctrl.text_ctrl)
        self._check_inputs()

    def get_strategy_name(self):
        methods_set_name = self.methods_set_textctrl.GetValue()
        settings_name   = self.settings_textctrl.GetValue()
        new_name = get_strategy_name(methods_set_name, settings_name)
        return new_name

    def _check_inputs(self, event=None):
        methods_set_name = self.methods_set_textctrl.GetValue()
        settings_name   = self.settings_textctrl.GetValue()
        new_name = get_strategy_name(methods_set_name, settings_name)
        self.save_as_text.SetLabel(pt.STRATEGY_SAVE_AS + 
                                   new_name)
        if len(methods_set_name) < 1 or len(settings_name) < 1:
            self.warning_text.SetLabel(pt.AT_LEAST_ONE_CHARACTER)
            self.ok_button.Enable(False)
            return
        for contraban, contraban_name in self.contraban_list.items():
            if (contraban in methods_set_name.lower() or 
                contraban in settings_name.lower()):
                self.warning_text.SetLabel(pt.NOT_CONTAIN + 
                                           ' %s.' % contraban_name)
                self.ok_button.Enable(False)
                return
        if ('custom' in get_methods_set_name(self.old_name).lower() and 
            get_methods_set_name(new_name) in self.all_methods_set_names):
            count = 0
            first_name = self.all_methods_set_names[0]
            old_methods_set_names = first_name
            for name in self.all_methods_set_names[1:]:
                old_methods_set_names += ", %s" % name
                count += 1
                if not count % 5:
                    old_methods_set_names += '\n'
            self.warning_text.SetLabel(pt.NOT_ONE_OF + old_methods_set_names)
            self.ok_button.Enable(False)
            return
        self.warning_text.SetLabel(pt.OK_TO_SAVE)
        self.ok_button.Enable(True)

        

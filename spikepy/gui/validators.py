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

import string

import wx

from spikepy.common import program_text as pt

class FloatValidator(wx.PyValidator):
    valid_characters = ".-%s%s" % (string.digits, chr(8))
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self._on_char)

    def Clone(self):
        return FloatValidator()

    def Validate(self, data=None):
        win = self.GetWindow()
        val = win.GetValue()

        try:
            float(val)
            win.SetBackgroundColour('white')
            return True
        except ValueError:
            win.SetBackgroundColour('pink')
            return False

    def _on_char(self, event):
        key = event.GetKeyCode()
        if key < 256:
            chr_key = chr(key)
            if chr(key) not in FloatValidator.valid_characters:
                return
            if chr(key) in string.ascii_letters:
                return
        event.Skip()
        wx.CallLater(10, self.Validate)

class CharacterSubsetValidator(wx.PyValidator):
    def __init__(self, valid_characters, **kwargs):
        # add backspace and enter keys to valid characters
        valid_characters += chr(8) + chr(13)
        self._valid_characters = valid_characters

        wx.PyValidator.__init__(self, **kwargs)
        self.Bind(wx.EVT_CHAR, self._on_char)

    def Clone(self):
        return CharacterSubsetValidator(self._valid_characters)

    def Validate(self, dlg=None):
        return True

    def _on_char(self, event):
        key = event.GetKeyCode()
        if key < 256 and chr(key) not in self._valid_characters:
            return # eat the event.
        event.Skip()

class NameValidator(CharacterSubsetValidator):
    def __init__(self, valid_characters, invalid_names=[], **kwargs):
        CharacterSubsetValidator.__init__(self, valid_characters, **kwargs)
        self._invalid_names = invalid_names

    def Clone(self):
        return self.__class__(self._valid_characters, 
                invalid_names=self._invalid_names)

    def Validate(self, dlg=None, can_exit=True):
        win = self.GetWindow()
        new_name = win.GetValue()

        # ensure current name is not one of the other names.
        has_error = False
        if new_name in self._invalid_names:
            if dlg is not None and hasattr(dlg, 'warning_text'):
                dlg.warning_text.SetLabel(pt.NAME_ALREADY_EXISTS % new_name)
            has_error = True
        if new_name.startswith('.'):
            if dlg is not None and hasattr(dlg, 'warning_text'):
                dlg.warning_text.SetLabel(pt.NAME_CANNOT_BEGIN_WITH)
            has_error = True
        if len(new_name) == 0:
            has_error = True
        if has_error:
            win.SetBackgroundColour('pink')
            return False
        else:
            if can_exit:
                if dlg is not None:
                    dlg.EndModal(wx.ID_OK)
                return True
            else:
                if dlg is not None:
                    dlg.warning_text.SetLabel('')
                win.SetBackgroundColour('white')
                return True

    def _reset_background_color(self):
        win = self.GetWindow()
        win.SetBackgroundColour('white')
        



"""
copyright (c) 2011  david morton

this program is free software: you can redistribute it and/or modify
it under the terms of the gnu general public license as published by
the free software foundation, either version 3 of the license, or
(at your option) any later version.

this program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.  see the
gnu general public license for more details.

you should have received a copy of the gnu general public license
along with this program.  if not, see <http://www.gnu.org/licenses/>.
"""
import wx

from spikepy.gui.valid_controls import ValidFloatControl 

# setup app and main_frame
app = wx.PySimpleApp()
main_frame = wx.Frame(None, title='Valid Controls DEMO',
                                 size=(400, 300))
sizer = wx.BoxSizer(orient=wx.VERTICAL)

def print_entry(entry):
    print entry

control = ValidFloatControl(main_frame, name='Example', min_value=0.0, 
        max_value=1.0, valid_entry_callback=print_entry)
control.SetValue('0.5')

sizer.Add(control)

# set sizer and run app
main_frame.SetSizer(sizer)
main_frame.Show()
app.MainLoop()

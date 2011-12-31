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

app = wx.PySimpleApp()
main_frame = wx.Frame(None, title='Choice Demo',
                                 size=(400, 300))

sizer = wx.BoxSizer(orient=wx.VERTICAL)


choice = wx.Choice(main_frame, choices=['blah', 'blerg', 'bleh'])
text = wx.TextCtrl(main_frame, size=(150, -1))
button = wx.Button(main_frame, label='Set')
value_button = wx.Button(main_frame, label='Set Value')

def print_choice(event):
    event.Skip()
    entry = choice.GetStringSelection()
    print '%s selected' % entry

def set_fn(event):
    event.Skip()
    t = text.GetValue()
    choice.SetStringSelection(t)
    print 'Setting choice to %s' % t

def set_value(event):
    event.Skip()
    t = text.GetValue()
    choice.SetValue(t)
    print 'Setting value to %s' % t

main_frame.Bind(wx.EVT_BUTTON, set_fn, button)
main_frame.Bind(wx.EVT_BUTTON, set_value, value_button)
main_frame.Bind(wx.EVT_CHOICE, print_choice, choice)

sizer.Add(text)
sizer.Add(button)
sizer.Add(value_button)
sizer.Add(choice)

# set sizer and run app
main_frame.SetSizer(sizer)
main_frame.Show()
app.MainLoop()

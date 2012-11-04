#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

from spikepy.gui.valid_controls import *
from spikepy.common.valid_types import *
from spikepy.gui.strategy_pane import ControlPanel


# setup app and main_frame
app = wx.PySimpleApp()
main_frame = wx.Frame(None, title='Valid Controls DEMO',
                                 size=(400, 300))
sizer = wx.BoxSizer(orient=wx.VERTICAL)

def print_entry(entry):
    print entry

control1 = make_control(main_frame, name='Float Between -10 and 2.4',
        valid_type=ValidFloat(min=-10, max=2.4, default=-3.14159))
control1.register_valid_entry_callback(print_entry)

control2 = ValidNumberControl(main_frame, name='Integer Greater than 3', 
        valid_type=ValidInteger(min=3, default=12), 
        valid_entry_callback=print_entry)

control3 = ValidBooleanControl(main_frame, name='Boolean', 
        valid_type=ValidFloat(default=True), 
        valid_entry_callback=print_entry)

control4 = ValidChoiceControl(main_frame, name='Choice', 
        valid_type=ValidOption('bleh', 'blah', 'blew', default='blah'), 
        valid_entry_callback=print_entry)

sizer.Add(control1)
sizer.Add(control2)
sizer.Add(control3)
sizer.Add(control4)

# set sizer and run app
main_frame.SetSizer(sizer)
main_frame.Show()
app.MainLoop()

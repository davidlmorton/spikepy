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
#! /usr/bin/python


import wx

from spikepy.common import path_utils

print "\nSpikepy configuration directories on platform: %s (%s)" % (wx.Platform, 
                                                        path_utils.platform())

data_dirs = path_utils.get_data_dirs(app_name='spikepy')

for level in data_dirs.keys():
    print "\n\t--%s--" % (level[0].upper() + level[1:].lower())
    for key, value in data_dirs[level].items():
        print "\t\t%s: %s" % (key, value)
    

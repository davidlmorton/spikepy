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
from types import MethodType

def disabled_set_ylim(axes, *args, **kwargs):
    pass

def make_into_raster_axes(axes):
    # monkey-patch the axes.set_ylim function
    if not hasattr(axes, '_old_set_ylim'):
        axes._old_set_ylim = axes.set_ylim
        axes.set_ylim = MethodType(disabled_set_ylim, axes, axes.__class__)

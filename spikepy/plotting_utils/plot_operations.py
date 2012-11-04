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

import time

def plot_operations(plot_dict, t,  axes):
    plot_links(plot_dict['link_list'], axes)
    plot_nodes(plot_dict['node_info'], axes)
    plot_labels(plot_dict['label_list'], axes)
    plot_time(t, axes)
    axes.set_frame_on(False)
    axes.set_xticks([])
    axes.set_yticks([])

def plot_time(t, axes):
    time_string = time.strftime('%H:%M:%S', time.gmtime(t))+\
            ('%s' % (t%1))[1:5]
    axes.text(0.03, 0.97, time_string, horizontalalignment='left', 
            verticalalignment='top', transform=axes.transAxes)

def plot_links(link_list, axes):
    for xs, ys, kwargs in link_list:
        axes.plot(xs, ys, **kwargs)


def plot_nodes(node_info, axes):
    xs = node_info['xs']
    ys = node_info['ys']
    kwargs = node_info['kwargs']
    axes.scatter(xs, ys, **kwargs)


def plot_labels(label_list, axes):
    for x, y, s, kwargs in label_list:
        axes.text(x, y, s, **kwargs)


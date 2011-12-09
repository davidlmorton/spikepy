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
import time
from types import MethodType

import numpy

from spikepy.plotting_utils.make_into_signal_axes import make_into_signal_axes 
from spikepy.plotting_utils.general import is_iterable, as_fraction_axes

unit_prefix_index = {-5:'f', -4:'p', -3:'n', -2:r'$\mu$', -1:'m', 0:'', 
                     1:'k', 2:'M', 3:'G',  4:'T', 5:'P'}

def make_into_publication_axes(axes, 
        axis='both',
        base_unit=('s', 'V'), 
        base_unit_prefix=('m', 'm'),
        plot_to_base_factor=(1.0, 1.0), 
        target_size_frac=(0.2, 0.2), 
        scale_bar_origin_frac=(0.7, 0.7), 
        live_update=True,
        chunks=[1, 2, 5, 10, 20, 25, 30, 50, 100, 200, 500],
        y_label_rotation='horizontal',
        color='black'):
    '''
        Makes the axes look like trace plots in publications.  That is, the
    frame is not drawn, and a scale bar for x and y is displayed instead.
    Inputs:
        axes: The axes you wish to format this way.
        axis: 'x', 'y', or 'both'
        base_unit: The base SI unit, for example: 'V', 'Hz', 'F', 'C'...
        base_unit_prefix: The prefix needed to get to the plotted units.
        plot_to_base_factor: The factor which converts plotted units to base
                             units. (i.e. pixels_to_um for an image)
        target_size_frac: The desired size of the scale bar, this may be off by
                          a bit, depending on the choice of <chunks>. (kwarg)
        scale_bar_origin_frac   : The position of the origin of the scale
                                  bar in fractional axes units.
        live_update: If True, the scale bars will update when ylim changes.
        chunks           : Passed on to get_scale_bar_info.
        y_label_rotation: the angle of the y label. Anything that a matplotlib
                Text object accepts as a rotation= kwarg.
        color: The color of the lines and labels.
    Returns:
        None       : It just alters the axes.
    '''
    if live_update:
        if not hasattr(axes, '_is_signal_axes'):
            make_into_signal_axes(axes)
        axes._live_updating_scalebars = True

    axes.set_frame_on(False)
    axes.set_xticks([])
    axes.set_yticks([])

    # parse inputs
    if is_iterable(base_unit):
        base_unit_x, base_unit_y = base_unit
    else:
        base_unit_x, base_unit_y = (base_unit, base_unit)

    if is_iterable(base_unit_prefix):
        base_unit_prefix_x, base_unit_prefix_y = base_unit_prefix
    else:
        base_unit_prefix_x, base_unit_prefix_y = (base_unit_prefix,
                base_unit_prefix)

    if is_iterable(plot_to_base_factor):
        plot_to_base_factor_x, plot_to_base_factor_y = plot_to_base_factor
    else:
        plot_to_base_factor_x, plot_to_base_factor_y = (plot_to_base_factor, 
                plot_to_base_factor)

    if is_iterable(target_size_frac):
        target_size_frac_x, target_size_frac_y = target_size_frac
    else:
        target_size_frac_x, target_size_frac_y = (target_size_frac, 
                target_size_frac)

    def create_x_scale_bar(axes):
        # clear old
        if hasattr(axes, '_x_scale_bar'):
            for line in axes._x_scale_bar:
                line.remove()
            del axes._x_scale_bar
        if hasattr(axes, '_x_scale_text'):
            axes._x_scale_text.remove()
            del axes._x_scale_text 

        x_min = numpy.min(axes.get_xlim())
        x_max = numpy.max(axes.get_xlim())
        x_range = x_max - x_min

        y_min = numpy.min(axes.get_ylim())
        y_max = numpy.max(axes.get_ylim())
        y_range = y_max - y_min

        scale_bar_info = get_scale_bar_info(target_size_frac_x, 
                x_range*plot_to_base_factor_x, 
                base_unit_prefix=base_unit_prefix_x, 
                chunks=chunks)

        bar_min = x_min + scale_bar_origin_frac[0]*x_range
        bar_max = bar_min + scale_bar_info['scale_base']/plot_to_base_factor_x
        bar_y = scale_bar_origin_frac[1]*y_range + y_min

        axes._x_scale_bar = axes.plot((bar_min, bar_max), 
                (bar_y, bar_y), linewidth=2, color=color, clip_on=False)

        bar_range = bar_max-bar_min
        bar_mid = (bar_min + bar_range/2.0)

        text = '%s %s%s' % (scale_bar_info['best_chunk'], 
                scale_bar_info['scale_unit_prefix'], 
                base_unit_x)
        f = axes.figure
        canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                f.get_figheight()*f.get_dpi())
        y_pix = as_fraction_axes(y=8, axes=axes, 
                canvas_size_in_pixels=canvas_size_in_pixels)*y_range
        axes._x_scale_text = axes.text(bar_mid, bar_y-y_pix, text,
                horizontalalignment='center', verticalalignment='top',
                color=color)

    def create_y_scale_bar(axes):
        # clear old
        if hasattr(axes, '_y_scale_bar'):
            for line in axes._y_scale_bar:
                line.remove()
            del axes._y_scale_bar
        if hasattr(axes, '_y_scale_text'):
            axes._y_scale_text.remove()
            del axes._y_scale_text 

        x_min = numpy.min(axes.get_xlim())
        x_max = numpy.max(axes.get_xlim())
        x_range = x_max - x_min

        y_min = numpy.min(axes.get_ylim())
        y_max = numpy.max(axes.get_ylim())
        y_range = y_max - y_min

        scale_bar_info = get_scale_bar_info(target_size_frac_y, 
                y_range*plot_to_base_factor_y, 
                base_unit_prefix=base_unit_prefix_y, 
                chunks=chunks)

        bar_min = scale_bar_origin_frac[1]*y_range + y_min
        bar_max = bar_min + scale_bar_info['scale_base']/plot_to_base_factor_y
        bar_x = scale_bar_origin_frac[0]*x_range + x_min

        axes._y_scale_bar = axes.plot((bar_x, bar_x), 
                (bar_min, bar_max), linewidth=2, color=color, clip_on=False)

        bar_range = bar_max-bar_min
        bar_mid = (bar_min + bar_range/2.0)

        text = '%s %s%s' % (scale_bar_info['best_chunk'], 
                scale_bar_info['scale_unit_prefix'], 
                base_unit_y)
        f = axes.figure
        canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                f.get_figheight()*f.get_dpi())
        x_pix = as_fraction_axes(x=8, axes=axes, 
                canvas_size_in_pixels=canvas_size_in_pixels)*x_range
        axes._y_scale_text = axes.text(bar_x-x_pix, bar_mid, text,
                horizontalalignment='right', verticalalignment='center',
                rotation=y_label_rotation,
                color=color)

    if axis in ['both', 'x']:
        axes._create_x_scale_bar = create_x_scale_bar 
    else:
        axes._create_x_scale_bar = lambda axes:None

    if axis in ['both', 'y']:
        axes._create_y_scale_bar = create_y_scale_bar
    else:
        axes._create_y_scale_bar = lambda axes:None

def update_scalebars(axes):
    axes._create_x_scale_bar(axes)
    axes._create_y_scale_bar(axes)

def get_scale_bar_info(target_frac, range_base, base_unit_prefix='', 
        chunks=[1, 2, 5, 10, 20, 25, 30, 50, 100, 200, 500]):
    '''
    Determines the size of the appropriate scale bar for an axis.
    Inputs:
        target_frac      : The target fraction of the axis the bar will be.
        range_base       : The length of the axis in base units.
        base_unit_prefix : The prefix of the base units, i.e. 'm' = milli,
                            and 'p' = pico, or -1 = milli, and -4 = pico.
        chunks           : Nice round numbers that are suitable for the length
                            of the scale bar.
    Returns:
        return_dict has keys:values
            scale_base   : The size of the scale bar in base (plotted) units.
            scale_frac   : The size of the scale bar as a fraction of 
                            <range_base>.
            best_chunk   : The chunk that should be used to label the scale.
            scale_unit_prefix : The scale unit prefix 'm', 'p', ect. to label
                                 the scale.

    '''
    base_unit_prefix_num = 0
    if isinstance(base_unit_prefix, type('str')):
        for unit_index, unit_prefix in unit_prefix_index.items():
            if unit_prefix == base_unit_prefix:
                base_unit_prefix_num = unit_index
    else:
        base_unit_prefix_num = int(base_unit_prefix)

    chunks = numpy.array(chunks)

    # range_frac = 1.0
    target_base = target_frac * range_base

    # snap that to the closest chunk.
    i = 0
    while target_base >= 1000.0:
        target_base /= 1000.0
        i += 1
    while target_base < 0.999:
        target_base *= 1000
        i -= 1
    # target_base is now between 0.999 and 1000.0

    diffs = numpy.abs(chunks-target_base)
    best_chunk_index = numpy.argmin(diffs)
    best_chunk = chunks[best_chunk_index]

    base = best_chunk*1000**i

    return_dict = {'scale_base':base,
                   'scale_frac':base/range_base,
                   'best_chunk':best_chunk,
                   'scale_unit_prefix':
                            unit_prefix_index[i+base_unit_prefix_num]}
    return return_dict


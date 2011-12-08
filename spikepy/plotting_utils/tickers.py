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
from matplotlib.ticker import MaxNLocator
from matplotlib import ticker
from matplotlib.dates import num2date

def set_tick_fontsize(axes, fontsize=12):
    for ticklabel in axes.get_yticklabels():
        ticklabel.set_size(fontsize)
    for ticklabel in axes.get_xticklabels():
        ticklabel.set_size(fontsize)

def format_axes_ticker(axes, axis='both', nbins=7, steps=[1,2,5,10], 
                       prune='lower', **kwargs):
    '''
    Sets the number of labeled ticks on the specified axis of the axes.
    Inputs:
        axes        : a matplotlib Axes2D object
        axis        : a string with either 'xaxis', 'yaxis', or 'both'
        nbins       : the number of tickmarks you want on the specified axis.
        steps       : something the MaxNLocator needs to make good choices.
        prune       : leave off a tick, one of 'lower', 'upper', 'both' or None
        **kwargs    : passed on to MaxNLocator
    Returns: None
    '''
    if axis == 'xaxis' or axis == 'both':
        axes.xaxis.set_major_locator(MaxNLocator(nbins=nbins, 
                                                 steps=steps, 
                                                 prune=prune,
                                                 **kwargs))
    if axis == 'yaxis' or axis == 'both':
        axes.yaxis.set_major_locator(MaxNLocator(nbins=nbins,
                                                 steps=steps,
                                                 prune=prune,
                                                 **kwargs))

def format_axis_ticker_for_times(axis, fmt='%I:%M:%S %p'):
    # The format for the x axis is set to the chosen string, 
    #  as defined from a numerical date:
    axis.set_major_formatter(ticker.FuncFormatter(
            lambda numdate, _: num2date(numdate).strftime(fmt)))
    # The formatting proper is done:
    axis.get_axes().get_figure().autofmt_xdate()

def format_axis_ticker_for_dates(axis, fmt='%b %d'):
    # The format for the x axis is set to the chosen string, 
    #  as defined from a numerical date:
    axis.set_major_formatter(ticker.FuncFormatter(
            lambda numdate, _: num2date(numdate).strftime(fmt)))
    # The formatting proper is done:
    axis.get_axes().get_figure().autofmt_xdate()

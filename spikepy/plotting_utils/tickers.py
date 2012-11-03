
from spikepy.plotting_utils.import_matplotlib import *

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

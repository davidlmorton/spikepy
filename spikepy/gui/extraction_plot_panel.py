import os

from wx.lib.pubsub import Publisher as pub
import wx
import numpy
from scipy import signal as scisig

from .multi_plot_panel import MultiPlotPanel
from .plot_panel import PlotPanel
from .utils import rgb_to_matplotlib_color
from .look_and_feel_settings import lfs
from . import program_text as pt

class ExtractionPlotPanel(MultiPlotPanel):
    def __init__(self, parent, name):
        self._dpi       = lfs.PLOT_DPI
        self._figsize   = lfs.PLOT_FIGSIZE
        self._facecolor = lfs.PLOT_FACECOLOR
        self.name       = name
        MultiPlotPanel.__init__(self, parent, figsize=self._figsize,
                                              facecolor=self._facecolor,
                                              edgecolor=self._facecolor,
                                              dpi=self._dpi)
        pub.subscribe(self._remove_trial,  topic="REMOVE_PLOT")
        pub.subscribe(self._trial_added,   topic='TRIAL_ADDED')
        pub.subscribe(self._trial_altered, topic='TRIAL_EXTRACTIONED')

        self._trials       = {}
        self._feature_axes = {}

    def _remove_trial(self, message=None):
        full_path = message.data
        del self._trials[full_path]
        del self._feature_axes[full_path]

    def _trial_added(self, message=None, trial=None):
        if message is not None:
            trial = message.data

        fullpath = trial.fullpath
        self._trials[fullpath] = trial
        self.add_plot(fullpath, figsize=self._figsize, 
                                facecolor=self._facecolor,
                                edgecolor=self._facecolor,
                                dpi=self._dpi)

    def _trial_altered(self, message=None):
        trial = message.data
        fullpath = trial.fullpath
        if fullpath == self._currently_shown:
            self.plot(fullpath)
            if fullpath in self._replot_panels:
                self._replot_panels.remove(fullpath)
        else:
            self._replot_panels.add(fullpath)

    def plot(self, fullpath):
        trial = self._trials[fullpath]
        figure = self._plot_panels[fullpath].figure
        
        if (fullpath not in self._feature_axes.keys()):
            self._create_axes(trial, figure, fullpath)
        self._plot_features(trial, figure, fullpath)

        self.draw_canvas(fullpath)

    def _create_axes(self, trial, figure, fullpath):
        axes = self._feature_axes[fullpath] = figure.add_subplot(1,1,1)
        axes.set_ylabel(pt.FEATURE_AMPLITUDE)
        axes.set_xlabel(pt.FEATURE_INDEX)

    def _plot_features(self, trial, figure, fullpath):
        if trial.extraction.results is not None:
            features = trial.extraction.results['features']
        else:
            return
        num_excluded_features = len(
                trial.extraction.results['excluded_features'])

        axes = self._feature_axes[fullpath]
        while axes.lines:
            del(axes.lines[0])     

        axes.set_autoscale_on(True)
        for feature in features:
            axes.plot(feature, linewidth=lfs.PLOT_LINEWIDTH_4,
                               marker='.')
        axes.set_xlim((0,len(features[0])-1))
        axes.set_title(pt.EXTRACTED_FEATURE_SETS + ': %d\n' % len(features) +
                       pt.EXCLUDED_FEATURE_SETS + 
                       ': %d' % num_excluded_features)

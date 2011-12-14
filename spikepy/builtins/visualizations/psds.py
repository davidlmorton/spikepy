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
import numpy

from spikepy.developer_tools.visualization import Visualization
from spikepy.plotting_utils.general import create_times_array, as_fraction 
from spikepy.plotting_utils.make_into_publication_axes import \
        make_into_publication_axes, update_scalebars 
from spikepy.common.valid_types import ValidFloat, ValidBoolean, ValidOption,\
        ValidInteger

background = {True:'black', False:'white'}
foreground = {True:'white', False:'black'}
line_color = {True:'cyan', False:'blue'}

class DetectionPSDVisualization(Visualization):
    name = 'Power Spectral Density (detection_filter)'
    requires = ['pf_psd', 'pf_freqs']
    found_under_tab = 'detection_filter'

    invert_colors = ValidBoolean(default=False)
    logscale = ValidBoolean(default=True)

    def _get_auxiliary_results(self, trial):
        return trial.df_psd.data, trial.df_freqs.data
    
    def _plot(self, trial, figure, logscale=True, invert_colors=False):
        pf_psd = trial.pf_psd.data
        pf_freqs = trial.pf_freqs.data

        f_psd, f_freqs = self._get_auxiliary_results(trial)
        have_filtered_results = (f_psd is not None)
    
        def as_frac(x=None, y=None):
            f = figure
            canvas_size_in_pixels = (f.get_figwidth()*f.get_dpi(),
                                    f.get_figheight()*f.get_dpi())
            return as_fraction(x=x, y=y, 
                    canvas_size_in_pixels=canvas_size_in_pixels)

        figure.set_facecolor(background[invert_colors])
        figure.set_edgecolor(foreground[invert_colors])
        figure.subplots_adjust(left=as_frac(x=80), 
                right=1.0-as_frac(x=35), 
                bottom=as_frac(y=40), 
                top=1.0-as_frac(y=25))

        axes = figure.add_subplot(111)

        axes.plot(pf_freqs, pf_psd, color=foreground[invert_colors],
            alpha=0.50, label='Pre-Filtered')

        if have_filtered_results:
            axes.plot(f_freqs, f_psd, color=line_color[invert_colors],
                    label='Filtered')

        legend = axes.legend(loc='upper right')
        frame = legend.get_frame()
        frame.set_facecolor(background[invert_colors])
        frame.set_edgecolor(foreground[invert_colors])
        for text in legend.texts:
            text.set_color(foreground[invert_colors])

        axes.set_ylabel('PSD (power/Hz)', color=foreground[invert_colors])
        axes.set_xlabel('Frequency (Hz)', color=foreground[invert_colors])

        if logscale:
            axes.set_yscale('log')

        # axes color fixing
        frame = axes.patch
        frame.set_facecolor(background[invert_colors])
        frame.set_edgecolor(foreground[invert_colors])
        for spine in axes.spines.values():
            spine.set_color(foreground[invert_colors])
        lines = axes.get_xticklines()
        lines.extend(axes.get_yticklines())
        for line in lines:
            line.set_color(foreground[invert_colors])
        labels = axes.get_xticklabels()
        labels.extend(axes.get_yticklabels())
        for label in labels:
            label.set_color(foreground[invert_colors])

class ExtractionPSDVisualization(DetectionPSDVisualization):
    name = 'Power Spectral Density (extraction_filter)'
    requires = ['pf_psd', 'pf_freqs']
    found_under_tab = 'extraction_filter'

    invert_colors = ValidBoolean(default=False)
    logscale = ValidBoolean(default=True)

    def _get_auxiliary_results(self, trial):
        return trial.ef_psd.data, trial.ef_freqs.data


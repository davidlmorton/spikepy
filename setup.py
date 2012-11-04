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
from distutils.core import setup

from spikepy import __version__ as VERSION

setup(name='Spikepy',
      version=VERSION,
      description='A python-based spike-sorting framework',
      author='David Morton',
      author_email='davidlmorton@gmail.com',
      url='http://code.google.com/p/spikepy/',
      packages = ['spikepy', 
                  'spikepy/test',
                  'spikepy/builtins',
                  'spikepy/builtins/strategies',
                  'spikepy/builtins/file_interpreters', 
                  'spikepy/builtins/data_interpreters', 
                  'spikepy/builtins/visualizations', 
                  'spikepy/builtins/methods', 
                  'spikepy/builtins/methods/auxiliary_psd', 
                  'spikepy/builtins/methods/auxiliary_resample', 
                  'spikepy/builtins/methods/auxiliary_spike_window', 
                  'spikepy/builtins/methods/clustering_k_means', 
                  'spikepy/builtins/methods/detection_threshold', 
                  'spikepy/builtins/methods/extraction_spike_window', 
                  'spikepy/builtins/methods/filtering_copy_detection', 
                  'spikepy/builtins/methods/filtering_fir', 
                  'spikepy/builtins/methods/filtering_iir', 
                  'spikepy/builtins/methods/filtering_wavelets', 
                  'spikepy/builtins/methods/filtering_none', 
                  'spikepy/common', 
                  'spikepy/developer', 
                  'spikepy/plotting_utils',
                  'spikepy/other',
                  'spikepy/other/callbacks',
                  'spikepy/utils',
                  'spikepy/utils/clustering_metrics/',
                  'spikepy/gui',
                  'spikepy/gui/images'],
    package_data = {'spikepy/builtins': ['spikepy.configspec',
                                        'spikepy.ini'],
                    'spikepy/gui/images': ['spikepy_splash.png',
                                           'down_arrow.png',
                                           'left_bar.png',
                                           'results_icon.png',
                                           'underline.png']},
    scripts=['spikepy/scripts/spikepy_gui.py', 
             'spikepy/scripts/spikepy_plugin_info.py'],
    license='GPL',
    platforms = ['windows', 'mac', 'linux']
    )


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

from setuptools import setup, find_packages

from spikepy import __version__ as VERSION

from sys import version_info

setup_requires = [
    'callbacks',
    'nose',
    'matplotlib',
    'numpy',
    'scipy',
    'wx',
    'configobj']

if version_info.major == 2 and version_info.minor < 7:
    setup_requires.append('argparse')

setup(name='Spikepy',
    version=VERSION,
    description='A python-based spike-sorting framework',
    author='David Morton',
    author_email='davidlmorton@gmail.com',
    url='http://code.google.com/p/spikepy/',
    install_requires = [
        ],
    setup_requires = setup_requires,
    tests_require = [
        'nose',
        'coverage',
        ],
    test_suite = 'tests',
    packages = find_packages(exclude=[
      'tests',
      'debian',
      'examples',
    ]),
    package_data = {
        'spikepy/builtins': [
            'spikepy.configspec',
            'spikepy.ini',
        ],
        'spikepy/gui/images': [
            'spikepy_splash.png',
            'down_arrow.png',
            'left_bar.png',
            'results_icon.png',
            'underline.png',
        ],
    },
    include_package_data=True,
    scripts=[
        'spikepy/scripts/spikepy_gui.py', 
        'spikepy/scripts/spikepy_plugin_info.py',
    ],
    license='GPL',
    platforms = ['windows', 'mac', 'linux']
)


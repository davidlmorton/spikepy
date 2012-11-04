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
import sys
import os
import shutil
from setuptools.command.easy_install import easy_install

class easy_install_default(easy_install):
  """ class easy_install had problems with the fist parameter not being
      an instance of Distribution, even though it was. This is due to
      some import-related mess.
      """

  def __init__(self):
    from distutils.dist import Distribution
    dist = Distribution()
    self.distribution = dist
    self.initialize_options()
    self._dry_run = None
    self.verbose = dist.verbose
    self.force = None
    self.help = 0
    self.finalized = 0

e = easy_install_default()
import distutils.errors
try:
  e.finalize_options()
except distutils.errors.DistutilsError:
  pass

# determine install path
install_path = e.install_dir

if os.path.exists(os.path.join(install_path, 'spikepy')):
    shutil.rmtree(os.path.join(install_path, 'spikepy'))
    

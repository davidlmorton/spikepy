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

from utils.wrap import wrap

__version__ = "0.82"

docstring = '''
Spikepy version %s

Spikepy is an offline spike-sorting package.  For more information please consult the wiki at http://code.google.com/p/spikepy/wiki/introduction

*GUI*: To invoke the graphical user interface use the script "spikepy_gui.py".
*API*: The API for spikepy is described in more detail in the wiki but a typical workflow is as follows:

    from spikepy import session
    s = session.Session()
    s.open_file(<filename>)
    s.current_strategy = <strategy_name>
    s.run()
    s.visualize(<trial name>, <visualization name>)
    s.export(<data-interpreter name>, <out filename>)
    s.save(<session filename>)''' % __version__

__doc__ = wrap(docstring, 76)

del docstring
del wrap

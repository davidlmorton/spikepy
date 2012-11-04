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

import matplotlib
# breaks pep-8 to put code here, but matplotlib 
#     requires this before importing wxagg backend
matplotlib.use('WXAgg', warn=False) 
from matplotlib.backends.backend_wxagg import \
        FigureCanvasWxAgg as Canvas, \
        NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

from matplotlib.ticker import MaxNLocator
from matplotlib import ticker
from matplotlib.dates import num2date 

__all__ = ['matplotlib', 'Canvas', 'Toolbar', 'Figure', 'MaxNLocator', 
        'ticker', 'num2date']


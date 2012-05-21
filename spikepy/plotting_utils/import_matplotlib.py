
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


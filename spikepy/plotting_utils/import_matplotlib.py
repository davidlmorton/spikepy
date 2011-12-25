
import matplotlib
matplotlib.use('WXAgg') # breaks pep-8 to put code here, but matplotlib 
                        #     requires this before importing wxagg backend
from matplotlib.backends.backend_wxagg import \
        FigureCanvasWxAgg as Canvas, \
        NavigationToolbar2WxAgg as Toolbar
from matplotlib.figure import Figure

from matplotlib.ticker import MaxNLocator
from matplotlib import ticker
from matplotlib.dates import num2date 

__all__ = ['matplotlib', 'Canvas', 'Toolbar', 'Figure', 'MaxNLocator', 
        'ticker', 'num2date']

def make_version_float(version_number_string):
    """
        Makes version numbers for matplotlib a float
    so they can be easily compared.
    """
    nums = version_number_string.split('.')
    result = 0.0
    for i, num in enumerate(nums):
        result += float(num)*10**(-3*i)
    return result

def matplotlib_version_too_low(min_version):
    version = matplotlib.__version__
    return (make_version_float(version) < make_version_float(min_version))

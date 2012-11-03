
from types import MethodType

def disabled_set_ylim(axes, *args, **kwargs):
    pass

def make_into_raster_axes(axes):
    # monkey-patch the axes.set_ylim function
    if not hasattr(axes, '_old_set_ylim'):
        axes._old_set_ylim = axes.set_ylim
        axes.set_ylim = MethodType(disabled_set_ylim, axes, axes.__class__)

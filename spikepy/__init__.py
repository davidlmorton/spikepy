
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

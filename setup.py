from distutils.core import setup

from spikepy import __version__ as VERSION

setup(name='Spikepy',
      version=VERSION,
      description='A python-based spike-sorting framework',
      author='David Morton',
      author_email='davidlmorton@gmail.com',
      url='http://code.google.com/p/spikepy/',
      packages = ['spikepy', 
                  'spikepy/tests',
                  'spikepy/builtins',
                  'spikepy/builtins/file_interpreters', 
                  'spikepy/builtins/file_interpreters/tests', 
                  'spikepy/builtins/methods', 
                  'spikepy/builtins/methods/clustering_k_means', 
                  'spikepy/builtins/methods/detection_voltage_threshold', 
                  'spikepy/builtins/methods/extraction_spike_window', 
                  'spikepy/builtins/methods/filtering_copy_detection', 
                  'spikepy/builtins/methods/filtering_fir', 
                  'spikepy/builtins/methods/filtering_iir', 
                  'spikepy/builtins/methods/filtering_none', 
                  'spikepy/common', 
                  'spikepy/common/tests', 
                  'spikepy/developer_tools', 
                  'spikepy/developer_tools/tests', 
                  'spikepy/gui', 
                  'spikepy/gui/images', 
                  'spikepy/plotting/'],
    package_data = {'spikepy/builtins': ['spikepy.configspec',
                                        'spikepy.ini']},
    scripts=['spikepy/scripts/spikepy_gui.py', 
             'spikepy/scripts/spikepy_plugin_info.py'],
    license='GPL',
    platforms = ['windows', 'mac', 'linux']
    )


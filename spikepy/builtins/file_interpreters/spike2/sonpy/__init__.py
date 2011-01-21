'''
===========
SON LIBRARY
===========
For reading data from CED's Spike2 Son files.

Based on SON Library 2.0 for MATLAB, written by Malcolm Lidierth at
King's College London.
(See http://www.kcl.ac.uk/depsta/biomedical/cfnr/lidierth.html)

Antonio Gonzalez
Department of Neuroscience
Karolinska Institutet
Antonio.Gonzalez@cantab.net

http://www.neuro.ki.se/broberger/

June 2006

History:

2006-07-18: modified by Antonio Gonzalez
2009-02-20: bug fixes and slight modifications by
            Christoph T. Weidemann (ctw@cogsci.info)

============
Requirements
============
To use this library you need SciPy (http://scipy.org).

=====
Usage
=====
It can be used in any of three ways, depending on your needs:

(A) Reading a channel:

>>> from sonpy import son
>>> filename = '/path/file.smr'
>>> chan = son.Channel(chan_number, filename)
>>> chan.data()      # Returns channel data. Type help(chan.data) for details.
>>> chan.type()      # Channel type.
>>> chan.fhead.[...] # File header. See dir(chan.fhead)
>>> chan.info.[...]  # Channel information. See dir(chan.info)

(B) Opening a Son file, then reading one or more channels:

>>> from sonpy import son
>>> filename = '/path/file.smr'
>>> f = son.File(filename)
>>> f.chan_list()   # Prints a list of available channels in file 'filename'.
>>> f.get_channel(N) # Selects a channel 'N', where N is the channel number.
>>> f.chNN.data()   # Returns data from channel 'N'.
>>> f.chNN.type()   # Returns channel 'N' type.

(C) Reading Son file information:

>>> from sonpy import son
>>> filename = '/path/file.smr'
>>> f = son.FileHeader(filename)
>>> dir(f)         # Elements in file header.
>>> f.chan_list()  # Prints a list of available channels in file 'filename'.
'''

import son
__all__ = ['son']
__version__ = 1.1

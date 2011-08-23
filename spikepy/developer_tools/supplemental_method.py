"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

class SupplementalMethod(object):
    '''
    This class should be subclassed in order for developers to add a new 
supplemental method to spikepy.  For example, a method to calculate the
principal components of a set of features, or the L factor of a cluster set.
    There is no need to instantiate (create an object from) the subclass, 
spikepy will handle that internally.  Therefore it is important to have 
an __init__ method which requires no arguments (asside from 'self' of course).

Method that subclasses are REQUIRED to implement:
    - run(*args, **kwargs)
        -- This method returns the supplemental result.  *args is built by
           spikepy based on the <_requires> class-variable defined below or
           in subclasses.  **kwargs are any additional arguments you wish to
           pass in.
        -- The <_provides> class-variable tells spikepy where to store the
           results in the trial object.  Spikepy will create a resource for
           storing the result if the name(s) provided do not already correspond
           to resources previously defined.
    '''
    #     Is this method stochastic in nature (generally gives different results
    # with the same inputs)?
    is_stochastic = False

    # what resources or attributes (of Trial objects) does this method need 
    # in order to run?
    _requires = []
    _provides = []

    def run(*args, **kwargs):
        raise NotImplementedError 



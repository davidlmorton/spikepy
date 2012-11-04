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


import numpy

def _m_sq(x, mu, vi):
    fdot = numpy.dot((x-mu), vi)
    dist = numpy.dot(fdot, (x-mu).T)
    return dist

def _mahalanobis_squared(x, mu, vi):
    '''
        Return the mahalanobis distance between x and mu given the
    inverse of the covariance matrix vi.
    '''
    if x.ndim == 1:
        return _m_sq(x, mu, vi)
    elif x.ndim == 2:
        r = numpy.empty(len(x), dtype=x.dtype)
        for i, xr in enumerate(x):
            r[i] = _m_sq(xr, mu, vi)
        return r
    else:
        raise ValueError('x must have either one or two dimensions, not %d' %
            x.ndim)

def mahalanobis_squared(x, data, use_pseudo_inverse=False):
    '''
        Return the mahalanobis distance between x and the centeroid of the
    data.
    '''
    mu = numpy.average(data, axis=0)
    cov = numpy.cov(data, rowvar=0)
    if use_pseudo_inverse:
        vi = numpy.linalg.pinv(cov)
    else:
        vi = numpy.linalg.inv(cov)
    return _mahalanobis_squared(x, mu, vi)


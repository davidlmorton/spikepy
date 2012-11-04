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

from scipy.stats import chi2

def l_ratio(clustered_mahalanobis_squared_dict,
        degrees_of_freedom):
    cmsd = clustered_mahalanobis_squared_dict 
    df = degrees_of_freedom 

    return_dict = {}
    for key in cmsd.keys():
        if key is not 'Rejected':
            l_value = 0.0
            other_keys = [k for k in cmsd[key].keys() if 
                    k not in ['Rejected', key]]
            for other_key in other_keys:
                for d_sqrd in cmsd[key][other_key]:
                    l_value += 1.0 - chi2.cdf(d_sqrd, df)
            l_ratio = l_value/len(cmsd[key][key])
            return_dict[key] = {'l_value':l_value, 'l_ratio':l_ratio}
    return return_dict

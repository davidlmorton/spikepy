"""
Copyright (C) 2012  David Morton

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
from sklearn.mixture import GMM
import numpy

from spikepy.developer.methods import ClusteringMethod
from spikepy.common.valid_types import ValidInteger, ValidOption, ValidBoolean

class ClusteringGMMSKLearn(ClusteringMethod):
    '''
        This class implements a gaussian mixture model clustering method using 
    the sklearn package.
    '''
    name = 'GMM (sklearn)'
    description = 'Gaussian Mixture Model using the sklearn package.'
    is_stochastic = True
    
    restarts = ValidInteger(1, 10000, default=10)
    
    choices = ['Use BIC', 'Use AIC'] + map(str, range(1, 21)) 
    number_of_clusters = ValidOption(*choices, default='Use BIC', description=
            'The number of clusters, or estimate the number of clusters via Baysian Information or Akaike Information Criterion.')
    covariance_type = ValidOption('spherical', 'tied', 'diag', 'full', 
            default='diag', description='Type of covariance parameters to use.')

    def run(self, features, number_of_clusters='Use BIC', restarts=10, 
            covariance_type='diag'):
        if number_of_clusters == 1:
            result = numpy.zeros(len(features), dtype=numpy.int32)
            return [result]
        if number_of_clusters == 'Use BIC':
            clusters = GMM_with_criterion(features, restarts=restarts,
                    criterion=bic, covariance_type=covariance_type)
        elif number_of_clusters == 'Use AIC':
            clusters = GMM_with_criterion(features, restarts=restarts,
                    criterion=aic, covariance_type=covariance_type)
        else:
            clusters = GMM_alone(features, restarts=restarts, 
                    number_of_clusters=int(number_of_clusters),
                    covariance_type=covariance_type)
        return [clusters]

def aic(model, data):
    return model.aic(data)

def bic(model, data):
    return model.bic(data)

def GMM_alone(features, restarts=10, number_of_clusters=3, 
        covariance_type='diag', return_model=False):
    model = GMM(n_components=number_of_clusters, n_init=restarts, 
            covariance_type=covariance_type)
    model.fit(features)
    if return_model:
        return model
    else:
        return model.predict(features)

def GMM_with_criterion(features, restarts=10, criterion=aic, **kwargs):
    # a heuristic to guess the maximum number of clusters to try.
    max_k = int(numpy.ceil(numpy.log(len(features)))) + 3

    scores = []
    clusters = []
    for k in range(1, max_k):
        model = GMM_alone(features, restarts=restarts, number_of_clusters=k,
                return_model=True, **kwargs)
        scores.append(criterion(model, features))
        clusters.append(model.predict(features))

    sorted_index_list = numpy.argsort(scores)
    return clusters[sorted_index_list[0]]
        

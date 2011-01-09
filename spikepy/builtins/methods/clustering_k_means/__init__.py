from spikepy.developer_tools.clustering_method import ClusteringMethod
from .control_panel import ControlPanel
from .run import run as runner

class ClusteringKMeans(ClusteringMethod):
    '''
    This class implements a k-means clustering method.
    '''
    def __init__(self):
        self.name = 'K-means'
        self.description = 'Just randomly assigns clusters (TESTING)'

    def make_control_panel(self, parent, **kwargs):
        return ControlPanel(parent, **kwargs)

    def run(self, feature_set_list, **kwargs):
        return runner(feature_set_list, **kwargs)

from sklearn.manifold import TSNE
class DimensionReductionAlgorithm:
    def __init__(self, data):
        self.data = data
    def run(self):
        return []
    def Tsne(self):
        x_embedded = TSNE(n_components=2).fit_transform(self.data)
        return x_embedded

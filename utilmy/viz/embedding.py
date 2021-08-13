
"""

https://try2explore.com/questions/10109123

https://mpld3.github.io/examples/index.html



"""
import random
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import mpld3,
import numpy as np, pandas as pd
import spacy
from scipy.cluster.hierarchy import ward, dendrogram
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from utilmy.viz.top_toolbar import TopToolbar


################################################################################################################
CSS = """
    text.mpld3-text, div.mpld3-tooltip {
      font-family:Arial, Helvetica, sans-serif;
    }
    g.mpld3-xaxis, g.mpld3-yaxis {
    display: none; }
    """




################################################################################################################
class vizEmbedding:
    def __init__(self, path="myembed.parquet", num_clusters=5, sep=";" config:dict):
        """
           from utilmy.viz.embedding import vizEmbedding
           myviz = vizEmbedding()
           myviz.dim_reduction()
           myviz.create_visualization()        
        
        
          id, label,   embedding
          0    'five'   [ 1.0, 7.0, 6.0 ]
          
          
        """

        self.path = path
        self.sep  = sep
        self.num_clusters = num_clusters
        self.dist = None

        
    def dim_reduction(self, mode="mds", col_embed='embed', ndim=2): 
        
        if ".csv"     in self.path :        df  = pd.read_csv(self.path, sep=self.sep)
        if ".parquet" in self.path :        df  = pd.read_parquet(self.path)
        
        
        vector_matrix = np.vstack( [ v for  v in  df[col_embed].values ] )   ## into 2D numpy array
        self.id_list  = np.arange(0, len(df))
        self.labels   = df["label"].values
        
        
        # vectors_matrix = np.vstack([nlp(text).vector for text in tqdm(self.texts)])
        self.dist = 1 - cosine_similarity(vectors_matrix)

        if mode == 'mds' :
            mds = MDS(n_components=ndim, dissimilarity="precomputed", random_state=1)
            pos = mds.fit_transform(self.dist)  # shape (n_components, n_samples)
            
        if mode == 'umap' :
            pass
        
        self.vectors_matrix = vectors_matrix
        self.pos = pos
        
        
        
    def create_clusters(self):        
        km = KMeans(n_clusters=self.num_clusters)
        km.fit( self.vectors_matrix)
        clusters = km.labels_.tolist()
        
        self.cluster_color = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(self.num_clusters)]        
        self.clusters      = clusters
        
        
    def create_visualization(self, mode='d3', **kw ):

        xs, ys = self.pos[:, 0], self.pos[:, 1]

        cluster_names = {i: f'Cluster {i}' for i in range(self.num_clusters)}
        text_label_and_text = [': '.join(t) for t in list(zip(self.text_labels, self.texts))]

        # create data frame that has the result of the MDS plus the cluster numbers and titles
        df = pd.DataFrame(dict(x=xs, y=ys, clusters=clusters, title=text_label_and_text))

        # group by cluster
        groups_clusters = df.groupby('clusters')

        # set up plot
        fig, ax = plt.subplots(figsize=(25, 15))  # set size
        ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling

        # iterate through groups to layer the plot
        # note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return
        # the appropriate color/label
        for name, group in groups_clusters:
            ax.plot(group.x, group.y, marker='o', linestyle='', ms=12, label=cluster_names[name],
                    color=self.cluster_color[name],
                    mec='none')
            ax.set_aspect('auto')
            ax.tick_params(axis='x',  # changes apply to the x-axis
                           which='both',  # both major and minor ticks are affected
                           bottom='off',  # ticks along the bottom edge are off
                           top='off',  # ticks along the top edge are off
                           labelbottom='off')
            ax.tick_params(axis='y',  # changes apply to the y-axis
                           which='both',  # both major and minor ticks are affected
                           left='off',  # ticks along the bottom edge are off
                           top='off',  # ticks along the top edge are off
                           labelleft='off')

        ax.legend(numpoints=1)  # show legend with only 1 point

        # add label in x,y position with the label as the
        for i in range(len(df)):
            ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=8)

        # uncomment the below to save the plot if need be
        plt.savefig(f'clusters_static-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.png', dpi=200)

        # Plot
        fig, ax = plt.subplots(figsize=(20, 15))  # set plot size
        ax.margins(0.03)  # Optional, just adds 5% padding to the autoscaling

        # iterate through groups to layer the plot
        for name, group in groups_clusters:
            points = ax.plot(group.x, group.y, marker='o', linestyle='', ms=18, label=cluster_names[name], mec='none',
                             color=self.cluster_color[name])
            ax.set_aspect('auto')
            labels = [i for i in group.title]

            # set tooltip using points, labels and the already defined 'css'
            tooltip = mpld3.plugins.PointHTMLTooltip(points[0], labels, voffset=10, hoffset=10, css=CSS)
            # connect tooltip to fig
            mpld3.plugins.connect(fig, tooltip, TopToolbar())

            # set tick marks as blank
            ax.axes.get_xaxis().set_ticks([])
            ax.axes.get_yaxis().set_ticks([])

            # set axis as blank
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)

        ax.legend(numpoints=1)  # show legend with only one dot
        mpld3.show()  # show the plot

    def draw_dendogram(self):
        linkage_matrix = ward(self.dist)  # define the linkage_matrix using ward clustering pre-computed distances
        fig, ax = plt.subplots(figsize=(15, 20))  # set size
        ax = dendrogram(linkage_matrix, orientation="right", labels=self.text_labels)
        plt.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
        plt.tight_layout()
        plt.savefig('dendogram_clusters.png', dpi=200)
        
        
        

        
        
        
 #nlp = spacy.load('en_vectors_web_lg')


def tokenize_text(text):
    return [
        token.lemma_
        for token
        in nlp(text)
        if not token.is_punct and
           not token.is_digit and
           not token.is_space and
           not token.like_num
    ]
        
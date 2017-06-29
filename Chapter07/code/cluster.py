# seven.cluster
# Use the louvain method to detect communities
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Jan 13 16:39:50 2014 -0500
#
# ID: cluster.py [] benjamin@bengfort.com $

"""
Use the louvain method to detect communities
"""

##########################################################################
## Imports
##########################################################################

import random
import community
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from collections import defaultdict
from graph import *


def example_clustering():

    G = nx.karate_club_graph()

    #first compute the best partition
    partition = community.best_partition(G)

    #drawing
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12,12))
    plt.axis('off')

    nx.draw_networkx_nodes(G, pos, node_size=200, cmap=plt.cm.RdYlBu, node_color=partition.values())
    nx.draw_networkx_edges(G,pos, alpha=0.5)
    plt.savefig("figure/karate_communities.png")

def detect_communities(graph, verbose=False):
    graph = graph_from_csv(graph)
    partition = community.best_partition(graph)
    if verbose:
        print "%i partitions" % len(set(partition.values()))
    nx.set_node_attributes(graph, 'partition', partition)
    return graph, partition

def communities_histogram(graph, verbose=False):
    graph, partition = detect_communities(graph, verbose)

    #plt.hist(partition.values(), bins=25, color="#0f6dbc")
    #plt.title("Size of Marvel Communities")
    #plt.xlabel("Community")
    #plt.ylabel("Nodes")

    parts = defaultdict(int)
    for part in partition.values():
        parts[part] += 1

    bubbles = nx.Graph()
    for part in parts.items():
        bubbles.add_node(part[0], size=part[1])

    pos = nx.random_layout(bubbles)
    plt.figure(figsize=(12,12))
    plt.axis('off')

    nx.draw_networkx_nodes(bubbles, pos,
        alpha=0.6, node_size=map(lambda x: x*6, parts.values()),
        node_color=[random.random() for x in parts.values()], cmap=plt.cm.RdYlBu)

    #plt.show()
    plt.savefig("figure/communities_histogram_alt.png")

if __name__ == '__main__':
    communities_histogram(HERO_NETWORK)

# seven.graph
# Generate a Graph from a CSV file
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Jan 03 16:35:39 2014 -0500
#
# ID: graph.py [] benjamin@bengfort.com $

"""
Generate a Graph from a CSV file
"""

##########################################################################
## Imports
##########################################################################

import networkx as nx
import unicodecsv as csv
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from operator import itemgetter

HERO_NETWORK = "data/hero-network.csv"
COMIC_HERO_NETWORK = "data/comic-hero-network.gdf"

def graph_from_csv(path):
    graph = nx.Graph(name="Heroic Social Network")
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        for row in reader:
            graph.add_edge(*row)
    return graph

def graph_from_gdf(path):
    graph = nx.Graph(name="Characters in Comics")
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        for row in reader:
            if 'nodedef' in row[0]:
                handler = lambda row,G: G.add_node(row[0], TYPE=row[1])
            elif 'edgedef' in row[0]:
                handler = lambda row,G: G.add_edge(*row)
            else:
                handler(row, graph)
    return graph

def average_degree(graph):
    total = 0
    count = 0
    for node in graph.nodes_iter():
        count += 1
        total += graph.degree(node)

    return float(total) / float(count)

def draw_degree_histogram(graph):
    plt.hist(graph.degree().values(), bins=500)
    plt.title("Connectedness of Marvel Characters")
    plt.xlabel("Degree")
    plt.ylabel("Frequency")
    #plt.show()
    plt.savefig("figure/degree_histogram.png")

def multi_comic_nodes(graph):
    for node in graph.nodes_iter():
        if graph.node[node]['TYPE'] == 'hero' and \
           len(graph.edges([node])) == 2:
                print node

def get_ego_graph(graph, character):
    """
    Expecting a graph_from_gdf
    """

    # Graph and Position
    ego = nx.ego_graph(graph, character, 3)
    pos = nx.spring_layout(ego)
    plt.figure(figsize=(12,12))
    plt.axis('off')

    # Coloration and Configuration
    ego.node[character]["TYPE"] = "center"
    valmap = { "comic": 0.25, "hero": 0.54, "center": 0.87 }
    types  = nx.get_node_attributes(ego, "TYPE")
    values = [valmap.get(types[node], 0.25) for node in ego.nodes()]

    # Draw
    nx.draw_networkx_edges(ego, pos, alpha=0.4)
    nx.draw_networkx_nodes(ego, pos,
                           node_size=80,
                           node_color=values,
                           cmap=plt.cm.hot, with_labels=False)

    #plt.show()
    plt.savefig("figure/longbow_ego_2hop.png")

def get_weighted_ego_graph(graph, character, hops=1):
    # Graph and Position
    ego = nx.ego_graph(graph, character, hops)
    pos = nx.spring_layout(ego)
    plt.figure(figsize=(12,12))
    plt.axis('off')

    # Coloration and Configuration
    ego.node[character]["TYPE"] = "center"
    valmap = { "hero": 0.0, "center": 1.0 }
    types  = nx.get_node_attributes(ego, "TYPE")
    values = [valmap.get(types[node], 0.25) for node in ego.nodes()]

    char_edges = ego.edges(data=True, nbunch=[character,])
    nonchar_edges = ego.edges(nbunch=[n for n in ego.nodes() if n != character])
    elarge=[(u,v) for (u,v,d) in char_edges if d['weight'] >=0.12]
    esmall=[(u,v) for (u,v,d) in char_edges if d['weight'] < 0.12]
    print set([d['weight'] for (u,v,d) in char_edges])

    # Draw
    nx.draw_networkx_nodes(ego, pos,
                           node_size=200,
                           node_color=values,
                           cmap=plt.cm.Paired, with_labels=False)

    nx.draw_networkx_edges(ego,pos,edgelist=elarge,
                        width=1.5, edge_color='b')
    nx.draw_networkx_edges(ego,pos,edgelist=esmall,
                        width=1,alpha=0.5,edge_color='b',style='dashed')
    nx.draw_networkx_edges(ego,pos,edgelist=nonchar_edges,
                        width=0.5,alpha=0.2,style='dashed')

    plt.show()
    #plt.savefig("figure/weighted_longbow_ego.png")

def dunbars_number(graph):
    data = np.array(graph.degree().values())
    print np.mean(data)
    print scipy.stats.mode(data)
    print np.median(data)

def draw_big_graph(graph):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(100,100))
    plt.axis('off')

    valmap = { "comic": 0.25, "hero": 0.54, "center": 0.87 }
    types  = nx.get_node_attributes(graph, "TYPE")
    values = [valmap.get(types[node], 0.25) for node in graph.nodes()]

    nx.draw_networkx_edges(ego, pos, alpha=0.4)
    nx.draw_networkx_nodes(ego, pos,
                           node_size=80,
                           node_color=values,
                           cmap=plt.cm.hot, with_labels=False)

    plt.savefig("figure/giant.png", dpi=1000)

def degree_centrality(graph):
    centrality = nx.degree_centrality(graph)
    nx.set_node_attributes(graph, 'centrality', centrality)
    degrees = sorted(centrality.items(), key=itemgetter(1), reverse=True)
    for idx, item in enumerate(degrees[0:10]):
        item = (idx+1,) + item + (graph.degree(item[0]),)
        print "%i. %s: %0.3f (%i)" % item

def betweenness_centrality(graph):
    #centrality = nx.betweenness_centrality(graph, normalized=True)
    #centrality = nx.closeness_centrality(graph)
    centrality = nx.eigenvector_centrality_numpy(graph)
    nx.set_node_attributes(graph, 'centrality', centrality)
    degrees = sorted(centrality.items(), key=itemgetter(1), reverse=True)
    for idx, item in enumerate(degrees[0:10]):
        item = (idx+1,) + item
        print "%i. %s: %0.3f" % item

def transform_to_weighted_heros(comics, outpath="data/weighted_heros.csv"):
    # Create new graph to fill in
    heros = nx.Graph(name="Weighted Heroic Social Network")

    # Iterate through all the nodes and their properties
    for node, data in graph.nodes(data=True):
        # We don't care about comics, only heros
        if data['TYPE'] == 'comic': continue
        # Add the hero and their properties (this will also update data)
        heros.add_node(node, **data) # Add or update nodes

        # Find all the heros connected via the comic books
        for comic in graph[node]:
            for alter in graph[comic]:
                # Skip the same hero in the comic
                if alter == node: continue

                # Setup the default edge
                if alter not in heros[node]:
                    heros.add_edge(node, alter, weight=0.0, label="knows")

                # The weight of the hero is the fraction of connections / 2
                heros[node][alter]["weight"] += 1.0 / (graph.degree(comic) *2)
    return heros

if __name__ == '__main__':
    #graph   = graph_from_csv(HERO_NETWORK)
    graph = graph_from_gdf(COMIC_HERO_NETWORK)
    print nx.info(graph)
    #print nx.triangles(graph)
    #print nx.transitivity(graph)
    #print nx.clustering(graph)
    #print nx.average_clustering(graph)
    #for subgraph in nx.connected_component_subgraphs(graph):
    #    print nx.diameter(subgraph)
    #    print nx.average_shortest_path_length(subgraph)
    #betweenness_centrality(graph)
    #print nx.density(graph)

    #degree_centrality(graph)
    #draw_degree_histogram(graph)
    #dunbars_number(graph)

    #print "Graph generated with %i nodes and %i edges" % (graph.number_of_nodes(), graph.number_of_edges())

    #print graph.order()
    #print graph.size()
    #print "Average degree: %0.3f" % average_degree(graph)
    #ctr = "LONGBOW/AMELIA GREER"
    #get_ego_graph(graph, ctr)

    #draw_big_graph(graph)

    #nx.draw_spring(ego)


    #multi_comic_nodes(graph)
    #heros = transform_to_weighted_heros(graph)
    #print nx.info(heros)
    #get_weighted_ego_graph(heros, "LONGBOW/AMELIA GREER")

    unigraph = graph.to_undirected()
    print len(unigraph.edges()) / len(graph.edges())

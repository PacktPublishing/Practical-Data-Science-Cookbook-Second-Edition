import networkx as nx
from operator import itemgetter
from graph import *

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

def nbest_centrality(graph, metric, n=10, attribute="centrality", **kwargs):
    centrality = metric(graph, **kwargs)
    nx.set_node_attributes(graph, attribute, centrality)
    degrees = sorted(centrality.items(), key=itemgetter(1), reverse=True)
    for idx, item in enumerate(degrees[0:n]):
        item = (idx+1,) + item
        print "%i. %s: %0.3f" % item

if __name__ == '__main__':
    graph   = graph_from_csv(HERO_NETWORK)
    print nx.info(graph)

    #nbest_centrality(graph, nx.degree_centrality)
    nbest_centrality(graph, nx.betweenness_centrality, normalized=True)
    #nbest_centrality(graph, nx.closeness_centrality)
    #nbest_centrality(graph, nx.eigenvector_centrality_numpy)

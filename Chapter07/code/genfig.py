#!/usr/bin/env python
# seven.genfig
# Generates Graph Figures for the Chapter
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Jan 09 21:29:38 2014 -0500
#
# ID: genfig.py [] benjamin@bengfort.com $

"""
Generates Graph Figures for the Chapter
"""

import networkx as nx
import matplotlib.pyplot as plt
from random import random

def figure_one():
    graph = nx.Graph()
    graph.add_edge('A', 'B')
    graph.add_edge('B', 'C')
    graph.add_edge('B', 'D')
    graph.add_edge('A', 'C')
    graph.add_edge('D', 'C')

    graph.add_edge('E', 'B')
    graph.add_edge('B', 'F')
    graph.add_edge('B', 'G')
    graph.add_edge('E', 'F')
    graph.add_edge('G', 'F')

    nx.draw_spring(graph, cmap=plt.get_cmap('Blues'), node_color=[random() for n in graph.nodes()])
    plt.savefig('figure/simple_graph.png')

def figure_two():
    p=nx.single_source_shortest_path_length(graph,'B')
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(8,8))
    nx.draw_networkx_edges(graph,pos,nodelist=['B'],alpha=0.4)
    nx.draw_networkx_nodes(graph,pos,nodelist=p.keys(),
                           node_size=80,
                           node_color=p.values(),
                           cmap=plt.cm.Reds_r)
    plt.axis('off')

def figure_three():
    graph = nx.Graph()
    #graph.add_edge('Abe', 'Ben')
    #graph.add_edge('Ben', 'Charlie')
    #graph.add_edge('Ben', 'Dave')
    graph.add_edge('Dave', 'Charlie')
    #graph.add_edge('Ben', 'Joe')
    graph.add_edge('Joe', 'Abe')
    #graph.add_edge('Frank', 'Ben')
    graph.add_edge('Frank', 'Charlie')

    nx.draw_spring(graph, cmap=plt.get_cmap('Blues'),
                   node_color=[random() for n in graph.nodes()],
                   with_labels=False)
    #plt.show()
    #plt.savefig('figure/structured_ego.png')
    plt.savefig('figure/isolated_ego.png')

def figure_four():
    graph = nx.Graph()
    graph.add_path(['A', 'B', 'C', 'D'])
    graph.add_path(['A', 'C', 'E', 'F'])
    graph.add_edge('E', 'G')
    graph.add_edge('B', 'E')

    nx.set_node_attributes(graph, 'color', nx.betweenness_centrality(graph, normalized=True))

    patha = [('A', 'B'), ('B', 'E'),]
    pathb = [('A', 'C'), ('C', 'E'),]
    pos = nx.spring_layout(graph, iterations=500)
    plt.figure(figsize=(8,8))
    plt.axis('off')

    nx.draw_networkx_nodes(graph, pos, cmap=plt.cm.Blues, node_color=[graph.node[n]['color'] for n in graph.nodes()], node_size=590)
    nx.draw_networkx_edges(graph, pos, alpha=0.4, width=1)
    nx.draw_networkx_edges(graph, pos, edgelist=patha, edge_color="#520fc6", width=1.5, alpha=0.6)
    nx.draw_networkx_edges(graph, pos, edgelist=pathb, edge_color="#f4002b", width=1.5, alpha=0.6)
    nx.draw_networkx_labels(graph, pos)

    plt.show()
    #plt.savefig('figure/path_distance.png')

def figure_five():
    graph = nx.Graph()
    graph.add_path(['A', 'B', 'C', 'D'])
    graph.add_path(['A', 'C', 'E', 'F'])
    graph.add_edge('E', 'G')
    graph.add_edge('B', 'E')

    #nx.set_node_attributes(graph, 'color', nx.betweenness_centrality(graph, normalized=True))
    #nx.set_node_attributes(graph, 'color', nx.closeness_centrality(graph))
    nx.set_node_attributes(graph, 'color', nx.eigenvector_centrality(graph))
    values = [graph.node[n]['color'] for n in graph.nodes()]
    pos = nx.spring_layout(graph, iterations=500)
    plt.figure(figsize=(8,8))
    plt.axis('off')

    nx.draw_networkx_nodes(graph, pos, cmap=plt.cm.Blues, node_color=values, node_size=590)
    nx.draw_networkx_edges(graph, pos, alpha=0.6, width=1)
    nx.draw_networkx_labels(graph, pos)

    #plt.show()
    #plt.savefig('figure/betweenness.png')
    #plt.savefig('figure/closeness.png')
    plt.savefig('figure/eigenvector.png')

if __name__ == '__main__':
    figure_five()

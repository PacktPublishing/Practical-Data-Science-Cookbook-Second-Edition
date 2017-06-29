#!/usr/bin/env python
# seven.random
# Generate a random graph
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Jan 10 00:01:54 2014 -0500
#
# ID: rgraph.py [] benjamin@bengfort.com $

"""
Generate a random graph
"""

import networkx as nx
import matplotlib.pyplot as plt

#G=nx.karate_club_graph()
#G=nx.florentine_families_graph()
G=nx.davis_southern_women_graph()
pos=nx.spring_layout(G)

# find node near center (0.5,0.5)
dmin=1
ncenter=0
for n in pos:
    x,y=pos[n]
    d=(x-0.5)**2+(y-0.5)**2
    if d<dmin:
        ncenter=n
        dmin=d

# color by path length from node near center
p=nx.single_source_shortest_path_length(G,ncenter)


# Draw the graph
plt.figure(figsize=(8,8))
nx.draw_networkx_edges(G,pos,nodelist=[ncenter],alpha=0.4)
nx.draw_networkx_nodes(G,pos,nodelist=p.keys(),
                       node_size=90,
                       node_color=p.values(),
                       cmap=plt.cm.Reds_r)

plt.xlim(-0.05,1.05)
plt.ylim(-0.05,1.05)
plt.axis('off')
plt.savefig('figure/example_social_viz.png')
plt.show()

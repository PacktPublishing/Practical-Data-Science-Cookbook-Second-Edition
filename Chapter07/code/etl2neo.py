#!/usr/bin/env python
# seven.etl2neo
# Generate Cypher statements for Graph
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Jan 09 20:44:42 2014 -0500
#
# ID: etl2neo.py [] benjamin@bengfort.com $

"""
Generate Cypher statements for Graph
"""

import re
import unicodecsv as csv

NODE_DELIM = re.compile(r'nodedef>name VARCHAR,type VARCHAR')
EDGE_DELIM = re.compile(r'edgedef>node1 VARCHAR,node2 VARCHAR')


def escape_cypher(s):
    return re.sub(r'([\"\'\\])', r'\\\1', s)

def handle_node(row):
    label = row[1].title()
    row.append(label)
    return "CREATE (n:{2} {{ name:'{0}', type:'{1}' }});".format(*[escape_cypher(item) for item in row])

def handle_edge(row):
    return "MATCH (a:Hero), (b:Comic) WHERE a.name='{0}' AND b.name='{1}' CREATE (a)-[r:IN]->(b);".format(*[escape_cypher(item) for item in row])

def read_graph(path):
    handler = None
    with open(path, 'rU') as data:
        reader = csv.reader(data)
        for row in reader:
            if 'nodedef' in row[0]:
                handler = handle_node
            elif 'edgedef' in row[0]:
                handler = handle_edge
            else:
                yield handler(row)

def write_graph(items, path):
    with open(path, 'w') as cql:
        cql.write("BEGIN\n")
        count = 0
        for row in items:
            count += 1
            if count % 500 == 0:
                cql.write("COMMIT\nBEGIN\n")
            cql.write(row)
            cql.write("\n")
        cql.write("COMMIT")
        print "Wrote %i rows" % count

if __name__ == '__main__':
    INPATH = "data/comic-hero-network.gdf"
    OTPATH = "data/comic-heros.cql"
    write_graph(read_graph(INPATH), OTPATH)

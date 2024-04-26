import sys
import re
import networkx as nx

from mininet.topo import Topo

def sndlib_to_networkx(file_path):
    # Create a new directed graph
    G = nx.DiGraph()
    demands =  {}

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            line = re.sub(r'[()]', '', line)
            data = line.split()
            #print(data)

            if not data or data[0] == "#":
                #skip commented or empty lines
                continue
            if len(data) < 3:
                #empty line, skip:
                continue
            elif len(data) == 3:
                #node
                node_id = data[0]
                node_lon = data[1]
                node_lat = data[2]
                G.add_node(node_id)
            elif len(data) == 6:
                #demand
                source = data[1]
                destination = data[2]
                demand = int(float(data[4]))
                demands[(source, destination)] = demand
            else:
                #assume link, may need to check further in some files
                source = data[1]
                target = data[2]
                bandwidth = data[7]
                power = data[8]

                G.add_edge(source, target, bandwidth=bandwidth, power=power)

    return G, demands


def networkx_to_mininet(G : nx.Graph, D : dict = None):

    topo =  Topo()

    switch_id_association = {}


    id = 0
    for node in G.nodes:

        switch_id_association[node] = "s%s" % id
        topo.addSwitch("s%s" % id)
        
        id += 1
    
    for s0, s1, data in G.edges(data=True):

        s0 = switch_id_association[s0]
        s1 = switch_id_association[s1]

        topo.addLink(s0, s1)#, bw=G[s0][s1]["bandwidth"])

    #print(switch_id_association)

    if not D:
        return topo

    new_demand = {}

    for (s0, s1), value in D.items():
        new_demand[(switch_id_association[s0], switch_id_association[s1])] = value

    #print(new_demand)

    return topo, new_demand



if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Please provide an input file path")
        sys.exit(1)
    
    G, D = sndlib_to_networkx(sys.argv[1])
    topo, D = networkx_to_mininet(G, D)
    print(topo.convertTo(nx.MultiGraph))




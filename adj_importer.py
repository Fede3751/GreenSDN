import networkx as nx
import re
from mininet.topo import Topo

def adj_importer(adj, rename=True):

    no_nodes =  0
    for link in adj:
        no_nodes = max(no_nodes, max(link)+1)

    degree = [0] * no_nodes

    for link in adj:
        degree[link[0]] += 1
        degree[link[1]] += 1


    adj_named = []
    for link in adj:
        u = link[0]
        v = link[1]

        if rename:

            if degree[u] == 1:
                u = "h%s"%u
            else:
                u = "s%s"%u
            
            if degree[v] == 1:
                v = "h%s"%v
            else:
                v = "s%s"%v        

        adj_named.append([u,v])


    return nx.from_edgelist(adj_named)
    



def to_mininet(G : nx.Graph):

    topo =  Topo()

    for u in G.nodes:
        if is_host_interface(u):
            topo.addHost(u)
        else:
            topo.addSwitch(u)

    for u,v in G.edges:
        topo.addLink(u, v)


    return topo



def is_host_interface(link):
    return link[0]=="h"
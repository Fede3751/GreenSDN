import networkx as nx
import random


def maxRESDN(G : nx.Graph, D : dict, umin = 0.5, umax = 1):

    D = D.copy()


    while D:
        next_demand = max(D.items(), key=lambda x: x[1])[0]
        source = next_demand[0]
        target = next_demand[1]
        demand = D[next_demand]

        D.pop(next_demand)

        path_to_use = pathMaxRESDN(G, source, target, demand, umin, umax)

        #for link in path_to_use:
        for i in range(len(path_to_use)-1):
            link = (path_to_use[i], path_to_use[i+1])
            G.nodes[link[0]]["active"] = True
            G.nodes[link[1]]["active"] = True
            G[link[0]][link[1]]["active"] = True
            G[link[0]][link[1]]["used_bandwidth"] += demand

        #print("One path placed")

    return G



def pathMaxRESDN(G : nx.Graph, source : str, target : str,  demand : int, umin = 0.5, umax = 1):

    max_RESDN = 0
    selected_paths = []

    #all_paths = list(nx.all_simple_edge_paths(G, source, target))
    #all_paths = list(nx.all_shortest_paths(G, source, target))
    #print(source, target, demand)
    #print(len(all_paths))
    
    #    next_demand = max(D.items(), key=lambda x: x[1])[0]

    G_trimmed = G.copy()

    for u,v,data in G.edges(data=True):
        if data["used_bandwidth"] + demand > data["bandwidth"]:
            G_trimmed.remove_edge(u,v)



    paths_tested = 0
    for path in nx.shortest_simple_paths(G_trimmed, source, target):


        if paths_tested >= 100:
            break
        paths_tested += 1

        candidate = True
        G_copy = G.copy()
        

        #for link in path:
        for i in range(len(path)-1):
            link = (path[i], path[i+1])
            link_data = G_copy[link[0]][link[1]]

            if link_data["used_bandwidth"] + demand > link_data["bandwidth"]:
                #print("Too much flow")
                #print(link_data["bandwidth"])
                candidate = False
                break
            else:
                G_copy[link[0]][link[1]]["used_bandwidth"] += demand
                G_copy[link[0]][link[1]]["active"] = True

        if not candidate:
            continue

        RESDN_value = RESDN(G_copy, umin, umax)

        if RESDN_value > max_RESDN:
            max_RESDN = RESDN_value
            selected_paths = [path]
        elif RESDN_value == max_RESDN:
            selected_paths.append(path)

    if len(selected_paths) > 1:
        selected_path =  min(selected_paths, key=lambda x: len(x))
    else:
        selected_path = selected_paths[0]

    #print(selected_path)
    return selected_path



def RESDN(G : nx.Graph, Umin : float = 0.2, Umax : float = 1):

    satisfy_utility = 0
    link_count = 0

    for link in G.edges(data=True):

        link = link[2]

        if not link["active"]:
            continue

        link_count += 1

        if Umin <= link["used_bandwidth"]/link["bandwidth"] <= Umax:
            satisfy_utility += 1
    
    return satisfy_utility/link_count



def is_host_interface(link):
    #pattern = re.compile(r"^h\d")
    #match = pattern.search(link)

    #return bool(match)

    return link[0] == "h"
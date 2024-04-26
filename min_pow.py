import networkx as nx
from mininet.topo import Topo


def heuristic_min_pow(network : Topo, G : nx.Graph, D : dict):


    D = D.copy()

    #first disable all links, we will now dinamically bring them up in responde with the demand 
    for (u,v,data) in G.edges(data=True):
        interfaces = data["interface"]
        #print(interfaces)
        #disable_link(data)


    #let's find our highest demand!
    next_port = 3751

    while D:

        next_demand = max(D.items(), key=lambda x: x[1])[0]

        host_source = next_demand[0]
        host_destination = next_demand[1]
        next_demand_value = D[next_demand]

        D.pop(next_demand)


        #find which links we are using to satisfy the next demand, and restore them
        path, value = min_path_pow(G, host_source, host_destination, next_demand_value)

        if not path:
            continue

        #links = shortest_path_link_data
        for i in range(len(path)-1):

            link = (path[i], path[i+1])

            G[link[0]][link[1]]["used_bandwidth"] += next_demand_value
            link_data = G[link[0]][link[1]]

            G[link[0]][link[1]]["active"] = True
            G.nodes[link[0]]["active"] = True
            G.nodes[link[1]]["active"] = True

            #restore_link(link_data)

        #host_source = network.get(host_source)
        #host_destination = network.get(host_destination)

        #host_destination.cmdPrint("python recv_udp.py {} &".format(next_port))
        #host_source.cmdPrint("python send_udp.py {} {} {} &".format(host_destination.IP(), next_port, next_demand_value))
        
        next_port+=1
    
    #start traffic of the given demand between the links


def min_path_pow(G, source, destination, demand):
    # A list to store the shortest path
    path = []

    # A variable to store the minimum power consumption
    min_power = float("inf")

    G_power_graph = G.copy()
    for (u, v, data) in G.edges(data=True):

        #print(u,v,data)
        
        if data["bandwidth"] - data["used_bandwidth"] < demand:
            G_power_graph.remove_edge(u, v)

        elif data["active"]:
            G_power_graph[u][v]["weight"] = 0

        else:
            G_power_graph[u][v]["weight"] = data["power"]
            if not G.nodes[u]["active"]:
                G_power_graph[u][v]["weight"] += G.nodes[u]["active_power"]
            if not G.nodes[v]["active"]:
                G_power_graph[u][v]["weight"] += G.nodes[v]["active_power"]


    #print(G_power_graph.edges(data=True))

    #print(source, destination, demand)
    #try:
    path = nx.dijkstra_path(G_power_graph, source, destination)
    #except:
    #    path = None
    #    pass
    # for i in range(len(path) - 1):
    #     nx.set_edge_attributes(G, {(path[i], path[i+1])  :{"active": True}})
    # for i in path:
    #     nx.set_node_attributes(G, {i: {"active": True}})

    # Return the shortest path with the minimum power consumption
    return (path, min_power)

from mininet.topo import Topo
from mininet.node import CPULimitedHost, OVSController, DefaultController, RemoteController
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser
from random import randrange
import random
import networkx as nx
import os
from geant.parse_totem import load_totem_topology, load_demand
from geant.load_big_demand import load_big_demand


import matplotlib.pyplot as plt

import os



#CONS FOR OPTIMIZATION PROBLEM
CONSUMPTION_PER_SWITCH = 20
CONSUMPTION_PER_PORT = 5
TIME_STEP = 5


parser = ArgumentParser(description="Jellyfish Tests")

parser.add_argument('-nse',
                    dest="nServers",
                    type=int,
                    action="store",
                    help="Number of servers",
                    default=16)

parser.add_argument('-nsw',
                    dest="nSwitches",
                    type=int,
                    action="store",
                    help="Number of switches",
                    default=20)

parser.add_argument('-np',
                     dest="nPorts",
                    type=int,
                    action="store",
                    help="Number of ports per switch",
                    default=4)

args = parser.parse_args()



class JFTopo(Topo):
    "Jellyfish Topology"

    def __init__(self, nServers, nSwitches, nPorts):
        super(JFTopo, self).__init__()
        self.nServers = nServers
        self.nSwitches = nSwitches
        self.nPorts = nPorts
        #self.create_topology()

    def create_topology(self):
        servers = []
        for n in range(self.nServers):
            servers.append(self.addHost('h%s' % n))

        switches = []
        openPorts = []
        for n in range(self.nSwitches):
            switches.append(self.addSwitch('s%s' % n))
            openPorts.append(self.nPorts)
        
        # Connect each server with a switch
        for n in range(self.nServers):
            #print("adding link h%s-s%s" % (n, n))
            #print(servers[n])
            #print(switches[n])
            self.addLink(servers[n], switches[n])
            #self.addLink(switches[n], servers[n]) #delay, bandwith?
            openPorts[n] -= 1
            # assume nPorts > 1
        
        # Manage the potential links, fully populate the set before creating
        links = set()
        switchesLeft = self.nSwitches
        consecFails = 0
        while switchesLeft > 1 and consecFails < 1000:
            s1 = randrange(self.nSwitches)
            while openPorts[s1] == 0:
                s1 = randrange(self.nSwitches)

            s2 = randrange(self.nSwitches)
            while openPorts[s2] == 0 or s1 == s2:
                s2 = randrange(self.nSwitches)

            if (s1, s2) in links:
                consecFails += 1
            else:
                consecFails = 0
                links.add((s1, s2))
                links.add((s2, s1))

                openPorts[s1] -= 1
                openPorts[s2] -= 1

                if openPorts[s1] == 0:
                    switchesLeft -= 1

                if openPorts[s2] == 0:
                    switchesLeft -= 1

        if switchesLeft > 0:
            for i in range(self.nSwitches):
                while openPorts[i] > 1:
                    while True:
                        # incremental expansion
                        rLink = random.sample(links, 2)
                        if (i, rLink[0]) in links:
                            continue
                        if (i, rLink[1]) in links:
                            continue

                        # Remove links
                        links.remove(rLink)
                        links.remove(rLink[::-1])

                        # Add new links
                        links.add((i, rLink[0]))
                        links.add((rLink[0], i))
                        links.add((i, rLink[1]))
                        links.add((rLink[1], i))

                        openPorts[i] -= 2

        for link in links:
            # prevent double counting
            if link[0] < link[1]:
                #print("adding link s%s-s%s" % (link[0], link[1]))
                #print(switches[link[0]])
                #print(switches[link[1]])
                self.addLink(switches[link[0]], switches[link[1]])
        # while 
        # pick random switch (make sure has open port)
        # pick 2nd random diff switch
        # connect if not connected already, decrement count for each of the switches port count, if = 0, decrement total count
        # if not connect add to fail counter, when reached 10 break
        # if 0 finish
        # if 1, check # ports, if 2/3 call port expansion (connects empty ports to existing link that is not this node), if 4call twice



        GMulti = self.convertTo(nx.MultiGraph)
        G = nx.Graph(GMulti)
        #print(G.edges)
        nx.draw(G)
        plt.show()

        new_link_data = {}

        for l in nx.node_link_data(G)["links"]:
            new_link_data[l["source"], l["target"]] = {"interface": link_interface(l), "bandwidth": 5, "used_bandwidth": 0, "power": 1, "active": False}

        #print(new_link_data)

        for (n1, n2, d) in G.edges(data=True):
            d.clear()

        nx.set_edge_attributes(G, new_link_data)
        nx.set_node_attributes(G, 10, "power")
        nx.set_node_attributes(G, False, "active")

        edges = G.edges(data=True)
        #print(edges)
        #print(G.nodes["s0"])

        return G
        

def is_host_interface(link):
    #pattern = re.compile(r"^h\d")
    #match = pattern.search(link)

    #return bool(match)

    return link[0] == "h"

def link_interface(link):
    return link["node1"]+"-eth"+str(link["port1"])+":"+link["node2"]+"-eth"+str(link["port2"])

def get_interfaces_from_link(input_string: str) -> tuple:
    if ':' not in input_string:
        return input_string, None
    before_colon, after_colon = input_string.split(':', 1)
    return before_colon, after_colon

def jellyfish():
    topo = JFTopo(nServers=args.nServers,nSwitches=args.nSwitches,nPorts=args.nPorts)
    network_graph = topo.create_topology()
    net = Mininet(topo=topo, link=TCLink, controller=RemoteController("localhost", ip="localhost", port=6633))
    net.start()


    dumpNodeConnections(net.hosts)
    #net.pingAll()

    
	#Don't start the Mininet Client	
    #CLI(net)
    return net, network_graph


def heuristic_min_pow(network : Topo, G : nx.Graph, D : dict):


    D = D.copy()

    #first disable all links, we will now dinamically bring them up in responde with the demand 
    for (u,v,data) in G.edges(data=True):
        interfaces = data["interface"]
        #print(interfaces)
        disable_link(data)


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

            restore_link(link_data)

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



def disable_link(link):
    return
    interface = get_interfaces_from_link(link["interface"])

    if not is_host_interface(interface[0]):
        os.system("sudo ifconfig "+interface[0]+" down")

    if(interface[1]):
        if not is_host_interface(interface[1]):
            os.system("sudo ifconfig "+interface[1]+" down")

def restore_link(link):
    return
    interface = get_interfaces_from_link(link["interface"])


    if not is_host_interface(interface[0]):
        os.system("sudo ifconfig "+interface[0]+" up")

    if(interface[1]):
        if not is_host_interface(interface[1]):
            os.system("sudo ifconfig "+interface[1]+" up")

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


def compute_power_used(G: nx.Graph, power_per_switch : int = CONSUMPTION_PER_SWITCH, power_per_link : int = CONSUMPTION_PER_PORT):

    power = 0
    node_active = 0
    node_inactive = 0
    link_active = 0
    link_inactive = 0

    for node, data in G.nodes(data=True):
        #print(data)
        if data["active"]:
            power += data["active_power"]
            node_active += 1
        else:
            power += data["idle_power"]
            node_inactive += 1
        
    
    for h1, h2, data in G.edges(data=True):
        if data["active"]:
            power += data["power"]
            link_active += 1
        else:
            link_inactive += 1

    return round(power, 3), node_active, link_active,

def random_demand(G: nx.Graph, pairs =  10, demand_range = [5, 15]):

    demand_dict = {}

    hosts = []

    # for u in G.nodes:
    #     if is_host_interface(u):
    #         hosts.append(u)

    for node in G.nodes:
        if G.degree(node) == 1:
            hosts.append(node)

    no_hosts = len(hosts)

    if no_hosts == 0:
        no_hosts = len(G.nodes)
        hosts = list(G.nodes)

    #if no_hosts < pairs * 2:
    #    pairs = int(no_hosts / 2)
    
    pairs_generated = 0
    while pairs_generated < pairs:

        random_u = 0
        random_v = 0

        while random_u == random_v:
            random_u = random.randint(0, no_hosts-1)
            random_v = random.randint(0, no_hosts-1)

        random_u = hosts[random_u]
        random_v = hosts[random_v]
        random_demand = random.randint(demand_range[0], demand_range[1])


        if (random_u, random_v) in demand_dict:
            continue

        demand_dict[(random_u, random_v)] = random_demand
        pairs_generated += 1

    return demand_dict


if __name__ == "__main__":

    resdn_consumptions = []
    minpow_consumptions = []


  
    jellyfish_adj = [
        [0,4],[0,9],[0,17],[0,23],[0,26],[1,15],[1,18],[1,21],[1,22],[1,27],[2,8],[2,11],
        [2,20],[2,22],[2,28],[3,14],[3,18],[3,19],[3,21],[3,29],[4,9],[4,15],[4,24],[4,30],
        [5,6],[5,8],[5,14],[5,19],[5,31],[6,7],[6,8],[6,19],[6,32],[7,11],[7,20],[7,22],
        [7,33],[8,25],[8,34],[9,15],[9,16],[9,35],[10,12],[10,13],[10,23],[10,25],[10,36],
        [11,13],[11,17],[11,37],[12,19],[12,21],[12,22],[12,38],[13,16],[13,23],[13,39],
        [14,15],[14,24],[14,40],[15,41],[16,18],[16,24],[16,42],[17,18],[17,25],[17,43],
        [18,44],[19,45],[20,23],[20,25],[20,46],[21,24],[21,47],[22,48],[23,49],[24,50],[25,51]
    ]

    fattree_adj = [
        [0,2],[0,3],[1,2],[1,3],[2,16],[2,17],[3,18],[3,19],[4,6],[4,7],[5,6],[5,7],
        [6,16],[6,17],[7,18],[7,19],[8,10],[8,11],[9,10],[9,11],[10,16],[10,17],[11,18],
        [11,19],[12,14],[12,15],[13,14],[13,15],[14,16],[14,17],[15,18],[15,19]
    ]

    nodes, adj, cap =  load_totem_topology("./geant/topology-anonymised.xml")
    #case = "IntraTM-2005-01-01-00-34.xml"
    #demand_pairs, demand_values = load_demand(f'./geant/traffic-matrices/{case}')
    #D = {}
    #for pair_ind in range(len(demand_pairs)):
    #    u = demand_pairs[pair_ind][0]
    #    v = demand_pairs[pair_ind][1]
    #    D[("s%s"%u, "s%s"%v)] = demand_values[pair_ind]


    #print(len(D))


    timestamp = 0
    #nodes = range(0, 3)

    while timestamp < 100:
        

        D = {}
        resdn_consumptions = []
        resdn_dumb_consumptions = []
        minpow_consumptions = []

        resdn_times = []
        minpow_times = []
        timestamp += 1

        while len(D) < 20:

            network_graph = nx.read_edgelist('data/fat_tree.edgelist')


            new_demand_ok = False
            while not new_demand_ok:
                new_elements = random_demand(network_graph, 2)
                new_demand_ok = True
                for key, val in new_elements.items():
                    if key in D:
                        new_demand_ok = False
                        break 
            D.update(new_elements)

            if len(D) % 2 == 1:
                print("ERROR")
                raise Exception("ERROR")

            print(len(D))

            consumptions = {}
            umin = 0.1
            new_link_data =  {}

            for l0, l1 in network_graph.edges():
                network_graph[l0][l1]["bandwidth"] = 100
                network_graph[l0][l1]["used_bandwidth"] = 0
                network_graph[l0][l1]["power"] = 0.42
                network_graph[l0][l1]["active"] = False
                network_graph[l0][l1]["interface"] = ""

            nx.set_node_attributes(network_graph, 31.69, "active_power")
            nx.set_node_attributes(network_graph, 7, "idle_power")
            nx.set_node_attributes(network_graph, False, "active")


            #network, network_graph = jellyfish()
            network_graph_copy = network_graph.copy()
            

            start = time()
            network_graph_copy = maxRESDN(network_graph_copy, D, umin = umin)
            maxresdn_time = time() - start
            resdn_times += [maxresdn_time]
            #nx.set_node_attributes(network_graph_copy, True, "active")

            consumptions[round(umin, 2)] = compute_power_used(network_graph_copy)


            network_graph_resdn_dumb = network_graph_copy.copy()
            for node in network_graph_resdn_dumb.nodes():
                network_graph_resdn_dumb.nodes[node]["active"] = True


            resdn_dumb_consumptions += [compute_power_used(network_graph_resdn_dumb)]

            best_umin = min(consumptions, key=consumptions.get)
            print("RESDN:")
            print("Umin: %s" % umin)
            print(compute_power_used(network_graph_copy))

            resdn_consumptions += [compute_power_used(network_graph_copy)]


            #network = Mininet(topo=topo, link=TCLink, controller=RemoteController("localhost", ip="localhost", port=6633))
            #network.start()
            print("MinPow")
            start = time()
            heuristic_min_pow(None, network_graph, D)
            min_pow_time = time() - start

            minpow_times += [min_pow_time]

            print(compute_power_used(network_graph))
            minpow_consumptions += [compute_power_used(network_graph)]

            #network.stop()
        #os.system("sudo mn -c")



        with open('results/jellyfish/resdn_result_optimized_umin_0.1.txt', 'a') as f:
            for i in resdn_consumptions:
                print(i, end="\t", file=f)
            print(" ", file=f)


        with open('results/jellyfish/resdn_times.txt', 'a') as f:
            for i in resdn_times:
                print(i, end="\t", file=f)
            print(" ", file=f)



        with open('results/jellyfish/minpow_result.txt', 'a') as f:
            for i in minpow_consumptions:
                print(i, end="\t", file=f)
            print(" ", file=f)


        with open('results/jellyfish/minpow_times.txt', 'a') as f:
            for i in minpow_times:
                print(i, end="\t", file=f)
            print(" ", file=f)


        with open('results/jellyfish/resdn_result_dumb.txt', 'a') as f:
            for i in resdn_dumb_consumptions:
                print(i, end="\t", file=f)
            print(" ", file=f)


        

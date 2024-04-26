import os
import xml.etree.ElementTree as ET

def load_topology(path):
    with open(path) as f:
        lines = f.readlines()
    
    i = lines.index('NODES (\n')
    j = lines.index(')\n', i)
    nodes = lines[i+1:j]
    nodes = {node.strip().split(' ')[0]:i+1 for i, node in enumerate(nodes)}

    i = lines.index('LINKS (\n')
    j = lines.index(')\n', i)
    links = lines[i+1:j]
    links_origin = [nodes[link.strip().split(' ')[2]] for link in links]
    links_dest = [nodes[link.strip().split(' ')[3]] for link in links]
    link_cap = [int(float(link.strip().split(' ')[-3])*1000) for link in links]

    return nodes, links_origin, links_dest, link_cap

def load_nodes(path):
    with open(path) as f:
        lines = f.readlines()
    
    i = lines.index('NODES (\n')
    j = lines.index(')\n', i)
    nodes = lines[i+1:j]
    nodes = {i+1:node.strip().split(' ')[0] for i, node in enumerate(nodes)}

    return nodes

def load_totem_topology(path):
    nums = {}
    nums[1] = "ch1.ch"
    nums[2] = "uk1.uk"
    nums[3] = "it1.it"
    nums[4] = "ny1.ny"
    nums[5] = "si1.si"
    nums[6] = "lu1.lu"
    nums[7] = "fr1.fr"
    nums[8] = "hr1.hr"
    nums[9] = "hu1.hu"
    nums[10] = "de1.de"
    nums[11] = "gr1.gr"
    nums[12] = "se1.se"
    nums[13] = "nl1.nl"
    nums[14] = "il1.il"
    nums[15] = "sk1.sk"
    nums[16] = "at1.at"
    nums[17] = "de2.de"
    nums[18] = "pt1.pt"
    nums[19] = "be1.be"
    nums[20] = "cz1.cz"
    nums[21] = "es1.es"
    nums[22] = "pl1.pl"
    nums[23] = "ie1.ie"

    

    

    # Parse XML file
    
    tree = ET.parse(path)
    root = tree.getroot()
    nodes = root.find('topology').find('nodes').findall('node')
    nodes = sorted([int(node.get('id')) for node in nodes])
    edges = root.find('topology').find('links').findall('link')
    links = {}
    for edge in edges:
        link = sorted([int(edge.find('from').get('node')), int(edge.find('to').get('node'))])
        #print(list(edge))
        links[tuple(link)] = int(edge.find('capacity').get('value'))
    #print(len(links))

    edges = []
    caps = []

    for pair, cap in links.items():
        edges.append([pair[0]-1, pair[1]-1])
        caps.append(cap*2)

    return nodes, edges, caps

def load_capacities(path):
    with open(path) as f:
        lines = f.readlines()
    
    i = lines.index('LINKS (\n')
    j = lines.index(')\n', i)
    links = lines[i+1:j]
    link_cap = [int(float(link.strip().split(' ')[-3])*1000) for link in links]

    return link_cap

def load_demand(path):
    
    tree = ET.parse(path)
    demands = tree.getroot().find('IntraTM').findall('src')
    H = {}
    for source in demands:
        src = int(source.get('id'))
        for destination in source:
            dst = int(destination.get('id'))
            if src == dst:
                continue
            pair = tuple(sorted([src-1, dst-1]))
            H[pair] = H.setdefault(pair, 0) + int(float(destination.text))
    #print(H)
    edges = []
    demands = []
    for pair, demand in H.items():
        edges.append(pair)
        demands.append(demand)

    return edges, demands


def load_demand_cluster(path):
    with open(path) as f:
        lines = f.readlines()

    edges, demands = [], []
    for line in lines:
        line = line.strip().split(' ')
        edges.append((int(line[0]), int(line[1])))
        demands.append(int(line[2]))

    return edges, demands


if __name__ == '__main__':
    nodes, links, caps = load_totem_topology('topology-anonymised.xml')
    case = "IntraTM-2005-01-01-00-45.xml"
    H_edges, H_weights = load_demand(f'traffic-matrices/{case}')
    
    print(nodes)
    print(links)
    print(caps)
    
    print(H_edges)
    print(H_weights)
    
    exit(0)
    
'''
    cases = sorted(os.listdir('traffic-matrices/'))[:300]

    demands = []
    for t, case in enumerate(cases):
        demands += load_demand(f'dynamic_load_test/traffic-matrices/{case}', t+34)


    string_edges = '['
    string_cap = '['
    for link, cap in links.items():
        string_edges += f'{link[0]}, {link[1]}; '
        string_cap += f'{cap*2}, '
    string_edges = string_edges[:-2] + '];'
    string_cap = string_cap[:-2] + '];'

    with open('dynamic_load_test/out/edges.txt', 'w') as f:
        f.write(string_edges)
    with open('dynamic_load_test/out/cap.txt', 'w') as f:
        f.write(string_cap)

    string = ''
    for demand in demands:
        string += f'{demand[0]} {demand[1]} {demand[2]} {demand[3]} {demand[4]}\n'
    #string = string[:-2] + '];'
    with open('dynamic_load_test/out/H.txt', 'w') as f:
        f.write(string)

    #print(len(cases))
    #print(len(demands))
        

'''

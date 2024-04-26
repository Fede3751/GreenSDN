def load_big_demand(file, input_ts, demand_nodes, demands_cap = 230):

    D = {}

    demands_allocated = 0

    with open(file, "r") as f:
        for line in f:
            
            data = line.split()
            
            u =  int(data[0])
            v = int(data[1])
            demand = int(data[2])
            timestamp = int(data[3])

            if timestamp > input_ts or demands_allocated >= demands_cap:
                break

            if timestamp == input_ts:
                if demands_allocated < demands_cap and u in demand_nodes and v in demand_nodes:
                    demands_allocated += 1
                    if (f"s{u}", f"s{v}") in D:
                        D[(f"s{u}", f"s{v}")] += demand
                    else:
                        D[(f"s{u}", f"s{v}")] = demand


    return D
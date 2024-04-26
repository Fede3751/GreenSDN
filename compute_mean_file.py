import sys
from ast import literal_eval as make_tuple

with open(sys.argv[1]) as f:

    COLS = 10

    total_lines = 0
    total_data = [0]*COLS
    total_links = [0]*COLS
    for line in f:
        datas = line.split('\t')
        #print(datas)
        for i in range(COLS):    

            #print(datas)

            data = make_tuple(datas[i])
            power_consumption = float(data[0])
            links_used = data[2]

            print(power_consumption, end="\t")
            #print(links_used, end="\t")

            total_data[i] += power_consumption
            total_links[i] += links_used
        total_lines += 1

        print("")

    
    for i in range(len(total_data)):
        total_data[i] /= total_lines
        #print(round(total_data[i], 3), end=" ")

    print("")

    for i in range(len(total_data)):
        total_links[i] /= total_lines
        #print(round(total_links[i], 3), end=" ")

    #print("")
        
def makeGraphLista(list):
    graph = {}
    for item in range(0, len(list)-1):
        if item == 0:
            graph[list[item]] = [list[item+1]]
        elif item == len(list)-1:
            graph[list[item]] = [list[item-1]]
        else:
            graph[list[item]] = [list[item-1], list[item+1]]
            
    return graph


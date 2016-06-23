from collections import defaultdict
from heapq import *
import Parameter as Para
import numpy as np

def dijkstra(edges, f, t):
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))
    q, seen = [(0,f,())], set()
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)

            if v1 == t: return (cost, path)

            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost+c, v2, path))

    return (float("inf"),())

# get relative path, absolute_path = relative_path + start_point
def dijkstra_rela(cost_l, s, e, offset_x, offset_y, max_x, max_y):
    q, seen = [(0, s, ())], set([])
    path = ()
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = ((v1[0]+offset_x,v1[1]+offset_y), path)

            if v1[0] == e[0] and v1[1] == e[1]:
                return (cost, path)

            for index in range(0, 8):
                offset = Para.offset_list[index]
                v2 = (v1[0] + offset[0], v1[1] + offset[1])
                if v2[0] < 0 or v2[1] < 0 or v2[0] >= max_x or v2[1] >= max_y:
                    continue
                if v2 not in seen and cost_l[index][(np.floor(v2[0]/Para.RESCALE_SIZE),np.floor(v2[1]/Para.RESCALE_SIZE))] != np.inf:
                    heappush(q, (cost + cost_l[index][(np.floor(v2[0]/Para.RESCALE_SIZE),np.floor(v2[1]/Para.RESCALE_SIZE))], v2, path))

    return (np.inf, path)
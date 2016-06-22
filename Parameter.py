EXTEND_SEARCH_SIZE = 20     # extend search area within the block of (start_point, end_point)
MAX_PASSABLE_COLOR = 70     # points with larger grey value are not passable
PATH_EDGE_SIZE = 0          # use mean value of an area to represent color of a point
PROB_ENLAGRED_TIMES = 10    # enlarge the probability of a pixel being thin ice/cloud by XXX times
PIXEL_RATIO = 0             # the importance of of a pixel's gray level in calculating cost, and that of corresponding pixel's
                            # probability of thin ice/cloud is 1-XXX
INF_THRESHOLD = 0.6         # if the pixel's probability of being thick ice/cloud lager than it, then this pixel is infeasible

DIFF = 0.01                 # the accepted difference range between longitude and latitude

RESCALE_SIZE = 20           # rescale size

# offset_list = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
offset_list = [[20, 0], [-20, 0], [0, 20], [0, -20], [20, 20], [20, -20], [-20, 20], [-20, -20]]
dist_list = [1, 1, 1, 1, 1.414, 1.414, 1.414, 1.414]
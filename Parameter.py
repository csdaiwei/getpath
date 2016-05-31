EXTEND_SEARCH_SIZE = 10    # extend search area within the block of (start_point, end_point)
MAX_PASSABLE_COLOR = 70     # points with larger grey value are not passable
PATH_EDGE_SIZE = 0          # use mean value of an area to represent color of a point
PROB_ENLAGRED_TIMES = 10	# enlarge the probability of a pixel being thin ice/cloud by XXX times
PIXEL_RATIO = 0			# the importance of of a pixel's gray level in calculating cost, and that of corresponding pixel's
                            # probability of thin ice/cloud is 1-XXX
INF_THRESHOLD = 0.6			# if the pixel's probability of being thick ice/cloud lager than it, then this pixel is infeasible
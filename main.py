import pdb
import cv2
import numpy as np

from utils import *
from math import sqrt
from dijkstra_algorithm import dijkstra


input_file = "input.png"
output_file = "output.png"


def color2cost(color):
    return color + 1


def matrix2edge(matrix, start_point, end_point):
    edges = []
    x_search_area = [0, 0]
    y_search_area = [0, 0]
    reachable_set = set([])
    w, h = matrix.shape

    x_search_area[0] = min(start_point[0], end_point[0]) - 100
    x_search_area[1] = max(start_point[0], end_point[0]) + 100
    y_search_area[0] = min(start_point[1], end_point[1]) - 100
    y_search_area[1] = max(start_point[1], end_point[1]) + 100

    for x in range(x_search_area[0], x_search_area[1]):
        for y in range(y_search_area[0], y_search_area[1]):
            if matrix[x][y] < 30:
                reachable_set.add((x, y))

    offset_list = [[1, 0], [-1, 0], [0, 1], [0, -1],
              [1, 1], [1, -1], [-1, 1], [-1, -1]]

    for x in range(x_search_area[0], x_search_area[1]):
        for y in range(y_search_area[0], y_search_area[1]):
            for offset in offset_list:
                p1 = (x, y)
                p2 = (x+offset[0], y+offset[1])
                if p1 in reachable_set and p2 in reachable_set:
                    p1_index = coor2index(p1[0], p1[1], w)
                    p2_index = coor2index(p2[0], p2[1], w)

                    p1_color = matrix_mean(matrix, p1[0], p1[1], area=2)
                    p2_color = matrix_mean(matrix, p2[0], p2[1], area=2)

                    dist = sqrt(offset[0]**2 + offset[1]**2)
                    cost = (color2cost(p1_color) + color2cost(p2_color)) * dist

                    edges.append((p1_index, p2_index, cost))

    return edges


def paint_path(img, start_point, end_point, path):
    w, h = matrix.shape
    path_points = []
    while path != ():
        node, path = path
        path_points.append(index2coor(node, w))

    img = paint_img(img, path_points, [0, 255, 0], area=0)      # path as green
    img = paint_img(img, [start_point], [255, 0, 0], area=2)    # start point as red
    img = paint_img(img, [end_point], [0, 0, 255], area=2)      # end point as blue

    return img


if __name__ == '__main__':

    # read png
    img = cv2.imread(input_file)
    matrix = img[:, :, 0]           # modis images are grey
    w, h = matrix.shape
    print "load image %d * %d"%(w, h)

    # convert image to weighted graph
    start_point = (2100, 2700)
    end_point = (3200, 3245)

    edges = matrix2edge(matrix, start_point, end_point)
    print "convert image to graph"

    # call dijkstra to get shortest path
    start_index = coor2index(start_point[0], start_point[1], w)
    end_index = coor2index(end_point[0], end_point[1], w)
    cost, path = dijkstra(edges, start_index, end_index)
    print "get shortest path"

    # paint the path and save as png
    img = paint_path(img, start_point, end_point, path)
    cv2.imwrite(output_file, img)



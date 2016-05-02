import numpy as np


def paint_img(img, points, color, area=0):
    for p in points:
        x, y = p[0], p[1]
        img[x-area:(x+area+1), y-area:(y+area+1)] = color
    return img


def coor2index(i, j, w):
    return i*w + j


def index2coor(index, w):
    j = index % w
    i = (index-j)/w
    return i, j


def get_color(matrix, i, j, area):
    return np.mean(matrix[(i-area):(i+area+1), (j-area):(j+area+1)])


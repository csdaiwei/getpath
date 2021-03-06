#encoding:utf-8
import cv2      #todo: use PIL instead of cv2
import pickle
import numpy as np
import Parameter as Para

from math import sqrt
from PIL import Image
from dijkstra_algorithm import *
from collections import defaultdict
from heapq import *


class ModisMap:

    def __init__(self, inputfile, probfile):        # probfile records the probability of a pixel being sea, cloud or ice
        s = probfile.split('_')
        f = open(probfile,'rb')
        self.prob = pickle.load(f)
        # self.prob_y_start = int(s[-4])
        # self.prob_y_end = int(s[-3])
        # self.prob_x_start = int(s[-2])
        # self.prob_x_end = int(s[-1].split('.')[-2])
        self.img = cv2.imread(inputfile)
        # self.img = Image.open(inputfile)
        self.matrix = self.img[:, :, 0]           # modis images are grey
        # print(self.matrix.shape)
        self.w, self.h = self.matrix.shape
        self.start_point = (0, 0)
        self.end_point = (0, 0)
        self.is_set = False     #weather start point and end point is set,起点和终点是否被设置

        # the ratio that separate cost contributes to overall cost
        self.alpha = 1
        self.beta = 0

        #use a str to represent the target to optimize, the correspondence is as follows
        #时间：time, 油耗：fuel etc.
        self.target = None      # target to optimize，需要优化的目标

        self.safe_margin = None     #safe margin，安全距离
        self.feasible_set = None    #feasible set，可行域
        self.edges = None   #cost edges，为Dijkstra算法生成的边的集合


    # 初始化像素点的分布，在计算可行域、计算像素点的cost时会用到（暂时都用像素点的值来代替）
    # todo:to save time,it may invoke self.__get_search_area function fisrt, and then only initalize distribution of pixs in the feasible set
    def __init_distribution(self):
        """
        initalize distribution of each pix
        """
        print("initalize distribution")


    #   初始化像素点的速度和方向，在考虑到时间纬度时速度和方向的信息
    # todo:to save time, it may invoke self.__get_search_area function first, and then only initalize speed and direction of pixs in the feasible set
    # todo: what's more, since threre are only a few pixs in the image will move, so the result may be saved in sparse format, which will accelerate other functions
    def __init_speed_direction(self):
        """
        initalize speed and direction
        """
        print("initalize speed and direction")


    # 设置路径的起始点和终点
    def set_startend_point(self, start_point, end_point):
        #todo:safety check
        for p in start_point[0], end_point[0]:
            assert 0 < p < self.h
        for p in start_point[1], end_point[1]:
            assert 0 < p < self.w

        self.start_point = start_point
        self.end_point = end_point

        self.is_set = True


    # 设置路径的相对起始位置和终止位置
    def set_startend_position(self, start_position, end_position):
        #todo: safety check
        for p in start_position+end_position:
            assert 0 < p < 1
        # self.start_point = (int(start_position[1] * self.w), int(start_position[0] * self.h))
        # self.end_point = (int(end_position[1] * self.w), int(end_position[0] * self.h))

        self.start_point = (int(start_position[1] * self.w), int(start_position[0] * self.h))
        self.end_point = (int(end_position[1] * self.w), int(end_position[0] * self.h))
        print('start_point',self.start_point)
        print('end_point',self.end_point)
        self.is_set = True


    # 设置需要优化的目标，比如时间、油耗等等

    def set_target(self,target):

        self.target = target
        print("optimize target to be:"+target)


    # 设置安全距离，保证船行驶的安全
    def set_safe_margin(self,safe_margin):
        self.safe_margin = safe_margin
        self.risk_region = set([])
        for xx in range(0, int(self.safe_margin)+1):
            for yy in range(0, int(self.safe_margin)+1):
                self.risk_region.add((xx, yy))
                self.risk_region.add((xx, -yy))
                self.risk_region.add((-xx, yy))
                self.risk_region.add((-xx, -yy))
        print("safe margin is set to be:"+str(safe_margin))


    # 根据起点和终点，获取最终的路径
    # point is relative for both input and output
    def getpath(self):
        assert self.is_set

        path, cost = self.getpath_absolute()
        #img = self.paint_path(path)
        relative_path = [(p[1]/float(self.h), p[0]/float(self.w)) for p in path]

        #return relative_path, img
        return relative_path, cost


    # 根据起点和终点，获取最终的路径
    # point is absolute for both input and output
    def getpath_absolute(self):

        self.__init_distribution()
        self.__init_speed_direction()
        #self.__init_feasible_region()
        self.__init_infeasible_set()
        # self.__init_edge_cost()
        cost_l = self.__init_edge_cost()
        # todo:safe check , assert all the prerequisite conditions are initalized
        assert self.is_set
        assert self.target is not None
        assert self.safe_margin is not None
        #assert self.feasible_set is not None
        # assert not self.edges == []

        x_search_area,y_search_area = self.get_search_area()

        rela_s = (np.floor((self.start_point[0]-x_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE,
                  np.floor((self.start_point[1]-y_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE)
        rela_e = (np.floor((self.end_point[0]-x_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE,
                  np.floor((self.end_point[1]-y_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE)
        cost, path = dijkstra_rela(cost_l, rela_s, rela_e, x_search_area[0], y_search_area[0],
                                        x_search_area[1]-x_search_area[0], y_search_area[1]-y_search_area[0])

        # start_point = (np.floor((self.start_point[0]-x_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE + x_search_area[0],
        #                np.floor((self.start_point[1]-y_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE + y_search_area[0])
        # end_point = (np.floor((self.end_point[0]-x_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE + x_search_area[0],
        #              np.floor((self.end_point[1]-y_search_area[0])/Para.RESCALE_SIZE)*Para.RESCALE_SIZE + y_search_area[0])
        # start_index = self.__coor2index(start_point[0], start_point[1])
        # end_index = self.__coor2index(end_point[0], end_point[1])
        #
        # cost, path = dijkstra(self.edges, start_index, end_index)

        path_points = []
        while path != ():
            node, path = path
            # path_points.append(self.__index2coor(node))
            path_points.append(node)

        return path_points, cost

    def getpath_for_refresh(self):
        self.__init_distribution()
        self.__init_speed_direction()
        #self.__init_feasible_region()
        self.__init_infeasible_set()
        # self.__init_edge_cost()
        cost_l = self.__init_edge_cost()
        # todo:safe check , assert all the prerequisite conditions are initalized
        assert self.is_set
        assert self.target is not None
        assert self.safe_margin is not None
        #assert self.feasible_set is not None
        # assert not self.edges == []

        x_search_area,y_search_area = self.get_search_area()

        return cost_l, x_search_area,y_search_area

    # paint the path
    def paint_path(self, path_points):
        w, h = self.matrix.shape

        img = self.img
        img = self.__img_fill(img, path_points, [0, 255, 0], area=0)      # path as green
        img = self.__img_fill(img, [self.start_point], [0, 0, 255], area=2)    # start point as red
        img = self.__img_fill(img, [self.end_point], [255, 0, 0], area=2)      # end point as blue

        return img

    # judge whether a pixel is in the range of 'probability matrix'
    # def __is_in(self, x, y):
    #     return (x > self.prob_x_start and y > self.prob_y_start and x < self.prob_x_end and y < self.prob_y_end)

    # 判断一个点是否可达
    # todo: this function needs to be override
    #todo: distribution of pix, safe margin and other infomation may be needed
    def __is_feasible_pix(self, x, y):
        """
        :type x:int x cooridate of matrix,
        :type y:int y cooridate of matrix,
        :rtype:bool whether (x,y) is feasible

        """
        return self.matrix[x][y] < Para.MAX_PASSABLE_COLOR


    # 大致初始化一个的可行域
    # todo:this function needs to be refined, rectangle may not be the best shape to choose and EXTEND_SEARCH_SIZE should be set more cautiously
    def get_search_area(self):
        x_search_area = [0, 0]
        y_search_area = [0, 0]
        x_search_area[0] = min(self.start_point[0], self.end_point[0]) - Para.EXTEND_SEARCH_SIZE
        x_search_area[1] = max(self.start_point[0], self.end_point[0]) + Para.EXTEND_SEARCH_SIZE
        y_search_area[0] = min(self.start_point[1], self.end_point[1]) - Para.EXTEND_SEARCH_SIZE
        y_search_area[1] = max(self.start_point[1], self.end_point[1]) + Para.EXTEND_SEARCH_SIZE
        return x_search_area,y_search_area


    # find unreachable area
    def __init_infeasible_set(self):
        self.infeasible_set = set([])
        x_search_area,y_search_area = self.get_search_area()
        search_pros = self.prob[x_search_area[0]:x_search_area[1],y_search_area[0]:y_search_area[1],2]
        coor = np.nonzero(search_pros > Para.INF_THRESHOLD)
        coor_pair = np.dstack((coor[0], coor[1]))[0]
        offset = np.array(list(self.risk_region))
        result = coor_pair + offset[:,np.newaxis]
        l,w,h = result.shape
        result = result.reshape((l*w,h))
        temp_set = set(map(tuple, result))
        print('change set')
        self.infeasible_set = self.infeasible_set | temp_set
        # for x in range(x_search_area[0], x_search_area[1]):
        #     for y in range(y_search_area[0], y_search_area[1]):
        #         # if the pixel is not in the range of probability file
        #         # if not self.__is_in(x, y):
        #         #     if self.matrix[x][y] > Para.MAX_PASSABLE_COLOR:
        #         #         self.infeasible_set.add((x, y))
        #         # else:
        #             # if the probability of the pixel being thick ice/cloud larger than INF_THRESHOLD, then we treat this pixel as infeasible
        #             curr_pros = self.get_thick_ice_probability(x,y)
        #             # print(x,y,curr_pros)
        #             if curr_pros > Para.INF_THRESHOLD:
        #                 current_coor = np.array([x,y])
        #                 offset = np.array(list(self.risk_region))
        #                 # result = offset + current_coor
        #                 result = offset + current_coor - (x_search_area[0], y_search_area[0])       # relative infeasible set!!!!
        #                 self.infeasible_set = self.infeasible_set | (set(map(tuple, result)))
        print('infeasible len',len(self.infeasible_set))

    #初始化可行域，在后续初始化Dijkstra算法的边集时，可行域里面的点都是可达的，其余点都是不可达的
    def __init_feasible_region(self):
        """
        intialize feasible region
        :rtype:
        """
        x_search_area,y_search_area = self.get_search_area()
        self.feasible_set = set([])
        for x in range(x_search_area[0], x_search_area[1]):
            for y in range(y_search_area[0], y_search_area[1]):
                if(self.__is_feasible_pix(x, y)):
                    self.feasible_set.add((x, y))


    # 获取一个像素点在当前目标下的cost
    # todo：this function may need the distrbution of a pix, and we may also need a function which maps distribution to target cost.The function can be extrct from history data
    # todo: If we do not use the detifition of the pix point cost, we may need to change to algorithm a lot
    def __get_target_cost(self, cost):
        assert self.target is not None
        if self.target.encode('UTF-8')=="路程":
            return self.__dist_cost(cost)
        elif self.target.encode('UTF-8')=="破冰":
            return self.__ice_cost(cost)
        elif self.target.encode('UTF-8')=='时间':
            return self.__time_cost(cost)
        elif self.target == 'ratio':
            if self.alpha == 1.0:
                return self.__dist_cost(cost)
            if self.beta == 1.0:
                return self.__ice_cost(cost)
            cost_dist = self.__dist_cost(cost)
            cost_ice = self.__ice_cost(cost)
            cost_l = []
            for i in range(len(cost_dist)):
                cost_l.append(self.alpha*cost_dist[i]+self.beta*cost_ice[i])
            return cost_l

    def __dist_cost(self,cost):
        cost_l = []
        for index in range(0, 8):
            cost_l.append(cost + Para.dist_list[index] + Para.REGULARIZER)
        return cost_l

    def __ice_cost(self,cost):
        cost_l = []
        x_search_area,y_search_area = self.get_search_area()
        for index in range(0, 8):
            offset = Para.offset_list[index]
            temp_cost = 1 - self.prob[(x_search_area[0]+offset[0]):(x_search_area[1]+offset[0]):Para.RESCALE_SIZE,
                          (y_search_area[0]+offset[1]):(y_search_area[1]+offset[1]):Para.RESCALE_SIZE,0] + \
                        self.prob[(x_search_area[0]+offset[0]):(x_search_area[1]+offset[0]):Para.RESCALE_SIZE,
                          (y_search_area[0]+offset[1]):(y_search_area[1]+offset[1]):Para.RESCALE_SIZE,2]
            cost_l.append(temp_cost + cost + Para.REGULARIZER)
        return cost_l

    def __time_cost(self,cost):
        cost_l = []
        x_search_area,y_search_area = self.get_search_area()
        for index in range(0, 8):
            offset = Para.offset_list[index]
            temp_cost = 1 - self.prob[(x_search_area[0]+offset[0]):(x_search_area[1]+offset[0]):Para.RESCALE_SIZE,
                          (y_search_area[0]+offset[1]):(y_search_area[1]+offset[1]):Para.RESCALE_SIZE,0] + \
                        self.prob[(x_search_area[0]+offset[0]):(x_search_area[1]+offset[0]):Para.RESCALE_SIZE,
                          (y_search_area[0]+offset[1]):(y_search_area[1]+offset[1]):Para.RESCALE_SIZE,2]
            cost_l.append((temp_cost+cost)*Para.dist_list[index]/Para.ICE_SPEED + (1-(temp_cost+cost))*Para.dist_list[index]/Para.SEA_SPEED)
        return cost_l

    def get_sea_probability(self,x,y):
        # return self.prob[x-self.prob_x_start, y-self.prob_y_start, 0]
        return self.prob[x, y, 0]

    def get_thin_ice_probability(self,x,y):
        # return self.prob[x-self.prob_x_start, y-self.prob_y_start, 1]
        return self.prob[x, y, 1]

    def get_thick_ice_probability(self,x,y):
        # return self.prob[x-self.prob_x_start, y-self.prob_y_start, 2]
        return self.prob[x, y, 2]

    def __get_probability_by_point(self,point,index):
        # return self.prob[point[0]-self.prob_x_start, point[1]-self.prob_y_start, index]
        return self.prob[point[0], point[1], index]

    def get_sea_probability_by_point(self,point):
        return self.__get_probability_by_point(point,0)

    def get_thin_ice_probability_by_point(self,point):
        return self.__get_probability_by_point(point,1)

    def get_thick_ice_probability_by_point(self,point):
        return self.__get_probability_by_point(point,2)

    # 初始化边集
    def __init_edge_cost(self):
        """
        intialize cost of egdes
        """
        #assert self.feasible_set is not None
        x_search_area,y_search_area = self.get_search_area()
        self.edges = []
        # x_cor_range = np.zeros((len_y,len_x), dtype=int) + np.arange(x_search_area[0],x_search_area[1])
        # y_cor_range = (np.zeros((len_x,len_y), dtype=int) + np.arange(y_search_area[0],y_search_area[1])).transpose()
        # x_y_cor_range_c = np.dstack((x_cor_range, y_cor_range))     # current coordinate
        # x_y_cor_range = []
        # # get offset coordinate
        # for index in range(0, 8):
        #     x_y_cor_range.append(x_y_cor_range_c + np.array(Para.offset_list[index]))

        len_x = x_search_area[1] - x_search_area[0]
        len_y = y_search_area[1] - y_search_area[0]
        # cost_c = self.prob[x_search_area[0]:x_search_area[1],y_search_area[0]:y_search_area[1],2]
        cost_c = np.zeros((len_x, len_y))
        if len(self.infeasible_set) != 0:
            infeasible_set = list(self.infeasible_set)
            fun = lambda x : x[0] < len_x and x[1] < len_y
            infeasible_set = np.array(filter(fun,infeasible_set))
            cost_c[np.array(infeasible_set[:,0]), np.array(infeasible_set[:, 1])] = np.inf   # if a pixel is infeasible, then the cost to reach it is inf
        # cost_c = self.__get_target_cost(cost_c[0:len_x:Para.RESCALE_SIZE,0:len_y:Para.RESCALE_SIZE])
        cost_c = cost_c[0:len_x:Para.RESCALE_SIZE,0:len_y:Para.RESCALE_SIZE]
        return self.__get_target_cost(cost_c)


        # for x in range(x_search_area[0], x_search_area[1], Para.RESCALE_SIZE):
        #     for y in range(y_search_area[0], y_search_area[1], Para.RESCALE_SIZE):
        #         for index in range(0,8):
        #             offset = Para.offset_list[index]
        #             p1 = (x, y)
        #             p2 = (x+offset[0], y+offset[1])
        #             #if p1 in self.feasible_set and p2 in self.feasible_set:
        #             if p1 not in self.infeasible_set and p2 not in self.infeasible_set:
        #                 p1_index = self.__coor2index(p1[0], p1[1])
        #                 p2_index = self.__coor2index(p2[0], p2[1])
        #
        #                 # when calculating a pixel's cost, take its probability of being thin ice/cloud into consideration
        #                 # if not self.__is_in(p1[0], p1[1]):  #out of range
        #                 #     p1_cost = self.__get_target_cost(p1[0], p1[1])
        #                 # else:
        #                 p1_cost = Para.PIXEL_RATIO * self.__get_target_cost(p1[0], p1[1]) + \
        #                               (1-Para.PIXEL_RATIO) * self.get_thick_ice_probability_by_point(p1) * Para.PROB_ENLAGRED_TIMES
        #                 # if not self.__is_in(p2[0], p2[1]):
        #                 #     p2_cost = self.__get_target_cost(p2[0], p2[1])
        #                 # else:
        #                 p2_cost = Para.PIXEL_RATIO * self.__get_target_cost(p2[0], p2[1]) + \
        #                               (1-Para.PIXEL_RATIO) * self.get_thick_ice_probability_by_point(p2) * Para.PROB_ENLAGRED_TIMES
        #                 dist = Para.dist_list[index]
        #                 cost = (p1_cost+p2_cost) * dist
        #                 self.edges.append((p1_index, p2_index, cost))


    def __index2coor(self, index):
        j = index % self.w
        i = (index-j)/self.w
        return i, j


    def __coor2index(self, i, j):
        return i*self.w + j



    def __img_fill(self, img, points, color, area=0):
        for p in points:
            x, y = p[0], p[1]
            img[x-area:(x+area+1), y-area:(y+area+1)] = color
        return img
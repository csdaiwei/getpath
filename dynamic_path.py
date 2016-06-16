from getpath import *
import cv2
import copy
import Parameter
class DynamicPath(ModisMap):
    def __init__(self, inputfile, probfile):
        ModisMap.__init__(self, inputfile, probfile)
        self.ices = []

    # todo: intialize the speed and poision of ices
    # in practice, this procedure will be replaced by yuhang
    def __init_ices__(self):
        self.base_x = 1800
        self.base_y = 1800
        base_x = 1800
        base_y = 1800
        self.cut_img = self.get_part_img(base_x, 2600, base_y, 2600)
        start_x = 450 + base_x
        start_y = 150 + base_y
        # 600,200
        size = 200
        ice1 = {}
        ice2 = {}
        ice3 = {}
        # ice1
        for i in range(start_x + 100, start_x + size):
            for j in range(start_y, start_y + size):
                if self.matrix[i,j]>Parameter.MAX_PASSABLE_COLOR:
                    self.cut_img[i - base_x, j - base_y, :] = [0, 0, 255]
                    ice1[(i, j)] = [0, 1]
        # ice2
        for i in range(start_x, start_x + 100):
            for j in range(start_y, start_y + 100):
                if self.matrix[i,j]>Parameter.MAX_PASSABLE_COLOR:
                    self.cut_img[i - base_x, j - base_y, :] = [0, 255, 0]
                    ice2[(i, j)] = [1, 0]
        # ice3
        for i in range(start_x, start_x + 100):
            for j in range(start_y + 100, start_y + size):
                if self.matrix[i,j]>Parameter.MAX_PASSABLE_COLOR:
                    self.cut_img[i - base_x, j - base_y, :] = [255, 0, 0]
                    ice3[(i, j)] = [1, 1]
        self.ices.append(ice1)
        self.ices.append(ice2)
        self.ices.append(ice3)
        return self.cut_img
    # todo:given time interval, position and speed of old ice, calculate position of the new ice
    def cal_new_coor(self,interval, i, j,v):
        new_i = i + interval*v[0]
        new_j = j + interval*v[1]
        return new_i, new_j
    # todo:given time interval and speed of ice, calulate the new position of the ice
    # todo: return two lists, the first list makes up with old ice's positions, and the second list makes up with corresponding new ice's position
    def get_ice_correspondence(self, interval):
        old_ice_pixs = []
        new_ice_pixs = []
        new_ices = []
        for old_ice in self.ices:
            new_ice = {}
            for old_key in old_ice:
                i, j = old_key
                v = old_ice[old_key]
                # print(i, j, v)
                new_i, new_j = self.cal_new_coor(interval, i, j, old_ice[old_key])
                new_key = (new_i, new_j)
                new_ice[new_key] = v
                old_ice_pixs.append(old_key)
                new_ice_pixs.append(new_key)
            new_ices.append(new_ice)
        # print(len(new_ice_pixs))
        return old_ice_pixs, new_ice_pixs, new_ices
    # todo: set the prob distribution of position (x,y) of the img
    def set_pros(self,x,y,pros):
       self.prob[x-self.prob_x_start, y-self.prob_y_start, :] = pros
    # todo:get the prob distribution of position (x,y) of the img
    def get_pros(self,x,y,prob_copy):
        return prob_copy[x-self.prob_x_start, y-self.prob_y_start, :]
    # todo: given ice position(x,y), calculate the region affected by the ice
    def __get_infeasible_by_pix(self,x,y):
        current_coor = np.array([x,y])
        offset = np.array(list(self.risk_region))
        result = offset + current_coor
        # print(len((set(map(tuple, result)))))
        return  set(map(tuple, result))
    # todo: given a list of ice pixs, calculate the infeasible set
    def get_infeasible_set(self,ice_pixs):
        ice_infeasible_set = set([])
        for pix in ice_pixs:
            x,y = pix
            ice_infeasible_set = ice_infeasible_set | self.__get_infeasible_by_pix(x,y)
        return ice_infeasible_set
    # todo: given time interval, update the prob, matrix and img
    def update(self,interval):
        # get corrspending position of old ices and new ices
        old_ice_pixs, new_ice_pixs, new_ices = self.get_ice_correspondence(interval)
        self.ices = new_ices

        # deep copy the objects
        prob_copy = copy.deepcopy(self.prob)
        matrix_copy = copy.deepcopy(self.matrix)
        img_copy = copy.deepcopy(self.img)
        cut_img_copy = copy.deepcopy(self.cut_img)
        for old_pix,new_pix in zip(old_ice_pixs,new_ice_pixs):

            old_i,old_j = old_pix
            new_i,new_j = new_pix
            # we make an assumption that if ices moves, the place it resided should become sea
            #update pros
            pros = [1,0,0]
            self.set_pros(old_i,old_j,pros)
            old_pros = self.get_pros(old_i,old_j,prob_copy)
            self.set_pros(new_i,new_j,old_pros)
            # update matrix
            self.matrix[old_i,old_j] = 0
            self.matrix[new_i,new_j] = matrix_copy[old_i,old_j]
            # update img
            self.img[old_i,old_j,:]=[0,0,0]
            self.img[new_i,new_j,:] = img_copy[old_i,old_j]
            # update cut_img for visualization
            self.cut_img[old_i-self.base_x,old_j-self.base_y,:] = [0,0,0]
            self.cut_img[new_i-self.base_x,new_j-self.base_y,:] = cut_img_copy[old_i-self.base_x,old_j-self.base_y,:]

    def get_part_img(self, start_x, end_x, start_y, end_y):
        return copy.deepcopy(self.img[start_x:end_x, start_y:end_y, :])
import os


directory = 'imgs/'
if not os.path.exists(directory):
    os.makedirs(directory)
inputfile = 'MOD02QKM.A2014005.2110.006.2014218155544_band1.jpg'
probfile = 'Pro_MOD02QKM.A2014005.2110.006.2014218155544_band1_90_5000_90_8000.txt'

# start point
start_point=(2500,1900)
# end point
end_point=(2300,2100)

# safe magin
margin = 5
# number of pixs the ship moved before recalculate the path
step = 10
# time interval to update the modis image
intervel = 1
dynamic_path = DynamicPath(inputfile, probfile)
dynamic_path.set_startend_point(start_point,end_point)
dynamic_path.set_safe_margin(margin)
dynamic_path.set_target('time')

# initialize the ices
dynamic_path.__init_ices__()
# record the
final_path = []
# img index
img_index = 0
while end_point not in final_path:

    path_points = dynamic_path.getpath_absolute()[::-1]
    current_path = path_points[:step]
    for point in current_path:
        final_path.append(point)

    print(current_path)
    for point in current_path[:-1]:
        x,y = point
        dynamic_path.cut_img[x-dynamic_path.base_x,y-dynamic_path.base_y] = [0,255,255]
    start_point = current_path[-1]
    dynamic_path.update(intervel)
    # update start point and end point
    dynamic_path.set_startend_point(start_point,end_point)
    img_index+=1
    cv2.imwrite(directory+'/cut_img'+str(img_index)+'.png',dynamic_path.cut_img)
    print('img'+str(img_index))

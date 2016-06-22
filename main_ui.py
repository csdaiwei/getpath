# encoding:utf-8

import pdb
import Tkinter as tk
import tkMessageBox
import numpy as np

from Tkinter import *
from getpath import ModisMap
from PIL import ImageTk, Image
from pyhdf.SD import SD, SDC
import Parameter as Para

from heapq import *

class MainWindow:
    def __init__(self, master):
        # self.inputfile = 'bright.png'
        self.inputfile = 'MOD02QKM.A2014005.2110.006.2014218155544_band1.jpg'
        self.probfile = 'Pro_MOD02QKM.A2014005.2110.006.2014218155544_band1_full.txt'
        self.hdffile = 'MOD02QKM.A2014005.2110.006.2014218155544.hdf'

        hdf = SD(self.hdffile, SDC.READ)
        self.longitude_matrix = hdf.select('Longitude').get().astype("double")
        self.latitude_matrix = hdf.select('Latitude').get().astype("double")
        # max_longitude = np.array(self.longitude_matrix).max()
        # min_longitude = np.array(self.longitude_matrix).min()
        # max_latitude = np.array(self.latitude_matrix).max()
        # min_latitude = np.array(self.latitude_matrix).min()
        # self.max_longitude = max_longitude if np.fabs(max_longitude - 180) > Para.DIFF else 180
        # self.min_longitude = min_longitude if np.fabs(min_longitude - (-180)) > Para.DIFF else -180
        # self.max_latitude = max_latitude if np.fabs(max_latitude - 90) > Para.DIFF else 90
        # self.min_latitude = min_latitude if np.fabs(min_latitude - (-90)) > Para.DIFF else -90

        self.model = ModisMap(self.inputfile, self.probfile)
        self.start_position = []
        self.end_position = []
        self.ask_position = []
        self.path = []

        self.canvas_start_point = None      #indexing canvas items
        self.canvas_end_point = None
        self.canvas_ask_point = None
        self.canvas_path = []
        self.canvas_geogrids = []
        self.show_geogrids = False
        self.click_canvas_to_set_start_point = True

        self.scale_level = [0.05, 0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2]
        self.current_scale = 1.0

        img = Image.open(self.inputfile)
        self.imtk = ImageTk.PhotoImage(img)

        # start to build ui elements
        # first of all, build main framework containing 3 frames
        # frame_left_top = tk.Frame(master, width=800, height=800)
        # frame_left_bottom = tk.Frame(master, width=800, height=60)
        # frame_right = tk.Frame(master, width=200, height=850)
        frame_left_top = tk.Frame(master, width=850, height=850)
        frame_left_bottom = tk.Frame(master, width=850, height=60)
        frame_right = tk.Frame(master, width=200, height=900)
        frame_left_top.grid(row=0, column=0, padx=2, pady=2)
        frame_left_bottom.grid(row=1, column=0, padx=2, pady=2)
        frame_right.grid(row=0, column=1, rowspan=2, padx=2, pady=2)

        # build frame left top
        # self.canvas = tk.Canvas(frame_left_top, width=800, height=800)
        self.canvas = tk.Canvas(frame_left_top, width=850, height=850)
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')

        self.rec = None
        self.text = None

        xbar = tk.Scrollbar(frame_left_top, orient=HORIZONTAL)
        xbar.config(command=self.canvas.xview)
        xbar.pack(side=BOTTOM, fill=X)

        ybar = tk.Scrollbar(frame_left_top)
        ybar.config(command=self.canvas.yview)
        ybar.pack(side=RIGHT, fill=Y)

        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.canvas.config(xscrollcommand=xbar.set)
        self.canvas.config(yscrollcommand=ybar.set)

        self.canvas.pack()

        # build frame left bottom
        b1 = tk.Radiobutton(frame_left_bottom, text="设置起点", value=1, command=self.__set_start_point_click)
        b1.select()
        b2 = tk.Radiobutton(frame_left_bottom, text="设置终点", value=2, command=self.__set_end_point_click)
        b3 = tk.Button(frame_left_bottom, text='更换modis图像', command=self.__open_filefolder)
        b4 = tk.Button(frame_left_bottom, text='显示/隐藏经纬网', command=self.__showhide_geogrids)
        self.b5 = tk.Button(frame_left_bottom, text='-', width=2, command=self.__zoomout)
        self.b6 = tk.Button(frame_left_bottom, text='+', width=2, command=self.__zoomin)
        b1.grid(row=0, column=0)
        b2.grid(row=0, column=1)
        b3.grid(row=0, column=2)
        b4.grid(row=0, column=3)
        self.b5.grid(row=0, column=5)
        self.b6.grid(row=0, column=7)

        blank = tk.Label(frame_left_bottom)
        blank.grid(row=0, column=4, padx=40)

        self.scale_text = tk.StringVar()
        self.scale_text.set('100%')
        scale_label = tk.Label(frame_left_bottom, textvariable=self.scale_text, width=6)
        scale_label.grid(row=0, column=6)

        # build frame right
        l1 = tk.Label(frame_right, text='起点经度')
        l2 = tk.Label(frame_right, text='起点纬度')
        l3 = tk.Label(frame_right, text='终点经度')
        l4 = tk.Label(frame_right, text='终点纬度')
        l5 = tk.Label(frame_right, text='最小间距')
        l6 = tk.Label(frame_right, text='优化目标')
        l7 = tk.Label(frame_right, text='查询经度')
        l8 = tk.Label(frame_right, text='查询纬度')
        l1.grid(row=0, column=0, pady=20)
        l2.grid(row=1, column=0, pady=20)
        l3.grid(row=2, column=0, pady=20)
        l4.grid(row=3, column=0, pady=20)
        l5.grid(row=4, column=0, pady=20)
        l6.grid(row=5, column=0, pady=20)
        l7.grid(row=8, column=0, pady=20)
        l8.grid(row=9, column=0, pady=20)

        self.e1 = tk.Entry(frame_right, width=10)
        self.e2 = tk.Entry(frame_right, width=10)
        self.e3 = tk.Entry(frame_right, width=10)
        self.e4 = tk.Entry(frame_right, width=10)
        self.e5 = tk.Entry(frame_right, width=10)
        self.e6 = tk.Entry(frame_right, width=10)
        self.e7 = tk.Entry(frame_right, width=10)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.e5.grid(row=4, column=1)
        self.e5.insert(0, "1")
        self.e6.grid(row=8, column=1)
        self.e7.grid(row=9, column=1)


        option_list = ['时间', '油耗', '路程']
        v = tk.StringVar(frame_right, option_list[0])
        om = tk.OptionMenu(frame_right, v, *option_list)
        om.config(width=9)
        om.grid(row=5, column=1)

        blank = tk.Label(frame_right, height=12)
        blank.grid(row=12)

        bgen = tk.Button(frame_right, command=self.__genpath, text='生成路径')
        bask = tk.Button(frame_right, command=self.__get_prob, text='查询')
        breset = tk.Button(frame_right, command=self.__reset, text='复位')
        bgen.grid(row=6, column=0, columnspan=2, pady=20)
        bask.grid(row=10, column=0, columnspan=2, pady=20)
        breset.grid(row=12, column=0, columnspan=2, pady=20)

        
        # callback bindings
        self.canvas.bind("<Button-1>", self.__canvas_click)
        self.canvas.bind("<Button-3>", self.__right_canvas_click)
        self.e1.bind('<Tab>' or '<Leave>' or '<Return>', self.__start_point_change)
        self.e2.bind('<Tab>' or '<Leave>' or '<Return>', self.__start_point_change)
        self.e3.bind('<Tab>' or '<Leave>' or '<Return>', self.__end_point_change)
        self.e4.bind('<Tab>' or '<Leave>' or '<Return>', self.__end_point_change)
        self.e6.bind('<Tab>' or '<Leave>' or '<Return>', self.__ask_point_change)
        self.e7.bind('<Tab>' or '<Leave>' or '<Return>', self.__ask_point_change)

        self.__rescale(0.2)



    def __position_to_geocoordinates(self, x_position, y_position):
        assert self.longitude_matrix.shape == self.latitude_matrix.shape
        xlen, ylen = self.longitude_matrix.shape  #2030 1354
        
        x, y = int(y_position * xlen), int(x_position * ylen)
        longitude = self.longitude_matrix[x, y]
        latitude = self.latitude_matrix[x, y]
        
        return (longitude, latitude)

    def __geocoordinates_to_position(self, longitude, latitude):
        assert self.longitude_matrix.shape == self.latitude_matrix.shape

        lon_mat = self.longitude_matrix
        lat_mat = self.latitude_matrix
        xlen, ylen = lat_mat.shape  #2030 1354

        vset = set([])
        for x in range(1, xlen-1):
            lon = lon_mat[x, :]
            y = np.fabs(lon - longitude).argmin()
            if (lon - longitude)[y] < Para.DIFF:
                vset.add((x, y))
        
        if len(vset) == 0:
            # not found, raise error
            print 'longitude not found, vset 0'
            raise ValueError('longitude not found, vset 0')
            # return   #todo

        vlist = list(vset)
        lat = np.array([lat_mat[v[0], v[1]] for v in vlist])
        t = np.fabs(lat - latitude).argmin()
        
        if (lat - latitude)[t] > Para.DIFF:
            #not found , raise error
            print 'latitude not found'
            raise ValueError('longitude not found, vset 0')
            # return #todo

        x, y = vlist[t]
        x_position, y_position = float(y)/ylen, float(x)/xlen
        
        return x_position, y_position


    def __draw_geogrid(self):

        if self.canvas_geogrids != []:
            for g in self.canvas_geogrids:
                self.__delete_canvas_item(g)
            self.canvas_geogrids = []

        lon_mat = self.longitude_matrix
        lat_mat = self.latitude_matrix

        xlen, ylen = lat_mat.shape  #2030 1354
        s = self.current_scale

        #todo : generate v from range of lon_mat/lat_mat

        # draw latitude lines
        for v in [-60, -65, -70, -75]:
            line_points = []
            for y in range(0, ylen):
                if y%10 != 0:
                    continue
                lat = lat_mat[:, y]
                x = np.fabs(lat - v).argmin()
                if x > 0 and x < xlen-1:
                    line_points.append((4*x, 4*y)) #8120 5416

            for i in range(0, len(line_points)-1):
                cx, cy = line_points[i]
                nx, ny = line_points[i+1]
                g = self.canvas.create_line(s*cy, s*cx, s*ny, s*nx, fill='yellow', width=1.5)  # x y different between matrix and canvas
                self.canvas_geogrids.append(g)


        # draw longitude lines
        for v in [140, 150, 160, 170, 180, -170, -160, -150]:
            line_points = []
            for x in range(0, xlen):
                if x%10 != 0:
                    continue
                lon = lon_mat[x, :]
                y = np.fabs(lon - v).argmin()
                if y > 0 and y < ylen-1:
                    line_points.append((4*x, 4*y)) #8120 5416

            for i in range(0, len(line_points)-1):
                cx, cy = line_points[i]
                nx, ny = line_points[i+1]
                g = self.canvas.create_line(s*cy, s*cx, s*ny, s*nx, fill='yellow', width=1.5)  # x y different between matrix and canvas
                self.canvas_geogrids.append(g)

        #self.show_geogrids = True
        

    def __draw_start_point(self):

        if self.start_position == []:
            return

        self.__delete_canvas_item(self.canvas_start_point)  # delete old and draw new
        x, y = int(self.start_position[0] * self.imtk.width()), int(self.start_position[1] * self.imtk.height())
        self.canvas_start_point = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='red')

    def __draw_end_point(self):

        if self.end_position == []:
            return

        self.__delete_canvas_item(self.canvas_end_point)  # delete old and draw new
        x, y = int(self.end_position[0] * self.imtk.width()), int(self.end_position[1] * self.imtk.height())
        self.canvas_end_point = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='blue')

    def __draw_ask_point(self):

        if self.ask_position == []:
            return

        self.__delete_canvas_item(self.canvas_ask_point)  # delete old and draw new
        x, y = int(self.ask_position[0] * self.imtk.width()), int(self.ask_position[1] * self.imtk.height())
        self.canvas_ask_point = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='green')


    def __draw_path(self):
        print('-----------draw-------------')
        for canvas_path_point in self.canvas_path:
            self.__delete_canvas_item(canvas_path_point)
        self.canvas_path = []

        for i in range(len(self.path) - 1):
            current_position, next_position = self.path[i], self.path[i + 1]
            current_x, current_y = current_position[0] * self.imtk.width(), current_position[1] * self.imtk.height()
            next_x, next_y = next_position[0] * self.imtk.width(), next_position[1] * self.imtk.height()
            canvas_path_point = self.canvas.create_line(current_x, current_y, next_x, next_y, fill='green')
            self.canvas_path.append(canvas_path_point)


    def __delete_canvas_item(self, item):
        if item is not None:
            self.canvas.delete(item)

    # rescale canvas
    def __rescale(self, new_scale):
        self.current_scale = new_scale
        self.scale_text.set('%d' % (new_scale * 100) + '%')

        img = Image.open(self.inputfile)
        new_size = (int(img.size[0] * new_scale), int(img.size[1] * new_scale))
        self.imtk = ImageTk.PhotoImage(img.resize(new_size, Image.ANTIALIAS))
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')
        self.canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

        self.__draw_start_point()
        self.__draw_end_point()
        self.__draw_ask_point()
        self.__draw_path()
        self.__get_prob()
        if self.show_geogrids:
            self.__draw_geogrid()



    # callback functions below

    def __set_start_point_click(self):
        self.click_canvas_to_set_start_point = True

    def __set_end_point_click(self):
        self.click_canvas_to_set_start_point = False

    def __start_point_change(self, event):
        try:
            longitude = float(self.e1.get())
            # if longitude > self.max_longitude or longitude < self.min_longitude:
            #     tkMessageBox.showerror('Wrong','Out of range!')
            #     pass
        except:
            if self.e1.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        try:
            latitude = float(self.e2.get())
            # if latitude > self.max_latitude or latitude < self.min_latitude:
            #     tkMessageBox.showerror('Wrong','Out of range!')
            #     pass
        except:
            if self.e2.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        # else:
        #     x_position, y_position = self.__geocoordinates_to_position(longitude, latitude)
        #     self.start_position = (x_position, y_position)
        #     self.__draw_start_point()
        try:
            x_position, y_position = self.__geocoordinates_to_position(longitude, latitude)
        except:
            tkMessageBox.showerror('Wrong','Out of range!')
            pass
        else:
            self.start_position = (x_position, y_position)
            self.__draw_start_point()

    def __end_point_change(self, event):
        try:
            longitude = float(self.e3.get())
        except:
            if self.e3.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        try:
            latitude = float(self.e4.get())
        except:
            if self.e4.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        try:
            x_position, y_position = self.__geocoordinates_to_position(longitude, latitude)
        except:
            tkMessageBox.showerror('Wrong','Out of range!')
            pass
        else:
            self.end_position = (x_position, y_position)
            self.__draw_end_point()

    def __ask_point_change(self, event):
        try:
            longitude = float(self.e6.get())
        except:
            if self.e6.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        try:
            latitude = float(self.e7.get())
        except:
            if self.e7.get() != "":
                tkMessageBox.showerror('Wrong','Invalid Input!')
            pass
        try:
            x_position, y_position = self.__geocoordinates_to_position(longitude, latitude)
        except:
            tkMessageBox.showerror('Wrong','Out of range!')
            pass
        else:
            self.ask_position = (x_position, y_position)
            self.__draw_ask_point()

    def __show_prob(self, x_cor, y_cor, x_position):
        prob_cotent = 'sea: ' + "{:.3f}".format(self.model.get_sea_probability(x_cor, y_cor)) + '\n' + \
            'thin ice/cloud: ' + "{:.3f}".format(self.model.get_thin_ice_probability(x_cor, y_cor)) + '\n' + \
            'thick ice/cloud: ' + "{:.3f}".format(self.model.get_thick_ice_probability(x_cor, y_cor))

        self.__delete_canvas_item(self.rec)
        self.__delete_canvas_item(self.text)
        x = self.ask_position[0]*self.imtk.width()
        y = self.ask_position[1]*self.imtk.height()
        self.rec = self.canvas.create_rectangle(x, y, x+200, y+60, outline="white", fill="white")
        self.text = self.canvas.create_text(x, y+30, anchor=W, font="Purisa", text=prob_cotent)

        print('sea: ', self.model.get_sea_probability(x_cor, y_cor))
        print('thin ice: ', self.model.get_thin_ice_probability(x_cor, y_cor))
        print('thick ice: ', self.model.get_thick_ice_probability(x_cor, y_cor))

    def __get_prob(self):
        if self.ask_position == []:
            return

        x_cor = self.ask_position[1] * self.model.w
        y_cor = self.ask_position[0] * self.model.h

        self.__show_prob(x_cor, y_cor, self.ask_position[0])

    # canvas click event
    def __canvas_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        x_position = float(x) / self.imtk.width()
        y_position = float(y) / self.imtk.height()

        if x_position >= 1 or y_position >= 1:
            return

        longitude, latitude = self.__position_to_geocoordinates(x_position, y_position)

        if self.click_canvas_to_set_start_point:

            self.start_position = (x_position, y_position)
            self.__draw_start_point()

            self.e1.delete(0, 'end')
            self.e1.insert(0, str('%0.2f'%longitude))
            self.e2.delete(0, 'end')
            self.e2.insert(0, str('%0.2f'%latitude))
        else:
            self.end_position = (x_position, y_position)
            self.__draw_end_point()

            self.e3.delete(0, 'end')
            self.e3.insert(0, str('%0.2f'%longitude))
            self.e4.delete(0, 'end')
            self.e4.insert(0, str('%0.2f'%latitude))
            
    def __right_canvas_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        x_position = float(x) / self.imtk.width()
        y_position = float(y) / self.imtk.height()

        if x_position >= 1 or y_position >= 1:
            return

        self.ask_position = (x_position, y_position)

        longitude, latitude = self.__position_to_geocoordinates(x_position, y_position)

        self.__draw_ask_point()

        self.e6.delete(0, 'end')
        self.e6.insert(0, str('%0.2f'%longitude))
        self.e7.delete(0, 'end')
        self.e7.insert(0, str('%0.2f'%latitude))

        x_cor = y_position * self.model.w
        y_cor = x_position * self.model.h

        self.__show_prob(x_cor, y_cor, x_position)

    # callback of bgen
    def __genpath(self):

        # input check
        for i in range(0, 4):
            entries = [self.e1, self.e2, self.e3, self.e4]
            names = ['起点经度', '起点纬度', '终点经度', '终点纬度', '最小间距']
            s = entries[i].get()
            try:
                v = float(s)
                if not 0 < v < 1:
                    pass
                    #raise Exception()  #todo
            except:
                tkMessageBox.showerror('Error', names[i] + '输入错误')
                return

        # read input data
        #start_position = (float(self.e1.get()), float(self.e2.get()))
        #end_position = (float(self.e3.get()), float(self.e4.get()))
        start_position = self.start_position
        end_position = self.end_position
        margin = float(self.e5.get())

        self.model.set_startend_position(start_position, end_position)
        self.model.set_target("time")
        self.model.set_safe_margin(margin)
        self.path = self.model.getpath()
        print(len(self.path))

        try:
            self.path = self.model.getpath()
        except:
            tkMessageBox.showerror('Danger','Exception in find path')
        else:
            if len(self.path)==0:
                tkMessageBox.showerror('Danger','Unreachable place')
            else:
                self.__draw_path()
                print(len(self.path))

    def __genpath_for_refresh(self):
        # input check
        for i in range(0, 4):
            entries = [self.e1, self.e2, self.e3, self.e4]
            names = ['起点经度', '起点纬度', '终点经度', '终点纬度', '最小间距']
            s = entries[i].get()
            try:
                v = float(s)
                if not 0 < v < 1:
                    pass
                    #raise Exception()  #todo
            except:
                tkMessageBox.showerror('Error', names[i] + '输入错误')
                return

        start_position = self.start_position
        end_position = self.end_position
        margin = float(self.e5.get())

        self.model.set_startend_position(start_position, end_position)
        self.model.set_target("time")
        self.model.set_safe_margin(margin)
        cost_l, x_search_area,y_search_area = self.model.getpath_for_refresh()
        rela_s = (self.model.start_point[0]-x_search_area[0], self.model.start_point[1]-y_search_area[0])
        rela_e = (self.model.end_point[0]-x_search_area[0], self.model.end_point[1]-y_search_area[0])
        try:
            cost, path = self.dijkstra_rela(cost_l, rela_s, rela_e, x_search_area[0], y_search_area[0],
                                        x_search_area[1]-x_search_area[0], y_search_area[1]-y_search_area[0])
        except:
            tkMessageBox.showerror('Danger','Unreachable place')

    def __process_path(self, path):
        path_points = []
        while path != ():
            node, path = path
            # path_points.append(self.__index2coor(node))
            path_points.append(node)

        relative_path = [(p[1]/float(self.model.h), p[0]/float(self.model.w)) for p in path_points]

        return relative_path

    def dijkstra_rela(self, cost_l, s, e, offset_x, offset_y, max_x, max_y):          # get relative path, absolute_path = relative_path + start_point
        q, seen = [(0, s, ())], set([])
        old_s = s
        while q:
            (cost,v1,path) = heappop(q)
            if v1 not in seen:
                seen.add(v1)
                path = ((v1[0]+offset_x,v1[1]+offset_y), path)

                if np.fabs(v1[0]-old_s[0]) + np.fabs(v1[1]-old_s[1]) > 30:
                    old_s = v1
                    self.path = self.__process_path(path)
                    self.__draw_path()

                if v1[0] == e[0] and v1[1] == e[1]:
                    return (cost, path)

                for index in range(0, 8):
                    offset = Para.offset_list[index]
                    v2 = (v1[0] + offset[0], v1[1] + offset[1])
                    if v2[0] < 0 or v2[1] < 0 or v2[0] >= max_x or v2[1] >= max_y:
                        continue
                    if v2 not in seen and cost_l[index][v2] != np.inf:
                        heappush(q, (cost + cost_l[index][v2], v2, path))

        raise ValueError('Path not found. Infeasible!')

    # callback of breset
    def __reset(self):

        # clear input entries
        for e in [self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7]:
            e.delete(0, 'end')
        self.e5.insert(0, "1")

        self.start_position = []
        self.end_position = []

        # clear canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')

    def __zoomout(self):
        scale = self.current_scale
        index = self.scale_level.index(scale)
        assert index >= 1
        new_scale = self.scale_level[index - 1]
        self.__rescale(new_scale)

        if index - 1 == 0:
            self.b5.config(state='disabled')
        if index == len(self.scale_level) - 1:
            self.b6.config(state='normal')

    def __zoomin(self):
        scale = self.current_scale
        index = self.scale_level.index(scale)
        assert index <= len(self.scale_level) - 2
        new_scale = self.scale_level[index + 1]
        self.__rescale(new_scale)

        if index + 1 == len(self.scale_level) - 1:
            self.b6.config(state='disabled')
        if index == 0:
            self.b5.config(state='normal')

    def __open_filefolder(self):
        from tkFileDialog import askopenfilename
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        self.inputfile = filename
        print(filename)
        img = Image.open(self.inputfile)
        self.imtk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')

    def __showhide_geogrids(self):
        if self.show_geogrids:
            #hide
            for g in self.canvas_geogrids:
                self.__delete_canvas_item(g)
            self.canvas_geogrids = []
            self.show_geogrids = False
        else:
            #show
            self.__draw_geogrid()
            self.show_geogrids = True


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modis')
    root.resizable(width=False, height=False)

    window = MainWindow(root)

    root.mainloop()

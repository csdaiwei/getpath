# encoding:utf-8

import pdb
import Tkinter as tk
import tkMessageBox

from Tkinter import *
from getpath import ModisMap
from PIL import ImageTk, Image
from pyhdf.SD import SD, SDC


class MainWindow:
    def __init__(self, master):
        # self.inputfile = 'bright.png'
        self.inputfile = 'MOD02QKM.A2014005.2110.006.2014218155544_band1.jpg'
        self.probfile = 'Pro_MOD02QKM.A2014005.2110.006.2014218155544_band1_90_5000_90_8000.txt'
        self.hdffile = 'MOD02QKM.A2014005.2110.006.2014218155544.hdf'

        self.longitude_matrix = []
        self.latitide_matrix = []
        self.__init_geocoordinates()    #fill in above two matrix

        ##self.model = ModisMap(self.inputfile, self.probfile)
        self.start_position = []
        self.end_position = []
        self.path = []

        self.carvas_start_point = None      #indexing canvas items
        self.carvas_end_point = None
        self.carvas_path = []
        self.click_carvas_to_set_start_point = True

        self.scale_level = [0.05, 0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2]
        self.current_scale = 1.0

        img = Image.open(self.inputfile)
        self.imtk = ImageTk.PhotoImage(img)

        # start to build ui elements
        # first of all, build main framework containing 3 frames
        frame_left_top = tk.Frame(master, width=800, height=800)
        frame_left_bottom = tk.Frame(master, width=800, height=60)
        frame_right = tk.Frame(master, width=200, height=850)
        frame_left_top.grid(row=0, column=0, padx=2, pady=2)
        frame_left_bottom.grid(row=1, column=0, padx=2, pady=2)
        frame_right.grid(row=0, column=1, rowspan=2, padx=2, pady=2)

        # build frame left top
        self.canvas = tk.Canvas(frame_left_top, width=800, height=800)
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')

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
        b3 = tk.Button(frame_left_bottom, text='更换modis图像')
        b4 = tk.Button(frame_left_bottom, text='显示risk图片')
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
        l1.grid(row=0, column=0, pady=20)
        l2.grid(row=1, column=0, pady=20)
        l3.grid(row=2, column=0, pady=20)
        l4.grid(row=3, column=0, pady=20)
        l5.grid(row=4, column=0, pady=20)
        l6.grid(row=5, column=0, pady=20)

        self.e1 = tk.Entry(frame_right, width=10)
        self.e2 = tk.Entry(frame_right, width=10)
        self.e3 = tk.Entry(frame_right, width=10)
        self.e4 = tk.Entry(frame_right, width=10)
        self.e5 = tk.Entry(frame_right, width=10)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.e5.grid(row=4, column=1)
        self.e5.insert(0, "1")

        option_list = ['时间', '油耗', '路程']
        v = tk.StringVar(frame_right, option_list[0])
        om = tk.OptionMenu(frame_right, v, *option_list)
        om.config(width=9)
        om.grid(row=5, column=1)

        blank = tk.Label(frame_right, height=8)
        blank.grid(row=6)

        bgen = tk.Button(frame_right, command=self.__genpath, text='生成路径')
        breset = tk.Button(frame_right, command=self.__reset, text='复位')
        bgen.grid(row=7, column=0, columnspan=2, pady=20)
        breset.grid(row=8, column=0, columnspan=2, pady=20)

        
        # callback bindings
        self.canvas.bind("<Button-1>", self.__canvas_click)
        self.e1.bind('<Key>', self.__start_point_change)
        self.e2.bind('<Key>', self.__start_point_change)
        self.e3.bind('<Key>', self.__end_point_change)
        self.e4.bind('<Key>', self.__end_point_change)

        self.__rescale(0.2)


    def __init_geocoordinates(self):
        hdf = SD(self.hdffile, SDC.READ)
        longtitude_data = hdf.select('Longitude')
        latitude_data = hdf.select('Latitude')
        
        self.longitude_matrix = longtitude_data.get().astype("double")
        self.latitude_matrix = latitude_data.get().astype("double")

        self.__geocoordinates_range()


    def __position_to_geocoordinates(self, x_position, y_position):
        assert self.longitude_matrix.shape == self.latitude_matrix.shape
        
        x, y = int(y_position * self.longitude_matrix.shape[0]), int(x_position * self.longitude_matrix.shape[1])
        longitude = self.longitude_matrix[x, y]
        latitude = self.latitude_matrix[x, y]
        
        return (longitude, latitude)

    def __geocoordinates_to_position(self, longitude, latitude):
        # todo
        pass


    def __geocoordinates_range(self):
        lon_mat = self.longitude_matrix
        lat_mat = self.latitude_matrix


    def __draw_start_point(self):

        if self.start_position == []:
            return

        self.__delete_carvas_item(self.carvas_start_point)  # delete old and draw new
        x, y = int(self.start_position[0] * self.imtk.width()), int(self.start_position[1] * self.imtk.height())
        self.carvas_start_point = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='red')

    def __draw_end_point(self):

        if self.end_position == []:
            return

        self.__delete_carvas_item(self.carvas_end_point)  # delete old and draw new
        x, y = int(self.end_position[0] * self.imtk.width()), int(self.end_position[1] * self.imtk.height())
        self.carvas_end_point = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='blue')

    def __draw_path(self):

        for carvas_path_point in self.carvas_path:
            self.__delete_carvas_item(carvas_path_point)
        self.carvas_path = []

        for i in range(len(self.path) - 1):
            current_position, next_position = self.path[i], self.path[i + 1]
            current_x, current_y = current_position[0] * self.imtk.width(), current_position[1] * self.imtk.height()
            next_x, next_y = next_position[0] * self.imtk.width(), next_position[1] * self.imtk.height()
            carvas_path_point = self.canvas.create_line(current_x, current_y, next_x, next_y, fill='green')
            self.carvas_path.append(carvas_path_point)


    def __delete_carvas_item(self, item):
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
        self.__draw_path()



    # callback functions below

    def __set_start_point_click(self):
        self.click_carvas_to_set_start_point = True

    def __set_end_point_click(self):
        self.click_carvas_to_set_start_point = False

    def __start_point_change(self, event):
        try:
            self.__draw_start_point()   #todo
        except:
            pass

    def __end_point_change(self, event):
        try:
            self.__draw_end_point()     #todo 
        except:
            pass

    # canvas click event
    def __canvas_click(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        x_position = float(x) / self.imtk.width()
        y_position = float(y) / self.imtk.height()

        if x_position >= 1 or y_position >= 1:
            return

        longitude, latitude = self.__position_to_geocoordinates(x_position, y_position)

        if self.click_carvas_to_set_start_point:

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

        s = self.e5.get()
        # try:
        #   v = float(s)
        #   if not 0 <= v <= 5:
        #       raise Exception()
        # except :
        #   tkMessageBox.showerror('Error', '最小间距应在0-5范围内')
        #   return

        # no input error, continue

        # read input data
        #start_position = (float(self.e1.get()), float(self.e2.get()))
        #end_position = (float(self.e3.get()), float(self.e4.get()))
        start_position = self.start_position
        end_position = self.end_position
        margin = float(self.e5.get())

        #self.model.set_startend_position(start_position, end_position)
        #self.model.set_target("time")
        #self.model.set_safe_margin(margin)
        #self.path = self.model.getpath()
        # print(len(self.path))
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


    # callback of breset
    def __reset(self):

        # clear input entries
        for e in [self.e1, self.e2, self.e3, self.e4, self.e5]:
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


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modis')
    root.resizable(width=False, height=False)

    window = MainWindow(root)

    root.mainloop()

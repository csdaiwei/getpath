#encoding:utf-8

import pdb
#import cv2

import Tkinter as tk
from Tkinter import *
import tkMessageBox
from Tkinter import W, E, N, S

from getpath import ModisMap
from PIL import ImageTk, Image


class MainWindow:
	def __set_start_point_click(self):
		self.click_carvas_to_set_start_point = True
	def __set_end_point_click(self):
		self.click_carvas_to_set_start_point = False
	def __init__(self, master):
		self.v = StringVar()
		self.v.set("L")
		self.inputfile = 'bright.png'
		self.m = ModisMap(self.inputfile)
		self.size = 800		#display image size

		self.carvas_start_point = None
		self.carvas_end_point = None
		self.carvas_path = []
		self.click_carvas_to_set_start_point = True
		self.model = ModisMap(self.inputfile)

		frame_left_top = tk.Frame(master, width=800, height=800)
		frame_left_bottom = tk.Frame(master, width=800, height=50)
		frame_right = tk.Frame(master, width=200, height=850)
		frame_left_top.grid(row=0, column=0, padx=2, pady=2)
		frame_left_bottom.grid(row=1, column=0, padx=2, pady=2)
		frame_right.grid(row=0, column=1, rowspan=2, padx=2, pady=2)
		
		# frame left top
		img = Image.open(self.inputfile)
		self.imtk = ImageTk.PhotoImage(img.resize((self.size, self.size), Image.ANTIALIAS))
		self.canvas = tk.Canvas(frame_left_top, width=self.size, height=self.size)
		self.canvas.create_image(self.size/2, self.size/2, image = self.imtk)
		self.canvas.bind("<Button-1>", self.__canvas_click)
		self.canvas.pack()



		b1 = tk.Radiobutton(frame_left_bottom, text="点击设置起点", variable=self.v, value=1,command=self.__set_start_point_click)
		b1.select()
		b2 = tk.Radiobutton(frame_left_bottom, text="点击设置终点", variable=self.v, value=2,command=self.__set_end_point_click)
		b3 = tk.Button(frame_left_bottom, text='点击更换modis图像')
		b4 = tk.Button(frame_left_bottom, text='点击显示risk图片')
		b5 = tk.Button(frame_left_bottom, text='其他功能')
		b1.grid(row=0, column=0)
		b2.grid(row=0, column=1)
		b3.grid(row=0, column=2)
		b4.grid(row=0, column=3)
		b5.grid(row=0, column=4)

		# frame right
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
		self.e5.insert(0,"1")

		v = tk.StringVar(frame_right)
		om = tk.OptionMenu(frame_right, v, '时间', '油耗', '路程')
		om.config(width=9)
		om.grid(row=5, column=1)

		# Radiobutton(frame_left_bottom, text="点击设置起点", variable=self.v, value=1,command=self.__set_start_point_click)



		blank = tk.Label(frame_right, height=8)
		blank.grid(row=6)

		bgen = tk.Button(frame_right, command=self.__genpath,text='生成路径')
		breset = tk.Button(frame_right, command=self.__reset, text='复位')
		bgen.grid(row=7, column=0, columnspan=2, pady=20)
		breset.grid(row=8, column=0, columnspan=2, pady=20)

		self.e1.bind('<Key>',self.__start_point_change)
		self.e2.bind('<Key>',self.__start_point_change)
		self.e3.bind('<Key>',self.__end_point_change)
		self.e4.bind('<Key>',self.__end_point_change)
	def __start_point_change(self,event):
		try:
			print(self.e1.get())
			print(self.e2.get())
			self.__draw_start_point()
		except:
			pass
	def __end_point_change(self,event):
		try:
			self.__draw_end_point()
		except:
			pass
	def __draw_start_point(self):
		self.__delete_start_point()
		start_position = (float(self.e1.get()), float(self.e2.get()))
		xs, ys = int(start_position[0]*self.size), int(start_position[1]*self.size)
		self.carvas_start_point = self.canvas.create_oval(xs-5, ys-5, xs+5, ys+5, fill='red')

	def __draw_end_point(self):
		self.__delete_end_point()
		end_position = (float(self.e3.get()), float(self.e4.get()))
		xe, ye = int(end_position[0]*self.size), int(end_position[1]*self.size)
		self.carvas_end_point = self.canvas.create_oval(xe-5, ye-5, xe+5, ye+5, fill='blue')


	def __delete_carvas_point(self,point):
		if point is not None:
			self.canvas.delete(point)
	def __delete_start_point(self):
		self.__delete_carvas_point(self.carvas_start_point)
	def __delete_end_point(self):
		self.__delete_carvas_point(self.carvas_end_point)

	# canvas click event
	def __canvas_click(self,event):
		x, y = event.x, event.y
		self.start_position = (float(x)/self.size, float(y)/self.size)
		x_position = float(x)/self.size
		y_position = float(y)/self.size

		if self.click_carvas_to_set_start_point:
			self.e1.delete(0,'end')
			self.e1.insert(0,x_position)
			self.e2.delete(0,'end')
			self.e2.insert(0,y_position)
			self.__draw_start_point()
		else:
			self.e3.delete(0,'end')
			self.e3.insert(0,x_position)
			self.e4.delete(0,'end')
			self.e4.insert(0,y_position)
			self.__draw_end_point()
	def __delete_path(self):
		for carvas_path_point in self.carvas_path:
			self.__delete_carvas_point(carvas_path_point)
		self.carvas_path = []
	# callback of bgen
	def __genpath(self):
		
		# input check
		for i in range(0, 3):
			entries = [self.e1, self.e2, self.e3, self.e4]
			names = ['起点经度', '起点纬度', '终点经度', '终点纬度', '最小间距']
			s = entries[i].get()
			try:
				v = float(s)
				if not 0 < v < 1:
					raise Exception()
			except :
			 	tkMessageBox.showerror('Error', names[i]+'输入错误')
			 	return
		
		s = self.e5.get()
		try:
			v = float(s)
			if not 0 <= v <= 5:
				raise Exception()
		except :
			tkMessageBox.showerror('Error', '最小间距应在0-5范围内')
			return

		# no input error, continue

		# read input data
		start_position = (float(self.e1.get()), float(self.e2.get()))
		end_position = (float(self.e3.get()), float(self.e4.get()))
		margin = float(self.e5.get())


		self.model.set_startend_position(start_position, end_position)
		self.model.set_target("time")
		self.model.set_safe_margin(margin)
		self.path = self.model.getpath()
		self.__draw_path()

	def __draw_path(self):
		self.__delete_path()
		for i in range(len(self.path)-1):
			current_point = self.path[i]
			next_point = self.path[i+1]
			current_x,current_y  = current_point[0]*self.size,current_point[1]*self.size
			next_x,next_y = next_point[0]*self.size,next_point[1]*self.size
			carvas_path_point = self.canvas.create_oval(current_x, current_y, next_x, next_y, fill='green')
			self.carvas_path.append(carvas_path_point)
		# for p in self.path:
		# 	print(p)
		# 	x, y = p[0]*self.size, p[1]*self.size
		# 	carvas_path_point = self.canvas.create_oval(x, y, x+1, y+1, fill='green')
		# 	self.carvas_path.append(carvas_path_point)

			 

	# callback of breset
	def __reset(self):
		
		# clear input entries
		for e in [self.e1, self.e2, self.e3, self.e4, self.e5]:
			e.delete(0, 'end')

		# clear canvas
		self.canvas.delete("all")
		self.canvas.create_image(self.size/2, self.size/2, image = self.imtk)



if __name__ == '__main__':
	root = tk.Tk()
	root.title('Modis')
	root.geometry('1000x850')
	root.resizable(width=False, height=False)
	
	window = MainWindow(root)

	root.mainloop()

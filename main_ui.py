import pdb
#import cv2

import Tkinter as tk
import tkMessageBox
from Tkinter import W, E, N, S

#from getpath import ModisMap
from PIL import ImageTk, Image


class MainWindow:

	def __init__(self, master):
		
		self.inputfile = 'input.png'
		self.size = 800

		frame_left_top = tk.Frame(master, width=800, height=800)
		frame_left_bottom = tk.Frame(master, width=800, height=50)
		frame_right = tk.Frame(master, width=200, height=850)
		frame_left_top.grid(row=0, column=0, padx=2, pady=2)
		frame_left_bottom.grid(row=1, column=0, padx=2, pady=2)
		frame_right.grid(row=0, column=1, rowspan=2, padx=2, pady=2)
		
		img = Image.open(self.inputfile)
		self.imtk = ImageTk.PhotoImage(img.resize((self.size, self.size), Image.ANTIALIAS))
		w = tk.Canvas(frame_left_top, width=self.size, height=self.size)
		w.create_image(self.size/2, self.size/2, image = self.imtk)
		w.pack()

		l1 = tk.Label(frame_right, text='entry1')
		l2 = tk.Label(frame_right, text='entry2')
		l3 = tk.Label(frame_right, text='entry3')
		l4 = tk.Label(frame_right, text='entry4')
		l5 = tk.Label(frame_right, text='entry5')
		l1.grid(row=0, column=0, pady=20)
		l2.grid(row=1, column=0, pady=20)
		l3.grid(row=2, column=0, pady=20)
		l4.grid(row=3, column=0, pady=20)
		l5.grid(row=4, column=0, pady=20)

		e1 = tk.Entry(frame_right, width=10)
		e2 = tk.Entry(frame_right, width=10)
		e3 = tk.Entry(frame_right, width=10)
		e4 = tk.Entry(frame_right, width=10)
		e1.grid(row=0, column=1)
		e2.grid(row=1, column=1)
		e3.grid(row=2, column=1)
		e4.grid(row=3, column=1)

		v = tk.StringVar(frame_right)
		om = tk.OptionMenu(frame_right, v, 'option1', 'option2', 'option3')
		om.config(width=9)
		om.grid(row=4, column=1)


		b1 = tk.Button(frame_left_bottom, text='button1')
		b2 = tk.Button(frame_left_bottom, text='button2')
		b3 = tk.Button(frame_left_bottom, text='button3')
		b4 = tk.Button(frame_left_bottom, text='button4')
		b5 = tk.Button(frame_left_bottom, text='button5')
		b1.grid(row=0, column=0)
		b2.grid(row=0, column=1)
		b3.grid(row=0, column=2)
		b4.grid(row=0, column=3)
		b5.grid(row=0, column=4)

		'''
		self.img = Image.open(self.inputfile)
		self.imtk = ImageTk.PhotoImage(self.img.resize((self.size, self.size), Image.ANTIALIAS))
		self.w = tk.Canvas(master, width=self.size, height=self.size)
		self.w.create_image(self.size/2, self.size/2, image = self.imtk)

		self.w.grid(row=0, column=0, rowspan=6, columnspan=4)

		l1 = tk.Label(master, text='entry1')
		l2 = tk.Label(master, text='entry2')
		l3 = tk.Label(master, text='entry3')
		l4 = tk.Label(master, text='entry4')
		l1.grid(row=0, column=4)
		l2.grid(row=1, column=4)
		l3.grid(row=2, column=4)
		l4.grid(row=3, column=4)

		e1 = tk.Entry(master, width=15)
		e2 = tk.Entry(master, width=15)
		e3 = tk.Entry(master, width=15)
		e4 = tk.Entry(master, width=15)
		e1.grid(row=0, column=5)
		e2.grid(row=1, column=5)
		e3.grid(row=2, column=5)
		e4.grid(row=3, column=5)


		b1 = tk.Button(master, text='button1')
		b2 = tk.Button(master, text='button2')
		b3 = tk.Button(master, text='button3')
		b4 = tk.Button(master, text='button4')
		b5 = tk.Button(master, text='button5')
		b1.grid(row=6, column=0)
		b2.grid(row=6, column=1)
		b3.grid(row=6, column=2)
		b4.grid(row=6, column=3)
		b5.grid(row=6, column=4)

		#self.w.bind("<Button-1>", self.__callback)
		#self.click_indice = 0
		#self.start_position = (0.0, 0.0)
		#self.end_position = (0.0, 0.0)
	'''

	

	'''
	def __callback(self, event):
		x, y = event.x, event.y

		#print x, y
		
		if self.click_indice == 0:
			self.w.create_oval(x-5, y-5, x+5, y+5, fill='red')
			self.click_indice += 1
			self.start_position = (float(x)/self.size, float(y)/self.size)
		
		elif self.click_indice == 1:
			self.w.create_oval(x-5, y-5, x+5, y+5, fill='blue')
			self.click_indice += 1
			self.end_position = (float(x)/self.size, float(y)/self.size)

			if tkMessageBox.askokcancel(message='find path?'):
				print 'find path'
				#path =  self.__getpath(self.start_position, self.end_position)
				
				#for p in path:
				#	x, y = p[0]*self.size, p[1]*self.size
				#	self.w.create_oval(x, y, x+1, y+1, fill='green')
				


	def __getpath(self, start_position, end_position):
		pass
		#m = ModisMap(self.inputfile)
		#m.set_startend_position(start_position, end_position)
		#path, img =  m.getpath()
		#cv2.imwrite('out.png', img)
		#return path
	'''


if __name__ == '__main__':
	root = tk.Tk()
	root.title('Modis')
	root.geometry('1000x850')
	root.resizable(width=False, height=False)
	
	window = MainWindow(root)

	root.mainloop()

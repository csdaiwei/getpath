import pdb
#import cv2

import Tkinter as tk
import tkMessageBox

#from getpath import ModisMap
from PIL import ImageTk, Image


class MainWindow:

	def __init__(self, master):
		
		self.inputfile = 'input.png'
		self.size = 600
		
		self.img = Image.open(self.inputfile)
		self.imtk = ImageTk.PhotoImage(self.img.resize((self.size, self.size), Image.ANTIALIAS))
		self.w = tk.Canvas(master, width=self.size, height=self.size)
		self.w.create_image(self.size/2, self.size/2, image = self.imtk)
		#self.w = tk.Label(master)
		#self.w.image = self.imtk

		self.w.grid(row=0, column=0, rowspan=6, columnspan=6)

		l1 = tk.Label(master, text='qi dian')
		l2 = tk.Label(master, text='zhongdian')
		l1.grid(row=0, column=6)
		l2.grid(row=1, column=6)

		e1 = tk.Entry(master)
		e2 = tk.Entry(master)
		e1.grid(row=0, column=7)
		e2.grid(row=1, column=7)

		b1 = tk.Button(master, text='Zoom in')
		b2 = tk.Button(master, text='Zoom out')
		b3 = tk.Button(master, text='Update Modis')
		b4 = tk.Button(master, text='Update Start')
		b5 = tk.Button(master, text='Update Destination')
		b6 = tk.Button(master, text='Find Path')
		b1.grid(row=6, column=0)
		b2.grid(row=6, column=1)
		b3.grid(row=6, column=2)
		b4.grid(row=6, column=3)
		b5.grid(row=6, column=4)
		b6.grid(row=6, column=5)

		#self.w.bind("<Button-1>", self.__callback)
		#self.click_indice = 0
		#self.start_position = (0.0, 0.0)
		#self.end_position = (0.0, 0.0)

	

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
	
	window = MainWindow(root)

	root.mainloop()

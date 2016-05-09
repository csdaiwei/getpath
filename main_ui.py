import pdb
import cv2

import Tkinter as tk
import tkMessageBox

from getpath import ModisMap
from PIL import ImageTk, Image


class MainWindow:

	def __init__(self, master):
		
		self.inputfile = 'input.png'
		self.size = 900
		self.click_indice = 0
		self.start_position = (0.0, 0.0)
		self.end_position = (0.0, 0.0)

		self.img = Image.open(self.inputfile)
		self.imtk = ImageTk.PhotoImage(self.img.resize((self.size, self.size), Image.ANTIALIAS))
		self.w = tk.Canvas(master, width = self.size, height = self.size)
		self.w.create_image(self.size/2, self.size/2, image = self.imtk)
		self.w.bind("<Button-1>", self.__callback)
		self.w.pack()
	

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
				path =  self.__getpath(self.start_position, self.end_position)
				
				for p in path:
					x, y = p[0]*self.size, p[1]*self.size
					self.w.create_oval(x, y, x+1, y+1, fill='green')
				
				print 'ok'


	def __getpath(self, start_position, end_position):
		m = ModisMap(self.inputfile)
		path, img =  m.getpath(start_position, end_position)
		cv2.imwrite('out.png', img)
		return path


if __name__ == '__main__':
	root = tk.Tk()
	
	window = MainWindow(root)

	root.mainloop()

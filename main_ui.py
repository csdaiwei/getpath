import pdb

import Tkinter as tk

from PIL import ImageTk, Image


class MainWindow:
	def __init__(self, master):
		
		self.size = 900
		self.click_indice = 0
		self.start_position = (0.0, 0.0)
		self.end_position = (0.0, 0.0)

		self.img = Image.open('input.png')
		self.imtk = ImageTk.PhotoImage(self.img.resize((900, 900), Image.ANTIALIAS))
		self.w = tk.Canvas(master, width = 900, height = 900)
		self.w.create_image(450, 450, image = self.imtk)
		self.w.bind("<Button-1>", self.__callback)
		self.w.pack()
	
	def __callback(self, event):
		x, y = event.x, event.y
		
		if self.click_indice == 0:
			self.w.create_oval(x, y, x+10, y+10, fill='red')
			self.click_indice += 1
			self.start_position = (float(x)/size, float(y)/size)
		elif self.click_indice == 1:
			self.w.create_oval(x, y, x+10, y+10, fill='blue')
			self.click_indice += 1
			self.end_position = (float(x)/size, float(y)/size)


if __name__ == '__main__':
	root = tk.Tk()
	
	window = MainWindow(root)

	root.mainloop()

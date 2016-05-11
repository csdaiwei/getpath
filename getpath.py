import pdb
import cv2
import numpy as np

from math import sqrt
from dijkstra_algorithm import dijkstra


class ModisMap:
	

	EXTEND_SEARCH_SIZE = 100    # extend search area within the block of (start_point, end_point)
	MAX_PASSABLE_COLOR = 30     # points with larger grey value are not passable
	PATH_EDGE_SIZE = 0          # use mean value of an area to represent color of a point


	def __init__(self, inputfile):
		self.img = cv2.imread(inputfile)
		self.matrix = self.img[:, :, 0]           # modis images are grey
		self.w, self.h = self.matrix.shape
		self.start_point = (0, 0)
		self.end_point = (0, 0)
		self.is_set = False

	def set_startend_point(self, start_point, end_point):
		#todo: safety check
		self.start_point = start_point
		self.end_point = end_point
		self.is_set = True

	def set_startend_position(self, start_position, end_position):
		#todo: safety check
		self.start_point = (int(start_position[1] * self.w), int(start_position[0] * self.h))
		self.end_point = (int(end_position[1] * self.w), int(end_position[0] * self.h))
		self.is_set = True
	
	# get relative path
	def getpath(self):
		assert self.is_set

		path = self.getpath_absolute()
		img = self.paint_path(path)

		relative_path = [(p[1]/float(self.h), p[0]/float(self.w)) for p in path]

		return relative_path, img

	# point is absolute for both input and output
	def getpath_absolute(self):
		assert self.is_set

		# convert image to weighted graph 
		start_point = self.start_point
		end_point = self.end_point
		edges = self.__matrix2edge(start_point, end_point)

		# call dijkstra to get shortest path
		start_index = self.__coor2index(start_point[0], start_point[1])
		end_index = self.__coor2index(end_point[0], end_point[1])
		cost, path = dijkstra(edges, start_index, end_index)

		path_points = []
		while path != ():
			node, path = path
			path_points.append(self.__index2coor(node))

		return path_points

	def paint_path(self, path_points):
		w, h = self.matrix.shape
	
		img = self.img
		img = self.__img_fill(img, path_points, [0, 255, 0], area=0)      # path as green
		img = self.__img_fill(img, [self.start_point], [0, 0, 255], area=2)    # start point as red
		img = self.__img_fill(img, [self.end_point], [255, 0, 0], area=2)      # end point as blue

		return img


	def __matrix2edge(self, start_point, end_point):
		edges = []
		x_search_area = [0, 0]
		y_search_area = [0, 0]
		reachable_set = set([])
		w, h = self.matrix.shape

		x_search_area[0] = min(start_point[0], end_point[0]) - ModisMap.EXTEND_SEARCH_SIZE
		x_search_area[1] = max(start_point[0], end_point[0]) + ModisMap.EXTEND_SEARCH_SIZE
		y_search_area[0] = min(start_point[1], end_point[1]) - ModisMap.EXTEND_SEARCH_SIZE
		y_search_area[1] = max(start_point[1], end_point[1]) + ModisMap.EXTEND_SEARCH_SIZE

		for x in range(x_search_area[0], x_search_area[1]):
			for y in range(y_search_area[0], y_search_area[1]):
				if self.matrix[x][y] < ModisMap.MAX_PASSABLE_COLOR:
					reachable_set.add((x, y))

		offset_list = [[1, 0], [-1, 0], [0, 1], [0, -1],
				  [1, 1], [1, -1], [-1, 1], [-1, -1]]
		dist_list = [1, 1, 1, 1, 1.414, 1.414, 1.414, 1.414]

		for x in range(x_search_area[0], x_search_area[1]):
			for y in range(y_search_area[0], y_search_area[1]):
				for index in range(0,8):
					offset = offset_list[index]
					p1 = (x, y)
					p2 = (x+offset[0], y+offset[1])
					if p1 in reachable_set and p2 in reachable_set:
						p1_index = self.__coor2index(p1[0], p1[1])
						p2_index = self.__coor2index(p2[0], p2[1])

						p1_color = self.__matrix_mean(self.matrix, p1[0], p1[1], area=ModisMap.PATH_EDGE_SIZE)
						p2_color = self.__matrix_mean(self.matrix, p2[0], p2[1], area=ModisMap.PATH_EDGE_SIZE)
						
						dist = dist_list[index]
						cost = (self.__color2cost(p1_color) + self.__color2cost(p2_color)) * dist

						edges.append((p1_index, p2_index, cost))
		return edges


	def __color2cost(self, color):
		return color/5 + 1


	def __index2coor(self, index):
		j = index % self.w
		i = (index-j)/self.w
		return i, j


	def __coor2index(self, i, j):
		return i*self.w + j


	def __matrix_mean(self, matrix, i, j, area):
		return np.mean(matrix[(i-area):(i+area+1), (j-area):(j+area+1)])


	def __img_fill(self, img, points, color, area=0):
		for p in points:
			x, y = p[0], p[1]
			img[x-area:(x+area+1), y-area:(y+area+1)] = color
		return img


if __name__ == '__main__':
	
	m = ModisMap('input.png')

	start_point = (2100, 2700)
	end_point = (3200, 3245)
	
	path =  m.getpath_absolute(start_point, end_point)

	print 'convert to edges...'

	img = m.paint_path(start_point, end_point, path)

	print 'get shortest path...'

	cv2.imwrite('out.png', img)

	print 'save as out.png'
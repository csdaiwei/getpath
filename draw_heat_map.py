#encoding:utf-8
from getpath import *
import os
inputfile = 'MOD02QKM.A2014005.2110.006.2014218155544_band1.jpg'
probfile = 'Pro_MOD02QKM.A2014005.2110.006.2014218155544_band1_90_5000_90_8000.txt'


modis_map = ModisMap(inputfile=inputfile,probfile=probfile)

directory = 'risks/'
if not os.path.exists(directory):
    os.makedirs(directory)
c = 0
import cv2
# i，j为risk图的左上角坐标
# 画出边长为800的正方形
step = 800
for i in [0,800,1600,2400,3200,4000]:
    for j in [0,800,1600,2400,3200,4000]:
        x_start = i
        x_end =i+step
        y_start = j
        y_end = j+step
        # 采用厚冰概率画risk图
        thick_ice_prob_matrix = modis_map.prob[x_start:x_end,y_start:y_end,2]

        cut_img = modis_map.matrix[(x_start+90):(x_end+90),(y_start+90):(y_end+90)]

        # 原始图片
        cv2.imwrite('risks/'+'origin_'+str(i)+'_'+str(j)+'_.png',cut_img)
        import matplotlib.pyplot as plt

        plt.pcolor(thick_ice_prob_matrix,cmap='seismic', vmin=0, vmax=1)
        plt.axis('equal')
        plt.xlim([0,x_end-x_start])
        plt.ylim([0,y_end-y_start])
        plt.colorbar()
        # 保存热力图
        plt.savefig('risks/'+'risk_'+str(i)+'_'+str(j)+'_.png')
        plt.clf()



# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 22:21:29 2023

@author: magnn


Sur l'image ci dessous, effectuer un slicing pour ne garder que la moitié de l'image
 (en son centre) et remplacer tous les pixels > 150 par des pixels = 255
"""

from scipy import misc
import matplotlib.pyplot as plt
face = misc.face(gray=True)
plt.imshow(face, cmap=plt.cm.gray)
plt.show()
print(face.shape)


x, y = face.shape
zoom_face = face[x//8 : -x//8, y //8: -y//8] # redimensionner en divisant chaque dimension par 4 (division entiere)
zoom_face[zoom_face>180] = 255 # boolean indexing
plt.imshow(zoom_face, cmap=plt.cm.gray)
plt.show()


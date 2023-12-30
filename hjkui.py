# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 20:43:06 2023

@author: magnn
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

r = 5
r0 = 0.3

angle = np.arange(np.pi/2, -3*np.pi/2, -np.pi/360)
fig, ax = plt.subplots()
ax.set_aspect('equal')
circle, = ax.plot(r * np.cos(angle), r * np.sin(angle), 'k')

t = np.linspace(0, r * np.cos(angle[0]), 4)
z = np.linspace(0, r * np.sin(angle[0]), 4)
line, = ax.plot(t, z)

x =  r * np.cos(angle[0])
y = r * np.sin(angle[0])
point, = ax.plot(x, y, 'o')

def update(frame):
    x = r * np.cos(angle[frame])
    y = r * np.sin(angle[frame])
    t = np.linspace(0, r * np.cos(angle[frame]), 4)
    z = np.linspace(0, r * np.sin(angle[frame]), 4)
    
    point.set_data(x, y)
    line.set_data(t, z)
    
    return point, line,

ani = animation.FuncAnimation(fig, update, frames=len(angle), interval=50, blit=True)

plt.show()

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 21:26:06 2023

@author: magnn
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
x = np.linspace(0, 5, 10)
y= x**2

f=interp1d(x, y, kind='linear')
new_x=np.linspace(0,5,30)
result = f(new_x)
plt.scatter(x,y)
plt.scatter(new_x, result, c='r')
plt.show()
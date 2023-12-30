# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 22:08:30 2023

@author: magnn
"""

import tkinter as tk
from time import strftime

def time():
    string = strftime('%H:%M:%S %p')
    lbl.config(text=string)
    lbl.after(1000, time)

root = tk.Tk()
root.title('Clock')

lbl = tk.Label(root, font=('calibri', 40, 'bold'), background='black', foreground='white')
lbl.pack(anchor='center')

time()
root.mainloop()

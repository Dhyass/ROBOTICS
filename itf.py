# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 15:02:33 2023

@author: magnn
"""

import tkinter as tk

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Alignement des cadres")

        # Créer les cadres
        frame1 = tk.Frame(root, width=200, height=100, bg='red')
        frame2 = tk.Frame(root, width=200, height=100, bg='green')
        frame3 = tk.Frame(root, width=200, height=100, bg='blue')

        # Placer les cadres en utilisant la gestion de mise en page (pack)
        frame1.pack(side=tk.LEFT, padx=10, pady=10)
        frame2.pack(side=tk.LEFT, padx=10, pady=10)
        frame3.pack(side=tk.LEFT, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()

# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 22:50:30 2023

@author: magnn
"""


import time

import tkinter as tk
from tkinter import ttk
from time import strftime
import serial
import tkinter.messagebox as messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import math


Longueur_d1 = 8 # distance entre la premiere et la deuxieme articulations
Longeur_d5 = 60 # 

distance_a2 = 135
distance_a3=147
distance_a4=59.7 # distance entre la dernier articulation et le centre d'attaque de l'outil (longeur de l'effecteur)

cursor="hand2" # type de curseur
justify="center" # 



class RobotController:
    MIN_ANGLE = -180
    MAX_ANGLE = 180

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot Controller")
        self.root.configure(background="lime")
        
    
    
        #self.fig, self.ax0 = plt.subplots()
        self.fig = None
        self.ax0 = None
        
        self.error_history = []
        
        # Variable de drapeau pour indiquer si le processus doit être arrêté
        self.stop_process_flag = False
        
         # Création d'un style ttk
        style = ttk.Style()
        style.configure("My.TLabelframe", background="blue")
        
        # Initialiser les paramètres du PID
        self.kp = 0.1  # Gain proportionnel
        self.ki = 0.01  # Gain intégral
        self.kd = 0.01  # Gain dérivé

        # Initialiser les erreurs PID
        self.prev_error = [0, 0, 0, 0, 0]
        self.integral = [0, 0, 0, 0, 0]

        # Initialiser les positions cibles
        self.target_positions = [0, 0, 0, 0, 0]

        # Initialiser les positions actuelles
        self.current_positions = [0, 0, 0, 0, 0]

         # Section Menu
        bold_font = ('Helvetica', 11, 'bold')

        self.menu_frame = ttk.LabelFrame(self.root, text="ROBOT CONTROL", labelanchor="n", padding=(5, 5), style="My.TLabelframe")
        self.menu_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, ipady=1)
       
        self.btn_start = tk.Button(self.menu_frame, text="✔ START",  command=self.start_robot, background="lime", 
                                   font=bold_font, height=2, width=20, cursor=cursor )
        self.btn_stop = tk.Button(self.menu_frame, text="STOP", command=self.stop_robot, 
                                  font=bold_font, height=2, width=20, cursor=cursor)
        self.btn_quit = tk.Button(self.menu_frame, text="EXIT", command=self.quit, 
                                  font=bold_font, height=2, width=20, cursor=cursor)
        self.btn_home = tk.Button(self.menu_frame, text="Home",  command=self.start_update_pid_home,  
                                  font=bold_font, height=2, width=20, cursor=cursor)
        
        # Créer un bouton pour déclencher la mise à jour PID
        self.btn_pid = tk.Button(self.menu_frame, text="PID", command=self.start_update_pid, 
                                 font=bold_font, height=2, width=20, cursor=cursor)
        
        
       # Configuration des boutons avec des marges
        for i, btn in enumerate([self.btn_start, self.btn_stop, self.btn_quit, self.btn_home, self.btn_pid ]):
           btn.grid(row=0, column=i, padx=10, pady=10)
          
        #section commandes 
        self.var_frame = ttk.LabelFrame(self.root, text="COMMANDE", labelanchor="n", padding=(5, 5), style="My.TLabelframe")
        self.var_frame.grid(row=1, column=0, padx=10, pady=10)
          
        # parameters
        self.param_frame = ttk.LabelFrame(self.var_frame, text="PARAMETERS", padding=(10,10))
        self.param_frame.grid( row=0, column=1, padx=10, pady=10)
        
        
        # Tool 0rientation section (Rotation)
        self.tool_rotat_frame = ttk.LabelFrame(self.var_frame, text="Tool Orientation", padding=(10,10))
        self.tool_rotat_frame.grid( row=0, column=2, padx=10, pady=10)
        
        
        # normal vector
        self.normal_vector_frame = ttk.LabelFrame(self.tool_rotat_frame, text="NORMAL VECTOR", padding=(10,10))
        self.normal_vector_frame.grid( row=0, column=0, padx=10, pady=10)
    
        self.nx = tk.DoubleVar()
        self.nx.set(0.0)  # Initialize to the initial value of nx
        
        self.ny = tk.DoubleVar()
        self.ny.set(0.0)  # Initialize to the initial value of ny
        
        self.nz = tk.DoubleVar()
        self.nz.set(0.0)  # Initialize to the initial value of nz
        
        self.create_normal_vector_widgets()
        
        # sliper vector
        self.slider_vector_frame = ttk.LabelFrame(self.tool_rotat_frame, text="SLIDER VECTOR", padding=(10,10))
        self.slider_vector_frame.grid( row=1, column=0, padx=10, pady=10)
        
        self.sx = tk.DoubleVar()
        self.sx.set(0.0)  # Initialize to the initial value of sx
        
        self.sy = tk.DoubleVar()
        self.sy.set(0.0)  # Initialize to the initial value of sy
        
        self.sz = tk.DoubleVar()
        self.sz.set(0.0)  # Initialize to the initial value of sz
        self.create_slider_vector_widgets()
        
        #approach vector
        self.approach_vector_frame = ttk.LabelFrame(self.tool_rotat_frame, text="APPROACH VECTOR", padding=(10,10))
        self.approach_vector_frame.grid( row=2, column=0, padx=10, pady=10)
        
        self.ax = tk.DoubleVar()
        self.ax.set(0.0)  # Initialize to the initial value of ax
        
        self.ay = tk.DoubleVar()
        self.ay.set(0.0)  # Initialize to the initial value of ay
        
        self.az = tk.DoubleVar()
        self.az.set(0.0)  # Initialize to the initial value of ax
        
        self.create_approach_vector_widgets()
        
        # subsections angles
        self.sub_frame = ttk.LabelFrame(self.var_frame, text=" ", labelanchor="n", padding=(10, 10))
        self.sub_frame.grid(row=0, column=0, padx=10, pady=10)

        # Section Angles
        self.angles_frame = ttk.LabelFrame(self.sub_frame, text="JIONT ANGLES (Deg)", labelanchor="n", padding=(10, 10))
        self.angles_frame.grid(row=0, column=0, padx=10, pady=10)

        self.angle_j1 = tk.DoubleVar()
        self.angle_j1.set(0.0)  # Initialize to the initial value of J1

        self.angle_j2 = tk.DoubleVar()
        self.angle_j2.set(0.0)  # Initialize to the initial value of J2

        self.angle_j3 = tk.DoubleVar()
        self.angle_j3.set(0.0)  # Initialize to the initial value of J3
        
        self.angle_j4 = tk.DoubleVar()
        self.angle_j4.set(0.0)  # Initialize to the initial value of J1

        self.angle_j5 = tk.DoubleVar()
        self.angle_j5.set(0.0)  # Initialize to the initial value of J2


        self.create_angle_widgets()

        # Section Positions de l'Outil
        self.tool_frame = ttk.LabelFrame(self.param_frame, text="TOOL POSITION", labelanchor="n", padding=(10, 10))
        self.tool_frame.grid(row=0, column=0, padx=10, pady=10)

        self.x_value = tk.DoubleVar()
        self.x_value.set(0.0)  # Initialize to the initial value of x

        self.y_value = tk.DoubleVar()
        self.y_value.set(0.0)  # Initialize to the initial value of y

        self.z_value = tk.DoubleVar()
        self.z_value.set(0.0)  # Initialize to the initial value of z

        self.create_tool_widgets()
    

        # Section Vitesses
        self.vitesses_frame = ttk.LabelFrame(self.param_frame, text="VELOCITIES", labelanchor="n", padding=(10, 10))
        self.vitesses_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.tool_velocity = tk.DoubleVar()
        self.tool_velocity.set(0.0)  # Initialize to the initial value of tool velocity

        self.base_motor_velocity = tk.DoubleVar()
        self.base_motor_velocity.set(0.0)   # Initialize to the initial value of base motor velocity

        self.tranverse_motor_velocity = tk.DoubleVar()
        self.tranverse_motor_velocity.set(0.0)  # Initialize to the initial value of 
        
        self.create_velocity_widgets()
        
        
        # Section COORDONNEES OBJETCS
        self.objet_coordonnes_frame = ttk.LabelFrame(self.param_frame, text="OBJECT CORDINATES", labelanchor="n", padding=(10, 10))
        self.objet_coordonnes_frame.grid(row=2, column=0, padx=10, pady=10)

        self.x_ob_value = tk.DoubleVar()
        self.x_ob_value.set(0.0)  # Initialize to the initial value of x

        self.y_ob_value = tk.DoubleVar()
        self.y_ob_value.set(0.0)  # Initialize to the initial value of y

        self.z_ob_value = tk.DoubleVar()
        self.z_ob_value.set(0.0)  # Initialize to the initial value of z

        self.create_objects_coordonnes_widgets()
        
        # angles cibles en fonction des la position de l'objet
        self.angle_j1_cible = tk.DoubleVar()
        self.angle_j1_cible.set(0.0)  # Initialize to the initial value of J1 cible

        self.angle_j2_cible = tk.DoubleVar()
        self.angle_j2_cible.set(0.0)  # Initialize to the initial value of J2 cible

        self.angle_j3_cible = tk.DoubleVar()
        self.angle_j3_cible.set(0.0)  # Initialize to the initial value of J3 cible
        
        self.angle_j4_cible = tk.DoubleVar()
        self.angle_j4_cible.set(0.0)  # Initialize to the initial value of J1 cible

        self.angle_j5_cible = tk.DoubleVar()
        self.angle_j5_cible.set(0.0)  # Initialize to the initial value of J2 cible

        # frame raspberry et trajectioir
        style.configure("My.TLabelframe", background="white")
        self.rt_frame = ttk.LabelFrame(self.sub_frame, text=" ", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.rt_frame.grid(row=1, column=0, padx=10, pady=10)
        
        # Section Raspberry Pi
        style.configure("My.TLabelframe", background="white")
        self.pi_frame = ttk.LabelFrame(self.rt_frame, text="RASPBERRY PI", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.pi_frame.grid(row=0, column=0, padx=10, pady=10)
        # defaut self.root, row = 3, col=0
        self.create_raspberry_pi_widgets()

        self.pi_serial = None
        
        # Section objects position
        style.configure("My.TLabelframe", background="white")
        self.object_frame = ttk.LabelFrame(self.rt_frame, text="OBJECT TRAJECTORY", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.object_frame.grid(row=0, column=1, padx=10, pady=10)
        self.create_objects_pose_widgets()

        # Display real-time clock
        self.clock_label = ttk.Label(self.menu_frame, text="",  background="white", 
                                  font=bold_font, width=15, justify="center")
        self.clock_label.grid(row=0, column=5, padx=10, pady=10)

        # Update clock every second
        self.update_clock()
    

    def update_clock(self):
        time_string = strftime("%H:%M:%S %p")
        self.clock_label.config(text=time_string)
        self.root.after(1000, self.update_clock)

    def create_raspberry_pi_widgets(self):
        bold_font = ('Helvetica', 11, 'bold')
        background="lime"
        height=1
        width=10
        self.pi_serial_port_label = tk.Label(self.pi_frame, text="Port:", font=bold_font, background="white")
        self.pi_serial_port_entry = tk.Entry(self.pi_frame, justify=justify, font=bold_font, width=width,
                                             textvariable=tk.StringVar(value="None"), fg='gray')
        self.pi_connect_button = tk.Button(self.pi_frame, text="Connect ", command=self.connect_to_pi,
                                           background=background, height=height, width=10, font=5, cursor=cursor)

        self.pi_serial_port_label.grid(row=0, column=0, padx=10, pady=5)
        self.pi_serial_port_entry.grid(row=0, column=1, padx=10, pady=5)
        self.pi_connect_button.grid(row=1, column=0, columnspan=2, pady=10)

    def create_objects_pose_widgets(self):
         bold_font = ('Helvetica', 11, 'bold')
         background="lime"
         height=1
         width=10
         self.object_label = tk.Label(self.object_frame, text="3D OBJECT", font=bold_font, background="white")
         self.object_entry = tk.Entry(self.object_frame, justify=justify, font=bold_font, width=width,
                                              textvariable=tk.StringVar(value="None"), fg='gray')
         self.object_button = tk.Button(self.object_frame, text="Trajectory", command=self.open_second_window,
                                            background=background, height=height, width=10, font=5, cursor=cursor)
         
        
         self.object_label.grid(row=0, column=0, padx=10, pady=5)
         self.object_entry.grid(row=0, column=1, padx=10, pady=5)
         self.object_button.grid(row=1, column=0, columnspan=2, pady=10)
         
    def create_angle_widgets(self):
        # Section Menu
        bold_font = ('Helvetica', 10, 'bold')
        background="lime"
        height=1
        font=5
        width=5
        background2="blue"
        width2=10
        fg='white'
        self.label_j1 = tk.Label(self.angles_frame, text="Angle J1:", font=bold_font)
        self.slider_j1 = ttk.Scale(self.angles_frame, from_=-360, to=360, variable=self.angle_j1,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j1(value), cursor=cursor)
        self.entry_j1 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"),justify=justify, font=bold_font, width=width2)
        self.btn_j1_inc = tk.Button(self.angles_frame, text="J1 +", command=self.increment_j1, 
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j1_dec = tk.Button(self.angles_frame, text="J1 -", command=self.decrement_j1,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)

        self.label_j2 = tk.Label(self.angles_frame, text="Angle J2:", font=bold_font)
        self.slider_j2 = ttk.Scale(self.angles_frame, from_=-360, to=360, variable=self.angle_j2,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j2(value), cursor=cursor)
        self.entry_j2 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j2_inc = tk.Button(self.angles_frame, text="J2 +", command=self.increment_j2,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j2_dec = tk.Button(self.angles_frame, text="J2 -", command=self.decrement_j2,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        
        self.label_j3 = tk.Label(self.angles_frame, text="Angle J3:",font=bold_font)
        self.slider_j3 = ttk.Scale(self.angles_frame, from_=-360, to=360, variable=self.label_j3,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j3(value), cursor=cursor)
        self.entry_j3 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j3_inc = tk.Button(self.angles_frame, text="J3 +", command=self.increment_j3,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j3_dec = tk.Button(self.angles_frame, text="J3 -", command=self.decrement_j3,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        self.label_j4 = tk.Label(self.angles_frame, text="Angle J4:", font=bold_font)
        self.slider_j4 = ttk.Scale(self.angles_frame, from_=-360, to=360, variable=self.label_j4,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j4(value), cursor=cursor)
        self.entry_j4 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j4_inc = tk.Button(self.angles_frame, text="J4 +", command=self.increment_j4,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j4_dec = tk.Button(self.angles_frame, text="J4 -", command=self.decrement_j4,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        self.label_j5 = tk.Label(self.angles_frame, text="Angle J5:", font=bold_font)
        self.slider_j5 = ttk.Scale(self.angles_frame, from_=-360, to=360, variable=self.label_j5,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j5(value), cursor=cursor)
        self.entry_j5 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j5_inc = tk.Button(self.angles_frame, text="J5 +", command=self.increment_j5,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j5_dec = tk.Button(self.angles_frame, text="J5 -", command=self.decrement_j5,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        
        
        # Configuration des boutons avec des marges
        for i, btn in enumerate([self.label_j1, self.slider_j1, self.entry_j1, self.btn_j1_inc,self.btn_j1_dec]):
            btn.grid(row=0, column=i, padx=10, pady=10)
            
        for i, btn in enumerate([self.label_j2, self.slider_j2, self.entry_j2, self.btn_j2_inc,self.btn_j2_dec]):
             btn.grid(row=1, column=i, padx=10, pady=10)

      
        for i, btn in enumerate([self.label_j3, self.slider_j3, self.entry_j3, self.btn_j3_inc,self.btn_j3_dec]):
             btn.grid(row=2, column=i, padx=10, pady=10)
        
        for i, btn in enumerate([self.label_j4, self.slider_j4, self.entry_j4, self.btn_j4_inc,self.btn_j4_dec]):
             btn.grid(row=3, column=i, padx=10, pady=10)
        
        for i, btn in enumerate([self.label_j5, self.slider_j5, self.entry_j5, self.btn_j5_inc,self.btn_j5_dec]):
             btn.grid(row=4, column=i, padx=10, pady=10)
        
        # Configurer les gestionnaires d'événements pour la touche "Entrée"
        self.entry_j1.bind('<Return>', lambda event, entry=self.entry_j1: self.handle_enter_angles_slider_update(event, entry))
        self.entry_j2.bind('<Return>', lambda event, entry=self.entry_j2: self.handle_enter_angles_slider_update(event, entry))
        self.entry_j3.bind('<Return>', lambda event, entry=self.entry_j3: self.handle_enter_angles_slider_update(event, entry))
        self.entry_j4.bind('<Return>', lambda event, entry=self.entry_j4: self.handle_enter_angles_slider_update(event, entry))
        self.entry_j5.bind('<Return>', lambda event, entry=self.entry_j5: self.handle_enter_angles_slider_update(event, entry))
    
    def handle_enter_angles_slider_update(self, event, entry):
          try:
              # Cette méthode sera appelée lorsque la touche "Entrée" est pressée
              j1_value = float(self.entry_j1.get())
              j2_value = float(self.entry_j2.get())
              j3_value = float(self.entry_j3.get())
              j4_value = float(self.entry_j4.get())
              j5_value = float(self.entry_j5.get())
      
              # Mettre à jour la variable associée au slider
              self.slider_j1.set(j1_value)
              self.slider_j2.set(j2_value)
              self.slider_j3.set(j3_value)
              self.slider_j4.set(j4_value)
              self.slider_j5.set(j5_value)
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          except ValueError:
             
              # Remettre la valeur précédente de la variable associée au slider
              self.entry_j1.delete(0, tk.END)
              self.entry_j1.insert(0, str(self.slider_j1.get()))
      
              self.entry_j2.delete(0, tk.END)
              self.entry_j2.insert(0, str(self.slider_j2.get()))
      
              self.entry_j3.delete(0, tk.END)
              self.entry_j3.insert(0, str(self.slider_j3.get()))
              
              self.entry_j4.delete(0, tk.END)
              self.entry_j4.insert(0, str(self.slider_j4.get()))
      
              self.entry_j5.delete(0, tk.END)
              self.entry_j5.insert(0, str(self.slider_j5.get()))
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          
    def create_tool_widgets(self):
        bold_font = ('Helvetica', 9, 'bold')
        #background="lime"
        width=10
        self.label_x = tk.Label(self.tool_frame, text="X (mm):", font=bold_font)
        self.slider_x = ttk.Scale(self.tool_frame, from_=-225, to=225, variable=self.x_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_x(value), cursor=cursor)
        self.entry_x = tk.Entry(self.tool_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_y = tk.Label(self.tool_frame, text="Y (mm):", font=bold_font)
        self.slider_y = ttk.Scale(self.tool_frame, from_=-220, to=207.55, variable=self.y_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_y(value), cursor=cursor)
        self.entry_y = tk.Entry(self.tool_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_z = tk.Label(self.tool_frame, text="Z (mm):", font=bold_font)
        self.slider_z = ttk.Scale(self.tool_frame, from_=-220, to=204.55, variable=self.z_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_z(value), cursor=cursor)
        self.entry_z = tk.Entry(self.tool_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_x.grid(row=0, column=0, padx=10, pady=10)
        self.slider_x.grid(row=0, column=1, padx=10, pady=10)
        self.entry_x.grid(row=0, column=2, padx=10, pady=10)

        self.label_y.grid(row=2, column=0, padx=10, pady=10)
        self.slider_y.grid(row=2, column=1, padx=10, pady=10)
        self.entry_y.grid(row=2, column=2, padx=10, pady=10)

        self.label_z.grid(row=4, column=0, padx=10, pady=10)
        self.slider_z.grid(row=4, column=1, padx=10, pady=10)
        self.entry_z.grid(row=4, column=2, padx=10, pady=10)
        
        # Configurer les gestionnaires d'événements pour la touche "Entrée"
        self.entry_x.bind('<Return>', lambda event, entry=self.entry_x: self.handle_enter_tool_slider_update(event, entry))
        self.entry_y.bind('<Return>', lambda event, entry=self.entry_y: self.handle_enter_tool_slider_update(event, entry))
        self.entry_z.bind('<Return>', lambda event, entry=self.entry_z: self.handle_enter_tool_slider_update(event, entry))
        
    def handle_enter_tool_slider_update(self, event, entry):
        try:
            # Cette méthode sera appelée lorsque la touche "Entrée" est pressée
            x_value = float(self.entry_x.get())
            y_value = float(self.entry_y.get())
            z_value = float(self.entry_z.get())
    
            # Mettre à jour la variable associée au slider
            self.slider_x.set(x_value)
            self.slider_y.set(y_value)
            self.slider_z.set(z_value)
    
            # Masquer le curseur en définissant la position à la fin du texte
            entry.icursor(tk.END)
        except ValueError:
           
            # Remettre la valeur précédente de la variable associée au slider
            self.entry_x.delete(0, tk.END)
            self.entry_x.insert(0, str(self.slider_x.get()))
    
            self.entry_y.delete(0, tk.END)
            self.entry_y.insert(0, str(self.slider_y.get()))
    
            self.entry_z.delete(0, tk.END)
            self.entry_z.insert(0, str(self.slider_z.get()))
    
            # Masquer le curseur en définissant la position à la fin du texte
            entry.icursor(tk.END)
     
     
  
    def create_velocity_widgets(self):
        bold_font = ('Helvetica', 9, 'bold')
        #background="brown"
        width=20
      
        self.label_tool_velocity = tk.Label(self.vitesses_frame, text="VT(m/s):", font=bold_font)
        self.entry_tool_velocity = tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
            
        self.label_base_motor_velocity = tk.Label(self.vitesses_frame, text="MB(tr/min):", font=bold_font)
        self.entry_base_motor_velocity = tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_tranverse_motor_velocity = tk.Label(self.vitesses_frame, text="M2(tr/min):", font=bold_font)
        self.entry_tranverse_motor_velocity= tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_tool_velocity.grid(row=0, column=0, padx=10, pady=10)
        self.entry_tool_velocity.grid(row=0, column=2, padx=10, pady=10)

        self.label_base_motor_velocity.grid(row=2, column=0, padx=10, pady=10)
        self.entry_base_motor_velocity.grid(row=2, column=2, padx=10, pady=10)

        self.label_tranverse_motor_velocity.grid(row=4, column=0, padx=10, pady=10)
        self.entry_tranverse_motor_velocity.grid(row=4, column=2, padx=10, pady=10)
        
        # Configurer les gestionnaires d'événements pour la touche "Entrée"
        self.entry_tool_velocity.bind('<Return>', lambda event, entry=self.entry_tool_velocity: self.handle_enter(event, entry))
        self.entry_base_motor_velocity.bind('<Return>', lambda event, entry=self.entry_base_motor_velocity: self.handle_enter(event, entry))
        self.entry_tranverse_motor_velocity.bind('<Return>', lambda event, entry=self.entry_tranverse_motor_velocity: self.handle_enter(event, entry))

    
    def create_objects_coordonnes_widgets(self):
        bold_font = ('Helvetica', 9, 'bold')
        #background="lime"
        width=20
       
        self.label_x_ob = tk.Label(self.objet_coordonnes_frame, text="X (mm):", font=bold_font)
        self.entry_x_ob = tk.Entry(self.objet_coordonnes_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_y_ob = tk.Label(self.objet_coordonnes_frame, text="Y (mm):", font=bold_font)
        self.entry_y_ob = tk.Entry(self.objet_coordonnes_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_z_ob = tk.Label(self.objet_coordonnes_frame, text="Z (mm):", font=bold_font)
        self.entry_z_ob = tk.Entry(self.objet_coordonnes_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_x_ob.grid(row=0, column=0, padx=10, pady=10)
        self.entry_x_ob.grid(row=0, column=1, padx=10, pady=10)

        self.label_y_ob.grid(row=2, column=0, padx=10, pady=10)
        self.entry_y_ob.grid(row=2, column=1, padx=10, pady=10)

        self.label_z_ob.grid(row=4, column=0, padx=10, pady=10)
        self.entry_z_ob.grid(row=4, column=1, padx=10, pady=10)
        

        # Configurer les gestionnaires d'événements pour la touche "Entrée"
        self.entry_x_ob.bind('<Return>', lambda event, entry=self.entry_x_ob: self.calculate_angles_cibles(event, entry))
        self.entry_y_ob.bind('<Return>', lambda event, entry=self.entry_y_ob: self.calculate_angles_cibles(event, entry))
        self.entry_z_ob.bind('<Return>', lambda event, entry=self.entry_z_ob: self.calculate_angles_cibles(event, entry))
    
        
    def create_normal_vector_widgets(self):
          bold_font = ('Helvetica', 9, 'bold')
          #background="lime"
          width=10
          self.label_nx = tk.Label(self.normal_vector_frame, text="nx:", font=bold_font)
          self.slider_nx = ttk.Scale(self.normal_vector_frame, from_=-1, to=1, variable=self.nx,
                                     orient=tk.HORIZONTAL, command=lambda value: self.update_ort_label_nx(value), cursor=cursor)
          self.entry_nx = tk.Entry(self.normal_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

          self.label_ny = tk.Label(self.normal_vector_frame, text="ny:", font=bold_font)
          self.slider_ny = ttk.Scale(self.normal_vector_frame, from_=-1, to=1, variable=self.ny,
                                     orient=tk.HORIZONTAL, command=lambda value: self.update_ort_label_ny(value), cursor=cursor)
          self.entry_ny = tk.Entry(self.normal_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

          self.label_nz = tk.Label(self.normal_vector_frame, text="nz:", font=bold_font)
          self.slider_nz = ttk.Scale(self.normal_vector_frame, from_=-1, to=1, variable=self.nz,
                                    orient=tk.HORIZONTAL, command=lambda value: self.update_ort_label_nz(value), cursor=cursor)
          self.entry_nz = tk.Entry(self.normal_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
          
          self.label_nx.grid(row=0, column=0, padx=10, pady=10)
          self.slider_nx.grid(row=0, column=1, padx=10, pady=10)
          self.entry_nx.grid(row=0, column=2, padx=10, pady=10)

          self.label_ny.grid(row=1, column=0, padx=10, pady=10)
          self.slider_ny.grid(row=1, column=1, padx=10, pady=10)
          self.entry_ny.grid(row=1, column=2, padx=10, pady=10)

          self.label_nz.grid(row=2, column=0, padx=10, pady=10)
          self.slider_nz.grid(row=2, column=1, padx=10, pady=10)
          self.entry_nz.grid(row=2, column=2, padx=10, pady=10)
    
          # Configurer les gestionnaires d'événements pour la touche "Entrée"
          self.entry_nx.bind('<Return>', lambda event, entry=self.entry_nx: self.handle_enter_normal_vector_slider_update(event, entry))
          self.entry_ny.bind('<Return>', lambda event, entry=self.entry_ny: self.handle_enter_normal_vector_slider_update(event, entry))
          self.entry_nz.bind('<Return>', lambda event, entry=self.entry_nz: self.handle_enter_normal_vector_slider_update(event, entry))
          
    def handle_enter_normal_vector_slider_update(self, event, entry):
          try:
              # Cette méthode sera appelée lorsque la touche "Entrée" est pressée
              nx_value = float(self.entry_nx.get())
              ny_value = float(self.entry_ny.get())
              nz_value = float(self.entry_nz.get())
      
              # Mettre à jour la variable associée au slider
              self.slider_nx.set(nx_value)
              self.slider_ny.set(ny_value)
              self.slider_nz.set(nz_value)
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          except ValueError:
             
              # Remettre la valeur précédente de la variable associée au slider
              self.entry_nx.delete(0, tk.END)
              self.entry_nx.insert(0, str(self.slider_nx.get()))
      
              self.entry_ny.delete(0, tk.END)
              self.entry_ny.insert(0, str(self.slider_ny.get()))
      
              self.entry_nz.delete(0, tk.END)
              self.entry_nz.insert(0, str(self.slider_nz.get()))
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          
    def create_slider_vector_widgets(self):
              bold_font = ('Helvetica', 9, 'bold')
              #background="lime"
              width=10
              self.label_sx = tk.Label(self.slider_vector_frame, text="sx:", font=bold_font)
              self.slider_sx = ttk.Scale(self.slider_vector_frame, from_=-1, to=1, variable=self.sx,
                                         orient=tk.HORIZONTAL, command=lambda value: self.update_slider_label_sx(value), cursor=cursor)
              self.entry_sx = tk.Entry(self.slider_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

              self.label_sy = tk.Label(self.slider_vector_frame, text="sy:", font=bold_font)
              self.slider_sy = ttk.Scale(self.slider_vector_frame, from_=-1, to=1, variable=self.sy,
                                         orient=tk.HORIZONTAL, command=lambda value: self.update_slider_label_sy(value), cursor=cursor)
              self.entry_sy = tk.Entry(self.slider_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

              self.label_sz = tk.Label(self.slider_vector_frame, text="sz:", font=bold_font)
              self.slider_sz = ttk.Scale(self.slider_vector_frame, from_=-1, to=1, variable=self.sz,
                                        orient=tk.HORIZONTAL, command=lambda value: self.update_slider_label_sz(value), cursor=cursor)
              self.entry_sz = tk.Entry(self.slider_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
              
              self.label_sx.grid(row=0, column=0, padx=10, pady=10)
              self.slider_sx.grid(row=0, column=1, padx=10, pady=10)
              self.entry_sx.grid(row=0, column=2, padx=10, pady=10)

              self.label_sy.grid(row=1, column=0, padx=10, pady=10)
              self.slider_sy.grid(row=1, column=1, padx=10, pady=10)
              self.entry_sy.grid(row=1, column=2, padx=10, pady=10)

              self.label_sz.grid(row=2, column=0, padx=10, pady=10)
              self.slider_sz.grid(row=2, column=1, padx=10, pady=10)
              self.entry_sz.grid(row=2, column=2, padx=10, pady=10)
              
                  
              # Configurer les gestionnaires d'événements pour la touche "Entrée"
              self.entry_sx.bind('<Return>', lambda event, entry=self.entry_sx: self.handle_enter_slider_vector_sliders_update(event, entry))
              self.entry_sy.bind('<Return>', lambda event, entry=self.entry_sy: self.handle_enter_slider_vector_sliders_update(event, entry))
              self.entry_sz.bind('<Return>', lambda event, entry=self.entry_sz: self.handle_enter_slider_vector_sliders_update(event, entry))
              
    def handle_enter_slider_vector_sliders_update(self, event, entry):
          try:
              # Cette méthode sera appelée lorsque la touche "Entrée" est pressée
              sx_value = float(self.entry_sx.get())
              sy_value = float(self.entry_sy.get())
              sz_value = float(self.entry_sz.get())
      
              # Mettre à jour la variable associée au slider
              self.slider_sx.set(sx_value)
              self.slider_sy.set(sy_value)
              self.slider_sz.set(sz_value)
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          except ValueError:
             
              # Remettre la valeur précédente de la variable associée au slider
              self.entry_sx.delete(0, tk.END)
              self.entry_sx.insert(0, str(self.slider_sx.get()))
      
              self.entry_sy.delete(0, tk.END)
              self.entry_sy.insert(0, str(self.slider_sy.get()))
      
              self.entry_sz.delete(0, tk.END)
              self.entry_sz.insert(0, str(self.slider_sz.get()))
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
    
    def create_approach_vector_widgets(self):
              bold_font = ('Helvetica', 9, 'bold')
              #background="lime"
              width=10
              self.label_ax = tk.Label(self.approach_vector_frame, text="ax:", font=bold_font)
              self.slider_ax = ttk.Scale(self.approach_vector_frame, from_=-0.92, to=1, variable=self.ax,
                                         orient=tk.HORIZONTAL, command=lambda value: self.update_approach_label_ax(value), cursor=cursor)
              self.entry_ax = tk.Entry(self.approach_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

              self.label_ay = tk.Label(self.approach_vector_frame, text="ay:", font=bold_font)
              self.slider_ay = ttk.Scale(self.approach_vector_frame, from_=-0.92, to=1, variable=self.ay,
                                         orient=tk.HORIZONTAL, command=lambda value: self.update_approach_label_ay(value), cursor=cursor)
              self.entry_ay = tk.Entry(self.approach_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
              
              self.label_az = tk.Label(self.approach_vector_frame, text="az:", font=bold_font)
              self.slider_az = ttk.Scale(self.approach_vector_frame, from_=-1, to=1, variable=self.az,
                                        orient=tk.HORIZONTAL, command=lambda value: self.update_approach_label_az(value), cursor=cursor)
              self.entry_az = tk.Entry(self.approach_vector_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
              
              self.label_ax.grid(row=0, column=0, padx=10, pady=10)
              self.slider_ax.grid(row=0, column=1, padx=10, pady=10)
              self.entry_ax.grid(row=0, column=2, padx=10, pady=10)

              self.label_ay.grid(row=1, column=0, padx=10, pady=10)
              self.slider_ay.grid(row=1, column=1, padx=10, pady=10)
              self.entry_ay.grid(row=1, column=2, padx=10, pady=10)

              self.label_az.grid(row=2, column=0, padx=10, pady=10)
              self.slider_az.grid(row=2, column=1, padx=10, pady=10)
              self.entry_az.grid(row=2, column=2, padx=10, pady=10)
              
              
              # Configurer les gestionnaires d'événements pour la touche "Entrée"
              self.entry_ax.bind('<Return>', lambda event, entry=self.entry_ax: self.handle_enter_approach_vector_sliders_update(event, entry))
              self.entry_ay.bind('<Return>', lambda event, entry=self.entry_ay: self.handle_enter_approach_vector_sliders_update(event, entry))
              self.entry_az.bind('<Return>', lambda event, entry=self.entry_az: self.handle_enter_approach_vector_sliders_update(event, entry))
              
    def handle_enter_approach_vector_sliders_update(self, event, entry):
          try:
              # Cette méthode sera appelée lorsque la touche "Entrée" est pressée
              ax_value = float(self.entry_ax.get())
              ay_value = float(self.entry_ay.get())
              az_value = float(self.entry_az.get())
      
              # Mettre à jour la variable associée au slider
              self.slider_ax.set(ax_value)
              self.slider_ay.set(ay_value)
              self.slider_az.set(az_value)
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)
          except ValueError:
             
              # Remettre la valeur précédente de la variable associée au slider
              self.entry_ax.delete(0, tk.END)
              self.entry_ax.insert(0, str(self.slider_ax.get()))
      
              self.entry_ay.delete(0, tk.END)
              self.entry_ay.insert(0, str(self.slider_ay.get()))
      
              self.entry_az.delete(0, tk.END)
              self.entry_az.insert(0, str(self.slider_az.get()))
      
              # Masquer le curseur en définissant la position à la fin du texte
              entry.icursor(tk.END)

    def validate_values(self, value, min_value, max_value, entry_widget):
        try:
            float_value = float(value)
            if min_value <= float_value <= max_value:
                return True
            else:
                messagebox.showerror("Error", f"Invalid value. Enter a value between {min_value} and {max_value}.")
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, f"{float_value:.2f}")
                return False
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Enter a valid numerical value.")
            entry_widget.delete(0, tk.END)
            return False

    def update_tool_velocity_label(self, value):
        if self.validate_values(value, -180, 180, self.entry_tool_velocity):
            self.entry_tool_velocity.delete(0, tk.END)
            self.entry_tool_velocity.insert(0, f"{float(value):.2f}")

    def update_base_motor_velocity_label(self, value):
        if self.validate_values(value, -180, 180, self.entry_base_motor_velocity):
            self.entry_base_motor_velocity.delete(0, tk.END)
            self.entry_base_motor_velocity.insert(0, f"{float(value):.2f}")

    def update_tranverse_motor_velocity_label(self, value):
        if self.validate_values(value, -180, 180, self.entry_tranverse_motor_velocity):
            self.entry_tranverse_motor_velocity.delete(0, tk.END)
            self.entry_tranverse_motor_velocity.insert(0, f"{float(value):.2f}")


    def connect_to_pi(self):
        pi_serial_port = self.pi_serial_port_entry.get()

        try:
            self.pi_serial = serial.Serial(pi_serial_port, baudrate=9600, timeout=1)
            print(f"Connecté à la Raspberry Pi sur le port série {pi_serial_port}")
        except Exception as e:
            print(f"Erreur lors de la connexion à la Raspberry Pi : {e}")

    def send_data_to_pi(self, data):
        if self.pi_serial:
            try:
                self.pi_serial.write(data.encode())
                print(f"Données envoyées à la Raspberry Pi : {data}")
            except Exception as e:
                print(f"Erreur lors de l'envoi de données à la Raspberry Pi : {e}")

    def receive_data_from_pi(self):
        if self.pi_serial:
            try:
                received_data = self.pi_serial.readline().decode().strip()
                print(f"Données reçues de la Raspberry Pi : {received_data}")
                return received_data
            except Exception as e:
                print(f"Erreur lors de la réception de données de la Raspberry Pi : {e}")
        return None

    def start_robot(self):
        print("Robot démarré")

    def stop_robot(self):
        print("Robot arrêté")
        self.stop_process_flag = True
        self.btn_pid.config(state=tk.NORMAL)
        self.btn_home.config(state=tk.NORMAL)
   
    def update_pid(self):
        self.target_positions = [self.angle_j1_cible.get(),self.angle_j2_cible.get(), self.angle_j3_cible.get(),
                                 self.angle_j4_cible.get(), self.angle_j5_cible.get()]

        self.current_positions = [self.angle_j1.get(), self.angle_j2.get(), self.angle_j3.get(),
                                  self.angle_j4.get(), self.angle_j5.get()]

        # Calculer les erreurs PID
        errors = [target - current for target, current in zip(self.target_positions, self.current_positions)]
        self.integral = [integral + error for integral, error in zip(self.integral, errors)]
        derivative = [error - prev_error for error, prev_error in zip(errors, self.prev_error)]

        # Calculer les commandes PID
        pid_commands = [self.kp * errors[i] + self.ki * self.integral[i] + self.kd * derivative[i] for i in range(len(errors))]

        # pour enregistrer l'erreur actuelle dans l'historique
        total_error = sum(errors)
        self.error_history.append(total_error)
        
        if not self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
           self.update_motors(pid_commands)

           # Mettre à jour l'erreur précédente
           self.prev_error = errors

           # Appel de la fonction pour mettre à jour la représentation graphique
           self.update_plot()
      
    def are_positions_close(self, current_positions, target_positions, tolerance):
          return all(abs(curr - target) < tolerance for curr, target in zip(current_positions, target_positions))
    
   
    def update_motors(self, commands):
    # Mettre à jour la position actuelle du moteur (simuler le mouvement)
        for i, command in enumerate(commands):
            new_position =round( min(self.current_positions[i] + command, self.current_positions[i] + 5),2)
            #getattr(self, f"angle_j{i + 1}", new_position)
            if i==0:
                self.angle_j1.set(new_position)
                self.entry_j1.delete(0, tk.END)
                self.entry_j1.insert(0, str(new_position))
            if i==1:
                self.angle_j2.set(new_position)
                self.entry_j2.delete(0, tk.END)
                self.entry_j2.insert(0, str(new_position))
            if i==2:
                self.angle_j3.set(new_position)
                self.entry_j3.delete(0, tk.END)
                self.entry_j3.insert(0, str(new_position))
            if i==3:
                self.angle_j4.set(new_position)
                self.entry_j4.delete(0, tk.END)
                self.entry_j4.insert(0, str(new_position))
            if i==4:
                self.angle_j5.set(new_position)
                self.entry_j5.delete(0, tk.END)
                self.entry_j5.insert(0, str(new_position))
                
       
            self.calculate_X()
            self.calculate_Y()
            self.calculate_Z()
                
                
            #self.angle_j[i + 1].set(new_position)
    
        # attente pause
        time.sleep(0.1)


    def update_plot(self):
        
        # Vérifier si la figure et l'axe existent
        if self.fig is None or self.ax0 is None:
           print("Erreur : la figure et l'axe doivent être créés en appelant open_second_window.")
           return
       
        #  tracer l'historique des erreurs
        self.ax0.clear()
        self.ax0.plot(self.error_history)
        self.ax0.set_xlabel('Iterations')
        self.ax0.set_ylabel('Total Error')
        self.ax0.set_title('PID') 
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    
    def start_update_pid(self):
        self.stop_process_flag = False
        self.open_second_window()
        # Désactiver le bouton pendant la mise à jour automatique
        self.btn_pid.config(state=tk.DISABLED)
        self.btn_home.config(state=tk.DISABLED)
        
        # Appeler la fonction update_pid de manière récursive jusqu'à ce que les valeurs soient égales aux valeurs cibles
        self.auto_update_pid()


    def auto_update_pid(self):
        self.update_pid()
        # Si la variable de drapeau indique de ne pas arrêter le processus, appeler récursivement
        if not self.stop_process_flag:
            # Vérifier si les valeurs sont égales aux valeurs cibles
            if self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
                # Si oui, activer à nouveau le bouton
                self.btn_pid.config(state=tk.NORMAL)
                self.btn_home.config(state=tk.NORMAL)
            else:
                
                # Si non, planifier la prochaine mise à jour après un court délai
                self.root.after(100, self.auto_update_pid)  # Appeler après 1000 ms (1 seconde)
        
            
        
        
    def increment_j1(self):
        current_value = self.angle_j1.get()
        if current_value < 180:
            self.angle_j1.set(current_value + 1)
            self.set_j1()

    def decrement_j1(self):
        current_value = self.angle_j1.get()
        if current_value > -180:
            self.angle_j1.set(current_value - 1)
            self.set_j1()
  
    def set_j1(self):
        angle_j1 = round(float(self.angle_j1.get()),2) 
        print(f"Réglage de l'angle J1 à {angle_j1} degrés")
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(angle_j1))
       
        self.calculate_X()
        self.calculate_Y()
        
        self.calculate_nX()
        self.calculate_ny()
        self.calculate_nz()
        
        self.calculate_sX()
        self.calculate_sy()
        self.calculate_sz()
        
        self.calculate_aX()
        self.calculate_ay()
        self.calculate_az()

    def increment_j2(self):
        current_value = self.angle_j2.get()
        if current_value < 180:
            self.angle_j2.set(current_value + 1)
            self.set_j2()

    def decrement_j2(self):
        current_value = self.angle_j2.get()
        if current_value > -180:
            self.angle_j2.set(current_value - 1)
            self.set_j2()

    def set_j2(self):
        angle_j2 =round(float(self.angle_j2.get()),2) 
        print(f"Réglage de l'angle J2 à {angle_j2} degrés")
        self.entry_j2.delete(0, tk.END)
        self.entry_j2.insert(0, str(angle_j2))
       # self.calculate_j3()
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
        
        self.calculate_nX()
        self.calculate_ny()
        self.calculate_nz()
        
        self.calculate_sX()
        self.calculate_sy()
        self.calculate_sz()
        
        self.calculate_aX()
        self.calculate_ay()
        self.calculate_az()
        
        
    def increment_j3(self):
        current_value = self.angle_j3.get()
        if current_value < 180:
            self.angle_j3.set(current_value + 1)
            self.set_j3()

    def decrement_j3(self):
        current_value = self.angle_j3.get()
        if current_value > -180:
            self.angle_j3.set(current_value - 1)
            self.set_j3()

    def set_j3(self):
        angle_j3 = round(float(self.angle_j3.get()),2) 
        print(f"Réglage de l'angle J3 à {angle_j3} degrés")
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(angle_j3))
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
        
        self.calculate_nX()
        self.calculate_ny()
        self.calculate_nz()
        
        self.calculate_sX()
        self.calculate_sy()
        self.calculate_sz()
        
        self.calculate_aX()
        self.calculate_ay()
        self.calculate_az()
        
           
    def increment_j4(self):
        current_value = self.angle_j4.get()
        if current_value < 180:
            self.angle_j4.set(current_value + 1)
            self.set_j4()

    def decrement_j4(self):
        current_value = self.angle_j4.get()
        if current_value > -180:
            self.angle_j4.set(current_value - 1)
            self.set_j4()

    def set_j4(self):
        angle_j4 = round(float(self.angle_j4.get()),2) 
        print(f"Réglage de l'angle J4 à {angle_j4} degrés")
        self.entry_j4.delete(0, tk.END)
        self.entry_j4.insert(0, str(angle_j4))
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
        
        self.calculate_nX()
        self.calculate_ny()
        self.calculate_nz()
        
        self.calculate_sX()
        self.calculate_sy()
        self.calculate_sz()
        
        self.calculate_aX()
        self.calculate_ay()
        self.calculate_az()
        
         
    def increment_j5(self):
        current_value = self.angle_j5.get()
        if current_value < 180:
            self.angle_j5.set(current_value + 1)
            self.set_j5()

    def decrement_j5(self):
        current_value = self.angle_j5.get()
        if current_value > -180:
            self.angle_j5.set(current_value - 1)
            self.set_j5()
            
  
    def set_j5(self):
        angle_j5 =round(float(self.angle_j5.get()),2) 
        print(f"Réglage de l'angle J5 à {angle_j5} degrés")
        self.entry_j5.delete(0, tk.END)
        self.entry_j5.insert(0, str(angle_j5))
        
        self.calculate_nX()
        self.calculate_ny()
        self.calculate_nz()
        
        self.calculate_sX()
        self.calculate_sy()
        self.calculate_sz()
        
        self.calculate_aX()
        self.calculate_ay()
        self.calculate_az()
        
        

    def update_angle_label_j1(self, value):
        try:
            angle_value = float(value)
            self.angle_j1.set(angle_value)
            self.set_j1()
        except ValueError:
            print("Valeur non valide pour l'angle J1.")

    def update_angle_label_j2(self, value):
        try:
            angle_value = float(value)
            self.angle_j2.set(angle_value)
            self.set_j2()
        except ValueError:
            print("Valeur non valide pour l'angle J2.")
            
    def update_angle_label_j3(self, value):
        try:
            angle_value = float(value)
            self.angle_j3.set(angle_value)
            self.set_j3()
        except ValueError:
            print("Valeur non valide pour l'angle J3.")

        
    
    def update_angle_label_j4(self, value):
        try:
            angle_value = float(value)
            self.angle_j4.set(angle_value)
            self.set_j4()
        except ValueError:
            print("Valeur non valide pour l'angle J4.")
    
    def update_angle_label_j5(self, value):
        try:
            angle_value = float(value)
            self.angle_j5.set(angle_value)
            self.set_j5()
        except ValueError:
            print("Valeur non valide pour l'angle J5.")
            
    def calculate_angles(self):
       
          # calcul j1
          x = self.x_value.get()
          y= self.y_value.get()
          j1 = math.atan2(y, x)
          
          # calcul j5
          
          nx= self.nx.get()
          ny= self.ny.get()
          sx= self.sx.get()
          sy= self.sy.get()
          s5=nx*math.sin(j1)-ny*math.cos(j1)
          c5=sx*math.sin(j1)-sy*math.cos(j1)
          j5=math.atan2(s5, c5)
          
          # calculate J234
          ax= self.ax.get()
          ay= self.ay.get()
          az= self.az.get()
          j234=math.atan2(-(ax*math.cos(j1)+ay*math.sin(j1)), -az)
          
          #calculate J3
          z=self.z_value.get()
         
          if math.cos(j1)!=0:
              c=(x/math.cos(j1)) + Longeur_d5*math.sin(j234)-distance_a4*math.cos(j234)
          else :
              c= Longeur_d5*math.sin(j234)-distance_a4*math.cos(j234)
          d= Longueur_d1 - distance_a4*math.sin(j234)- Longeur_d5*math.cos(j234)-z
          
          c3=(c**2+d**2-distance_a3**2-distance_a2**2)/(2*distance_a2*distance_a3)
          s3=(1-c3**2)**0.5
          c3=float(c3)
          if c3 >1 :
              print(f"ay limite {ay}")
          s3=float(s3)
          j3=math.atan2(s3, c3)
          
          #calculate J2
          r=distance_a3*c3 + distance_a2
          s=distance_a3*s3
          j2=math.atan2((r*d-s*c), (r*c+s*d))
          
          
          # calculate j4
          j4 = j234-(j3+j2)
          
          # convert and display J1
          j1 =round(math.degrees(j1),2)
          self.angle_j1.set(j1)
          self.entry_j1.delete(0, tk.END)
          self.entry_j1.insert(0, str(j1))
          
          # convert and display J5
          j5 =round(math.degrees(j5),2)
          self.angle_j5.set(j5)
          self.entry_j5.delete(0, tk.END)
          self.entry_j5.insert(0, str(j5))
          
          j3=round(math.degrees(j3),2)
          self.angle_j3.set(j3)
          self.entry_j3.delete(0, tk.END)
          self.entry_j3.insert(0, str(j3))
          
          # convert and display J2
          j2 =round(math.degrees(j2),2)
          self.angle_j2.set(j2)
          self.entry_j2.delete(0, tk.END)
          self.entry_j2.insert(0, str(j2))
          
          
          # convert and display J4
          j4 =round(math.degrees(j4),2)
          self.angle_j4.set(j4)
          self.entry_j4.delete(0, tk.END)
          self.entry_j4.insert(0, str(j4))
              
    # calcul des angles cibles
    def calculate_angles_cibles(self, event, entry ):
          

          # calcul j1
          x = float(self.entry_x_ob.get())
          y= float(self.entry_y_ob.get())
          j1 = math.atan2(y, x)
          #print(f"j1 est : {j1}")
          
          
          # calcul j5
          
          nx= self.nx.get()
          ny= self.ny.get()
          sx= self.sx.get()
          sy= self.sy.get()
          s5=nx*math.sin(j1)-ny*math.cos(j1)
          c5=sx*math.sin(j1)-sy*math.cos(j1)
          j5=math.atan2(s5, c5)
          
          # calculate J234
          ax= self.ax.get()
          ay= self.ay.get()
          az= self.az.get()
          j234=math.atan2(-(ax*math.cos(j1)+ay*math.sin(j1)), -az)
          
          #calculate J3
          z=float(self.entry_z_ob.get())
         
          
          if math.cos(j1)!=0:
              c=(x/math.cos(j1)) + Longeur_d5*math.sin(j234)-distance_a4*math.cos(j234)
          else :
              c= Longeur_d5*math.sin(j234)-distance_a4*math.cos(j234)
              
          d= Longueur_d1 - distance_a4*math.sin(j234)- Longeur_d5*math.cos(j234)-z
          
          c3=(c**2+d**2-distance_a3**2-distance_a2**2)/(2*distance_a2*distance_a3)
          s3=(1-c3**2)**0.5
          c3=float(c3)
          if c3 >1 :
              print(f"ay limite {ay}")
          s3=float(s3)
          j3=math.atan2(s3, c3)
          
          #calculate J2
          r=distance_a3*c3 + distance_a2
          s=distance_a3*s3
          j2=math.atan2((r*d-s*c), (r*c+s*d))
          
          
          # calculate j4
          j4 = j234-(j3+j2)
          
          # convert and display J1
          j1 =round(math.degrees(j1),2)
          self.angle_j1_cible.set(j1)
          
          # convert and display J5
          j5 =round(math.degrees(j5),2)
          self.angle_j5_cible.set(j5)
         
          j3=round(math.degrees(j3),2)
          self.angle_j3_cible.set(j3)
        
          
          # convert and display J2
          j2 =round(math.degrees(j2),2)
          self.angle_j2_cible.set(j2)
     
        
          # convert and display J4
          j4 =round(math.degrees(j4),2)
          self.angle_j4_cible.set(j4)
        
          
          # Masquer le curseur en définissant la position à la fin du texte
          
          entry.icursor(tk.END)
            
            
         # calcul de x
    def calculate_X(self):
         # Calcul de J3 en fonction de J1 et J2
         j1 = self.angle_j1.get()
         j1=math.radians(j1)
         j2 = self.angle_j2.get()
         j2=math.radians(j2)
         j3 = self.angle_j3.get()
         j3=math.radians(j3)
         j4 = self.angle_j4.get()
         j4=math.radians(j4)
         x=math.cos(j1)*(distance_a2*math.cos(j2) + distance_a3*math.cos(j2+j3) + distance_a4*math.cos(j2+j3+j4) - 
                         Longeur_d5*math.sin(j2+j3+j4))
         x=round(x,2)
         self.x_value.set(x)
         self.entry_x.delete(0, tk.END)
         self.entry_x.insert(0, str(x))

    def set_x(self):
        x_value = round(float(self.x_value.get()),2)
        print(f"Réglage de X à {x_value} mm")
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(x_value))
        
        self.calculate_angles()
        
        # calcul de y
    def calculate_Y(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        y=math.sin(j1)*(distance_a2*math.cos(j2) + distance_a3*math.cos(j2+j3) + distance_a4*math.cos(j2+j3+j4) - 
                        Longeur_d5*math.sin(j2+j3+j4))
        y=round(y,2)
        self.y_value.set(y)
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y))
        
    def set_y(self):
        y_value = round(float(self.y_value.get()),2)
        print(f"Réglage de Y à {y_value} mm")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y_value))
        
        self.calculate_angles()
        
    # calcul de y
    def calculate_Z(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        z=(Longueur_d1 - distance_a2*math.sin(j2) - distance_a3*math.sin(j2+j3) - distance_a4*math.sin(j2+j3+j4) -
           Longeur_d5*math.cos(j2+j3+j4))
        z=round(z,2)
        self.z_value.set(z)
        self.entry_z.delete(0, tk.END)
        self.entry_z.insert(0, str(z))
    
    def set_z(self):
        z_value = round(float(self.z_value.get()),2)
        print(f"Réglage de Z à {z_value} mm")
        self.entry_z.delete(0, tk.END)
        self.entry_z.insert(0, str(z_value))
        self.calculate_angles()
    
    def update_pos_label_x(self, value):
        try:
            value_x= float(value)
            self.x_value.set(value_x)
            self.set_x()
        except ValueError:
            print("Valeur non valide pour X.")
    def update_pos_label_y(self, value):
        try:
            value_y= float(value)
            self.y_value.set(value_y)
            self.set_y()
        except ValueError:
            print("Valeur non valide pour Y.")
            
            
    def update_pos_label_z(self, value):
        try:
            value_z= float(value)
            self.z_value.set(value_z)
            self.set_z()
        except ValueError:
            print("Valeur non valide pour Z.")
            
          # calcul de nx
    def calculate_nX(self):
          # Calcul de J3 en fonction de J1 et J2
          j1 = self.angle_j1.get()
          j1=math.radians(j1)
          j2 = self.angle_j2.get()
          j2=math.radians(j2)
          j3 = self.angle_j3.get()
          j3=math.radians(j3)
          j4 = self.angle_j4.get()
          j4=math.radians(j4)
          j5 = self.angle_j5.get()
          j5=math.radians(j5)
          nx=math.cos(j1)*math.cos(j5)*math.cos(j2+j3+j4) + math.sin(j1)*math.sin(j5)
          nx=round(nx,2)
          self.nx.set(nx)
          self.entry_nx.delete(0, tk.END)
          self.entry_nx.insert(0, str(nx))
    
    def update_ort_label_nx(self, value):
        try:
            value_nx= float(value)
            self.nx.set(value_nx)
            self.set_nx()
        except ValueError:
            print("Valeur non valide pour nX.")
    
    def set_nx(self):
        nx = round(float(self.nx.get()),2)
        print(f"Réglage de nx à {nx}")
        self.entry_nx.delete(0, tk.END)
        self.entry_nx.insert(0, str(nx))
        
        self.calculate_angles()
      
        
    
        # calcul de ny
    def calculate_ny(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        ny=math.sin(j1)*math.cos(j5)*math.cos(j2+j3+j4) - math.cos(j1)*math.sin(j5)
        ny=round(ny,2)
        self.ny.set(ny)
        self.entry_ny.delete(0, tk.END)
        self.entry_ny.insert(0, str(ny))
    
    def update_ort_label_ny(self, value):
        try:
            value_ny= float(value)
            self.ny.set(value_ny)
            self.set_ny()
        except ValueError:
            print("Valeur non valide pour ny.")
    
    def set_ny(self):
        ny = round(float(self.ny.get()),2)
        print(f"Réglage de nx à {ny}")
        self.entry_ny.delete(0, tk.END)
        self.entry_ny.insert(0, str(ny))
        
        self.calculate_angles()
        
    
    
        # calcul de nz
    def calculate_nz(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        nz= - math.cos(j5)*math.sin(j2+j3)
        nz=round(nz,2)
        self.nz.set(nz)
        self.entry_nz.delete(0, tk.END)
        self.entry_nz.insert(0, str(nz))
        
    def update_ort_label_nz(self, value):
        try:
            value_nz= float(value)
            self.nz.set(value_nz)
            self.set_nz()
        except ValueError:
            print("Valeur non valide pour nz.")
    
    def set_nz(self):
        nz = round(float(self.nz.get()),2)
        print(f"Réglage de nx à {nz}")
        self.entry_nz.delete(0, tk.END)
        self.entry_nz.insert(0, str(nz))
        
        self.calculate_angles()
        
    
       # calcul de sx
    def calculate_sX(self):
       # Calcul de J3 en fonction de J1 et J2
       j1 = self.angle_j1.get()
       j1=math.radians(j1)
       j2 = self.angle_j2.get()
       j2=math.radians(j2)
       j3 = self.angle_j3.get()
       j3=math.radians(j3)
       j4 = self.angle_j4.get()
       j4=math.radians(j4)
       j5 = self.angle_j5.get()
       j5=math.radians(j5)
       sx= -math.cos(j1)*math.sin(j5)*math.cos(j2+j3+j4) + math.sin(j1)*math.cos(j5)
       sx=round(sx,2)
       self.sx.set(sx)
       self.entry_sx.delete(0, tk.END)
       self.entry_sx.insert(0, str(sx))
        
    def update_slider_label_sx(self, value):
        try:
            value_sx= float(value)
            self.sx.set(value_sx)
            self.set_sx()
        except ValueError:
            print("Valeur non valide pour sx.")
    
    def set_sx(self):
        sx = round(float(self.sx.get()),2)
        print(f"Réglage de sx à {sx}")
        self.entry_sx.delete(0, tk.END)
        self.entry_sx.insert(0, str(sx))
        
        self.calculate_angles()
        
        # calcul de sy
    def calculate_sy(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        sy= -math.sin(j1)*math.sin(j5)*math.cos(j2+j3+j4) - math.cos(j1)*math.sin(j5)
        sy=round(sy,2)
        self.sy.set(sy)
        self.entry_sy.delete(0, tk.END)
        self.entry_sy.insert(0, str(sy))
        
    def update_slider_label_sy(self, value):
        try:
            value_sy= float(value)
            self.sy.set(value_sy)
            self.set_sy()
        except ValueError:
            print("Valeur non valide pour sy.")
    
    def set_sy(self):
        sy = round(float(self.sy.get()),2)
        print(f"Réglage de sy à {sy}")
        self.entry_sy.delete(0, tk.END)
        self.entry_sy.insert(0, str(sy))
        
        self.calculate_angles()
        
        # calcul de sz
    def calculate_sz(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        sz= math.sin(j5)*math.cos(j2+j3+j4) 
        sz=round(sz,2)
        self.sz.set(sz)
        self.entry_sz.delete(0, tk.END)
        self.entry_sz.insert(0, str(sz))
    
    def update_slider_label_sz(self, value):
        try:
            value_sz= float(value)
            self.sz.set(value_sz)
            self.set_sz()
        except ValueError:
            print("Valeur non valide pour sz.")
    
    def set_sz(self):
        sz = round(float(self.sz.get()),2)
        print(f"Réglage de sz à {sz}")
        self.entry_sz.delete(0, tk.END)
        self.entry_sz.insert(0, str(sz))
        
        self.calculate_angles()
    
        # calcul de ax
    def calculate_aX(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        ax= -math.cos(j1)*math.sin(j2+j3+j4) 
        ax=round(ax,2)
        self.ax.set(ax)
        self.entry_ax.delete(0, tk.END)
        self.entry_ax.insert(0, str(ax))
        
    def update_approach_label_ax(self, value):
        try:
            value_ax= float(value)
            self.ax.set(value_ax)
            self.set_ax()
        except ValueError:
            print("Valeur non valide pour ax.")
    
    def set_ax(self):
        ax = round(float(self.ax.get()),2)
        print(f"Réglage de ax à {ax}")
        self.entry_ax.delete(0, tk.END)
        self.entry_ax.insert(0, str(ax))
        
        self.calculate_angles()
        
        
        # calcul de ay
    def calculate_ay(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j1=math.radians(j1)
        j2 = self.angle_j2.get()
        j2=math.radians(j2)
        j3 = self.angle_j3.get()
        j3=math.radians(j3)
        j4 = self.angle_j4.get()
        j4=math.radians(j4)
        j5 = self.angle_j5.get()
        j5=math.radians(j5)
        ay= -math.sin(j1)*math.sin(j2+j3+j4) 
        ay=round(ay,2)
        self.ay.set(ay)
        self.entry_ay.delete(0, tk.END)
        self.entry_ay.insert(0, str(ay))
        
    def update_approach_label_ay(self, value):
        try:
            value_ay= float(value)
            self.ay.set(value_ay)
            self.set_ay()
        except ValueError:
            print("Valeur non valide pour ay.")
    
    def set_ay(self):
        ay = round(float(self.ay.get()),2)
        print(f"Réglage de ay à {ay}")
        self.entry_ay.delete(0, tk.END)
        self.entry_ay.insert(0, str(ay))
        
        self.calculate_angles()
        
    
       # calcul de az
    def calculate_az(self):
       # Calcul de J3 en fonction de J1 et J2
       j1 = self.angle_j1.get()
       j1=math.radians(j1)
       j2 = self.angle_j2.get()
       j2=math.radians(j2)
       j3 = self.angle_j3.get()
       j3=math.radians(j3)
       j4 = self.angle_j4.get()
       j4=math.radians(j4)
       j5 = self.angle_j5.get()
       j5=math.radians(j5)
       az= -math.cos(j2+j3+j4) 
       az=round(az,2)
       self.az.set(az)
       self.entry_az.delete(0, tk.END)
       self.entry_az.insert(0, str(az))
    
    def update_approach_label_az(self, value):
        try:
            value_az= float(value)
            self.az.set(value_az)
            self.set_az()
        except ValueError:
            print("Valeur non valide pour az.")
    
    def set_az(self):
        az = round(float(self.az.get()),2)
        print(f"Réglage de ay à {az}")
        self.entry_az.delete(0, tk.END)
        self.entry_az.insert(0, str(az))
        
        self.calculate_angles()
    def start_update_pid_home(self):
        self.stop_process_flag = False
        self.open_second_window()
        # Désactiver le bouton pendant la mise à jour automatique
        self.btn_pid.config(state=tk.DISABLED)
        self.btn_home.config(state=tk.DISABLED)
        
        # Appeler la fonction update_pid de manière récursive jusqu'à ce que les valeurs soient égales aux valeurs cibles
        self.auto_update_pid_home()

    def auto_update_pid_home(self):
        self.update_pid_home()
        # Si la variable de drapeau indique de ne pas arrêter le processus, appeler récursivement
        if not self.stop_process_flag:
            # Vérifier si les valeurs sont égales aux valeurs cibles
            if self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
                # Si oui, activer à nouveau le bouton
                self.btn_pid.config(state=tk.NORMAL)
                self.btn_home.config(state=tk.NORMAL)
            else:
                
                # Si non, planifier la prochaine mise à jour après un court délai
                self.root.after(100, self.auto_update_pid_home)  # Appeler après 1000 ms (1 seconde)
        
            
       
        
    def update_pid_home(self):
        self.target_positions = [90, 90, -90,
                                 -90, 0]

        self.current_positions = [self.angle_j1.get(), self.angle_j2.get(), self.angle_j3.get(),
                                  self.angle_j4.get(), self.angle_j5.get()]

        # Calculer les erreurs PID
        errors = [target - current for target, current in zip(self.target_positions, self.current_positions)]
        self.integral = [integral + error for integral, error in zip(self.integral, errors)]
        derivative = [error - prev_error for error, prev_error in zip(errors, self.prev_error)]

        # Calculer les commandes PID
        pid_commands = [self.kp * errors[i] + self.ki * self.integral[i] + self.kd * derivative[i] for i in range(len(errors))]

        # pour enregistrer l'erreur actuelle dans l'historique
        total_error = sum(errors)
        self.error_history.append(total_error)
        
        if not self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
           self.update_motors_home(pid_commands)

           # Mettre à jour l'erreur précédente
           self.prev_error = errors

           # Appel de la fonction pour mettre à jour la représentation graphique
           self.update_plot()
            

    def update_motors_home(self, commands):
    # Mettre à jour la position actuelle du moteur (simuler le mouvement)
        for i, command in enumerate(commands):
            new_position =round( min(self.current_positions[i] + command, self.current_positions[i] + 5),2)
            #getattr(self, f"angle_j{i + 1}", new_position)
            if i==0:
                self.angle_j1.set(new_position)
                self.entry_j1.delete(0, tk.END)
                self.entry_j1.insert(0, str(new_position))
            if i==1:
                self.angle_j2.set(new_position)
                self.entry_j2.delete(0, tk.END)
                self.entry_j2.insert(0, str(new_position))
            if i==2:
                self.angle_j3.set(new_position)
                self.entry_j3.delete(0, tk.END)
                self.entry_j3.insert(0, str(new_position))
            if i==3:
                self.angle_j4.set(new_position)
                self.entry_j4.delete(0, tk.END)
                self.entry_j4.insert(0, str(new_position))
            if i==4:
                self.angle_j5.set(new_position)
                self.entry_j5.delete(0, tk.END)
                self.entry_j5.insert(0, str(new_position))
                
          
            self.calculate_X()
            self.calculate_Y()
            self.calculate_Z()
                
            self.calculate_nX()
            self.calculate_ny()
            self.calculate_nz()
                
            self.calculate_sX()
            self.calculate_sy()
            self.calculate_sz()
                
            self.calculate_aX()
            self.calculate_ay()
            self.calculate_az()
             
            #self.angle_j[i + 1].set(new_position)
    
        # attente pause
        time.sleep(0.1)
        
    def open_second_window(self):
        # Créer la figure et l'axe pour le graphique
        self.fig, self.ax0 = plt.subplots()
        self.ax0.set_xlabel('Iterations')
        self.ax0.set_ylabel('Total Error')
        self.ax0.set_title('PID') 
        plt.show()
        
    def quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    controller = RobotController()
    controller.run()
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 07:36:38 2023
@author: magnn
"""

import tkinter as tk
from tkinter import ttk
from time import strftime
import serial
import tkinter.messagebox as messagebox

import math


Longueur_d1 = 260
Longeur_d5 = 171

distance_a2 = 228
distance_a3=228
distance_a4=90

cursor="hand2" # type de curseur
justify="center"

class RobotController:
    MIN_ANGLE = -180
    MAX_ANGLE = 180

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot Controller")

         # Création d'un style ttk
        style = ttk.Style()
        style.configure("My.TLabelframe", background="blue")

         # Section Menu
        bold_font = ('Helvetica', 12, 'bold')

        self.menu_frame = ttk.LabelFrame(self.root, text="CONTROLE DU ROBOT", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.menu_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
       
        self.btn_start = tk.Button(self.menu_frame, text="✔ Démarrer",  command=self.start_robot, background="lime", 
                                   font=bold_font, height=2, width=20, cursor=cursor )
        self.btn_stop = tk.Button(self.menu_frame, text="Arrêter", command=self.stop_robot, 
                                  font=bold_font, height=2, width=20, cursor=cursor)
        self.btn_quit = tk.Button(self.menu_frame, text="Quitter", command=self.quit, 
                                  font=bold_font, height=2, width=20, cursor=cursor)
        self.btn_home = tk.Button(self.menu_frame, text="Home",  command=self.robot_home,  
                                  font=bold_font, height=2, width=20, cursor=cursor)

       # Configuration des boutons avec des marges
        for i, btn in enumerate([self.btn_start, self.btn_stop, self.btn_quit, self.btn_home]):
           btn.grid(row=0, column=i, padx=10, pady=10)
          
        #section commandes 
        self.var_frame = ttk.LabelFrame(self.root, text="COMMANDE", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.var_frame.grid(row=1, column=0, padx=10, pady=10)
          
        # parameters
        self.param_frame = ttk.LabelFrame(self.var_frame, text="Parameters", padding=(10,10))
        self.param_frame.grid(row=0, column=1, padx=10, pady=10)
        
        # subsections angles
        self.sub_frame = ttk.LabelFrame(self.var_frame, text=" ", labelanchor="n", padding=(10, 10))
        self.sub_frame.grid(row=0, column=0, padx=10, pady=10)

        # Section Angles
        self.angles_frame = ttk.LabelFrame(self.sub_frame, text="JOINT ANGLES (Deg)", labelanchor="n", padding=(10, 10))
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
        self.tool_frame = ttk.LabelFrame(self.param_frame, text="POSITION OUTIL", labelanchor="n", padding=(10, 10))
        self.tool_frame.grid(row=0, column=0, padx=10, pady=10)

        self.x_value = tk.DoubleVar()
        self.x_value.set(0.0)  # Initialize to the initial value of x

        self.y_value = tk.DoubleVar()
        self.y_value.set(0.0)  # Initialize to the initial value of y

        self.z_value = tk.DoubleVar()
        self.z_value.set(0.0)  # Initialize to the initial value of z

        self.create_tool_widgets()

        # Section Vitesses
        self.vitesses_frame = ttk.LabelFrame(self.param_frame, text="VITESSES", labelanchor="n", padding=(10, 10))
        self.vitesses_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.tool_velocity = tk.DoubleVar()
        self.tool_velocity.set(0.0)  # Initialize to the initial value of tool velocity

        self.base_motor_velocity = tk.DoubleVar()
        self.base_motor_velocity.set(0.0)   # Initialize to the initial value of base motor velocity

        self.tranverse_motor_velocity = tk.DoubleVar()
        self.tranverse_motor_velocity.set(0.0)  # Initialize to the initial value of 
        
        self.create_velocity_widgets()

        # Section Raspberry Pi
        style.configure("My.TLabelframe", background="white")
        self.pi_frame = ttk.LabelFrame(self.sub_frame, text="RASPBERRY PI", labelanchor="n", padding=(10, 10), style="My.TLabelframe")
        self.pi_frame.grid(row=1, column=0, padx=10, pady=10)
        # defaut self.root, row = 3, col=0
        self.create_raspberry_pi_widgets()

        self.pi_serial = None

        # Display real-time clock
        self.clock_label = ttk.Label(self.menu_frame, text="",  background="white", 
                                  font=bold_font, width=15, justify="center")
        self.clock_label.grid(row=0, column=4, padx=10, pady=10)

        # Update clock every second
        self.update_clock()

    def update_clock(self):
        time_string = strftime("%H:%M:%S %p")
        self.clock_label.config(text=time_string)
        self.root.after(1000, self.update_clock)

    def create_raspberry_pi_widgets(self):
        bold_font = ('Helvetica', 12, 'bold')
        background="lime"
        height=1
        width=20
        self.pi_serial_port_label = tk.Label(self.pi_frame, text="Port Raspberry :", font=bold_font, background="white")
        self.pi_serial_port_entry = tk.Entry(self.pi_frame, justify=justify, font=bold_font, width=width)
        self.pi_connect_button = tk.Button(self.pi_frame, text="Connect To Raspberry", command=self.connect_to_pi,
                                           background=background, height=height, width=17, font=5, cursor=cursor)

        self.pi_serial_port_label.grid(row=0, column=0, padx=10, pady=5)
        self.pi_serial_port_entry.grid(row=0, column=1, padx=10, pady=5)
        self.pi_connect_button.grid(row=1, column=0, columnspan=2, pady=10)


    def create_angle_widgets(self):
        # Section Menu
        bold_font = ('Helvetica', 12, 'bold')
        background="lime"
        height=1
        font=5
        width=5
        background2="blue"
        width2=10
        fg='white'
        self.label_j1 = tk.Label(self.angles_frame, text="Angle J1:", font=bold_font)
        self.slider_j1 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.angle_j1,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j1(value), cursor=cursor)
        self.entry_j1 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"),justify=justify, font=bold_font, width=width2)
        self.btn_j1_inc = tk.Button(self.angles_frame, text="J1 +", command=self.increment_j1, 
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j1_dec = tk.Button(self.angles_frame, text="J1 -", command=self.decrement_j1,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)

        self.label_j2 = tk.Label(self.angles_frame, text="Angle J2:", font=bold_font)
        self.slider_j2 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.angle_j2,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j2(value), cursor=cursor)
        self.entry_j2 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j2_inc = tk.Button(self.angles_frame, text="J2 +", command=self.increment_j2,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j2_dec = tk.Button(self.angles_frame, text="J2 -", command=self.decrement_j2,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        
        self.label_j3 = tk.Label(self.angles_frame, text="Angle J3:",font=bold_font)
        self.slider_j3 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.label_j3,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j3(value), cursor=cursor)
        self.entry_j3 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j3_inc = tk.Button(self.angles_frame, text="J3 +", command=self.increment_j3,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j3_dec = tk.Button(self.angles_frame, text="J3 -", command=self.decrement_j3,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        self.label_j4 = tk.Label(self.angles_frame, text="Angle J4:", font=bold_font)
        self.slider_j4 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.label_j4,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j4(value), cursor=cursor)
        self.entry_j4 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j4_inc = tk.Button(self.angles_frame, text="J4 +", command=self.increment_j4,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j4_dec = tk.Button(self.angles_frame, text="J4 -", command=self.decrement_j4,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        self.label_j5 = tk.Label(self.angles_frame, text="Angle J5:", font=bold_font)
        self.slider_j5 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.label_j5,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j5(value), cursor=cursor)
        self.entry_j5 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width2)
        self.btn_j5_inc = tk.Button(self.angles_frame, text="J5 +", command=self.increment_j5,
                                    background=background, height=height, width=width, font=font, cursor=cursor)
        self.btn_j5_dec = tk.Button(self.angles_frame, text="J5 -", command=self.decrement_j5,
                                    background=background2, height=height, width=width, font=font, cursor=cursor, fg=fg)
        
        # 
        # Configuration des boutons avec des marges
        for i, btn in enumerate([self.label_j1, self.slider_j1, self.entry_j1, self.btn_j1_inc,self.btn_j1_dec]):
            btn.grid(row=0, column=i, padx=10, pady=10)
            
        for i, btn in enumerate([self.label_j2, self.slider_j2, self.entry_j2, self.btn_j2_inc,self.btn_j2_dec]):
             btn.grid(row=1, column=i, padx=10, pady=10)

        """
        self.label_j2.grid(row=2, column=0, padx=10, pady=10)
        self.slider_j2.grid(row=2, column=1, padx=10, pady=10)
        self.entry_j2.grid(row=2, column=2, padx=10, pady=10)
        self.btn_j2_inc.grid(row=3, column=1, padx=10, pady=10)
        self.btn_j2_dec.grid(row=3, column=2, padx=10, pady=10)
        """
        for i, btn in enumerate([self.label_j3, self.slider_j3, self.entry_j3, self.btn_j3_inc,self.btn_j3_dec]):
             btn.grid(row=2, column=i, padx=10, pady=10)
        
        for i, btn in enumerate([self.label_j4, self.slider_j4, self.entry_j4, self.btn_j4_inc,self.btn_j4_dec]):
             btn.grid(row=3, column=i, padx=10, pady=10)
        
        for i, btn in enumerate([self.label_j5, self.slider_j5, self.entry_j5, self.btn_j5_inc,self.btn_j5_dec]):
             btn.grid(row=4, column=i, padx=10, pady=10)
        

    def create_tool_widgets(self):
        bold_font = ('Helvetica', 12, 'bold')
        #background="lime"
        width=7
        width=10
        self.label_x = tk.Label(self.tool_frame, text="X (mm):", font=bold_font)
        self.slider_x = ttk.Scale(self.tool_frame, from_=-600, to=600, variable=self.x_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_x(value), cursor=cursor)
        self.entry_x = tk.Entry(self.tool_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_y = tk.Label(self.tool_frame, text="Y (mm):", font=bold_font)
        self.slider_y = ttk.Scale(self.tool_frame, from_=-600, to=600, variable=self.y_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_y(value), cursor=cursor)
        self.entry_y = tk.Entry(self.tool_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_z = tk.Label(self.tool_frame, text="Z (mm):", font=bold_font)
        self.slider_z = ttk.Scale(self.tool_frame, from_=-180, to=180, variable=self.z_value,
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
        
    def create_velocity_widgets(self):
        bold_font = ('Helvetica', 12, 'bold')
        #background="brown"
        width=7
        width=10
        self.label_tool_velocity = tk.Label(self.vitesses_frame, text="V_Tool (m/s):", font=bold_font)
        self.slider_tool_velocity = ttk.Scale(self.vitesses_frame, from_=-180, to=180, variable=self.tool_velocity,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_tool_velocity_label(value), cursor=cursor)
        self.entry_tool_velocity = tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)
            
        self.label_base_motor_velocity = tk.Label(self.vitesses_frame, text="M_Base (tr/min):", font=bold_font)
        self.slider_base_motor_velocity = ttk.Scale(self.vitesses_frame, from_=-180, to=180, variable=self.base_motor_velocity,
                                       orient=tk.HORIZONTAL, command=lambda value: self.update_base_motor_velocity_label(value), cursor=cursor)
        self.entry_base_motor_velocity = tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_tranverse_motor_velocity = tk.Label(self.vitesses_frame, text="Moteur2 (tr/min):", font=bold_font)
        self.slider_tranverse_motor_velocity= ttk.Scale(self.vitesses_frame, from_=-180, to=180, variable=self.tranverse_motor_velocity,
                                       orient=tk.HORIZONTAL, command=lambda value: self.update_tranverse_motor_velocity_label(value), cursor=cursor)
        self.entry_tranverse_motor_velocity= tk.Entry(self.vitesses_frame, textvariable=tk.StringVar(value="0.0"), justify=justify, font=bold_font, width=width)

        self.label_tool_velocity.grid(row=0, column=0, padx=10, pady=10)
        self.slider_tool_velocity.grid(row=0, column=1, padx=10, pady=10)
        self.entry_tool_velocity.grid(row=0, column=2, padx=10, pady=10)

        self.label_base_motor_velocity.grid(row=2, column=0, padx=10, pady=10)
        self.slider_base_motor_velocity.grid(row=2, column=1, padx=10, pady=10)
        self.entry_base_motor_velocity.grid(row=2, column=2, padx=10, pady=10)

        self.label_tranverse_motor_velocity.grid(row=4, column=0, padx=10, pady=10)
        self.slider_tranverse_motor_velocity.grid(row=4, column=1, padx=10, pady=10)
        self.entry_tranverse_motor_velocity.grid(row=4, column=2, padx=10, pady=10)

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
    
    def calculate_j1(self):
        # Calcul de J3 en fonction de J1 et J2
        x = self.x_value.get()
        y= self.y_value.get()
        j1 = math.atan2(y, x)
        j1 =math.degrees(j1)
        self.angle_j1.set(j1)
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(j1))

    def set_j1(self):
        angle_j1 = int(self.angle_j1.get())
        print(f"Réglage de l'angle J1 à {angle_j1} degrés")
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(angle_j1))
       # self.calculate_j3()
        self.calculate_X()
        self.calculate_Y()

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
        angle_j2 = int(self.angle_j2.get())
        print(f"Réglage de l'angle J2 à {angle_j2} degrés")
        self.entry_j2.delete(0, tk.END)
        self.entry_j2.insert(0, str(angle_j2))
       # self.calculate_j3()
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
        
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
        angle_j3 = int(self.angle_j3.get())
        print(f"Réglage de l'angle J3 à {angle_j3} degrés")
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(angle_j3))
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
           
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
        angle_j4 = int(self.angle_j4.get())
        print(f"Réglage de l'angle J4 à {angle_j4} degrés")
        self.entry_j4.delete(0, tk.END)
        self.entry_j4.insert(0, str(angle_j4))
        self.calculate_X()
        self.calculate_Y()
        self.calculate_Z()
        
         
    def increment_j5(self):
        current_value = self.angle_j5.get()
        if current_value < 180:
            self.angle_j5.set(current_value + 1)
            self.set_j5()

    def decrement_j5(self):
        current_value = self.angle_j3.get()
        if current_value > -180:
            self.angle_j5.set(current_value - 1)
            self.set_j5()

    def set_j5(self):
        angle_j5 = int(self.angle_j5.get())
        print(f"Réglage de l'angle J5 à {angle_j5} degrés")
        self.entry_j5.delete(0, tk.END)
        self.entry_j5.insert(0, str(angle_j5))
        

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

    def calculate_j3(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j2 = self.angle_j2.get()
        j3 = 360 - (j1 + j2)
        self.angle_j3.set(j3)
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(j3))
    
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
         self.x_value.set(x)
         self.entry_x.delete(0, tk.END)
         self.entry_x.insert(0, str(x))

    def set_x(self):
        x_value = int(self.x_value.get())
        print(f"Réglage de X à {x_value} mm")
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(x_value))
        self.calculate_j1()
        
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
        self.y_value.set(y)
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y))
        
    def set_y(self):
        y_value = int(self.y_value.get())
        print(f"Réglage de Y à {y_value} mm")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y_value))
        self.calculate_j1()
    
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
        self.z_value.set(z)
        self.entry_z.delete(0, tk.END)
        self.entry_z.insert(0, str(z))
    
    def set_z(self):
        z_value = int(self.z_value.get())
        print(f"Réglage de Z à {z_value} mm")
        self.entry_z.delete(0, tk.END)
        self.entry_z.insert(0, str(z_value))
    
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
            
    def robot_home(self):
        # Méthode pour revenir à la position d'origine du robot
        self.angle_j1.set(90)
        self.angle_j2.set(-90.0)
        self.angle_j3.set(90)
        self.angle_j4.set(-90.0)
        self.angle_j5.set(0.0)
        
        #self.calculate_j3()
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(self.angle_j1.get()))
        
        self.entry_j2.delete(0, tk.END)
        self.entry_j2.insert(0, str(self.angle_j2.get()))
        
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(self.angle_j3.get())) 
        
        self.entry_j4.delete(0, tk.END)
        self.entry_j4.insert(0, str(self.angle_j4.get())) 
        
        self.entry_j5.delete(0, tk.END)
        self.entry_j5.insert(0, str(self.angle_j5.get())) 
        
        self.calculate_X()
        self.entry_x.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ x
        self.entry_x.insert(0, str(self.x_value.get()))  # Mettez à jour la valeur de Z dans le champ
        
        self.calculate_Y()
        self.entry_y.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ y
        self.entry_y.insert(0, str(self.y_value.get()))  # Mettez à jour la valeur de Z dans le champ
        
        self.calculate_Z()
        self.entry_z.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ Z
        self.entry_z.insert(0, str(self.z_value.get()))  # Mettez à jour la valeur de Z dans le champ


    def quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    controller = RobotController()
    controller.run()
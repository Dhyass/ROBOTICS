# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 06:00:03 2023

@author: magnn
"""



import tkinter as tk
from tkinter import ttk
from time import strftime
import serial
from PIL import Image, ImageTk

class RobotController:
    MIN_ANGLE = -180
    MAX_ANGLE = 180

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robot Controller")
        
        

        # Section Menu
        # Section Menu
        self.menu_frame = ttk.LabelFrame(self.root, text="Menu", labelanchor="n", padding=(10, 10))
        self.menu_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)  # Adjusted columnspan

        self.btn_start = tk.Button(self.menu_frame, text="Démarrer",  command=self.start_robot)
        self.btn_stop = tk.Button(self.menu_frame, text="Arrêter",  command=self.stop_robot)
        self.btn_quit = tk.Button(self.menu_frame, text="Quitter",  command=self.quit)
        self.btn_home = tk.Button(self.menu_frame, text="Home",  command=self.robot_home)

        self.btn_start.grid(row=0, column=0, padx=10, pady=10)
        self.btn_stop.grid(row=0, column=1, padx=10, pady=10)
        self.btn_quit.grid(row=0, column=2, padx=10, pady=10)
        self.btn_home.grid(row=0,column=3, padx=10,pady=10)
        
        # Section Angles
        self.angles_frame = ttk.LabelFrame(self.root, text="JIONT ANGLES(Deg)", labelanchor="n", padding=(10, 10))
        self.angles_frame.grid(row=1, column=0, padx=10, pady=10)

        self.angle_j1 = tk.DoubleVar()
        self.angle_j1.set(0.0)  # Initialize to the initial value of J1

        self.angle_j2 = tk.DoubleVar()
        self.angle_j2.set(0.0)  # Initialize to the initial value of J2

        self.angle_j3 = tk.DoubleVar()
        self.angle_j3.set(0.0)  # Initialize to the initial value of J3

        self.label_j1 = tk.Label(self.angles_frame, text="Angle J1:")
        self.slider_j1 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.angle_j1,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j1(value))
        self.entry_j1 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"))
        self.btn_j1_inc = tk.Button(self.angles_frame, text="J1 +", command=self.increment_j1)
        self.btn_j1_dec = tk.Button(self.angles_frame, text="J1 -", command=self.decrement_j1)

        self.label_j2 = tk.Label(self.angles_frame, text="Angle J2:")
        self.slider_j2 = ttk.Scale(self.angles_frame, from_=-180, to=180, variable=self.angle_j2,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_angle_label_j2(value))
        self.entry_j2 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"))
        self.btn_j2_inc = tk.Button(self.angles_frame, text="J2 +", command=self.increment_j2)
        self.btn_j2_dec = tk.Button(self.angles_frame, text="J2 -", command=self.decrement_j2)

        self.label_j3 = tk.Label(self.angles_frame, text="Angle J3:")
        self.entry_j3 = tk.Entry(self.angles_frame, textvariable=tk.StringVar(value="0.0"))

        self.label_j1.grid(row=0, column=0, padx=10, pady=10)
        self.slider_j1.grid(row=0, column=1, padx=10, pady=10)
        self.entry_j1.grid(row=0, column=2, padx=10, pady=10)
        self.btn_j1_inc.grid(row=1, column=1, padx=10, pady=10)
        self.btn_j1_dec.grid(row=1, column=2, padx=10, pady=10)

        self.label_j2.grid(row=2, column=0, padx=10, pady=10)
        self.slider_j2.grid(row=2, column=1, padx=10, pady=10)
        self.entry_j2.grid(row=2, column=2, padx=10, pady=10)
        self.btn_j2_inc.grid(row=3, column=1, padx=10, pady=10)
        self.btn_j2_dec.grid(row=3, column=2, padx=10, pady=10)

        self.label_j3.grid(row=4, column=0, padx=10, pady=10)
        self.entry_j3.grid(row=4, column=1, padx=10, pady=10)
        
        # Section Positons de l'outils
        self.tool_frame = ttk.LabelFrame(self.root, text="Position Outil", labelanchor="n", padding=(10, 10))
        self.tool_frame.grid(row=1, column=1, padx=10, pady=10)

        self.x_value = tk.DoubleVar()
        self.x_value.set(0.0)  # Initialize to the initial value of x

        self.y_value = tk.DoubleVar()
        self.y_value.set(0.0)  # Initialize to the initial value of y

        self.z_value = tk.DoubleVar()
        self.z_value.set(0.0)  # Initialize to the initial value of z

        self.label_x = tk.Label(self.tool_frame , text="X (mm):")
        self.slider_x = ttk.Scale(self.tool_frame , from_=-180, to=180, variable=self.x_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_x(value))
        self.entry_x = tk.Entry(self.tool_frame , textvariable=tk.StringVar(value="0.0"))
        

        self.label_y = tk.Label(self.tool_frame , text="Y (mm):")
        self.slider_y = ttk.Scale(self.tool_frame , from_=-180, to=180, variable=self.y_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_y(value))
        self.entry_y = tk.Entry(self.tool_frame , textvariable=tk.StringVar(value="0.0"))
        

        self.label_z = tk.Label(self.tool_frame , text="Z (mm):")
        self.slider_z = ttk.Scale(self.tool_frame , from_=-180, to=180, variable=self.z_value,
                                   orient=tk.HORIZONTAL, command=lambda value: self.update_pos_label_z(value))
        self.entry_z = tk.Entry(self.tool_frame , textvariable=tk.StringVar(value="0.0"))

        self.label_x.grid(row=0, column=0, padx=10, pady=10)
        self.slider_x.grid(row=0, column=1, padx=10, pady=10)
        self.entry_x.grid(row=0, column=2, padx=10, pady=10)
        

        self.label_y.grid(row=2, column=0, padx=10, pady=10)
        self.slider_y.grid(row=2, column=1, padx=10, pady=10)
        self.entry_y.grid(row=2, column=2, padx=10, pady=10)
        
        self.label_z.grid(row=4, column=0, padx=10, pady=10)
        self.slider_z.grid(row=4, column=1,padx=10,pady=10)
        self.entry_z.grid(row=4, column=2, padx=10, pady=10)

        # Section Vitesses
        self.vitesses_frame = ttk.LabelFrame(self.root, text="Vitesses", labelanchor="n", padding=(10, 10))
        self.vitesses_frame.grid(row=2, column=0, padx=10, pady=10)

        # Add your elements for the Vitesses section here...

        # Section Raspberry Pi
        self.pi_frame = ttk.LabelFrame(self.root, text="Raspberry Pi", labelanchor="n", padding=(10, 10))
        self.pi_frame.grid(row=3, column=0, padx=10, pady=10)

        self.pi_serial_port_label = tk.Label(self.pi_frame, text="Port série de la Raspberry Pi:")
        self.pi_serial_port_entry = tk.Entry(self.pi_frame)
        self.pi_connect_button = tk.Button(self.pi_frame, text="Connecter à la Raspberry Pi", command=self.connect_to_pi)

        self.pi_serial_port_label.grid(row=0, column=0, padx=10, pady=5)
        self.pi_serial_port_entry.grid(row=0, column=1, padx=10, pady=5)
        self.pi_connect_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.pi_serial = None

        # ... (Remaining code)

        # Affichage de l'heure en temps réel
        self.clock_label = ttk.Label(self.root, text="")
        self.clock_label.grid(row=4, column=0, pady=10)

        # Mise à jour de l'heure chaque seconde
        self.update_clock()

    def update_clock(self):
        time_string = strftime("%H:%M:%S %p")
        self.clock_label.config(text=time_string)
        self.root.after(1000, self.update_clock)

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

    # Remaining methods unchanged
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

    def set_j1(self):
        angle_j1 = int(self.angle_j1.get())
        print(f"Réglage de l'angle J1 à {angle_j1} degrés")
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(angle_j1))
        self.calculate_j3()

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
        self.calculate_j3()

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

    def calculate_j3(self):
        # Calcul de J3 en fonction de J1 et J2
        j1 = self.angle_j1.get()
        j2 = self.angle_j2.get()
        j3 = 360 - (j1 + j2)
        self.angle_j3.set(j3)
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(j3))
    
    def set_x(self):
        x_value = int(self.x_value.get())
        print(f"Réglage de X à {x_value} mm")
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(x_value))
    
    def set_y(self):
        y_value = int(self.y_value.get())
        print(f"Réglage de Y à {y_value} mm")
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y_value))
        
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
        self.angle_j1.set(30.0)
        self.angle_j2.set(-70.0)
        self.calculate_j3()
        self.entry_j1.delete(0, tk.END)
        self.entry_j1.insert(0, str(30.0))
        
        self.entry_j2.delete(0, tk.END)
        self.entry_j2.insert(0, str(-70.0))
        
        self.entry_j3.delete(0, tk.END)
        self.entry_j3.insert(0, str(self.angle_j3.get())) 
        
        self.x_value.set(-10.0)
        self.entry_x.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ x
        self.entry_x.insert(0, str(-110.0))  # Mettez à jour la valeur de Z dans le champ
        self.y_value.set(90.0)
        self.entry_y.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ y
        self.entry_y.insert(0, str(90.0))  # Mettez à jour la valeur de Z dans le champ
        self.z_value.set(-110.0)
        self.entry_z.delete(0, tk.END)  # Supprimez la valeur actuelle dans le champ Z
        self.entry_z.insert(0, str(-110.0))  # Mettez à jour la valeur de Z dans le champ


    def quit(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    controller = RobotController()
    controller.run()

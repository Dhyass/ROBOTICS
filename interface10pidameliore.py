# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 22:14:46 2023

@author: magnn
"""

import time
import tkinter as tk

class YourClassName:
    def update_pid(self):
        self.target_positions = [self.angle_j1_cible.get(), self.angle_j2_cible.get(), self.angle_j3_cible.get(),
                                self.angle_j4_cible.get(), self.angle_j5_cible.get()]

        self.current_positions = [self.angle_j1.get(), self.angle_j2.get(), self.angle_j3.get(),
                                  self.angle_j4.get(), self.angle_j5.get()]

        errors = [target - current for target, current in zip(self.target_positions, self.current_positions)]
        self.integral = [integral + error for integral, error in zip(self.integral, errors)]
        derivative = [error - prev_error for error, prev_error in zip(errors, self.prev_error)]

        pid_commands = [self.kp * errors[i] + self.ki * self.integral[i] + self.kd * derivative[i] for i in range(len(errors))]

        total_error = sum(errors)
        self.error_history.append(total_error)

        if not self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
            self.update_motors(pid_commands)
            self.prev_error = errors
            self.update_plot()

    def are_positions_close(self, current_positions, target_positions, tolerance):
        return all(abs(curr - target) < tolerance for curr, target in zip(current_positions, target_positions))

    def update_motors(self, commands):
        for i, command in enumerate(commands):
            new_position = round(min(self.current_positions[i] + command, self.current_positions[i] + 5), 2)
            setattr(self, f"angle_j{i + 1}", new_position)
            entry = getattr(self, f"entry_j{i + 1}")
            entry.delete(0, tk.END)
            entry.insert(0, str(new_position))

        self.calculate_coordinates()
        time.sleep(0.1)

    def calculate_coordinates(self):
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

    def update_plot(self):
        self.ax0.clear()
        self.ax0.plot(self.error_history)
        self.ax0.set_xlabel('Iterations')
        self.ax0.set_ylabel('Total Error')
        self.ax0.set_title('PID')
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def start_update_pid(self):
        self.disable_buttons()
        self.auto_update_pid()

    def disable_buttons(self):
        self.btn_pid.config(state=tk.DISABLED)
        self.btn_home.config(state=tk.DISABLED)

    def auto_update_pid(self):
        self.update_pid()

        if self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
            self.enable_buttons()
        else:
            self.root.after(100, self.auto_update_pid)

    def enable_buttons(self):
        self.btn_pid.config(state=tk.NORMAL)
        self.btn_home.config(state=tk.NORMAL)

    def start_update_pid_home(self):
        self.disable_buttons()
        self.auto_update_pid_home()

    def auto_update_pid_home(self):
        self.update_pid_home()

        if self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
            self.enable_buttons()
        else:
            self.root.after(100, self.auto_update_pid_home)

    def update_pid_home(self):
        self.target_positions = [90, 90, -90, -90, 0]
        self.current_positions = [getattr(self, f"angle_j{i + 1}").get() for i in range(5)]

        errors = [target - current for target, current in zip(self.target_positions, self.current_positions)]
        self.integral = [integral + error for integral, error in zip(self.integral, errors)]
        derivative = [error - prev_error for error, prev_error in zip(errors, self.prev_error)]

        pid_commands = [self.kp * errors[i] + self.ki * self.integral[i] + self.kd * derivative[i] for i in range(len(errors))]

        total_error = sum(errors)
        self.error_history.append(total_error)

        if not self.are_positions_close(self.current_positions, self.target_positions, tolerance=0.1):
            self.update_motors(pid_commands)
            self.prev_error = errors
            self.update_plot()

# Add other methods as needed...

# Example usage:
# instance = YourClassName()
# instance.start_update_pid()

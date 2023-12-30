import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import numpy as np

def f(x, amplitude=1.0):
    return amplitude * (np.cos(x) + np.sin(x)**2)

class PlotWindow:
    def __init__(self, master):
        self.master = master
        master.title("Function Plot")

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.plot_area = self.figure.add_subplot(1, 1, 1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.amplitude = 1.0
        self.animation = FuncAnimation(self.figure, self.update_plot, interval=100)

    def update_plot(self, frame):
        x_values = np.linspace(0, 2 * np.pi, 1000)
        y_values = f(x_values, amplitude=self.amplitude)

        self.plot_area.clear()
        self.plot_area.plot(x_values, y_values, label=r'$f(x) = \cos(x) + \sin^2(x)$')
        self.plot_area.set_xlabel('x')
        self.plot_area.set_ylabel('f(x)')
        self.plot_area.legend()

        # Example of changing amplitude over time
        self.amplitude += 0.1

class MainWindow:
    def __init__(self, master):
        self.master = master
        master.title("Main Window")

        self.btn_afficher = tk.Button(master, text="Afficher", command=self.show_plot_window)
        self.btn_afficher.pack()

        self.btn_animer = tk.Button(master, text="Animer", command=self.animate_plot)
        self.btn_animer.pack()

        self.btn_afficher_precedent = tk.Button(master, text="Afficher Prémettant", command=self.show_previous_plot_window)
        self.btn_afficher_precedent.pack()

    def show_plot_window(self):
        plot_window = tk.Toplevel(self.master)
        app = PlotWindow(plot_window)

    def animate_plot(self):
        # Access the amplitude variable from the PlotWindow instance
        if hasattr(self, 'plot_window_instance') and self.plot_window_instance:
            self.plot_window_instance.amplitude = 1.0  # Reset amplitude
            self.plot_window_instance.animation.event_source.start()

    def show_previous_plot_window(self):
        self.show_plot_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

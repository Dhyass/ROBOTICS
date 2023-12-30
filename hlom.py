import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

def update(frame):
    current_time = datetime.now()
    hours = current_time.hour % 12
    minutes = current_time.minute
    seconds = current_time.second
    
    hour_angle = np.radians(-(hours + minutes/60) * 30)
    minute_angle = np.radians(-minutes * 6)
    second_angle = np.radians(-seconds * 6)
    
    hour_hand.set_data([0, 0.5 * np.cos(hour_angle)], [0, 0.5 * np.sin(hour_angle)])
    minute_hand.set_data([0, 0.7 * np.cos(minute_angle)], [0, 0.7 * np.sin(minute_angle)])
    second_hand.set_data([0, 0.9 * np.cos(second_angle)], [0, 0.9 * np.sin(second_angle)])

ani = FuncAnimation(plt.gcf(), update, interval=1000)

plt.axis('equal')
plt.axis('on')
hour_hand, = plt.plot([], [], 'k-', lw=3)
minute_hand, = plt.plot([], [], 'k-', lw=2)
second_hand, = plt.plot([], [], 'r-', lw=1)

# Add labels for hours, minutes, and seconds
for i in range(1, 13):
    angle = np.radians(i * 30)
    plt.text(1.15 * np.cos(angle), 1.15 * np.sin(angle), str(i), ha='center', va='center', fontweight='bold')

for i in range(0, 60, 5):
    angle = np.radians(i * 6)
    plt.text(0.95 * np.cos(angle), 0.95 * np.sin(angle), str(i), ha='center', va='center', fontsize=8)

plt.show()

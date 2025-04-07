import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pycirclize import Circos

# Create figure and polar axes
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, projection='polar')
circos = Circos(sectors={"clock": 12}, space=0)
sector = circos.sectors[0]

# Plot static elements (clock face)
track = sector.add_track(r_lim=(100, 105))  # Outer circle beyond numbers
major_xticks = np.arange(0, 12, 1) + 1
track.xticks(major_xticks, outer=False, show_bottom_line=True)
minor_xticks = np.arange(0, 12, 0.2)
track.xticks(minor_xticks, outer=False, tick_length=1)

# Plot hour numbers with color, inside the outer circle
for x in major_xticks:
    track.text(str(x), x=x, r=93, size=15, adjust_rotation=False, color="darkblue")

# Render the static clock face
circos.plotfig(ax=ax)

# Set a light gray background
ax.set_facecolor("#f0f0f0")

# Initialize clock hands with distinct colors
hour_line, = ax.plot([0, 0], [0, 40], lw=4, color='darkgreen')
minute_line, = ax.plot([0, 0], [0, 70], lw=2, color='purple')
second_line, = ax.plot([0, 0], [0, 80], lw=1, color='orange')

# Store lines for animation
lines = [hour_line, minute_line, second_line]

def update(frame):
    # Slightly faster animation (multiplier increased from 1 to 2)
    seconds = (frame * 2) % 12
    minutes = (frame * 2 / 60) % 12
    hours = (frame * 2 / 720) % 12
    
    # Convert to radians, explicitly clockwise (12 → 1 → 2)
    hour_theta = 2 * np.pi - (hours * 2 * np.pi / 12)
    minute_theta = 2 * np.pi - (minutes * 2 * np.pi / 12)
    second_theta = 2 * np.pi - (seconds * 2 * np.pi / 12)
    
    # Adjust for 12 o'clock alignment
    hour_theta = (hour_theta + np.pi/2) % (2 * np.pi)
    minute_theta = (minute_theta + np.pi/2) % (2 * np.pi)
    second_theta = (second_theta + np.pi/2) % (2 * np.pi)
    
    # Update each line's position
    lines[0].set_data([0, hour_theta], [0, 40])
    lines[1].set_data([0, minute_theta], [0, 70])
    lines[2].set_data([0, second_theta], [0, 80])
    
    return lines

# Create animation, faster with interval=100 (was 200)
ani = FuncAnimation(fig, update, frames=60, interval=100, blit=True)

# Adjust plot settings
ax.set_ylim(0, 110)
ax.set_yticks([])
ax.set_xticks([])
ax.set_theta_direction(1)
ax.set_theta_offset(np.pi/2)

# Save animation as clockwise.mp4
ani.save('clockwise.mp4', writer='ffmpeg', fps=10)

# Show animation
plt.show()

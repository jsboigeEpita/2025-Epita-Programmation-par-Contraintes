import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from satelliteOrbit import satellite_position
from imagingTaskGeneration import generate_random_points

def animate_orbit(speed=1, MU=398600.4418, A=7000, EC=0.01, IC=45, OMEGA=60, W=30, R=6371, NUM_FRAMES=1000):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # create the expected trajectory of satellite
    t_full_orbit = np.linspace(0, 2 * np.pi * np.sqrt(A**3 / MU), 50)
    trajectory = np.array([satellite_position(t, MU, A, EC, IC, OMEGA, W)[:3] for t in t_full_orbit])

    t_initial = 0

    random_points = generate_random_points(15, R)

    # sphere to represent the Earth
    u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:20j]
    x_earth = R * np.cos(u) * np.sin(v)
    y_earth = R * np.sin(u) * np.sin(v)
    z_earth = R * np.cos(v)

    def update_frame(frame):
        ax.clear()

        # Earth
        ax.plot_surface(x_earth, y_earth, z_earth, color='blue', alpha=0.5)

        # satellite position at the current time
        t = t_initial + frame * speed
        x, y, z, _ = satellite_position(t, MU, A, EC, IC, OMEGA, W)

        ax.scatter(x, y, z, color='red', marker='o', s=30, label='Satellite Position')
        ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], color='green', label='Expected Trajectory')

        # random points on the Earth's surface
        for point in random_points:
            ax.scatter(point[0], point[1], point[2], color='red', marker='x', s=50)

        ax.scatter([], [], [], color='red', marker='x', s=50, label='Imaging Points')

        ax.legend()
        ax.set_xlim([-1.5*R, 1.5*R])
        ax.set_ylim([-1.5*R, 1.5*R])
        ax.set_zlim([-1.5*R, 1.5*R])
        ax.set_box_aspect([1, 1, 1])

        return ax.scatter(x, y, z)

    ani = FuncAnimation(fig, update_frame, frames=NUM_FRAMES, interval=50, blit=False)

    plt.show()

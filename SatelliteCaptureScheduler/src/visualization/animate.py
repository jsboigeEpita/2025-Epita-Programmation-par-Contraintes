import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from core.satellite import Satellite, SatelliteConfig
from core.imaging_task import ImagingTask
from visualization.visibility import can_image_points, all_availability


def animate_orbit(
    speed=1,
    number_of_satellites=1,
    number_of_tasks=10,
    labels=["Tokyo"],
    MU=398600.4418,
    A=[7000],
    EC=[0.01],
    IC=[45],
    OMEGA=[60],
    W=[30],
    R=6371,
    NUM_FRAMES=1000,
    min_elevation_angle=10,
):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # For displaying imaging status text
    status_text = fig.text(0.02, 0.02, "", fontsize=10)

    # generating the task points
    t_initial = 0

    # sphere to represent the Earth
    u, v = np.mgrid[0 : 2 * np.pi : 30j, 0 : np.pi : 20j]
    x_earth = R * np.cos(u) * np.sin(v)
    y_earth = R * np.sin(u) * np.sin(v)
    z_earth = R * np.cos(v)

    # creating imaging points
    satellite_imaging = ImagingTask(labels=labels, radius=R, number_of_tasks=number_of_tasks)

    # creating satellites
    satellites = []
    trajectories = []
    for i in range(number_of_satellites):
        # new_satellite = Satellite(MU, A[i], EC[i], IC[i], OMEGA[i], W[i])

        new_satellite = Satellite(
            SatelliteConfig(
                MU=MU,
                A=A[i],
                EC=EC[i],
                IC=IC[i],
                OMEGA=OMEGA[i],
                W=W[i],
                R=R,
                NUM_FRAMES=NUM_FRAMES,
                memory_capacity_gb=5,
                image_size_per_km2_gb=0.15,
                image_duration_per_km2_sec=3.5,
                max_photo_duration_s=120,
                recalibration_time_s=30,
                speed_kms_per_s=speed,
            )
        )


        satellites.append(new_satellite)
        # create the expected trajectory of satellite
        t_full_orbit = np.linspace(0, 2 * np.pi * np.sqrt(A[i] ** 3 / MU), 50)
        trajectories.append(
            np.array([new_satellite.position_at(t)[:3] for t in t_full_orbit])
        )

    all_availability(0, 8640, satellites, satellite_imaging)

    def update_frame(frame):
        ax.clear()
        # Earth
        ax.plot_surface(x_earth, y_earth, z_earth, color="blue", alpha=0.3)
        # Current time
        t = t_initial + frame * speed

        # Rotate Earth points according to current time
        rotated_task_points = satellite_imaging.rotate_earth(t)

        # Check visibility for each satellite
        all_visibility_data = []
        for i in range(number_of_satellites):
            visibility_data = can_image_points(
                satellites[i], satellite_imaging, t, min_elevation_angle
            )
            all_visibility_data.append(visibility_data)

            # Draw satellite
            x, y, z, _ = satellites[i].position_at(t)
            ax.scatter(x, y, z, color="red", marker="o", s=50)

            # Draw trajectory
            ax.plot(
                trajectories[i][:, 0],
                trajectories[i][:, 1],
                trajectories[i][:, 2],
                color="green",
                alpha=0.5,
            )

            # Draw line of sight to visible points
            for point_idx, is_visible, elevation in visibility_data:
                if is_visible:
                    point = rotated_task_points[point_idx]
                    ax.plot(
                        [x, point[0]],
                        [y, point[1]],
                        [z, point[2]],
                        "y--",
                        alpha=0.7,
                        linewidth=1,
                    )

        # Plot all task points with color based on visibility
        for idx, point in enumerate(rotated_task_points):
            # Check if any satellite can see this point
            any_visible = False
            max_elevation = 0
            for sat_idx in range(number_of_satellites):
                point_vis = all_visibility_data[sat_idx][idx]
                if point_vis[1]:  # is_visible
                    any_visible = True
                    max_elevation = max(max_elevation, point_vis[2])

            # Color the point based on visibility
            if any_visible:
                ax.scatter(
                    point[0],
                    point[1],
                    point[2],
                    color="lime",
                    marker="o",
                    s=40,
                    edgecolor="black",
                )
            else:
                ax.scatter(
                    point[0], point[1], point[2], color="black", marker="o", s=30
                )

        # Update status text
        status_text.set_text(f"Time: {t:.1f}s")

        # Set plot properties
        ax.set_title("Satellite Orbit and Imaging Capability Visualization")
        ax.set_xlim([-1.5 * R, 1.5 * R])
        ax.set_ylim([-1.5 * R, 1.5 * R])
        ax.set_zlim([-1.5 * R, 1.5 * R])
        ax.set_box_aspect([1, 1, 1])

        # Add a legend
        scatter1 = plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="red",
            markersize=10,
            label="Satellite",
        )
        scatter2 = plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="lime",
            markersize=10,
            label="Visible Point",
        )
        scatter3 = plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="black",
            markersize=10,
            label="Non-visible Point",
        )
        line1 = plt.Line2D([0], [0], color="green", lw=2, label="Trajectory")
        line2 = plt.Line2D(
            [0], [0], color="red", lw=2, linestyle="--", label="Line of Sight"
        )

        ax.legend(
            handles=[scatter1, scatter2, scatter3, line1, line2], loc="upper right"
        )

        return ax

    ani = FuncAnimation(fig, update_frame, frames=NUM_FRAMES, interval=50, blit=False)

    plt.show()

    return ani


"""
MU: standard gravitational parameter (here earth)
A:  average distance from the center of the planet (here earth) to satellite
E: aka eccentricity, shape of the orbit. 0 = perfect circle
I:  aka inclination, how tilted the satellite's orbit is relative to Earth's equator (could change to add more satelite)
OMEGA: jsp ce que ca represent hassoul but in degrees 'direction to the ascending node'
W: The angle that tells us where the satellite is closest to Earth in its orbit.
R: earth radius
NUM_FRAMES: number of frames for the visualisations
"""

# Parameters for three satellites
MU = 398600.4418
A = [7000, 7500, 8000]
EC = [0.01, 0.02, 0.03]
IC = [45, 50, 55]
OMEGA = [60, 125, 200]
W = [30, 35, 40]
R = 6371
NUM_FRAMES = 1000
LABELS = [
    "Tokyo",
    "New York",
    "London",
    "Paris",
    "Berlin",
    "Sydney",
    "Rome",
    "Madrid",
    "Toronto",
    "Mexico City",
    "Rio de Janeiro",
    "Cape Town",
    "Mumbai",
    "Bangkok",
    "Seoul",
    "Dubai",
    "Istanbul",
    "Moscow",
    "Beijing",
    "Shanghai",
    "Singapore",
    "Hong Kong",
    "Amsterdam",
    "Vienna",
    "Buenos Aires",
    "Cairo",
    "Johannesburg",
    "Lisbon",
    "Stockholm",
    "Helsinki",
]


# animate_orbit(
#     speed=50,
#     number_of_satellites=1,
#     number_of_tasks=30,
#     labels=LABELS,
#     MU=MU,
#     A=A,
#     EC=EC,
#     IC=IC,
#     OMEGA=OMEGA,
#     W=W,
#     R=R,
#     NUM_FRAMES=NUM_FRAMES,
#)

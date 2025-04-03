import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from satellite import Satellite
#from imagingTaskGeneration import generate_random_points
from imagingTaskGeneration import ImagingTask
from available import can_image_points

def animate_orbit(speed=1, number_of_satellites=1, number_of_tasks=10, MU=398600.4418, 
                 A=[7000], EC=[0.01], IC=[45], OMEGA=[60], W=[30], R=6371, NUM_FRAMES=1000,
                 min_elevation_angle=10):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # For displaying imaging status text
    status_text = fig.text(0.02, 0.02, "", fontsize=10)
    
    # generating the task points
    t_initial = 0
    
    # sphere to represent the Earth
    u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:20j]
    x_earth = R * np.cos(u) * np.sin(v)
    y_earth = R * np.sin(u) * np.sin(v)
    z_earth = R * np.cos(v)
    
    # creating imaging points
    satellite_imaging = ImagingTask(num_points=number_of_tasks, radius=R)
    
    # creating satellites
    satellites = []
    trajectories = []
    for i in range(number_of_satellites):
        new_satellite = Satellite(MU, A[i], EC[i], IC[i], OMEGA[i], W[i])
        satellites.append(new_satellite)
        # create the expected trajectory of satellite
        t_full_orbit = np.linspace(0, 2 * np.pi * np.sqrt(A[i]**3 / MU), 50)
        trajectories.append(np.array([new_satellite.position_at(t)[:3] for t in t_full_orbit]))
    
    def update_frame(frame):
        ax.clear()
        
        # Earth
        ax.plot_surface(x_earth, y_earth, z_earth, color='blue', alpha=0.3)
        
        # Current time
        t = t_initial + frame * speed
        
        # Rotate Earth points according to current time
        rotated_task_points = satellite_imaging.rotate_earth(t)
        
        # Check visibility for each satellite
        all_visibility_data = []
        for i in range(number_of_satellites):
            visibility_data = can_image_points(satellites[i], satellite_imaging, t, min_elevation_angle)
            all_visibility_data.append(visibility_data)
            for visibility in visibility_data:
                if visibility[1]:
                    print(visibility)
            # Draw satellite
            x, y, z, _ = satellites[i].position_at(t)
            ax.scatter(x, y, z, color='red', marker='o', s=50)
            
            # Draw trajectory
            ax.plot(trajectories[i][:, 0], trajectories[i][:, 1], trajectories[i][:, 2], 
                   color='green', alpha=0.5)
            
            # Draw line of sight to visible points
            for point_idx, is_visible, elevation in visibility_data:
                if is_visible:
                    point = rotated_task_points[point_idx]
                    ax.plot([x, point[0]], [y, point[1]], [z, point[2]], 
                           'y--', alpha=0.7, linewidth=1)
        
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
                ax.scatter(point[0], point[1], point[2], color='lime', marker='o', s=40, 
                          edgecolor='black')
            else:
                ax.scatter(point[0], point[1], point[2], color='black', marker='o', s=30)
        
        # Update status text
        status_text.set_text(f"Time: {t:.1f}s")
        
        # Set plot properties
        ax.set_title("Satellite Orbit and Imaging Capability Visualization")
        ax.set_xlim([-1.5*R, 1.5*R])
        ax.set_ylim([-1.5*R, 1.5*R])
        ax.set_zlim([-1.5*R, 1.5*R])
        ax.set_box_aspect([1, 1, 1])
        
        # Add a legend
        scatter1 = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Satellite')
        scatter2 = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lime', markersize=10, label='Visible Point')
        scatter3 = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=10, label='Non-visible Point')
        line1 = plt.Line2D([0], [0], color='green', lw=2, label='Trajectory')
        line2 = plt.Line2D([0], [0], color='red', lw=2, linestyle='--', label='Line of Sight')
        
        ax.legend(handles=[scatter1, scatter2, scatter3, line1, line2], loc='upper right')
        
        return ax
    
    ani = FuncAnimation(fig, update_frame, frames=NUM_FRAMES, interval=50, blit=False)
    
    plt.show()
    
    return ani
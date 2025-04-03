import numpy as np

class ImagingTask:
    def __init__(self, num_points, radius):
        self.points = self.generate_random_points(num_points, radius)
        self.earth_radius = radius

    def generate_random_points(self, num_points, radius):
        """
        Generate random points on the Earth's surface
        """
        points = []
        for _ in range(num_points):
            u = np.random.uniform(0, 2 * np.pi)
            v = np.random.uniform(0, np.pi)
            x = radius * np.cos(u) * np.sin(v)
            y = radius * np.sin(u) * np.sin(v)
            z = radius * np.cos(v)
            points.append((x, y, z))
        return points
    
    def rotate_earth(self, t, period=86400):
        """
        Rotate points on Earth based on time t (in seconds).

        Parameters:
        - points: List of (x, y, z) tuples representing points on Earth.
        - t: Time elapsed in seconds.
        - period: Rotation period of Earth (default 86400 seconds for 24-hour cycle).

        Returns:
        - List of updated (x, y, z) points.
        """
        # Earth's angular velocity (radians per second)
        omega = (2 * np.pi) / period
        
        # Rotation angle for the given time
        theta = omega * t  # Rotation angle in radians

        # Rotation matrix around the Z-axis (Earth's rotational axis)
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta),  np.cos(theta), 0],
            [0,             0,             1]
        ])

        # Rotate each point
        rotated_points = [tuple(R @ np.array(p)) for p in self.points]

        return rotated_points
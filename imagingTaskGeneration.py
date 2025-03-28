import numpy as np

def generate_random_points(num_points, radius):
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

def are_points_on_surface(points, radius, tolerance=1e-6):
    """
    Check if the points are on the surface of a sphere with the given radius.
    """
    for point in points:
        x, y, z = point
        distance = np.sqrt(x**2 + y**2 + z**2)
        if not np.isclose(distance, radius, atol=tolerance):
            return False
    return True

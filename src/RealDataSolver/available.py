import numpy as np

def can_image_points(satellite, imaging_task, t, min_elevation_angle=10):
    """
    Check if a satellite can image points on Earth at time t.
    """
    # Get satellite position at time t
    sat_x, sat_y, sat_z, _ = satellite.position_at(t)
    sat_pos = np.array([sat_x, sat_y, sat_z])
    
    # Get rotated Earth points at time t
    rotated_points = imaging_task.rotate_earth(t)
    
    results = []
    
    for i, point in enumerate(rotated_points):
        point_pos = np.array(point)
        
        # Vector from Earth point to satellite
        point_to_sat = sat_pos - point_pos
        
        # Distance from point to satellite
        distance = np.linalg.norm(point_to_sat)
        
        # Calculate elevation angle
        normal = point_pos / np.linalg.norm(point_pos)  # Unit vector pointing away from Earth's center
        cos_elev_compl = np.dot(point_to_sat, normal) / np.linalg.norm(point_to_sat)
        elevation_angle = 90 - np.degrees(np.arccos(np.clip(cos_elev_compl, -1.0, 1.0)))
        
        # Check if the satellite is above the Earth's surface from the point's perspective
        is_visible = (distance < imaging_task.earth_radius and elevation_angle >= min_elevation_angle)
        
        if (is_visible):
            print('NTM')
        results.append((i, is_visible, elevation_angle))
    
    return results

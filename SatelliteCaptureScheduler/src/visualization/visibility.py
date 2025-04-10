import numpy as np

EARTH_RADIUS = 6378

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
        normal = point_pos / np.linalg.norm(
            point_pos
        )  # Unit vector pointing away from Earth's center
        cos_elev_compl = np.dot(point_to_sat, normal) / np.linalg.norm(point_to_sat)
        elevation_angle = 90 - np.degrees(np.arccos(np.clip(cos_elev_compl, -1.0, 1.0)))

        # Check if the satellite is above the Earth's surface from the point's perspective
        is_visible = (
            distance < imaging_task.earth_radius
            and elevation_angle >= min_elevation_angle
        )

        results.append((i, is_visible, elevation_angle))

    return results


def check_satellite_see_point_specific_time(
    t, satelliteCoordonates, taskCoordonates, min_elevation_angle=10
):
    sat_pos = np.array(
        [satelliteCoordonates[0], satelliteCoordonates[1], satelliteCoordonates[2]]
    )
    task_pos = np.array([taskCoordonates[0], taskCoordonates[1], taskCoordonates[2]])

    # Vector from Earth point to satellite
    task_to_sat = sat_pos - task_pos

    # Distance from point to satellite
    distance = np.linalg.norm(task_to_sat)

    # Calculate elevation angle
    normal = task_pos / np.linalg.norm(
        task_pos
    )  # Unit vector pointing away from Earth's center
    cos_elev_compl = np.dot(task_to_sat, normal) / np.linalg.norm(task_to_sat)
    elevation_angle = 90 - np.degrees(np.arccos(np.clip(cos_elev_compl, -1.0, 1.0)))

    # Check if the satellite is above the Earth's surface from the point's perspective
    is_visible = distance < EARTH_RADIUS and elevation_angle >= min_elevation_angle

    return is_visible


def check_satellite_see_point(
    t, end, satellite, tasks, taskNumber, min_elevation_angle=10, time_step=60
):
    """
    Return the time window until when it sees it
    if True return (True, [begin (t), end (t + toAddToCounter)], toAddToCounter), else returns False return (False, [t, t], 0)
    """

    satelliteCoordonates = satellite.position_at(t)
    rotated_task_points = tasks.rotate_earth(t)
    taskCoordonates = rotated_task_points[taskNumber]

    is_visible = check_satellite_see_point_specific_time(
        t, satelliteCoordonates, taskCoordonates, min_elevation_angle
    )
    time_window = [t, t]
    toAddToCounter = time_step

    if is_visible:
        while (
            check_satellite_see_point_specific_time(
                t + toAddToCounter,
                satelliteCoordonates,
                taskCoordonates,
                min_elevation_angle,
            )
            and t + toAddToCounter <= end
        ):

            toAddToCounter += time_step
            time_window[1] += time_step
            satelliteCoordonates = satellite.position_at(t + toAddToCounter)
            rotated_task_points = tasks.rotate_earth(t + toAddToCounter)
            taskCoordonates = rotated_task_points[taskNumber]

    return (is_visible, time_window, toAddToCounter)


def all_availability(
    begin, end, satellites, tasks, min_elevation_angle=10, time_step=10
):
    """
    Calculate all availability windows for imaging tasks.

    Returns:
    - Dictionary mapping location labels to lists of time windows
    - Each time window is [start_time, end_time]
    """
    availability = []
    labels = tasks.getLabels()

    availabilityDico = {}
    for sat_idx, satellite in enumerate(satellites):
        for i, label in enumerate(labels):
            currentTime = begin
            while currentTime < end:
                available = check_satellite_see_point(
                    currentTime,
                    end,
                    satellite,
                    tasks,
                    i,
                    min_elevation_angle,
                    time_step,
                )
                if available[0]:
                    time_window = available[1]

                    # Add time window with metadata
                    window_data = {
                        "satellite": sat_idx,
                        "location_index": i,
                        "location": label,
                        "start_time": time_window[0],
                        "end_time": time_window[1],
                    }
                    availability.append(window_data)

                    # Group by location
                    if label in availabilityDico:
                        availabilityDico[label].append(time_window)
                    else:
                        availabilityDico[label] = [time_window]

                    currentTime += available[2]
                else:
                    currentTime += time_step

    return availabilityDico  # Return the mapping from location to time windows

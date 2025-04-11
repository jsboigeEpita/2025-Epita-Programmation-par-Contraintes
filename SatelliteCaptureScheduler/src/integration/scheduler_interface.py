import numpy as np
import yaml
import os
import sys
from ortools.sat.python import cp_model

from core.satellite import Satellite
from core.request import Request, RequestConfig
from core.imaging_task import ImagingTask
from visualization.visibility import all_availability
from solver.scheduler import SatelliteScheduler


def convert_to_solver_input(enriched_locations, satellites: list[Satellite]):
    """
    Convert the enriched location data from LLM into a format suitable for the solver.
    Add time windows for each location based on satellite visibility.
    """
    # Create satellites
    # Using some typical orbital parameters for Earth observation satellites
    # MU = 398600.4418  # Earth's gravitational parameter (km^3/s^2)
    # satellites = [Satellite(MU, 6800, 0.0001, 51.6, 80, 30)]  # ISS-like orbit

    # Create imaging tasks
    points = []
    labels = []

    for loc in enriched_locations:
        if loc["gps_coordinates"]["latitude"] is not None:
            lat_rad = np.radians(loc["gps_coordinates"]["latitude"])
            lon_rad = np.radians(loc["gps_coordinates"]["longitude"])

            # Convert latitude/longitude to 3D coordinates on Earth's surface
            earth_radius = 6378  # Earth radius in km
            x = earth_radius * np.cos(lat_rad) * np.cos(lon_rad)
            y = earth_radius * np.cos(lat_rad) * np.sin(lon_rad)
            z = earth_radius * np.sin(lat_rad)

            points.append((x, y, z))
            labels.append(loc["location"])

    # Only proceed if we have valid points
    if not points:
        return []

    # Create imaging task object
    imaging_task = ImagingTask(labels=labels, radius=6378, points=points)

    # Define time range (24 hours)
    begin_time = 0
    end_time = 86400  # 24 hours in seconds

    # Calculate availability windows
    availability_dict = all_availability(
        begin_time,
        end_time,
        satellites,
        imaging_task,
        min_elevation_angle=15,
        time_step=60,
    )

    # Create the solver requests
    solver_requests_yaml = []
    solver_requests = []

    for loc in enriched_locations:
        if loc["gps_coordinates"]["latitude"] is not None:
            # Check if we have availability windows for this location
            location_windows = availability_dict.get(loc["location"], [])

            if not location_windows:
                # If no visibility windows, use default time window
                time_window = (0, 86400)  # Full day
            else:
                # Use the first availability window for simplicity
                # In a more complex implementation, you could merge windows or pick the best one
                time_window = location_windows[0]

            solver_requests_yaml.append(
                {
                    "location": loc["location"],
                    "coordinates": (
                        loc["gps_coordinates"]["latitude"],
                        loc["gps_coordinates"]["longitude"],
                    ),
                    "priority": loc.get("priority", 3),
                    "area_size_km2": loc.get("area_size_km2", 1.0),
                    "time_window_sec": time_window,
                }
            )

            solver_requests.append(
                Request(
                    RequestConfig(
                        loc["location"],
                        (loc["gps_coordinates"]["latitude"], loc["gps_coordinates"]["longitude"]),
                        loc.get("priority", 3),
                        loc.get("area_size_km2", 1.0),
                        time_window,
                    )
                )
            )

    # Save the solver requests to a YAML file

    # Create a directory for outputs if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Save to YAML file
    yaml_file_path = os.path.join(output_dir, "solver_input.yaml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml.dump(solver_requests_yaml, yaml_file, default_flow_style=False)

    print(f"Solver input saved to {yaml_file_path}")
    return solver_requests


def run_satellite_scheduler(enriched_locations, satellite:Satellite):
    """
    Run the satellite scheduler with the enriched location data.
    Returns the scheduled observations.
    """

    # Utiliser la fonction convert_to_solver_input pour préparer les données
    solver_requests = convert_to_solver_input(enriched_locations, [satellite])

    if not solver_requests:
        return {"observations": [], "error": "No valid locations with GPS coordinates"}

    # Run the solver
    scheduler = SatelliteScheduler(satellite, solver_requests)
    status, results = scheduler.solve()
    scheduler.print_solution(status, results)

    # Format results
    formatted_results = {
        "observations": [],
        "status": (
            "optimal"
            if status == cp_model.OPTIMAL
            else "feasible" if status == cp_model.FEASIBLE else "infeasible"
        ),
    }

    # Process results
    total_memory = 0
    for r in results:
        result_entry = {
            "location": r["location"],
            "priority": r["priority"],
            "success": r.get("selected", False),
        }

        if r.get("selected", False):
            result_entry.update(
                {
                    "start_time": r["start_time"],
                    "duration": r["duration"],
                    "end_time": r["start_time"] + r["duration"],
                    "memory_used_gb": r["memory_used"],
                }
            )
            total_memory += r["memory_used"]

        formatted_results["observations"].append(result_entry)

    formatted_results["total_memory_used_gb"] = total_memory
    formatted_results["memory_capacity_gb"] = satellite.memory_capacity_gb
    # Save the formatted results to a YAML file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    yaml_file_path = os.path.join(output_dir, "scheduler_results.yaml")
    with open(yaml_file_path, "w") as yaml_file:
        yaml.dump(formatted_results, yaml_file, default_flow_style=False)

    print(f"Scheduler results saved to {yaml_file_path}")
    return formatted_results

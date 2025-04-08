import json
import numpy as np
from datetime import datetime, timedelta
from satellite import Satellite
from imagingTaskGeneration import ImagingTask
from available import all_availability
from satellite_solver import satellite_solver, cp_model

def convert_to_solver_input(enriched_locations):
    """
    Convert the enriched location data from LLM into a format suitable for the solver.
    Add time windows for each location based on satellite visibility.
    """
    # Create satellites
    # Using some typical orbital parameters for Earth observation satellites
    MU = 398600.4418  # Earth's gravitational parameter (km^3/s^2)
    satellites = [
        Satellite(MU, 7000, 0.0001, 98.5, 120, 45),   # Sun-synchronous orbit
        Satellite(MU, 6800, 0.0001, 51.6, 80, 30)     # ISS-like orbit
    ]
    
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
    imaging_task = ImagingTask(len(points), labels, 6378)
    imaging_task.points = points  # Override random points with our actual points
    
    # Define time range (24 hours)
    begin_time = 0
    end_time = 86400  # 24 hours in seconds
    
    # Calculate availability windows
    availability_dict = all_availability(begin_time, end_time, satellites, imaging_task, min_elevation_angle=15, time_step=60)
    
    # Create the solver requests
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
            
            solver_requests.append({
                "location": loc["location"],
                "coordinates": (loc["gps_coordinates"]["latitude"], loc["gps_coordinates"]["longitude"]),
                "priority": loc.get("priority", 3),
                "area_size_km2": loc.get("area_size_km2", 1.0),
                "time_window_sec": time_window
            })
    
    return solver_requests

def run_satellite_scheduler(enriched_locations):
    """
    Run the satellite scheduler with the enriched location data.
    Returns the scheduled observations.
    """
    # Satellite parameters
    satellite = {
        "memory_capacity_gb": 10,
        "image_size_per_km2_gb": 0.15,
        "image_duration_per_km2_sec": 3.5,
        "max_photo_duration_s": 180,
        "simultaneous_tasks": False,
        "recalibration_time_s": 30,
        "speed_kms_per_s": 50
    }
    
    # Utiliser la fonction convert_to_solver_input pour préparer les données
    solver_requests = convert_to_solver_input(enriched_locations)
    
    if not solver_requests:
        return {"observations": [], "error": "No valid locations with GPS coordinates"}
    
    # Run the solver
    status, results = satellite_solver(satellite, solver_requests)
    
    # Format results
    formatted_results = {
        "observations": [],
        "status": "optimal" if status == cp_model.OPTIMAL else "feasible" if status == cp_model.FEASIBLE else "infeasible"
    }
    
    # Process results
    total_memory = 0
    for r in results:
        result_entry = {
            "location": r["location"],
            "priority": r["priority"],
            "success": r.get("selected", False)
        }
        
        if r.get("selected", False):
            result_entry.update({
                "start_time": r["start_time"],
                "duration": r["duration"],
                "end_time": r["start_time"] + r["duration"],
                "memory_used_gb": r["memory_used"]
            })
            total_memory += r["memory_used"]
        
        formatted_results["observations"].append(result_entry)
    
    formatted_results["total_memory_used_gb"] = total_memory
    formatted_results["memory_capacity_gb"] = satellite["memory_capacity_gb"]
    
    return formatted_results

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from satellite import Satellite
from imagingTaskGeneration import ImagingTask
from available import all_availability

LABELS = [
    "Tokyo", "New York", "London", "Paris", "Berlin",
    "Sydney", "Rome", "Madrid", "Toronto", "Mexico City",
    "Rio de Janeiro", "Cape Town", "Mumbai", "Bangkok", "Seoul",
    "Dubai", "Istanbul", "Moscow", "Beijing", "Shanghai",
    "Singapore", "Hong Kong", "Amsterdam", "Vienna", "Buenos Aires",
    "Cairo", "Johannesburg", "Lisbon", "Stockholm", "Helsinki"
]

def generateTimeWindow(number_of_satellites=1, number_of_tasks=30, labels=LABELS, MU=398600.4418, 
                A=[7000], EC=[0.01], IC=[45], OMEGA=[60], W=[30], R=6371):
    
    satellite_imaging = ImagingTask(num_points=number_of_tasks, labels=labels, radius=R)
    
    # creating satellites
    satellites = []
    for i in range(number_of_satellites):
        new_satellite = Satellite(MU, A[i], EC[i], IC[i], OMEGA[i], W[i])
        satellites.append(new_satellite)
    
    windows = all_availability(0, 8640, satellites, satellite_imaging)
    
    return windows

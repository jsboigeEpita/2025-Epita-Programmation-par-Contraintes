import sys
import os

sys.path.append(os.path.abspath("src"))

from src.core.request import Request, RequestConfig
from src.core.satellite import Satellite, SatelliteConfig
from src.solver.scheduler import SatelliteScheduler

# Example usage
satellite = Satellite(
    SatelliteConfig(
        MU=398600.4418,
        A=[7000, 7500, 8000],
        EC=[0.01, 0.02, 0.03],
        IC=[45, 50, 55],
        OMEGA=[60, 125, 200],
        W=[30, 35, 40],
        R=6371,
        NUM_FRAMES=1000,
        memory_capacity_gb=5,
        image_size_per_km2_gb=0.15,
        image_duration_per_km2_sec=3.5,
        max_photo_duration_s=120,
        recalibration_time_s=30,
        speed_kms_per_s=50,
    )
)

requests = [
    Request(RequestConfig("New-York", (40.730610, -73.935242), 3, 6, (500, 1200))),
    Request(RequestConfig("Los-Angeles", (34.052235, -118.243683), 5, 8, (600, 1300))),
    Request(RequestConfig("Chicago", (41.878113, -87.629799), 2, 4, (700, 1400))),
    Request(
        RequestConfig("San-Francisco", (37.774929, -122.419416), 4, 5, (800, 1500))
    ),
    Request(RequestConfig("Miami", (25.761680, -80.191790), 3, 7, (400, 1100))),
    Request(RequestConfig("Seattle", (47.608013, -122.335167), 4, 6, (900, 1600))),
    Request(RequestConfig("Houston", (29.760427, -95.369803), 2, 5, (600, 1300))),
    Request(RequestConfig("Boston", (42.360081, -71.058880), 3, 4, (450, 1150))),
]


scheduler = SatelliteScheduler(satellite, requests)
status, results = scheduler.solve()
scheduler.print_solution(status, results)

import numpy as np
import math
from dataclasses import dataclass


@dataclass
class SatelliteConfig:

    # For the visualization
    MU: float 
    A: list[int]
    EC: list[float]
    IC: list[int]
    OMEGA: list[int]
    W: list[int]
    R: int
    NUM_FRAMES: int

    # For the solver
    memory_capacity_gb: float
    image_size_per_km2_gb: float
    image_duration_per_km2_sec: float
    max_photo_duration_s: int
    recalibration_time_s: int
    speed_kms_per_s: int


class Satellite:
    def __init__(self, config: SatelliteConfig) -> None:
        # For the visualization
        self.MU = config.MU
        self.A = config.A
        self.EC = config.EC
        self.IC = np.radians(config.IC)
        self.OMEGA = np.radians(config.OMEGA)
        self.W = np.radians(config.W)
        self.R = config.R
        self.NUM_FRAMES = config.NUM_FRAMES

        # For the solver
        self.memory_capacity_gb = config.memory_capacity_gb
        self.image_size_per_km2_gb = config.image_size_per_km2_gb
        self.image_duration_per_km2_sec = config.image_duration_per_km2_sec
        self.max_photo_duration_s = config.max_photo_duration_s
        self.recalibration_time_s = config.recalibration_time_s
        self.speed_kms_per_s = config.speed_kms_per_s

    def position_at(self, t: int) -> tuple[int]:
        """
        Calculate the position of the satellite at a given time t.
        """
        # How fast the satellite orbits Earth
        n = np.sqrt(self.MU / (self.A**3))

        # Approximate position in orbit
        M = n * t

        # Solve Kepler's equation
        E = M
        for _ in range(5):
            E = M + self.EC * np.sin(E)

        nu = 2 * np.arctan2(
            np.sqrt(1 + self.EC) * np.sin(E / 2), np.sqrt(1 - self.EC) * np.cos(E / 2)
        )

        # Distance from the center of the Earth to the satellite
        r = (self.A * (1 - self.EC**2)) / (1 + self.EC * np.cos(nu))
        x_p = r * np.cos(nu)
        y_p = r * np.sin(nu)

        # Calculate the values for the rotation of the orbit
        cos_w, sin_w = np.cos(self.W), np.sin(self.W)
        cos_i, sin_i = np.cos(self.IC), np.sin(self.IC)
        cos_omega, sin_omega = np.cos(self.OMEGA), np.sin(self.OMEGA)

        # Turn into 3D
        x = (cos_omega * cos_w - sin_omega * sin_w * cos_i) * x_p + (
            -cos_omega * sin_w - sin_omega * cos_w * cos_i
        ) * y_p
        y = (sin_omega * cos_w + cos_omega * sin_w * cos_i) * x_p + (
            -sin_omega * sin_w + cos_omega * cos_w * cos_i
        ) * y_p
        z = (sin_w * sin_i) * x_p + (cos_w * sin_i) * y_p

        return x, y, z, r

    def calculate_distance(self, coord1: tuple[int], coord2: tuple[int]) -> int:

        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        r = 6371

        return int(c * r / self.speed_kms_per_s)

    def calculate_memory_usage(self, area_size_km2: int) -> float:
        return area_size_km2 * self.image_size_per_km2_gb

    def calculate_capture_duration(self, area_size_km2: int) -> int:
        duration = min(
            area_size_km2 * self.image_duration_per_km2_sec, self.max_photo_duration_s
        )
        return duration

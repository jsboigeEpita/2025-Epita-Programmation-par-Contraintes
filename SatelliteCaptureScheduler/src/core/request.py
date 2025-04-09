from dataclasses import dataclass


@dataclass
class RequestConfig:
    location: str
    coordinates: tuple[int]
    priority: int
    area_size_km2: int
    time_window_sec: tuple[int]


class Request:
    def __init__(self, config: RequestConfig) -> None:
        self.location = config.location
        self.coordinates = config.coordinates
        self.priority = config.priority
        self.area_size_km2 = config.area_size_km2
        self.time_window_sec = config.time_window_sec

from dataclasses import dataclass


@dataclass
class StarSystem:
    id: int
    name: str
    star_type: str
    distance_ly: float | None = None

@dataclass
class Planet:
    id: int
    name: str
    planet_type: str
    radius_km: float
    mass_earth: float
    star_system_id: int

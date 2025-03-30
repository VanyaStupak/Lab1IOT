from dataclasses import dataclass
from domain.gps import Gps

@dataclass
class Parking:
    free_parking: bool
    gps: Gps
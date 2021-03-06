from enum import Enum

__all__ = ["DataTypes", "ObsTypes"]


class DataTypes(Enum):
    CRDS = "CRDS"
    GCWERKS = "GCWERKS"
    FOOTPRINT = "FOOTPRINT"
    NOAA = "NOAA"
    EUROCOM = "EUROCOM"
    THAMESBARRIER = "THAMESBARRIER"
    ICOS = "ICOS"
    CRANFIELD = "CRANFIELD"


class ObsTypes(Enum):
    SURFACE = "ObsSurface"
    SATELLITE = "ObsSatellite"
    FLASK = "ObsFlask"

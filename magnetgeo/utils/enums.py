from enum import Enum

class Side(Enum):
    """Side position enumeration for chamfers and cuts"""
    HIGH_POTENTIAL = "HP"
    LOW_POTENTIAL = "BP"

class RadialSide(Enum):
    """Radial position enumeration"""
    INNER = "rint"
    OUTER = "rext"

class GrooveType(Enum):
    """Groove type enumeration"""
    INNER = "rint"
    OUTER = "rext"

class ShapePosition(Enum):
    """Position of shape relative to helix"""
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    ALTERNATE = "ALTERNATE"

class DetailLevel(Enum):
    """Detail level for superconducting magnets"""
    NONE = "None"
    DBLPANCAKE = "dblpancake"
    PANCAKE = "pancake"
    TAPE = "tape"

class ProbeType(Enum):
    """Probe type enumeration"""
    VOLTAGE_TAPS = "voltage_taps"
    TEMPERATURE = "temperature"
    MAGNETIC_FIELD = "magnetic_field"

class MagnetType(Enum):
    """Magnet component type enumeration"""
    HELIX_LOW_RESISTANCE = "HL"
    HELIX_HIGH_RESISTANCE = "HR"
    BITTER = "Bitter"
    SUPRA = "Supra"

class CutFormat(Enum):
    """Supported cut file formats"""
    LNCMI = "lncmi"
    SALOME = "salome"

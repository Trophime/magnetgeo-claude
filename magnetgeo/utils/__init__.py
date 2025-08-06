"""
MagnetGeo utilities module

This module provides common utilities used throughout the magnetgeo package.
"""

from .enums import *
from .validation import *

__all__ = [
    # Enums
    "Side",
    "RadialSide",
    "GrooveType",
    "ShapePosition",
    "DetailLevel",
    "ProbeType",
    "MagnetType",
    "CutFormat",
    # Validation functions
    "validate_positive",
    "validate_non_negative",
    "validate_angle",
    "validate_bounds",
    "validate_enum_value",
    "validate_list_length",
    "validate_string_not_empty",
]

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
MagnetGeo Components Package

This package contains all magnet component classes organized by type:
- Main magnet components (Helix, Bitter, Supra, etc.)
- Container components (Insert, Bitters, Supras, MSite)
- Structural components (Ring, Screen, CurrentLeads)
- Support components (Chamfer, Groove, Model3D, etc.)
"""

# Import support components
from . import support

# Import main components when they're refactored
# TODO: Add these as they get refactored:
# from .helix import Helix
# from .bitter import Bitter
# from .supra import Supra
# from .insert import Insert
# etc.

__all__ = ['support']

# Version info
__version__ = "0.1.0"
__author__ = "MagnetGeo Development Team"

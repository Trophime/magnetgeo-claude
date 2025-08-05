"""
MagnetGeo base classes module

This module provides the foundational base classes for the entire
magnetgeo package. All component types inherit from these bases.
"""

from .serializable import SerializableBase
from .geometry import GeometryMixin, CollectionGeometryMixin
from .support_base import SupportComponentBase
from .component_base import MagnetComponentBase
from .structural_base import StructuralComponentBase
from .container_base import MagnetContainerBase

__all__ = [
    'SerializableBase',
    'GeometryMixin',
    'CollectionGeometryMixin', 
    'SupportComponentBase',
    'MagnetComponentBase',
    'StructuralComponentBase',
    'MagnetContainerBase'
]

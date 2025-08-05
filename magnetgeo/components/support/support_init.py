#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Support components for magnetgeo

This module contains refactored support components that inherit from
SupportComponentBase and provide enhanced validation and type safety.
"""

from .chamfer import Chamfer
from .groove import Groove
from .model3d import Model3D
from .modelaxi import ModelAxi
from .coolingslit import CoolingSlit
from .tierod import Tierod
from .shape import Shape
from .shape2d import Shape2D
from .probe import Probe

__all__ = [
    'Chamfer', 'Groove', 'Model3D', 'ModelAxi', 
    'CoolingSlit', 'Tierod', 'Shape', 'Shape2D', 'Probe'
]

# Version info
__version__ = "0.1.0"
__author__ = "MagnetGeo Development Team"

# Support class registry for dynamic loading
SUPPORT_CLASSES = {
    "Chamfer": Chamfer,
    "Groove": Groove,
    "Model3D": Model3D,
    "ModelAxi": ModelAxi,
    "CoolingSlit": CoolingSlit,
    "Tierod": Tierod,
    "Shape": Shape,
    "Shape2D": Shape2D,
    "Probe": Probe,
}


def get_support_class(class_name: str):
    """
    Get support class by name
    
    Args:
        class_name: Name of the support class
        
    Returns:
        Support class or None if not found
    """
    return SUPPORT_CLASSES.get(class_name)


def list_support_classes():
    """
    List all available support classes
    
    Returns:
        List of support class names
    """
    return list(SUPPORT_CLASSES.keys())


def create_support_object(class_name: str, data: dict, debug: bool = False):
    """
    Create support object from class name and data
    
    Args:
        class_name: Name of the support class
        data: Dictionary with object parameters
        debug: Whether to print debug info
        
    Returns:
        Created support object or None if class not found
    """
    cls = get_support_class(class_name)
    if cls and hasattr(cls, 'from_dict'):
        return cls.from_dict(data, debug=debug)
    return None

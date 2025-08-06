#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS (High Temperature Superconductor) Geometry Components

This module provides geometric definitions for superconducting magnet structures:
- Tape: HTS tape geometric dimensions
- Pancake: Coil geometric structure  
- Isolation: Insulation layer geometry
- DblPancake: Double pancake geometric assembly
- HTSinsert: Complete HTS geometric structure

These components provide pure geometric definitions without material properties
or electromagnetic analysis. They serve as support structures for the Supra
magnet component.
"""

from .tape import Tape
from .pancake import Pancake
from .isolation import Isolation
from .dblpancake import DblPancake
from .structure import HTSinsert
from .factory import create_uniform_structure, create_from_config

__all__ = [
    'Tape',
    'Pancake', 
    'Isolation',
    'DblPancake',
    'HTSinsert',
    'create_uniform_structure',
    'create_from_config'
]

# Version info
__version__ = "1.0.0"
__author__ = "MagnetGeo Development Team"

# Component registry for dynamic loading
HTS_COMPONENTS = {
    "Tape": Tape,
    "Pancake": Pancake,
    "Isolation": Isolation,
    "DblPancake": DblPancake,
    "HTSinsert": HTSinsert,
}


def get_hts_component(class_name: str):
    """
    Get HTS component class by name
    
    Args:
        class_name: Name of the HTS component class
        
    Returns:
        Component class or None if not found
    """
    return HTS_COMPONENTS.get(class_name)


def list_hts_components():
    """
    List all available HTS component classes
    
    Returns:
        List of HTS component class names
    """
    return list(HTS_COMPONENTS.keys())


def create_hts_component(class_name: str, data: dict, debug: bool = False):
    """
    Create HTS component object from class name and data
    
    Args:
        class_name: Name of the HTS component class
        data: Dictionary with component parameters
        debug: Whether to print debug info
        
    Returns:
        Created component object or None if class not found
    """
    cls = get_hts_component(class_name)
    if cls and hasattr(cls, 'from_dict'):
        return cls.from_dict(data, debug=debug)
    elif cls:
        try:
            return cls(**data)
        except Exception as e:
            if debug:
                print(f"Failed to create {class_name}: {e}")
            return None
    
    if debug:
        print(f"HTS component {class_name} not found")
    return None


def get_package_info():
    """
    Get HTS components package information
    
    Returns:
        Dictionary with package information
    """
    return {
        "version": __version__,
        "components": list_hts_components(),
        "total_components": len(HTS_COMPONENTS),
        "focus": "Pure geometric definitions for HTS structures"
    }


if __name__ == "__main__":
    info = get_package_info()
    print(f"MagnetGeo HTS Components v{info['version']}")
    print(f"Available components: {', '.join(info['components'])}")
    print(f"Focus: {info['focus']}")

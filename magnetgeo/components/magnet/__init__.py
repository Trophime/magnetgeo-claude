#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Magnet components package

This package contains the main magnetic field-generating components:
- Helix: Helical coil magnets (HL and HR types)
- Bitter: Bitter disk magnets with cooling slits
- Supra: Superconducting magnets with detailed structure
"""

from .helix import Helix
from .bitter import Bitter
from .supra import Supra

__all__ = ['Helix', 'Bitter', 'Supra']

# Version info
__version__ = "0.1.0"
__author__ = "MagnetGeo Development Team"

# Magnet class registry for dynamic loading
MAGNET_CLASSES = {
    "Helix": Helix,
    "Bitter": Bitter,
    "Supra": Supra,
}

# Type mapping for YAML/JSON loading
MAGNET_TYPE_MAP = {
    "HL": Helix,  # Low resistance helix
    "HR": Helix,  # High resistance helix
    "Bitter": Bitter,
    "Supra": Supra,
}


def get_magnet_class(class_name: str):
    """
    Get magnet class by name
    
    Args:
        class_name: Name of the magnet class
        
    Returns:
        Magnet class or None if not found
    """
    return MAGNET_CLASSES.get(class_name)


def get_magnet_class_by_type(magnet_type: str):
    """
    Get magnet class by magnet type
    
    Args:
        magnet_type: Type identifier ("HL", "HR", "Bitter", "Supra")
        
    Returns:
        Magnet class or None if not found
    """
    return MAGNET_TYPE_MAP.get(magnet_type)


def list_magnet_classes():
    """
    List all available magnet classes
    
    Returns:
        List of magnet class names
    """
    return list(MAGNET_CLASSES.keys())


def list_magnet_types():
    """
    List all available magnet types
    
    Returns:
        List of magnet type identifiers
    """
    return list(MAGNET_TYPE_MAP.keys())


def create_magnet(class_name: str, data: dict, debug: bool = False):
    """
    Create magnet object from class name and data
    
    Args:
        class_name: Name of the magnet class
        data: Dictionary with magnet parameters
        debug: Whether to print debug info
        
    Returns:
        Created magnet object or None if class not found
    """
    cls = get_magnet_class(class_name)
    if cls and hasattr(cls, 'from_dict'):
        return cls.from_dict(data, debug=debug)
    elif cls:
        # Try direct construction
        try:
            return cls(**data)
        except Exception as e:
            if debug:
                print(f"Failed to create {class_name}: {e}")
            return None
    return None


def create_magnet_by_type(magnet_type: str, data: dict, debug: bool = False):
    """
    Create magnet object from type and data
    
    Args:
        magnet_type: Type identifier
        data: Dictionary with magnet parameters
        debug: Whether to print debug info
        
    Returns:
        Created magnet object or None if type not found
    """
    cls = get_magnet_class_by_type(magnet_type)
    if cls and hasattr(cls, 'from_dict'):
        return cls.from_dict(data, debug=debug)
    elif cls:
        try:
            return cls(**data)
        except Exception as e:
            if debug:
                print(f"Failed to create {magnet_type}: {e}")
            return None
    return None


def get_package_info():
    """
    Get information about the magnet components package
    
    Returns:
        Dictionary with package information
    """
    return {
        "version": __version__,
        "available_classes": list_magnet_classes(),
        "available_types": list_magnet_types(),
        "total_classes": len(MAGNET_CLASSES),
    }


if __name__ == "__main__":
    info = get_package_info()
    print(f"MagnetGeo Magnet Components v{info['version']}")
    print(f"Available classes: {', '.join(info['available_classes'])}")
    print(f"Available types: {', '.join(info['available_types'])}")

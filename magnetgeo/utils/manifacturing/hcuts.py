#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Manufacturing cut utilities

This module provides functionality for generating cut files for various
CAD and simulation formats, particularly for helical magnet components.

Ported and enhanced from pytho_magnetgeo/hcuts.py
"""

import os
import math
from typing import Any, Dict, Optional
from enum import Enum

# Try to import validation utilities
try:
    from ..validation import validate_string_not_empty, validate_positive
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    def validate_string_not_empty(val, name): pass
    def validate_positive(val, name): pass

# Try to import enums
try:
    from ..enums import CutFormat
except ImportError:
    class CutFormat(Enum):
        """Cut file formats"""
        LNCMI = "lncmi"
        SALOME = "salome"


def lncmi_cut(object: Any, filename: str, append: bool = False, z0: float = 0):
    """
    Create LNCMI format cut file
    
    Args:
        object: Helix object with modelaxi attribute
        filename: Output filename
        append: Whether to append to existing file
        z0: Z-axis offset
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(filename, "filename")
    
    # Validate object has required attributes
    if not hasattr(object, 'modelaxi'):
        raise ValueError("Object must have modelaxi attribute")
    
    modelaxi = object.modelaxi
    if not hasattr(modelaxi, 'turns') or not hasattr(modelaxi, 'pitch'):
        raise ValueError("Object modelaxi must have turns and pitch attributes")
    
    # Determine file mode
    flag = "a" if append else "w"
    
    # Calculate initial parameters
    theta = 0
    z = z0
    
    # Determine sign based on object properties
    sign = -1 if getattr(object, 'odd', False) else 1
    
    # Get shape information
    shape_id = 1  # Default shape ID
    if hasattr(object, 'shape') and object.shape:
        if hasattr(object.shape, 'id'):
            shape_id = object.shape.id
        elif hasattr(object.shape, 'name'):
            # Try to extract ID from name or use hash
            shape_id = abs(hash(object.shape.name)) % 1000
    
    # File format for LNCMI
    tab = "\t"
    
    try:
        with open(filename, flag) as f:
            # Write header
            f.write(f"#theta[rad]{tab}Shape_id[]{tab}tZ[mm]\n")
            f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")
            
            # Write helical path points
            for i, (turn, pitch) in enumerate(zip(modelaxi.turns, modelaxi.pitch)):
                theta += turn * (2 * math.pi) * sign
                z -= turn * pitch
                f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")
                
    except IOError as e:
        raise RuntimeError(f"Failed to write LNCMI cut file {filename}: {e}")


def salome_cut(object: Any, filename: str, append: bool = False, z0: float = 0):
    """
    Create SALOME format cut file
    
    Args:
        object: Helix object with modelaxi attribute
        filename: Output filename
        append: Whether to append to existing file
        z0: Z-axis offset
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(filename, "filename")
    
    # Validate object has required attributes
    if not hasattr(object, 'modelaxi'):
        raise ValueError("Object must have modelaxi attribute")
    
    modelaxi = object.modelaxi
    if not hasattr(modelaxi, 'turns') or not hasattr(modelaxi, 'pitch'):
        raise ValueError("Object modelaxi must have turns and pitch attributes")
    
    # Determine file mode
    flag = "a" if append else "w"
    
    # Calculate initial parameters
    theta = 0
    z = z0
    
    # Determine sign based on object properties  
    sign = -1 if getattr(object, 'odd', False) else 1
    
    # Get radial information
    r0 = getattr(object, 'r', [0, 1])[0]  # Inner radius
    
    try:
        with open(filename, flag) as f:
            # Write SALOME-specific header
            f.write("# SALOME Helix Cut Data\n")
            f.write("# X[mm]\tY[mm]\tZ[mm]\n")
            
            # Write initial point
            x = r0 * math.cos(theta)
            y = r0 * math.sin(theta)
            f.write(f"{x:12.6f}\t{y:12.6f}\t{z:12.6f}\n")
            
            # Write helical path points
            for i, (turn, pitch) in enumerate(zip(modelaxi.turns, modelaxi.pitch)):
                theta += turn * (2 * math.pi) * sign
                z -= turn * pitch
                x = r0 * math.cos(theta)
                y = r0 * math.sin(theta)
                f.write(f"{x:12.6f}\t{y:12.6f}\t{z:12.6f}\n")
                
    except IOError as e:
        raise RuntimeError(f"Failed to write SALOME cut file {filename}: {e}")


def create_cut(
    object: Any, 
    format: str, 
    name: str, 
    append: bool = False, 
    z0: float = 0,
    output_dir: Optional[str] = None
):
    """
    Create cut file in specified format
    
    Args:
        object: Helix object with modelaxi attribute
        format: Output format ("lncmi" or "salome")
        name: Base name for output file
        append: Whether to append to existing file
        z0: Z-axis offset
        output_dir: Optional output directory
        
    Raises:
        ValueError: If format is not supported
        RuntimeError: If file creation fails
    """
    if VALIDATION_AVAILABLE:
        validate_string_not_empty(format, "format")
        validate_string_not_empty(name, "name")
    
    # Define supported formats
    format_info = {
        "lncmi": {
            "function": lncmi_cut,
            "extension": "_lncmi.iso"
        },
        "salome": {
            "function": salome_cut, 
            "extension": "_cut_salome.dat"
        }
    }
    
    format_lower = format.lower()
    if format_lower not in format_info:
        supported = list(format_info.keys())
        raise ValueError(f"Unsupported format '{format}'. Supported formats: {supported}")
    
    # Get format details
    format_data = format_info[format_lower]
    write_function = format_data["function"]
    extension = format_data["extension"]
    
    # Build filename
    filename = f"{name}{extension}"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)
    
    # Create the cut file
    try:
        write_function(object, filename, append, z0)
        print(f"Created cut file: {filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to create cut file {filename}: {e}")


def get_supported_formats() -> list:
    """
    Get list of supported cut file formats
    
    Returns:
        List of supported format strings
    """
    return ["lncmi", "salome"]


def validate_helix_object(object: Any) -> bool:
    """
    Validate that object has required attributes for cut generation
    
    Args:
        object: Object to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not hasattr(object, 'modelaxi'):
        return False
    
    modelaxi = object.modelaxi
    if not hasattr(modelaxi, 'turns') or not hasattr(modelaxi, 'pitch'):
        return False
    
    # Check that turns and pitch are sequences
    try:
        iter(modelaxi.turns)
        iter(modelaxi.pitch)
    except TypeError:
        return False
    
    # Check that turns and pitch have same length
    if len(modelaxi.turns) != len(modelaxi.pitch):
        return False
    
    return True


def estimate_cut_points(object: Any) -> int:
    """
    Estimate number of points that will be generated in cut file
    
    Args:
        object: Helix object
        
    Returns:
        Estimated number of points
    """
    if not validate_helix_object(object):
        return 0
    
    # Base point + one point per turn segment
    return 1 + len(object.modelaxi.turns)


def get_cut_file_info(filename: str) -> Dict[str, Any]:
    """
    Get information about a cut file
    
    Args:
        filename: Path to cut file
        
    Returns:
        Dictionary with file information
    """
    if not os.path.exists(filename):
        return {"exists": False}
    
    info = {
        "exists": True,
        "size": os.path.getsize(filename),
        "format": "unknown"
    }
    
    # Determine format from extension
    if filename.endswith("_lncmi.iso"):
        info["format"] = "lncmi"
    elif filename.endswith("_cut_salome.dat"):
        info["format"] = "salome"
    
    # Count lines for point estimation
    try:
        with open(filename, 'r') as f:
            lines = sum(1 for line in f if line.strip() and not line.startswith('#'))
            info["points"] = lines
    except IOError:
        info["points"] = -1
    
    return info


# Backward compatibility aliases
def create_lncmi_cut(object: Any, filename: str, append: bool = False, z0: float = 0):
    """Backward compatibility alias for lncmi_cut"""
    lncmi_cut(object, filename, append, z0)


def create_salome_cut(object: Any, filename: str, append: bool = False, z0: float = 0):
    """Backward compatibility alias for salome_cut"""
    salome_cut(object, filename, append, z0)
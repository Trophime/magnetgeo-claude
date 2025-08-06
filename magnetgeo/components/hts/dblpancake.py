#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS Double Pancake geometric definition

Defines the geometric structure of double pancake assemblies consisting of
two pancakes with isolation between them.
"""

from typing import Dict, Any, List, Union
from .pancake import Pancake
from .isolation import Isolation

try:
    from ...base.support_base import SupportComponentBase
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    SupportComponentBase = object


def flatten(nested_list: List) -> List:
    """Flatten nested list structure"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


class DblPancake(SupportComponentBase if BASE_AVAILABLE else object):
    """
    HTS double pancake geometric definition
    
    Represents the geometric structure of a double pancake assembly
    consisting of two identical pancakes with isolation between them.
    
    Attributes:
        z0: Center position of double pancake assembly (mm)
        pancake: Pancake geometry (both pancakes assumed identical)
        isolation: Isolation geometry between pancakes
    """
    
    yaml_tag = "!DblPancake"
    
    def __init__(
        self,
        z0: float,
        pancake: Pancake = None,
        isolation: Isolation = None,
    ):
        """
        Initialize double pancake geometry
        
        Args:
            z0: Center position of double pancake assembly
            pancake: Pancake geometry (both assumed identical)
            isolation: Isolation geometry between pancakes
        """
        if BASE_AVAILABLE:
            super().__init__()
        
        self.z0 = float(z0)
        self.pancake = pancake if pancake is not None else Pancake()
        self.isolation = isolation if isolation is not None else Isolation()
        
        self.validate()
    
    def validate(self) -> None:
        """Validate double pancake geometric parameters"""
        if BASE_AVAILABLE:
            super().validate()
        
        if self.pancake:
            self.pancake.validate()
        if self.isolation:
            self.isolation.validate()
    
    def getPancake(self) -> Pancake:
        """Get pancake geometry object"""
        return self.pancake
    
    def getIsolation(self) -> Isolation:
        """Get isolation geometry object"""
        return self.isolation
    
    def setZ0(self, z0: float) -> None:
        """Set center position"""
        self.z0 = float(z0)
    
    def setPancake(self, pancake: Pancake) -> None:
        """Set pancake geometry"""
        self.pancake = pancake
        if self.pancake:
            self.pancake.validate()
    
    def setIsolation(self, isolation: Isolation) -> None:
        """Set isolation geometry"""
        self.isolation = isolation
        if self.isolation:
            self.isolation.validate()
    
    def getR0(self) -> float:
        """Get inner radius of double pancake"""
        return self.pancake.getR0() if self.pancake else 0.0
    
    def getR1(self) -> float:
        """Get outer radius of double pancake"""
        return self.pancake.getR1() if self.pancake else 0.0
    
    def getZ0(self) -> float:
        """Get center position"""
        return self.z0
    
    def getZ1(self) -> float:
        """Get bottom position"""
        return self.z0 - self.getH() / 2.0
    
    def getZ2(self) -> float:
        """Get top position"""
        return self.z0 + self.getH() / 2.0
    
    def getW(self) -> float:
        """Get radial width of double pancake"""
        return self.pancake.getW() if self.pancake else 0.0
    
    def getH(self) -> float:
        """Get total height of double pancake assembly"""
        pancake_height = 2.0 * self.pancake.getH() if self.pancake else 0.0
        isolation_height = self.isolation.getH() if self.isolation else 0.0
        return pancake_height + isolation_height
    
    def getArea(self) -> float:
        """Get cross-sectional area of double pancake in r-z plane"""
        return self.getW() * self.getH()
    
    def getVolume_cylindrical(self) -> float:
        """
        Get cylindrical volume of double pancake
        
        Returns:
            Volume assuming cylindrical geometry
        """
        import math
        
        if not self.pancake:
            return 0.0
        
        r_outer = self.getR1()
        r_inner = self.getR0()
        height = self.getH()
        
        return math.pi * (r_outer**2 - r_inner**2) * height
    
    def getFillingFactor(self) -> float:
        """
        Get geometric filling factor for double pancake
        
        Returns:
            Filling factor as fraction (0.0 to 1.0)
        """
        total_area = self.getArea()
        if total_area == 0 or not self.pancake or not self.pancake.tape:
            return 0.0
        
        # Two pancakes worth of tape area
        tape_area = 2.0 * self.pancake.n * self.pancake.tape.getArea_Sc()
        return tape_area / total_area
    
    def get_pancake_positions(self) -> tuple:
        """
        Get z-positions of the two pancakes
        
        Returns:
            Tuple of (z_bottom_pancake, z_top_pancake)
        """
        if not self.pancake:
            return (self.z0, self.z0)
        
        pancake_height = self.pancake.getH()
        isolation_height = self.isolation.getH() if self.isolation else 0.0
        
        # Bottom pancake center
        z_bottom = self.z0 - (isolation_height / 2.0 + pancake_height / 2.0)
        
        # Top pancake center  
        z_top = self.z0 + (isolation_height / 2.0 + pancake_height / 2.0)
        
        return (z_bottom, z_top)
    
    def get_names(self, name: str, detail: str, verbose: bool = False) -> Union[str, List[str]]:
        """
        Get component names for meshing/CAD
        
        Args:
            name: Base name for components
            detail: Detail level ("dblpancake", "pancake", "turn", or "tape")
            verbose: Whether to print verbose info
            
        Returns:
            Component name(s) based on detail level
        """
        if detail == "dblpancake":
            return name
        
        names = []
        
        # Bottom pancake
        if self.pancake:
            p0_names = self.pancake.get_names(f"{name}_p0", detail, verbose)
            if isinstance(p0_names, str):
                names.append(p0_names)
            else:
                names.extend(p0_names)
        
        # Isolation between pancakes
        if self.isolation and not self.isolation.is_empty():
            iso_names = self.isolation.get_names(f"{name}_isolation", detail, verbose)
            names.extend(iso_names)
        
        # Top pancake
        if self.pancake:
            p1_names = self.pancake.get_names(f"{name}_p1", detail, verbose)
            if isinstance(p1_names, str):
                names.append(p1_names)
            else:
                names.extend(p1_names)
        
        if verbose:
            print(f"DblPancake '{name}' components ({detail}): {len(names)} items")
        
        return names
    
    def get_bounds(self) -> tuple:
        """
        Get geometric bounds as (r_bounds, z_bounds)
        
        Returns:
            Tuple of ([r_min, r_max], [z_min, z_max])
        """
        r_min = self.getR0()
        r_max = self.getR1()
        z_min = self.getZ1()
        z_max = self.getZ2()
        
        return ([r_min, r_max], [z_min, z_max])
    
    def get_component_positions(self) -> Dict[str, Dict[str, float]]:
        """
        Get detailed positions of all components
        
        Returns:
            Dictionary with component position information
        """
        z_bottom, z_top = self.get_pancake_positions()
        
        positions = {
            "assembly": {
                "z_center": self.z0,
                "z_bottom": self.getZ1(),
                "z_top": self.getZ2(),
                "r_inner": self.getR0(),
                "r_outer": self.getR1()
            },
            "bottom_pancake": {
                "z_center": z_bottom,
                "z_bottom": z_bottom - self.pancake.getH()/2 if self.pancake else z_bottom,
                "z_top": z_bottom + self.pancake.getH()/2 if self.pancake else z_bottom
            },
            "top_pancake": {
                "z_center": z_top,
                "z_bottom": z_top - self.pancake.getH()/2 if self.pancake else z_top,
                "z_top": z_top + self.pancake.getH()/2 if self.pancake else z_top
            }
        }
        
        if self.isolation and not self.isolation.is_empty():
            positions["isolation"] = {
                "z_center": self.z0,
                "z_bottom": self.z0 - self.isolation.getH()/2,
                "z_top": self.z0 + self.isolation.getH()/2
            }
        
        return positions
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'DblPancake':
        """
        Create DblPancake from dictionary
        
        Args:
            data: Dictionary with double pancake parameters
            debug: Whether to print debug info
            
        Returns:
            DblPancake instance
        """
        if debug:
            print(f"Creating DblPancake from: {data}")
        
        z0 = data.get("z0", 0)
        
        # Handle pancake data
        pancake_data = data.get("pancake", {})
        if isinstance(pancake_data, dict):
            pancake = Pancake.from_dict(pancake_data, debug=debug)
        else:
            # Assume it's already a Pancake object
            pancake = pancake_data
        
        # Handle isolation data
        isolation_data = data.get("isolation", {})
        if isinstance(isolation_data, dict):
            isolation = Isolation.from_dict(isolation_data, debug=debug)
        else:
            # Assume it's already an Isolation object
            isolation = isolation_data
        
        return cls(z0, pancake, isolation)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "z0": self.z0,
            "pancake": self.pancake.to_dict() if self.pancake else {},
            "isolation": self.isolation.to_dict() if self.isolation else {}
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"DblPancake(z0={self.z0}, pancake={self.pancake}, isolation={self.isolation})"
    
    def __str__(self) -> str:
        """Detailed string representation"""
        msg = f"HTS Double Pancake Geometry:\n"
        msg += f"  Center position: {self.z0:.3f} mm\n"
        msg += f"  Total height: {self.getH():.3f} mm\n"
        msg += f"  Inner radius: {self.getR0():.3f} mm\n"
        msg += f"  Outer radius: {self.getR1():.3f} mm\n"
        msg += f"  Radial width: {self.getW():.3f} mm\n"
        
        if self.pancake:
            msg += f"  Pancake turns: {self.pancake.getN()}\n"
            z_bottom, z_top = self.get_pancake_positions()
            msg += f"  Bottom pancake at: {z_bottom:.3f} mm\n"
            msg += f"  Top pancake at: {z_top:.3f} mm\n"
        
        if self.isolation and not self.isolation.is_empty():
            msg += f"  Isolation height: {self.isolation.getH():.3f} mm\n"
            msg += f"  Isolation layers: {self.isolation.getLayer()}\n"
        
        msg += f"  Filling factor: {self.getFillingFactor():.1%}"
        return msg


def create_symmetric_dblpancake(z0: float, pancake: Pancake, 
                               isolation_height: float) -> DblPancake:
    """
    Create symmetric double pancake with uniform isolation
    
    Args:
        z0: Center position
        pancake: Pancake geometry (used for both pancakes)
        isolation_height: Height of isolation between pancakes
        
    Returns:
        DblPancake instance
    """
    if not isinstance(pancake, Pancake):
        raise TypeError("pancake must be a Pancake instance")
    
    # Create isolation with same radial extent as pancake
    from .isolation import create_uniform_isolation
    isolation = create_uniform_isolation(
        r0=pancake.getR0(),
        width=pancake.getW(),
        height=isolation_height
    )
    
    return DblPancake(z0, pancake, isolation)


def create_minimal_dblpancake(z0: float, pancake: Pancake) -> DblPancake:
    """
    Create double pancake with minimal isolation (thin Kapton layer)
    
    Args:
        z0: Center position
        pancake: Pancake geometry
        
    Returns:
        DblPancake instance with thin isolation
    """
    # Create thin Kapton isolation (typical thickness)
    from .isolation import create_kapton_isolation
    isolation = create_kapton_isolation(
        r0=pancake.getR0(),
        thickness=pancake.getW(),
        height=0.1,  # 0.1mm Kapton
        n_layers=1
    )
    
    return DblPancake(z0, pancake, isolation)


def create_vacuum_dblpancake(z0: float, pancake: Pancake, 
                           vacuum_gap: float = 1.0) -> DblPancake:
    """
    Create double pancake with vacuum isolation
    
    Args:
        z0: Center position
        pancake: Pancake geometry
        vacuum_gap: Vacuum gap height
        
    Returns:
        DblPancake instance with vacuum isolation
    """
    from .isolation import create_vacuum_isolation
    isolation = create_vacuum_isolation(
        r0=pancake.getR0(),
        gap=pancake.getW(),
        height=vacuum_gap
    )
    
    return DblPancake(z0, pancake, isolation)

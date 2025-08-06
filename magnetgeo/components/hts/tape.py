#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS Tape geometric definition

Defines the geometric properties of HTS (High Temperature Superconductor) tapes
including superconductor width, tape height, and insulation thickness.
"""

from typing import Dict, Any, List

try:
    from ...base.support_base import SupportComponentBase
    from ...utils.validation import validate_non_negative
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    SupportComponentBase = object
    def validate_non_negative(val, name): pass


class Tape(SupportComponentBase if BASE_AVAILABLE else object):
    """
    HTS tape geometric definition
    
    Represents the cross-sectional geometry of an HTS tape consisting of
    a superconducting layer and co-wound insulation.
    
    Attributes:
        w: Width of superconductor layer (mm)
        h: Height/thickness of tape (mm)
        e: Thickness of co-wound insulation (mm)
    """
    
    yaml_tag = "!Tape"
    
    def __init__(self, w: float = 0, h: float = 0, e: float = 0) -> None:
        """
        Initialize HTS tape geometry
        
        Args:
            w: Width of superconductor layer
            h: Height/thickness of tape
            e: Thickness of co-wound insulation
        """
        if BASE_AVAILABLE:
            super().__init__()
        
        self.w = float(w)
        self.h = float(h)
        self.e = float(e)
        
        self.validate()
    
    def validate(self) -> None:
        """Validate tape geometric parameters"""
        if BASE_AVAILABLE:
            super().validate()
        
        validate_non_negative(self.w, "w (superconductor width)")
        validate_non_negative(self.h, "h (tape height)")
        validate_non_negative(self.e, "e (insulation thickness)")
    
    def getH(self) -> float:
        """Get tape height"""
        return self.h
    
    def getW(self) -> float:
        """Get total tape width (superconductor + insulation)"""
        return self.w + self.e
    
    def getW_Sc(self) -> float:
        """Get superconductor width"""
        return self.w
    
    def getW_Isolation(self) -> float:
        """Get insulation width"""
        return self.e
    
    def getArea(self) -> float:
        """Get total tape cross-sectional area"""
        return self.getW() * self.h
    
    def getArea_Sc(self) -> float:
        """Get superconductor cross-sectional area"""
        return self.w * self.h
    
    def getArea_Isolation(self) -> float:
        """Get insulation cross-sectional area"""
        return self.e * self.h
    
    def getFillingFactor(self) -> float:
        """
        Get geometric filling factor (ratio of SC to total area)
        
        Returns:
            Filling factor as fraction (0.0 to 1.0)
        """
        total_area = self.getArea()
        if total_area == 0:
            return 0.0
        return self.getArea_Sc() / total_area
    
    def get_names(self, name: str, detail: str, verbose: bool = False) -> List[str]:
        """
        Get component names for meshing/CAD
        
        Args:
            name: Base name for components
            detail: Detail level (unused for tape)
            verbose: Whether to print verbose info
            
        Returns:
            List of component names
        """
        names = []
        if self.w > 0:
            names.append(f"{name}_SC")
        if self.e > 0:
            names.append(f"{name}_Insulation")
        
        if verbose and names:
            print(f"Tape components: {names}")
        
        return names
    
    def get_cross_section_points(self, center_y: float = 0.0) -> List[List[float]]:
        """
        Get points defining tape cross-section for 2D visualization
        
        Args:
            center_y: Y-coordinate of tape center
            
        Returns:
            List of [x, y] points defining tape outline
        """
        half_height = self.h / 2.0
        
        if self.e > 0:
            # Tape with insulation - create layered rectangle
            points = [
                [0, center_y - half_height],           # Bottom left
                [self.w, center_y - half_height],      # SC bottom right
                [self.w, center_y + half_height],      # SC top right
                [self.w + self.e, center_y + half_height], # Insulation top right
                [self.w + self.e, center_y - half_height], # Insulation bottom right  
                [0, center_y - half_height]            # Close shape
            ]
        else:
            # Simple rectangle for SC only
            points = [
                [0, center_y - half_height],
                [self.w, center_y - half_height],
                [self.w, center_y + half_height],
                [0, center_y + half_height],
                [0, center_y - half_height]
            ]
        
        return points
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Tape':
        """
        Create Tape from dictionary
        
        Args:
            data: Dictionary with tape parameters
            debug: Whether to print debug info
            
        Returns:
            Tape instance
        """
        if debug:
            print(f"Creating Tape from: {data}")
        
        w = data.get("w", 0)
        h = data.get("h", 0)
        e = data.get("e", 0)
        
        return cls(w, h, e)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "w": self.w,
            "h": self.h,
            "e": self.e
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Tape(w={self.w}, h={self.h}, e={self.e})"
    
    def __str__(self) -> str:
        """Detailed string representation"""
        msg = f"HTS Tape Geometry:\n"
        msg += f"  Superconductor width: {self.w:.3f} mm\n"
        msg += f"  Tape height: {self.h:.3f} mm\n"
        msg += f"  Insulation thickness: {self.e:.3f} mm\n"
        msg += f"  Total width: {self.getW():.3f} mm\n"
        msg += f"  Total area: {self.getArea():.6f} mm²\n"
        msg += f"  Filling factor: {self.getFillingFactor():.1%}"
        return msg


def create_standard_tape(width: float, height: float, 
                        insulation_ratio: float = 0.1) -> Tape:
    """
    Create standard HTS tape with given dimensions
    
    Args:
        width: Total tape width
        height: Tape height
        insulation_ratio: Ratio of insulation to total width
        
    Returns:
        Tape instance
    """
    validate_non_negative(width, "width")
    validate_non_negative(height, "height")
    
    if not 0 <= insulation_ratio <= 1:
        raise ValueError("insulation_ratio must be between 0 and 1")
    
    insulation_width = width * insulation_ratio
    sc_width = width - insulation_width
    
    return Tape(w=sc_width, h=height, e=insulation_width)


def create_rebco_tape(width: float = 4.0, height: float = 0.1) -> Tape:
    """
    Create typical REBCO tape geometry
    
    Args:
        width: SC width (default 4mm, typical for commercial tapes)
        height: Tape height (default 0.1mm)
        
    Returns:
        Tape instance with typical REBCO proportions
    """
    # Typical REBCO: ~10% insulation
    insulation = width * 0.1
    return Tape(w=width, h=height, e=insulation)


def create_bismuth_tape(width: float = 3.0, height: float = 0.2) -> Tape:
    """
    Create typical Bismuth (1G) tape geometry
    
    Args:
        width: SC width (default 3mm)
        height: Tape height (default 0.2mm, thicker than REBCO)
        
    Returns:
        Tape instance with typical Bismuth proportions
    """
    # Bismuth tapes typically have more insulation
    insulation = width * 0.15
    return Tape(w=width, h=height, e=insulation)


# Factory functions registry
TAPE_FACTORIES = {
    "standard": create_standard_tape,
    "rebco": create_rebco_tape,
    "bismuth": create_bismuth_tape,
}


def create_tape_from_spec(tape_type: str, **kwargs) -> Tape:
    """
    Create tape from specification type
    
    Args:
        tape_type: Type of tape ("standard", "rebco", "bismuth")
        **kwargs: Parameters for specific tape type
        
    Returns:
        Tape instance
    """
    if tape_type not in TAPE_FACTORIES:
        raise ValueError(f"Unknown tape type '{tape_type}'. "
                        f"Available types: {list(TAPE_FACTORIES.keys())}")
    
    factory = TAPE_FACTORIES[tape_type]
    return factory(**kwargs)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Chamfer class with validation and type safety
"""

import math
from typing import Optional, Dict, Any
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_positive, validate_angle, validate_enum_value
from ...utils.enums import Side, RadialSide


class Chamfer(SupportComponentBase):
    """
    Chamfer definition with improved validation and type safety
    
    A chamfer is a beveled edge connecting two surfaces. It can be defined
    either by angle and length, or by radial offset and length.
    
    Attributes:
        name: Chamfer identifier
        side: Axial position ("HP" or "BP")
        rside: Radial position ("rint" or "rext") 
        l: Axial length of chamfer
        alpha: Chamfer angle in degrees (optional)
        dr: Radial offset (optional)
    """
    
    yaml_tag = "!Chamfer"
    
    def __init__(
        self, 
        side: str, 
        rside: str, 
        alpha: float, 
        l: float,
        name: str = ""
    ):
        """
        Initialize chamfer
        
        Args:
            side: Axial position ("HP" or "BP")
            rside: Radial position ("rint" or "rext")
            alpha: Chamfer angle in degrees
            l: Axial length of chamfer
            name: Optional chamfer name
        """
        super().__init__(name)
        self.side = side
        self.rside = rside
        self.alpha = alpha
        self.l = l
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate chamfer parameters"""
        super().validate()
        
        # Validate required parameters
        validate_positive(self.l, "l")
        validate_angle(self.alpha, 0, 89, "alpha")
        validate_enum_value(self.side, Side, "side")
        validate_enum_value(self.rside, RadialSide, "rside")
    
    def getRadius(self) -> float:
        """
        Calculate radial offset from angle and length
        
        Returns:
            Radial offset in same units as length
        """
        return self.l * math.tan(math.radians(self.alpha))
    
    def get_dr(self) -> float:
        """Alias for getRadius() for backward compatibility"""
        return self.getRadius()
    
    def get_angle(self) -> float:
        """Get chamfer angle in degrees"""
        return self.alpha
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Chamfer':
        """
        Create Chamfer from dictionary
        
        Args:
            data: Dictionary with chamfer parameters
            debug: Whether to print debug info
            
        Returns:
            Chamfer instance
        """
        if debug:
            print(f"Creating Chamfer from: {data}")
        
        # Handle both old and new data formats
        name = data.get("name", "")
        side = data["side"]
        rside = data["rside"]
        alpha = data["alpha"]
        l = data["L"] if "L" in data else data["l"]  # Support both cases
        
        return cls(side=side, rside=rside, alpha=alpha, l=l, name=name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "side": self.side,
            "rside": self.rside,
            "alpha": self.alpha,
            "L": self.l  # Use "L" for backward compatibility
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(side={self.side}, rside={self.rside}, "
                f"alpha={self.alpha}, L={self.l})")


def Chamfer_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Chamfer.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Chamfer", Chamfer_constructor)

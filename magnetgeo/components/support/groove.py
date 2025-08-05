#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Groove class with validation and type safety
"""

from typing import Dict, Any
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_non_negative, validate_enum_value
from ...utils.enums import GrooveType


class Groove(SupportComponentBase):
    """
    Groove definition with improved validation
    
    Grooves are rectangular channels cut into the surface of a component.
    They are assumed to be "square-like" in cross-section.
    
    Attributes:
        name: Groove identifier
        gtype: Groove type ("rint" or "rext")
        n: Number of grooves
        eps: Depth of groove
    """
    
    yaml_tag = "!Groove"
    
    def __init__(
        self, 
        gtype: str = None, 
        n: int = 0, 
        eps: float = 0.0,
        name: str = ""
    ):
        """
        Initialize groove
        
        Args:
            gtype: Groove type ("rint" or "rext")
            n: Number of grooves
            eps: Depth of groove
            name: Optional groove name
        """
        super().__init__(name)
        self.gtype = gtype
        self.n = n
        self.eps = eps
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate groove parameters"""
        super().validate()
        
        # Only validate if groove is actually defined
        if self.gtype is not None:
            validate_enum_value(self.gtype, GrooveType, "gtype")
        
        if self.n < 0:
            raise ValueError(f"Number of grooves must be non-negative, got {self.n}")
            
        validate_non_negative(self.eps, "eps")
    
    def is_empty(self) -> bool:
        """Check if groove is empty (no grooves defined)"""
        return self.gtype is None or self.n == 0 or self.eps == 0.0
    
    def get_total_volume_reduction(self, radius: float, height: float) -> float:
        """
        Calculate total volume removed by grooves
        
        Args:
            radius: Base radius where grooves are cut
            height: Height over which grooves extend
            
        Returns:
            Total volume reduction
        """
        if self.is_empty():
            return 0.0
        
        # Simplified calculation - assumes rectangular grooves
        groove_volume = self.eps * self.eps * height  # Square cross-section
        return self.n * groove_volume
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Groove':
        """
        Create Groove from dictionary
        
        Args:
            data: Dictionary with groove parameters
            debug: Whether to print debug info
            
        Returns:
            Groove instance
        """
        if debug:
            print(f"Creating Groove from: {data}")
        
        # Handle empty groove case
        if not data or data.get("n", 0) == 0:
            return cls()  # Empty groove
        
        name = data.get("name", "")
        gtype = data.get("gtype")
        n = data.get("n", 0)
        eps = data.get("eps", 0.0)
        
        return cls(gtype=gtype, n=n, eps=eps, name=name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "gtype": self.gtype,
            "n": self.n,
            "eps": self.eps
        }
    
    def __repr__(self) -> str:
        """String representation"""
        if self.is_empty():
            return f"{self.__class__.__name__}(empty)"
        return (f"{self.__class__.__name__}(gtype={self.gtype}, n={self.n}, "
                f"eps={self.eps})")


def Groove_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Groove.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Groove", Groove_constructor)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Tierod class with validation and type safety
"""

from typing import Dict, Any, Union
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_positive, validate_non_negative
from ...utils.io import load_file


class Tierod(SupportComponentBase):
    """
    Tie rod definition with improved validation
    
    Tie rods are structural elements that provide mechanical support
    and electrical connections in magnet assemblies. They are characterized
    by their position, count, and cross-sectional shape.
    
    Attributes:
        r: Radial position of tie rods
        n: Number of tie rods
        dh: Hydraulic diameter (for cooling calculations)
        sh: Cross-sectional area of single tie rod
        shape: 2D shape definition (Shape2D object or filename)
    """
    
    yaml_tag = "!Tierod"
    
    def __init__(
        self, 
        r: float, 
        n: int, 
        dh: float, 
        sh: float, 
        shape: Union[Any, str],
        name: str = ""
    ):
        """
        Initialize tie rod
        
        Args:
            r: Radial position of tie rods
            n: Number of tie rods
            dh: Hydraulic diameter
            sh: Cross-sectional area of single tie rod
            shape: 2D shape (Shape2D object or filename)
            name: Optional tie rod name
        """
        super().__init__(name)
        self.r = r
        self.n = n
        self.dh = dh
        self.sh = sh
        self._shape_data = shape
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate tie rod parameters"""
        super().validate()
        
        validate_positive(self.r, "r")
        
        if self.n <= 0:
            raise ValueError(f"Number of tie rods must be positive, got {self.n}")
            
        validate_positive(self.dh, "dh")
        validate_positive(self.sh, "sh")
    
    @property
    def shape(self):
        """
        Get shape object (lazy loading)
        
        Returns:
            Shape2D object defining tie rod cross-section
        """
        if hasattr(self, '_shape_object'):
            return self._shape_object
        
        if isinstance(self._shape_data, str):
            # Load from file
            try:
                from ..shape2d import Shape2D
                self._shape_object = load_file(f"{self._shape_data}.yaml", Shape2D)
            except ImportError:
                # Fallback if Shape2D not available
                import yaml
                with open(f"{self._shape_data}.yaml", 'r') as f:
                    self._shape_object = yaml.load(f, Loader=yaml.FullLoader)
        else:
            self._shape_object = self._shape_data
        
        return self._shape_object
    
    def get_total_area(self) -> float:
        """
        Calculate total cross-sectional area of all tie rods
        
        Returns:
            Total area = n * sh
        """
        return self.n * self.sh
    
    def get_angular_spacing(self) -> float:
        """
        Calculate angular spacing between tie rods
        
        Returns:
            Angular spacing in degrees (360 / n)
        """
        return 360.0 / self.n if self.n > 0 else 0.0
    
    def get_positions(self) -> list:
        """
        Get angular positions of all tie rods
        
        Returns:
            List of angular positions in degrees
        """
        if self.n <= 0:
            return []
        
        spacing = self.get_angular_spacing()
        return [i * spacing for i in range(self.n)]
    
    def get_structural_properties(self) -> Dict[str, float]:
        """
        Get structural properties of tie rod assembly
        
        Returns:
            Dictionary with structural properties
        """
        import math
        
        # Second moment of area for circular cross-section (approximation)
        # I = pi * d^4 / 64, where d is diameter from hydraulic diameter
        diameter = self.dh  # Approximation
        moment_of_inertia = math.pi * diameter**4 / 64
        
        return {
            "total_area": self.get_total_area(),
            "angular_spacing": self.get_angular_spacing(),
            "diameter_approx": diameter,
            "moment_of_inertia_single": moment_of_inertia,
            "total_moment_of_inertia": self.n * moment_of_inertia
        }
    
    def calculate_equivalent_thickness(self, radius: float = None) -> float:
        """
        Calculate equivalent annular thickness for material calculations
        
        Args:
            radius: Reference radius (uses self.r if not provided)
            
        Returns:
            Equivalent thickness
        """
        import math
        ref_radius = radius or self.r
        return self.n * self.sh / (2 * math.pi * ref_radius)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Tierod':
        """
        Create Tierod from dictionary
        
        Args:
            data: Dictionary with tie rod parameters
            debug: Whether to print debug info
            
        Returns:
            Tierod instance
        """
        if debug:
            print(f"Creating Tierod from: {data}")
        
        name = data.get("name", "")
        r = data["r"]
        n = data["n"]
        dh = data["dh"]
        sh = data["sh"]
        shape = data["shape"]
        
        return cls(r=r, n=n, dh=dh, sh=sh, shape=shape, name=name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        # Handle shape serialization
        shape_data = self._shape_data
        if hasattr(self._shape_data, 'to_dict'):
            shape_data = self._shape_data.to_dict()
        elif hasattr(self._shape_data, 'name'):
            shape_data = self._shape_data.name  # Use name reference
        
        return {
            "name": self.name,
            "r": self.r,
            "n": self.n,
            "dh": self.dh,
            "sh": self.sh,
            "shape": shape_data
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(r={self.r}, n={self.n}, "
                f"dh={self.dh}, sh={self.sh})")


def Tierod_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Tierod.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Tierod", Tierod_constructor)

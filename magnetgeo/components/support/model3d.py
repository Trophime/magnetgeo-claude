#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Model3D class with validation
"""

from typing import Dict, Any
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_string_not_empty


class Model3D(SupportComponentBase):
    """
    3D Model configuration with improved validation
    
    Defines the 3D modeling parameters for generating CAD models
    from axisymmetric definitions.
    
    Attributes:
        cad: CAD system identifier
        with_shapes: Whether to include shape cuts
        with_channels: Whether to include cooling channels
    """
    
    yaml_tag = "!Model3D"
    
    def __init__(
        self, 
        cad: str, 
        with_shapes: bool = False, 
        with_channels: bool = False,
        name: str = ""
    ):
        """
        Initialize 3D model configuration
        
        Args:
            cad: CAD system identifier
            with_shapes: Whether to include shape cuts
            with_channels: Whether to include cooling channels
            name: Optional model name
        """
        super().__init__(name)
        self.cad = cad
        self.with_shapes = with_shapes
        self.with_channels = with_channels
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate 3D model parameters"""
        super().validate()
        
        validate_string_not_empty(self.cad, "cad")
        
        if not isinstance(self.with_shapes, bool):
            raise TypeError("with_shapes must be boolean")
            
        if not isinstance(self.with_channels, bool):
            raise TypeError("with_channels must be boolean")
    
    def get_model_type(self) -> str:
        """
        Get model type based on configuration
        
        Returns:
            Model type string ("HR" for high resistance, "HL" for low resistance)
        """
        if self.with_shapes and self.with_channels:
            return "HR"  # High resistance (with cooling channels)
        return "HL"  # Low resistance (simple helix)
    
    def is_complex_model(self) -> bool:
        """Check if this is a complex model with shapes and channels"""
        return self.with_shapes and self.with_channels
    
    def get_required_features(self) -> list:
        """Get list of required CAD features"""
        features = ["basic_geometry"]
        
        if self.with_shapes:
            features.append("shape_cuts")
            
        if self.with_channels:
            features.append("cooling_channels")
            
        return features
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Model3D':
        """
        Create Model3D from dictionary
        
        Args:
            data: Dictionary with model parameters
            debug: Whether to print debug info
            
        Returns:
            Model3D instance
        """
        if debug:
            print(f"Creating Model3D from: {data}")
        
        name = data.get("name", "")
        cad = data["cad"]
        with_shapes = data.get("with_shapes", False)
        with_channels = data.get("with_channels", False)
        
        return cls(
            cad=cad, 
            with_shapes=with_shapes, 
            with_channels=with_channels, 
            name=name
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "cad": self.cad,
            "with_shapes": self.with_shapes,
            "with_channels": self.with_channels
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(cad={self.cad}, "
                f"with_shapes={self.with_shapes}, with_channels={self.with_channels})")


def Model3D_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Model3D.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Model3D", Model3D_constructor)

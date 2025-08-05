#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Shape class with validation and type safety
"""

from typing import Dict, Any, List
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_positive, validate_angle, validate_enum_value
from ...utils.enums import ShapePosition


class Shape(SupportComponentBase):
    """
    Shape definition for helical cuts with improved validation
    
    Shapes define cutting patterns that can be added to helical windings
    to create cooling channels or other features.
    
    Attributes:
        name: Shape identifier
        profile: Name of the cut profile to be added
        length: Angular length of shape in degrees (single value or list)
        angle: Angle between consecutive shapes in degrees (single value or list)
        onturns: Which turns to add cuts to (single value or list)
        position: Position relative to helix ("ABOVE", "BELOW", "ALTERNATE")
    """
    
    yaml_tag = "!Shape"
    
    def __init__(
        self,
        name: str,
        profile: str,
        length: List[float] = None,
        angle: List[float] = None,
        onturns: List[int] = None,
        position: str = "ABOVE"
    ):
        """
        Initialize shape
        
        Args:
            name: Shape identifier
            profile: Name of cut profile
            length: Angular length(s) in degrees
            angle: Angle(s) between consecutive shapes in degrees
            onturns: Turn number(s) to add cuts to
            position: Position relative to helix
        """
        super().__init__(name)
        self.profile = profile
        self.length = length or [0.0]
        self.angle = angle or [0.0]
        self.onturns = onturns or [1]
        self.position = position
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate shape parameters"""
        super().validate()
        
        # Validate profile
        if not isinstance(self.profile, str):
            raise TypeError("profile must be a string")
        
        # Validate lists
        if not isinstance(self.length, list):
            raise TypeError("length must be a list")
        if not isinstance(self.angle, list):
            raise TypeError("angle must be a list")
        if not isinstance(self.onturns, list):
            raise TypeError("onturns must be a list")
        
        # Validate length values
        for i, length_val in enumerate(self.length):
            if length_val < 0:
                raise ValueError(f"length[{i}] must be non-negative, got {length_val}")
            if length_val > 360:
                raise ValueError(f"length[{i}] must be <= 360°, got {length_val}")
        
        # Validate angle values
        for i, angle_val in enumerate(self.angle):
            if angle_val < 0:
                raise ValueError(f"angle[{i}] must be non-negative, got {angle_val}")
            if angle_val > 360:
                raise ValueError(f"angle[{i}] must be <= 360°, got {angle_val}")
        
        # Validate turn numbers
        for i, turn_num in enumerate(self.onturns):
            if turn_num < 1:
                raise ValueError(f"onturns[{i}] must be >= 1, got {turn_num}")
        
        # Validate position
        validate_enum_value(self.position, ShapePosition, "position")
    
    def get_total_shapes_per_turn(self) -> int:
        """
        Calculate total number of shapes per turn
        
        Returns:
            Number of shapes based on angle spacing
        """
        if not self.angle or self.angle[0] == 0:
            return 0
        return int(360.0 / self.angle[0])
    
    def get_total_shapes(self, total_turns: int) -> int:
        """
        Calculate total number of shapes for all turns
        
        Args:
            total_turns: Total number of turns in helix
            
        Returns:
            Total number of shapes
        """
        shapes_per_turn = self.get_total_shapes_per_turn()
        affected_turns = len(self.onturns)
        
        if self.position == "ALTERNATE":
            # Alternating pattern affects different turns
            return shapes_per_turn * (total_turns // 2)
        else:
            return shapes_per_turn * affected_turns
    
    def is_empty(self) -> bool:
        """Check if shape is effectively empty"""
        return (not self.profile or 
                all(l == 0 for l in self.length) or 
                all(a == 0 for a in self.angle))
    
    def get_angular_positions(self, turn_number: int) -> List[float]:
        """
        Get angular positions of shapes for a specific turn
        
        Args:
            turn_number: Turn number (1-based)
            
        Returns:
            List of angular positions in degrees
        """
        if turn_number not in self.onturns:
            return []
        
        if self.is_empty():
            return []
        
        positions = []
        angle_step = self.angle[0] if self.angle else 360.0
        
        if angle_step > 0:
            num_shapes = int(360.0 / angle_step)
            for i in range(num_shapes):
                position = i * angle_step
                
                # Apply position offset based on turn number
                if self.position == "ALTERNATE" and turn_number % 2 == 0:
                    position += angle_step / 2  # Offset for even turns
                
                positions.append(position % 360.0)
        
        return positions
    
    def get_shape_info(self) -> Dict[str, Any]:
        """
        Get comprehensive shape information
        
        Returns:
            Dictionary with shape properties
        """
        return {
            "name": self.name,
            "profile": self.profile,
            "is_empty": self.is_empty(),
            "shapes_per_turn": self.get_total_shapes_per_turn(),
            "affected_turns": self.onturns,
            "position_strategy": self.position,
            "angular_spacing": self.angle[0] if self.angle else 0,
            "angular_length": self.length[0] if self.length else 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Shape':
        """
        Create Shape from dictionary
        
        Args:
            data: Dictionary with shape parameters
            debug: Whether to print debug info
            
        Returns:
            Shape instance
        """
        if debug:
            print(f"Creating Shape from: {data}")
        
        name = data.get("name", "")
        profile = data.get("profile", "")
        length = data.get("length", [0.0])
        angle = data.get("angle", [0.0])
        onturns = data.get("onturns", [1])
        position = data.get("position", "ABOVE")
        
        # Ensure lists
        if not isinstance(length, list):
            length = [length]
        if not isinstance(angle, list):
            angle = [angle]
        if not isinstance(onturns, list):
            onturns = [onturns]
        
        return cls(
            name=name, profile=profile, length=length, 
            angle=angle, onturns=onturns, position=position
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "profile": self.profile,
            "length": self.length,
            "angle": self.angle,
            "onturns": self.onturns,
            "position": self.position
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}(name={self.name}, profile={self.profile}, "
                f"length={self.length}, angle={self.angle}, onturns={self.onturns}, "
                f"position={self.position})")


def Shape_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Shape.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Shape", Shape_constructor)

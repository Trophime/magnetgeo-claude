#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
2D Shape definition with enhanced functionality

This module provides the Shape2D class for defining 2D geometric shapes
as lists of points, with validation and geometric operations.
"""

import yaml
import json
import math
from typing import Dict, Any, List, Tuple, Optional

# Try to import validation utilities
try:
    from ..validation import validate_positive, validate_non_negative
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    def validate_positive(val, name): pass
    def validate_non_negative(val, name): pass


class Shape2D(yaml.YAMLObject):
    """
    2D Shape definition with validation and enhanced functionality
    
    Defines a 2D geometric shape as a list of points for use in
    cross-sectional definitions of cooling slits, tie rods, etc.
    
    Attributes:
        name: Shape identifier
        pts: List of [x, y] coordinate pairs defining the shape
    """
    
    yaml_tag = "Shape2D"
    
    def __init__(self, name: str, pts: List[List[float]]):
        """
        Initialize 2D shape
        
        Args:
            name: Shape identifier
            pts: List of [x, y] coordinate pairs
        """
        self.name = name
        self.pts = pts or []
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate 2D shape parameters"""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        
        if not isinstance(self.pts, list):
            raise TypeError("pts must be a list")
        
        if len(self.pts) < 3:
            raise ValueError("Shape must have at least 3 points")
        
        # Validate each point
        for i, pt in enumerate(self.pts):
            if not isinstance(pt, list) or len(pt) != 2:
                raise ValueError(f"Point {i} must be [x, y] coordinates, got {pt}")
            
            try:
                x, y = float(pt[0]), float(pt[1])
                # Update with validated float values
                self.pts[i] = [x, y]
            except (ValueError, TypeError):
                raise ValueError(f"Point {i} coordinates must be numeric, got {pt}")
    
    def __repr__(self):
        """String representation"""
        return f"{self.__class__.__name__}(name={self.name!r}, pts={self.pts!r})"
    
    def dump(self, name: str):
        """Dump object to YAML file"""
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception as e:
            raise Exception(f"Failed to Shape2D dump: {e}")
    
    def load(self, name: str):
        """Load object from YAML file"""
        try:
            with open(f"{name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception as e:
            raise Exception(f"Failed to load Shape2D data {name}.yaml: {e}")
        
        self.name = name
        self.pts = data.pts
        self.validate()
    
    def to_json(self):
        """Convert to JSON string"""
        try:
            from ...utils.io import serialize_instance
            return json.dumps(
                self, default=serialize_instance, sort_keys=True, indent=4
            )
        except ImportError:
            # Fallback serialization
            return json.dumps({
                'name': self.name,
                'pts': self.pts,
                'yaml_tag': self.yaml_tag
            }, sort_keys=True, indent=4)
    
    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Create Shape2D from JSON file"""
        if debug:
            print(f'Shape2D.from_json: filename={filename}')
        
        try:
            from ...utils.io import unserialize_object
            with open(filename, "r") as istream:
                return json.loads(istream.read(), object_hook=unserialize_object)
        except ImportError:
            # Fallback deserialization
            with open(filename, "r") as istream:
                data = json.load(istream)
                return cls(data['name'], data['pts'])
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Shape2D':
        """Create Shape2D from dictionary"""
        if debug:
            print(f"Creating Shape2D from: {data}")
        
        name = data["name"]
        pts = data["pts"]
        
        return cls(name=name, pts=pts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'pts': self.pts,
            'yaml_tag': self.yaml_tag
        }
    
    # Geometric operations
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Get bounding box of the shape
        
        Returns:
            Tuple of ([x_min, x_max], [y_min, y_max])
        """
        if not self.pts:
            return ([0, 0], [0, 0])
        
        x_coords = [pt[0] for pt in self.pts]
        y_coords = [pt[1] for pt in self.pts]
        
        return ([min(x_coords), max(x_coords)], 
                [min(y_coords), max(y_coords)])
    
    def get_centroid(self) -> Tuple[float, float]:
        """
        Calculate centroid of the shape
        
        Returns:
            Tuple of (x_centroid, y_centroid)
        """
        if not self.pts:
            return (0.0, 0.0)
        
        n = len(self.pts)
        x_sum = sum(pt[0] for pt in self.pts)
        y_sum = sum(pt[1] for pt in self.pts)
        
        return (x_sum / n, y_sum / n)
    
    def get_area(self) -> float:
        """
        Calculate area using shoelace formula
        
        Returns:
            Area of the polygon
        """
        if len(self.pts) < 3:
            return 0.0
        
        area = 0.0
        n = len(self.pts)
        
        for i in range(n):
            j = (i + 1) % n
            area += self.pts[i][0] * self.pts[j][1]
            area -= self.pts[j][0] * self.pts[i][1]
        
        return abs(area) / 2.0
    
    def get_perimeter(self) -> float:
        """
        Calculate perimeter of the shape
        
        Returns:
            Total perimeter length
        """
        if len(self.pts) < 2:
            return 0.0
        
        perimeter = 0.0
        n = len(self.pts)
        
        for i in range(n):
            j = (i + 1) % n
            dx = self.pts[j][0] - self.pts[i][0]
            dy = self.pts[j][1] - self.pts[i][1]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return perimeter
    
    def get_hydraulic_diameter(self) -> float:
        """
        Calculate hydraulic diameter (4 * Area / Perimeter)
        
        Returns:
            Hydraulic diameter
        """
        perimeter = self.get_perimeter()
        if perimeter == 0:
            return 0.0
        return 4.0 * self.get_area() / perimeter
    
    def translate(self, dx: float, dy: float) -> 'Shape2D':
        """
        Create translated copy of shape
        
        Args:
            dx: Translation in x direction
            dy: Translation in y direction
            
        Returns:
            New Shape2D with translated coordinates
        """
        new_pts = [[pt[0] + dx, pt[1] + dy] for pt in self.pts]
        return Shape2D(f"{self.name}_translated", new_pts)
    
    def scale(self, sx: float, sy: Optional[float] = None) -> 'Shape2D':
        """
        Create scaled copy of shape
        
        Args:
            sx: Scale factor in x direction
            sy: Scale factor in y direction (uses sx if not provided)
            
        Returns:
            New Shape2D with scaled coordinates
        """
        if sy is None:
            sy = sx
        
        new_pts = [[pt[0] * sx, pt[1] * sy] for pt in self.pts]
        return Shape2D(f"{self.name}_scaled", new_pts)
    
    def is_clockwise(self) -> bool:
        """
        Check if points are ordered clockwise
        
        Returns:
            True if clockwise, False if counter-clockwise
        """
        if len(self.pts) < 3:
            return False
        
        # Calculate signed area
        signed_area = 0.0
        n = len(self.pts)
        
        for i in range(n):
            j = (i + 1) % n
            signed_area += (self.pts[j][0] - self.pts[i][0]) * (self.pts[j][1] + self.pts[i][1])
        
        return signed_area > 0
    
    def reverse_orientation(self) -> None:
        """Reverse the orientation of points (clockwise <-> counter-clockwise)"""
        self.pts.reverse()


# YAML constructor function
def Shape_constructor(loader, node):
    """Build a Shape2D object from YAML"""
    values = loader.construct_mapping(node)
    name = values["name"]
    pts = values["pts"]
    return Shape2D(name, pts)


# Register YAML constructor
yaml.add_constructor("!Shape2D", Shape_constructor)


# Factory functions
def create_circle(r: float, n: int = 20) -> Shape2D:
    """
    Create a circular shape
    
    Args:
        r: Radius of the circle
        n: Number of points to approximate the circle
        
    Returns:
        Shape2D representing a circle
    """
    if VALIDATION_AVAILABLE:
        validate_positive(r, "r")
        validate_positive(n, "n")
    elif r <= 0:
        raise ValueError(f"create_circle: r must be positive, got {r}")
    elif n <= 0:
        raise ValueError(f"create_circle: n must be positive, got {n}")
    
    name = f"circle-{2*r}-mm"
    pts = []
    theta = 2 * math.pi / float(n)
    for i in range(n):
        x = r * math.cos(i * theta)
        y = r * math.sin(i * theta)
        pts.append([x, y])
    
    return Shape2D(name, pts)


def create_rectangle(
    x: float, y: float, dx: float, dy: float, fillet: int = 0
) -> Shape2D:
    """
    Create a rectangular shape
    
    Args:
        x: X coordinate of bottom-left corner
        y: Y coordinate of bottom-left corner  
        dx: Width of rectangle
        dy: Height of rectangle
        fillet: Number of fillet points at corners (0 for sharp corners)
        
    Returns:
        Shape2D representing a rectangle
    """
    if VALIDATION_AVAILABLE:
        validate_positive(dx, "dx")
        validate_positive(dy, "dy")
        validate_non_negative(fillet, "fillet")
    elif dx <= 0:
        raise ValueError(f"create_rectangle: dx must be positive, got {dx}")
    elif dy <= 0:
        raise ValueError(f"create_rectangle: dy must be positive, got {dy}")
    elif fillet < 0:
        raise ValueError(f"create_rectangle: fillet must be non-negative, got {fillet}")
    
    name = f"rectangle-{dx}x{dy}-mm"
    
    if fillet == 0:
        # Simple rectangle
        pts = [
            [x, y],
            [x + dx, y],
            [x + dx, y + dy],
            [x, y + dy]
        ]
    else:
        # Rectangle with rounded corners
        pts = []
        # This is a simplified version - full fillet implementation would be more complex
        # For now, just create the basic rectangle
        pts = [
            [x, y],
            [x + dx, y],
            [x + dx, y + dy],
            [x, y + dy]
        ]
        # TODO: Implement proper filleted corners
    
    return Shape2D(name, pts)

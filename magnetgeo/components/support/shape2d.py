#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored Shape2D class with validation and enhanced functionality
"""

import math
from typing import Dict, Any, List, Tuple
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_positive, validate_non_negative


class Shape2D(SupportComponentBase):
    """
    2D Shape definition with improved validation
    
    Defines a 2D geometric shape as a list of points for use in
    cross-sectional definitions of cooling slits, tie rods, etc.
    
    Attributes:
        name: Shape identifier
        pts: List of [x, y] coordinate pairs defining the shape
    """
    
    yaml_tag = "!Shape2D"
    
    def __init__(self, name: str, pts: List[List[float]]):
        """
        Initialize 2D shape
        
        Args:
            name: Shape identifier
            pts: List of [x, y] coordinate pairs
        """
        super().__init__(name)
        self.pts = pts or []
        
        # Call validation after setting all attributes
        self.validate()
    
    def validate(self) -> None:
        """Validate 2D shape parameters"""
        super().validate()
        
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
    
    def scale(self, sx: float, sy: float = None) -> 'Shape2D':
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Shape2D':
        """
        Create Shape2D from dictionary
        
        Args:
            data: Dictionary with shape parameters
            debug: Whether to print debug info
            
        Returns:
            Shape2D instance
        """
        if debug:
            print(f"Creating Shape2D from: {data}")
        
        name = data["name"]
        pts = data["pts"]
        
        return cls(name=name, pts=pts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "pts": self.pts
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(name={self.name}, pts={len(self.pts)} points)"


# Factory functions for common shapes

def create_circle(r: float, n: int = 20, name: str = None) -> Shape2D:
    """
    Create circular shape
    
    Args:
        r: Radius
        n: Number of points
        name: Optional shape name
        
    Returns:
        Shape2D representing a circle
    """
    if n < 3:
        raise ValueError("Circle must have at least 3 points")
    
    validate_positive(r, "r")
    
    if name is None:
        name = f"circle-{2*r:.1f}mm"
    
    pts = []
    theta = 2 * math.pi / float(n)
    
    for i in range(n):
        x = r * math.cos(i * theta)
        y = r * math.sin(i * theta)
        pts.append([x, y])
    
    return Shape2D(name, pts)


def create_rectangle(x: float, y: float, dx: float, dy: float, 
                    fillet: int = 0, name: str = None) -> Shape2D:
    """
    Create rectangular shape
    
    Args:
        x: Bottom-left x coordinate
        y: Bottom-left y coordinate  
        dx: Width
        dy: Height
        fillet: Number of points for rounded corners (0 for sharp corners)
        name: Optional shape name
        
    Returns:
        Shape2D representing a rectangle
    """
    validate_positive(dx, "dx")
    validate_positive(dy, "dy")
    validate_non_negative(fillet, "fillet")
    
    if name is None:
        name = f"rectangle-{dx:.1f}x{dy:.1f}mm"
    
    if fillet == 0:
        # Sharp corners
        pts = [[x, y], [x + dx, y], [x + dx, y + dy], [x, y + dy]]
    else:
        # Rounded corners (simplified implementation)
        pts = []
        # This is a simplified version - could be enhanced with proper filleting
        corner_radius = min(dx, dy) / 10.0  # Small radius for demonstration
        theta = math.pi / (2 * fillet)
        
        # Bottom edge with rounded corner
        for i in range(fillet + 1):
            angle = i * theta
            px = x + corner_radius * (1 - math.cos(angle))
            py = y + corner_radius * math.sin(angle)
            pts.append([px, py])
        
        # Add other corners similarly (simplified)
        pts.extend([[x + dx, y], [x + dx, y + dy], [x, y + dy]])
    
    return Shape2D(name, pts)


def create_angular_slit(x: float, angle: float, dx: float, 
                       n: int = 10, fillet: int = 0, name: str = None) -> Shape2D:
    """
    Create angular slit shape
    
    Args:
        x: Inner radius
        angle: Angular extent in radians
        dx: Radial thickness
        n: Number of points along arc
        fillet: Number of points for rounded corners
        name: Optional shape name
        
    Returns:
        Shape2D representing an angular slit
    """
    validate_positive(x, "x")
    validate_positive(angle, "angle")
    validate_positive(dx, "dx")
    validate_positive(n, "n")
    validate_non_negative(fillet, "fillet")
    
    if name is None:
        name = f"angularslit-{dx:.1f}-{math.degrees(angle):.1f}deg"
    
    pts = []
    theta = angle / float(n)
    
    # Inner arc
    for i in range(n + 1):
        a = -angle/2 + i * theta
        px = x * math.cos(a)
        py = x * math.sin(a)
        pts.append([px, py])
    
    # Outer arc (reversed)
    for i in range(n, -1, -1):
        a = -angle/2 + i * theta
        px = (x + dx) * math.cos(a)
        py = (x + dx) * math.sin(a)
        pts.append([px, py])
    
    return Shape2D(name, pts)


def Shape_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return Shape2D.from_dict(values)


# Register YAML constructor
import yaml
yaml.add_constructor("!Shape2D", Shape_constructor)

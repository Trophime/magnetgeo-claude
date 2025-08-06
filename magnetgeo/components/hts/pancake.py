#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS Pancake geometric definition

Defines the geometric structure of HTS pancake coils including
inner radius, turn count, tape geometry, and mandrel dimensions.
"""

from typing import Dict, Any, List, Union
from .tape import Tape

try:
    from ...base.support_base import SupportComponentBase
    from ...utils.validation import validate_non_negative, validate_positive
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    SupportComponentBase = object
    def validate_non_negative(val, name): pass
    def validate_positive(val, name): pass


class Pancake(SupportComponentBase if BASE_AVAILABLE else object):
    """
    HTS pancake coil geometric definition
    
    Represents the geometric structure of a flat coil (pancake) of HTS tape
    wound around a central mandrel.
    
    Attributes:
        r0: Inner radius of pancake coil (mm)
        mandrin: Mandrel inner radius for mesh purposes (mm)
        tape: Tape geometry object
        n: Number of tape turns
    """
    
    yaml_tag = "!Pancake"
    
    def __init__(
        self, 
        r0: float = 0, 
        tape: Tape = None, 
        n: int = 0, 
        mandrin: float = 0
    ) -> None:
        """
        Initialize pancake geometry
        
        Args:
            r0: Inner radius of pancake coil
            tape: Tape geometry object
            n: Number of tape turns
            mandrin: Mandrel inner radius
        """
        if BASE_AVAILABLE:
            super().__init__()
        
        self.r0 = float(r0)
        self.mandrin = float(mandrin)
        self.tape = tape if tape is not None else Tape()
        self.n = int(n)
        
        self.validate()
    
    def validate(self) -> None:
        """Validate pancake geometric parameters"""
        if BASE_AVAILABLE:
            super().validate()
        
        validate_non_negative(self.r0, "r0 (inner radius)")
        validate_non_negative(self.mandrin, "mandrin (mandrel radius)")
        
        if self.n < 0:
            raise ValueError("Number of turns must be non-negative")
        
        if self.mandrin > self.r0:
            raise ValueError(f"Mandrel radius ({self.mandrin}) must be <= inner radius ({self.r0})")
        
        if self.tape:
            self.tape.validate()
    
    def getN(self) -> int:
        """Get number of turns"""
        return self.n
    
    def getTape(self) -> Tape:
        """Get tape geometry object"""
        return self.tape
    
    def getR0(self) -> float:
        """Get pancake inner radius"""
        return self.r0
    
    def getMandrin(self) -> float:
        """Get mandrel inner radius"""
        return self.mandrin
    
    def getR1(self) -> float:
        """Get pancake outer radius"""
        if self.tape and self.n > 0:
            return self.r0 + self.n * self.tape.getW()
        return self.r0
    
    def getW(self) -> float:
        """Get pancake radial width"""
        return self.getR1() - self.getR0()
    
    def getH(self) -> float:
        """Get pancake height (same as tape height)"""
        return self.tape.getH() if self.tape else 0.0
    
    def getArea(self) -> float:
        """Get pancake cross-sectional area in r-z plane"""
        return self.getW() * self.getH()
    
    def getR(self) -> List[float]:
        """
        Get list of tape turn inner radii
        
        Returns:
            List of radii for each tape turn
        """
        if not self.tape or self.n == 0:
            return []
        
        radii = []
        ri = self.getR0()
        dr = self.tape.getW()
        
        for i in range(self.n):
            radii.append(ri)
            ri += dr
        
        return radii
    
    def get_turn_centers(self) -> List[float]:
        """
        Get radial positions of tape turn centers
        
        Returns:
            List of center radii for each turn
        """
        if not self.tape or self.n == 0:
            return []
        
        centers = []
        ri = self.getR0()
        dr = self.tape.getW()
        
        for i in range(self.n):
            centers.append(ri + dr / 2.0)
            ri += dr
        
        return centers
    
    def getFillingFactor(self) -> float:
        """
        Get geometric filling factor (ratio of tape area to total pancake area)
        
        Returns:
            Filling factor as fraction (0.0 to 1.0)
        """
        total_area = self.getArea()
        if total_area == 0 or not self.tape:
            return 0.0
        
        tape_area = self.n * self.tape.getArea()
        return tape_area / total_area
    
    def get_names(self, name: str, detail: str, verbose: bool = False) -> Union[str, List[str]]:
        """
        Get component names for meshing/CAD
        
        Args:
            name: Base name for components
            detail: Detail level ("pancake", "turn", or "tape")
            verbose: Whether to print verbose info
            
        Returns:
            Component name(s) based on detail level
        """
        if detail == "pancake":
            return name
        
        names = []
        
        # Add mandrel if present
        if self.mandrin < self.r0:
            names.append(f"{name}_Mandrel")
        
        if detail == "turn":
            # Individual turns
            for i in range(self.n):
                names.append(f"{name}_Turn{i}")
        elif detail == "tape":
            # Individual tape components per turn
            for i in range(self.n):
                tape_names = self.tape.get_names(f"{name}_Turn{i}", detail)
                names.extend(tape_names)
        else:
            # Default: just pancake name
            names.append(name)
        
        if verbose:
            print(f"Pancake '{name}' components ({detail}): {names}")
        
        return names
    
    def get_bounds(self) -> tuple:
        """
        Get geometric bounds as (r_bounds, z_bounds)
        
        Returns:
            Tuple of ([r_min, r_max], [z_min, z_max])
        """
        r_min = self.mandrin if self.mandrin < self.r0 else self.r0
        r_max = self.getR1()
        
        half_height = self.getH() / 2.0
        z_min = -half_height
        z_max = half_height
        
        return ([r_min, r_max], [z_min, z_max])
    
    def calculate_length(self) -> float:
        """
        Calculate total length of tape in pancake
        
        Returns:
            Total tape length (mm)
        """
        if not self.tape or self.n == 0:
            return 0.0
        
        import math
        
        total_length = 0.0
        radii = self.get_turn_centers()
        
        for radius in radii:
            circumference = 2 * math.pi * radius
            total_length += circumference
        
        return total_length
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'Pancake':
        """
        Create Pancake from dictionary
        
        Args:
            data: Dictionary with pancake parameters
            debug: Whether to print debug info
            
        Returns:
            Pancake instance
        """
        if debug:
            print(f"Creating Pancake from: {data}")
        
        r0 = data.get("r0", 0)
        mandrin = data.get("mandrin", 0)
        n = data.get("ntapes", data.get("n", 0))  # Support both field names
        
        # Handle tape data
        tape_data = data.get("tape", {})
        if isinstance(tape_data, dict):
            tape = Tape.from_dict(tape_data, debug=debug)
        else:
            # Assume it's already a Tape object
            tape = tape_data
        
        return cls(r0, tape, n, mandrin)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "r0": self.r0,
            "mandrin": self.mandrin,
            "ntapes": self.n,
            "tape": self.tape.to_dict() if self.tape else {}
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"Pancake(r0={self.r0}, n={self.n}, tape={self.tape}, mandrin={self.mandrin})"
    
    def __str__(self) -> str:
        """Detailed string representation"""
        msg = f"HTS Pancake Geometry:\n"
        msg += f"  Inner radius: {self.r0:.3f} mm\n"
        msg += f"  Outer radius: {self.getR1():.3f} mm\n"
        msg += f"  Radial width: {self.getW():.3f} mm\n"
        msg += f"  Height: {self.getH():.3f} mm\n"
        msg += f"  Number of turns: {self.n}\n"
        msg += f"  Mandrel radius: {self.mandrin:.3f} mm\n"
        if self.tape:
            msg += f"  Tape width: {self.tape.getW():.3f} mm\n"
            msg += f"  Total length: {self.calculate_length():.1f} mm\n"
        msg += f"  Filling factor: {self.getFillingFactor():.1%}"
        return msg


def create_uniform_pancake(r0: float, r1: float, height: float, 
                          tape_width: float, mandrin_offset: float = 1.0) -> Pancake:
    """
    Create pancake that fills specified radial space uniformly
    
    Args:
        r0: Inner radius
        r1: Outer radius
        height: Pancake height
        tape_width: Tape total width
        mandrin_offset: Mandrel offset from inner radius
        
    Returns:
        Pancake instance
    """
    validate_positive(r1 - r0, "radial width")
    validate_positive(height, "height")
    validate_positive(tape_width, "tape_width")
    
    radial_width = r1 - r0
    n_turns = int(radial_width / tape_width) if tape_width > 0 else 0
    
    # Create tape with standard proportions
    tape = Tape(w=tape_width * 0.9, h=height, e=tape_width * 0.1)
    mandrin = max(0, r0 - mandrin_offset)
    
    return Pancake(r0=r0, tape=tape, n=n_turns, mandrin=mandrin)


def create_solenoid_pancake(r0: float, n_turns: int, tape: Tape, 
                           mandrin_offset: float = 1.0) -> Pancake:
    """
    Create solenoid-style pancake with specified number of turns
    
    Args:
        r0: Inner radius
        n_turns: Number of turns
        tape: Tape geometry
        mandrin_offset: Mandrel offset from inner radius
        
    Returns:
        Pancake instance
    """
    validate_positive(r0, "r0")
    validate_positive(n_turns, "n_turns")
    
    if not isinstance(tape, Tape):
        raise TypeError("tape must be a Tape instance")
    
    mandrin = max(0, r0 - mandrin_offset)
    
    return Pancake(r0=r0, tape=tape, n=n_turns, mandrin=mandrin)


def create_racetrack_pancake(r0: float, straight_length: float, 
                            n_turns: int, tape: Tape) -> Pancake:
    """
    Create racetrack-shaped pancake (placeholder for future implementation)
    
    Args:
        r0: Inner radius of curved sections
        straight_length: Length of straight sections
        n_turns: Number of turns
        tape: Tape geometry
        
    Returns:
        Pancake instance (circular approximation for now)
        
    Note:
        This is a placeholder. Full racetrack geometry would require
        additional geometric definitions beyond simple pancake model.
    """
    # For now, approximate as circular with equivalent area
    import math
    
    # Approximate equivalent radius
    curved_circumference = 2 * math.pi * r0
    total_length_per_turn = curved_circumference + 2 * straight_length
    equiv_radius = total_length_per_turn / (2 * math.pi)
    
    return Pancake(r0=r0, tape=tape, n=n_turns, mandrin=r0 * 0.9)

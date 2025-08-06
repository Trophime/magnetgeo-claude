#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Refactored CoolingSlit class with validation and type safety
"""

from typing import Dict, Any, Union
from ...base.support_base import SupportComponentBase
from ...utils.validation import validate_positive, validate_angle
from ...utils.io import load_file

import yaml


class CoolingSlit(SupportComponentBase):
    """
    Cooling slit definition with improved validation

    Cooling slits are channels cut into magnet components for coolant flow.
    They are characterized by their position, count, hydraulic properties,
    and cross-sectional shape.

    Attributes:
        r: Radial position of slits
        angle: Angular shift from reference (degrees)
        n: Number of slits
        dh: Hydraulic diameter (4*Area/Perimeter)
        sh: Cross-sectional area of single slit
        shape: 2D shape definition (Shape2D object or filename)
    """

    yaml_tag = "!Slit"

    def __init__(
        self,
        r: float,
        angle: float,
        n: int,
        dh: float,
        sh: float,
        shape: Union[Any, str],
        name: str = "",
    ):
        """
        Initialize cooling slit

        Args:
            r: Radial position of slits
            angle: Angular shift from reference (degrees)
            n: Number of slits
            dh: Hydraulic diameter
            sh: Cross-sectional area of single slit
            shape: 2D shape (Shape2D object or filename)
            name: Optional slit name
        """
        super().__init__(name)
        self.r = r
        self.angle = angle
        self.n = n
        self.dh = dh
        self.sh = sh
        self._shape_data = shape

        # Call validation after setting all attributes
        self.validate()

    def validate(self) -> None:
        """Validate cooling slit parameters"""
        super().validate()

        validate_positive(self.r, "r")
        validate_angle(self.angle, 0, 360, "angle")

        if self.n <= 0:
            raise ValueError(f"Number of slits must be positive, got {self.n}")

        validate_positive(self.dh, "dh")
        validate_positive(self.sh, "sh")

    @property
    def shape(self):
        """
        Get shape object (lazy loading)

        Returns:
            Shape2D object defining slit cross-section
        """
        if hasattr(self, "_shape_object"):
            return self._shape_object

        if isinstance(self._shape_data, str):
            # Load from file
            try:
                from ...utils.geometry.shape2d import Shape2D

                self._shape_object = load_file(f"{self._shape_data}.yaml", Shape2D)
            except ImportError:
                # Fallback if Shape2D not available
                import yaml

                with open(f"{self._shape_data}.yaml", "r") as f:
                    self._shape_object = yaml.load(f, Loader=yaml.FullLoader)
        else:
            self._shape_object = self._shape_data

        return self._shape_object

    def get_total_area(self) -> float:
        """
        Calculate total cross-sectional area of all slits

        Returns:
            Total area = n * sh
        """
        return self.n * self.sh

    def get_wetted_perimeter(self) -> float:
        """
        Calculate wetted perimeter for a single slit

        Returns:
            Wetted perimeter = 4 * sh / dh
        """
        return 4 * self.sh / self.dh

    def get_total_wetted_perimeter(self) -> float:
        """
        Calculate total wetted perimeter for all slits

        Returns:
            Total wetted perimeter = n * (4 * sh / dh)
        """
        return self.n * self.get_wetted_perimeter()

    def get_equivalent_annular_thickness(self, radius: float = None) -> float:
        """
        Calculate equivalent annular ring thickness

        This represents the thickness of an annular ring that would have
        the same cross-sectional area as all the slits combined.

        Args:
            radius: Reference radius (uses self.r if not provided)

        Returns:
            Equivalent thickness: eps = n * sh / (2 * pi * r)
        """
        import math

        ref_radius = radius or self.r
        return self.n * self.sh / (2 * math.pi * ref_radius)

    def get_flow_properties(self) -> Dict[str, float]:
        """
        Get flow-related properties

        Returns:
            Dictionary with flow properties
        """
        return {
            "total_area": self.get_total_area(),
            "hydraulic_diameter": self.dh,
            "wetted_perimeter_single": self.get_wetted_perimeter(),
            "total_wetted_perimeter": self.get_total_wetted_perimeter(),
            "equivalent_thickness": self.get_equivalent_annular_thickness(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> "CoolingSlit":
        """
        Create CoolingSlit from dictionary

        Args:
            data: Dictionary with slit parameters
            debug: Whether to print debug info

        Returns:
            CoolingSlit instance
        """
        if debug:
            print(f"Creating CoolingSlit from: {data}")

        name = data.get("name", "")
        r = data["r"]
        angle = data["angle"]
        n = data["n"]
        dh = data["dh"]
        sh = data["sh"]
        shape = data["shape"]

        return cls(r=r, angle=angle, n=n, dh=dh, sh=sh, shape=shape, name=name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        # Handle shape serialization
        shape_data = self._shape_data
        if hasattr(self._shape_data, "to_dict"):
            shape_data = self._shape_data.to_dict()
        elif hasattr(self._shape_data, "name"):
            shape_data = self._shape_data.name  # Use name reference

        return {
            "name": self.name,
            "r": self.r,
            "angle": self.angle,
            "n": self.n,
            "dh": self.dh,
            "sh": self.sh,
            "shape": shape_data,
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}(r={self.r}, angle={self.angle}, "
            f"n={self.n}, dh={self.dh}, sh={self.sh})"
        )


def CoolingSlit_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    return CoolingSlit.from_dict(values)


# Register YAML constructor

yaml.add_constructor("!Slit", CoolingSlit_constructor)

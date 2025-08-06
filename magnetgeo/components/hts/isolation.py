#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS Isolation geometric definition

Defines the geometric structure of isolation layers between HTS components
including multi-layer insulation configurations.
"""

from typing import Dict, Any, List
import warnings

try:
    from ...base.support_base import SupportComponentBase
    from ...utils.validation import validate_non_negative

    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    SupportComponentBase = object

    def validate_non_negative(val, name):
        pass


class Isolation(SupportComponentBase if BASE_AVAILABLE else object):
    """
    HTS isolation layer geometric definition

    Represents the geometric structure of insulation layers between
    superconducting components, supporting multi-layer configurations.

    Attributes:
        r0: Inner radius of isolation structure (mm)
        w: Widths of different isolation layers (mm)
        h: Heights of different isolation layers (mm)
    """

    yaml_tag = "!Isolation"

    def __init__(self, r0: float = 0, w: List[float] = None, h: List[float] = None):
        """
        Initialize isolation geometry

        Args:
            r0: Inner radius of isolation structure
            w: Widths of isolation layers (list for multi-layer)
            h: Heights of isolation layers (list for multi-layer)
        """
        if BASE_AVAILABLE:
            super().__init__()

        self.r0 = float(r0)
        self.w = w if w is not None else []
        self.h = h if h is not None else []

        self.validate()

    def validate(self) -> None:
        """Validate isolation geometric parameters"""
        if BASE_AVAILABLE:
            super().validate()

        validate_non_negative(self.r0, "r0 (inner radius)")

        for i, width in enumerate(self.w):
            validate_non_negative(width, f"w[{i}] (layer width)")

        for i, height in enumerate(self.h):
            validate_non_negative(height, f"h[{i}] (layer height)")

        # Warn if layer counts don't match
        if len(self.w) != len(self.h) and self.w and self.h:
            warnings.warn(
                f"Width and height lists have different lengths: "
                f"{len(self.w)} widths, {len(self.h)} heights"
            )

    def getR0(self) -> float:
        """Get inner radius of isolation structure"""
        return self.r0

    def getW(self) -> float:
        """Get maximum isolation width"""
        return max(self.w) if self.w else 0.0

    def getR1(self) -> float:
        """Get outer radius of isolation structure"""
        return self.r0 + self.getW()

    def getH_Layer(self, i: int) -> float:
        """
        Get height of specific isolation layer

        Args:
            i: Layer index

        Returns:
            Height of layer i, or 0 if index out of range
        """
        if 0 <= i < len(self.h):
            return self.h[i]
        return 0.0

    def getW_Layer(self, i: int) -> float:
        """
        Get width of specific isolation layer

        Args:
            i: Layer index

        Returns:
            Width of layer i, or 0 if index out of range
        """
        if 0 <= i < len(self.w):
            return self.w[i]
        return 0.0

    def getH(self) -> float:
        """Get total isolation height (sum of all layers)"""
        return sum(self.h)

    def getLayer(self) -> int:
        """Get number of isolation layers"""
        return len(self.w)

    def getArea(self) -> float:
        """Get isolation cross-sectional area in r-z plane"""
        return self.getW() * self.getH()

    def getVolume_cylindrical(self) -> float:
        """
        Get cylindrical volume of isolation

        Returns:
            Volume assuming cylindrical geometry
        """
        import math

        if not self.w or not self.h:
            return 0.0

        r_outer = self.getR1()
        r_inner = self.r0
        height = self.getH()

        return math.pi * (r_outer**2 - r_inner**2) * height

    def get_layer_radii(self) -> List[tuple]:
        """
        Get radial bounds for each isolation layer

        Returns:
            List of (r_inner, r_outer) tuples for each layer
        """
        if not self.w:
            return []

        layers = []
        r_current = self.r0

        for width in self.w:
            r_next = r_current + width
            layers.append((r_current, r_next))
            r_current = r_next

        return layers

    def get_names(self, name: str, detail: str, verbose: bool = False) -> List[str]:
        """
        Get component names for meshing/CAD

        Args:
            name: Base name for components
            detail: Detail level ("isolation" or "layer")
            verbose: Whether to print verbose info

        Returns:
            List of component names
        """
        if detail == "layer" and len(self.w) > 1:
            # Individual layers
            names = []
            for i in range(len(self.w)):
                names.append(f"{name}_Layer{i}")
        else:
            # Single isolation name
            names = [name]

        if verbose:
            print(f"Isolation '{name}' components ({detail}): {names}")

        return names

    def get_bounds(self) -> tuple:
        """
        Get geometric bounds as (r_bounds, z_bounds)

        Returns:
            Tuple of ([r_min, r_max], [z_min, z_max])
        """
        r_min = self.r0
        r_max = self.getR1()

        half_height = self.getH() / 2.0
        z_min = -half_height
        z_max = half_height

        return ([r_min, r_max], [z_min, z_max])

    def is_empty(self) -> bool:
        """Check if isolation is effectively empty"""
        return (
            not self.w
            or all(w == 0 for w in self.w)
            or not self.h
            or all(h == 0 for h in self.h)
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> "Isolation":
        """
        Create Isolation from dictionary

        Args:
            data: Dictionary with isolation parameters
            debug: Whether to print debug info

        Returns:
            Isolation instance
        """
        if debug:
            print(f"Creating Isolation from: {data}")

        r0 = data.get("r0", 0)
        w = data.get("w", [])
        h = data.get("h", [])

        # Handle single values as lists
        if not isinstance(w, list):
            w = [w] if w else []
        if not isinstance(h, list):
            h = [h] if h else []

        return cls(r0, w, h)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {"r0": self.r0, "w": self.w, "h": self.h}

    def __repr__(self) -> str:
        """String representation"""
        return f"Isolation(r0={self.r0}, w={self.w}, h={self.h})"

    def __str__(self) -> str:
        """Detailed string representation"""
        msg = "HTS Isolation Geometry:\n"
        msg += f"  Inner radius: {self.r0:.3f} mm\n"
        msg += f"  Outer radius: {self.getR1():.3f} mm\n"
        msg += f"  Total width: {self.getW():.3f} mm\n"
        msg += f"  Total height: {self.getH():.3f} mm\n"
        msg += f"  Number of layers: {self.getLayer()}\n"

        if len(self.w) > 1:
            msg += "  Layer details:\n"
            for i, (width, height) in enumerate(zip(self.w, self.h[: len(self.w)])):
                msg += f"    Layer {i}: width={width:.3f} mm, height={height:.3f} mm\n"

        return msg


def create_uniform_isolation(r0: float, width: float, height: float) -> Isolation:
    """
    Create single-layer uniform isolation

    Args:
        r0: Inner radius
        width: Isolation width
        height: Isolation height

    Returns:
        Isolation instance
    """
    validate_non_negative(r0, "r0")
    validate_non_negative(width, "width")
    validate_non_negative(height, "height")

    return Isolation(r0, [width], [height])


def create_multilayer_isolation(r0: float, layer_specs: List[tuple]) -> Isolation:
    """
    Create multi-layer isolation from specifications

    Args:
        r0: Inner radius
        layer_specs: List of (width, height) tuples for each layer

    Returns:
        Isolation instance
    """
    validate_non_negative(r0, "r0")

    if not layer_specs:
        return Isolation(r0, [], [])

    widths = []
    heights = []

    for i, spec in enumerate(layer_specs):
        if len(spec) != 2:
            raise ValueError(f"Layer spec {i} must be (width, height) tuple")

        width, height = spec
        validate_non_negative(width, f"layer {i} width")
        validate_non_negative(height, f"layer {i} height")

        widths.append(width)
        heights.append(height)

    return Isolation(r0, widths, heights)


def create_vacuum_isolation(r0: float, gap: float, height: float) -> Isolation:
    """
    Create vacuum isolation (thin gap)

    Args:
        r0: Inner radius
        gap: Vacuum gap width
        height: Gap height

    Returns:
        Isolation instance representing vacuum space
    """
    return create_uniform_isolation(r0, gap, height)


def create_kapton_isolation(
    r0: float, thickness: float, height: float, n_layers: int = 1
) -> Isolation:
    """
    Create Kapton film isolation (typical for HTS applications)

    Args:
        r0: Inner radius
        thickness: Kapton thickness per layer
        height: Total height
        n_layers: Number of Kapton layers

    Returns:
        Isolation instance
    """
    validate_non_negative(thickness, "thickness")

    if n_layers <= 0:
        raise ValueError("Number of layers must be positive")

    if n_layers == 1:
        return create_uniform_isolation(r0, thickness, height)
    else:
        # Multiple identical layers
        layer_specs = [(thickness, height)] * n_layers
        return create_multilayer_isolation(r0, layer_specs)


def create_graded_isolation(
    r0: float,
    thickness_start: float,
    thickness_end: float,
    height: float,
    n_layers: int = 3,
) -> Isolation:
    """
    Create graded isolation with varying layer thickness

    Args:
        r0: Inner radius
        thickness_start: Starting layer thickness
        thickness_end: Final layer thickness
        height: Total height
        n_layers: Number of graded layers

    Returns:
        Isolation instance with graded thickness
    """
    validate_non_negative(thickness_start, "thickness_start")
    validate_non_negative(thickness_end, "thickness_end")

    if n_layers <= 0:
        raise ValueError("Number of layers must be positive")

    if n_layers == 1:
        # Single layer - use average thickness
        avg_thickness = (thickness_start + thickness_end) / 2
        return create_uniform_isolation(r0, avg_thickness, height)

    # Create graded layers
    layer_specs = []
    for i in range(n_layers):
        # Linear interpolation
        factor = i / (n_layers - 1)
        thickness = thickness_start + factor * (thickness_end - thickness_start)
        layer_specs.append((thickness, height))

    return create_multilayer_isolation(r0, layer_specs)


# Isolation factory registry
ISOLATION_FACTORIES = {
    "uniform": create_uniform_isolation,
    "multilayer": create_multilayer_isolation,
    "vacuum": create_vacuum_isolation,
    "kapton": create_kapton_isolation,
    "graded": create_graded_isolation,
}


def create_isolation_from_spec(isolation_type: str, **kwargs) -> Isolation:
    """
    Create isolation from specification type

    Args:
        isolation_type: Type of isolation
        **kwargs: Parameters for specific isolation type

    Returns:
        Isolation instance
    """
    if isolation_type not in ISOLATION_FACTORIES:
        raise ValueError(
            f"Unknown isolation type '{isolation_type}'. "
            f"Available types: {list(ISOLATION_FACTORIES.keys())}"
        )

    factory = ISOLATION_FACTORIES[isolation_type]
    return factory(**kwargs)

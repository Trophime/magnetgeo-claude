#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides OuterCurrentLead class for structural components
"""

import json
import yaml
from typing import List

try:
    from ...base.structural_base import StructuralComponentBase
    BASE_CLASS_AVAILABLE = True
except ImportError:
    # Fallback for systems without the new base classes
    StructuralComponentBase = object
    BASE_CLASS_AVAILABLE = False


class OuterCurrentLead(StructuralComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Outer Current Lead structural component
    
    Attributes:
        name: Lead identifier
        r: Radial bounds [R0, R1]
        h: Height
        bar: Bar configuration [R, DX, DY, L]
        support: Support configuration [DX0, DZ, Angle, Angle_Zero]
    """

    yaml_tag = "OuterCurrentLead"

    def __init__(
        self, 
        name: str = "None", 
        r: List[float] = None, 
        h: float = 0.0, 
        bar: List = None, 
        support: List = None
    ):
        """
        Initialize OuterCurrentLead object
        
        Args:
            name: Lead identifier
            r: Radial bounds [R0, R1]
            h: Height
            bar: Bar configuration [R, DX, DY, L]
            support: Support configuration [DX0, DZ, Angle, Angle_Zero]
        """
        if BASE_CLASS_AVAILABLE:
            # Use the new base class validation
            super().__init__(name, r or [], h=h, bar=bar or [], support=support or [])
        else:
            # Legacy validation
            self.name = name
            self.r = r or []
            
        self.h = h
        self.bar = bar or []
        self.support = support or []

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[str]:
        """
        Get channels for this component
        
        Args:
            mname: Base name for channels
            hideIsolant: Whether to hide isolant channels
            debug: Whether to print debug info
            
        Returns:
            Empty list (current leads don't typically have channels)
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """
        Get isolants for this component
        
        Args:
            mname: Base name
            debug: Whether to print debug info
            
        Returns:
            Empty list (current leads don't typically have isolants)
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> List[str]:
        """
        Get names for markers/regions
        
        Args:
            mname: Base name prefix
            is2D: Whether generating 2D names
            verbose: Whether to print verbose info
            
        Returns:
            List of region names
        """
        solid_names = []

        prefix = f"{mname}_" if mname else ""
        solid_names.append(f"{prefix}{self.name}_OuterCurrentLead")
        
        if verbose:
            print(f"OuterCurrentLead/get_names: solid_names {len(solid_names)}")
            
        return solid_names

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, "
            f"h={self.h!r}, bar={self.bar!r}, support={self.support!r})"
        )

    def dump(self):
        """Dump object to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to dump OuterCurrentLead data")

    def load(self):
        """Load object from YAML file"""
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load OuterCurrentLead data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.h = data.h
        self.bar = data.bar
        self.support = data.support

    def to_json(self) -> str:
        """Convert to JSON string"""
        try:
            # Try to use existing deserialize module for compatibility
            from ...deserialize import serialize_instance
            return json.dumps(
                self, default=serialize_instance, sort_keys=True, indent=4
            )
        except ImportError:
            # Fallback to basic JSON serialization
            data = {
                "__classname__": self.__class__.__name__,
                "name": self.name,
                "r": self.r,
                "h": self.h,
                "bar": self.bar,
                "support": self.support
            }
            return json.dumps(data, sort_keys=True, indent=4)

    def write_to_json(self):
        """Write to JSON file"""
        jsondata = self.to_json()
        try:
            with open(f"{self.name}.json", "w") as ofile:
                ofile.write(str(jsondata))
        except Exception:
            raise Exception(f"Failed to write to {self.name}.json")

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Create OuterCurrentLead from JSON file"""
        try:
            from ...deserialize import unserialize_object
            
            if debug:
                print(f"OuterCurrentLead.from_json: filename={filename}")
                
            with open(filename, "r") as istream:
                return json.loads(
                    istream.read(), object_hook=unserialize_object
                )
        except ImportError:
            # Fallback JSON loading
            if debug:
                print(f"OuterCurrentLead.from_json: filename={filename} (fallback mode)")
                
            with open(filename, "r") as istream:
                data = json.load(istream)
                
            return cls(
                name=data.get("name", "None"),
                r=data.get("r", []),
                h=data.get("h", 0.0),
                bar=data.get("bar", []),
                support=data.get("support", [])
            )

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create OuterCurrentLead from dictionary"""
        return cls(
            name=data.get("name", "None"),
            r=data.get("r", []),
            h=data.get("h", 0.0),
            bar=data.get("bar", []),
            support=data.get("support", [])
        )

    def validate(self) -> None:
        """Validate outer current lead parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        else:
            # Basic validation for legacy mode
            if not isinstance(self.name, str):
                raise TypeError("OuterCurrentLead name must be a string")
            if not isinstance(self.r, list):
                raise ValueError("r must be a list")
            
        # Additional validation
        if not isinstance(self.h, (int, float)) or self.h < 0:
            raise ValueError("h must be a non-negative number")
        
        if not isinstance(self.bar, list):
            raise ValueError("bar must be a list")
            
        if not isinstance(self.support, list):
            raise ValueError("support must be a list")


def OuterCurrentLead_constructor(loader, node):
    """YAML constructor for OuterCurrentLead"""
    values = loader.construct_mapping(node)
    name = values.get("name", "None")
    r = values.get("r", [])
    h = values.get("h", 0.0)
    bar = values.get("bar", [])
    support = values.get("support", [])
    
    return OuterCurrentLead(name, r, h, bar, support)


# Register YAML constructor
yaml.add_constructor("!OuterCurrentLead", OuterCurrentLead_constructor)
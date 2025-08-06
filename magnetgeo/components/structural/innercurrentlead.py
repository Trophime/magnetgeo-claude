#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides InnerCurrentLead class for structural components
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


class InnerCurrentLead(StructuralComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Inner Current Lead structural component
    
    Attributes:
        name: Lead identifier
        r: Radial bounds [R0, R1]
        h: Height
        holes: Hole configuration [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
        support: Support configuration [R2, DZ]
        fillet: Whether to use fillets
    """

    yaml_tag = "InnerCurrentLead"

    def __init__(
        self,
        name: str,
        r: List[float],
        h: float = 0.0,
        holes: List = None,
        support: List = None,
        fillet: bool = False,
    ) -> None:
        """
        Initialize InnerCurrentLead object
        
        Args:
            name: Lead identifier
            r: Radial bounds [R0, R1]
            h: Height
            holes: Hole configuration
            support: Support configuration
            fillet: Whether to use fillets
        """
        if BASE_CLASS_AVAILABLE:
            # Use the new base class validation
            super().__init__(name, r, h=h, holes=holes or [], support=support or [], fillet=fillet)
        else:
            # Legacy validation
            self.name = name
            self.r = r
            
        self.h = h
        self.holes = holes or []
        self.support = support or []
        self.fillet = fillet

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
        solid_names.append(f"{prefix}{self.name}_InnerCurrentLead")
        
        if verbose:
            print(f"InnerCurrentLead/get_names: solid_names {len(solid_names)}")
            
        return solid_names

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, "
            f"h={self.h!r}, holes={self.holes!r}, support={self.support!r}, "
            f"fillet={self.fillet!r})"
        )

    def dump(self):
        """Dump object to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to dump InnerCurrentLead data")

    def load(self):
        """Load object from YAML file"""
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load InnerCurrentLead data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.h = data.h
        self.holes = data.holes
        self.support = data.support
        self.fillet = data.fillet

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
                "holes": self.holes,
                "support": self.support,
                "fillet": self.fillet
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
        """Create InnerCurrentLead from JSON file"""
        try:
            from ...deserialize import unserialize_object
            
            if debug:
                print(f"InnerCurrentLead.from_json: filename={filename}")
                
            with open(filename, "r") as istream:
                return json.loads(
                    istream.read(), object_hook=unserialize_object
                )
        except ImportError:
            # Fallback JSON loading
            if debug:
                print(f"InnerCurrentLead.from_json: filename={filename} (fallback mode)")
                
            with open(filename, "r") as istream:
                data = json.load(istream)
                
            return cls(
                name=data["name"],
                r=data["r"],
                h=data.get("h", 0.0),
                holes=data.get("holes", []),
                support=data.get("support", []),
                fillet=data.get("fillet", False)
            )

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create InnerCurrentLead from dictionary"""
        return cls(
            name=data["name"],
            r=data["r"],
            h=data.get("h", 0.0),
            holes=data.get("holes", []),
            support=data.get("support", []),
            fillet=data.get("fillet", False)
        )

    def validate(self) -> None:
        """Validate inner current lead parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        else:
            # Basic validation for legacy mode
            if not isinstance(self.name, str):
                raise TypeError("InnerCurrentLead name must be a string")
            if not isinstance(self.r, list) or len(self.r) != 2:
                raise ValueError("r must be a list of [r_min, r_max]")
            
        # Additional validation
        if not isinstance(self.h, (int, float)) or self.h < 0:
            raise ValueError("h must be a non-negative number")
        
        if not isinstance(self.holes, list):
            raise ValueError("holes must be a list")
            
        if not isinstance(self.support, list):
            raise ValueError("support must be a list")
            
        if not isinstance(self.fillet, bool):
            raise ValueError("fillet must be a boolean")


def InnerCurrentLead_constructor(loader, node):
    """YAML constructor for InnerCurrentLead"""
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    h = values.get("h", 0.0)
    holes = values.get("holes", [])
    support = values.get("support", [])
    fillet = values.get("fillet", False)
    
    return InnerCurrentLead(name, r, h, holes, support, fillet)


# Register YAML constructor
yaml.add_constructor("!InnerCurrentLead", InnerCurrentLead_constructor)

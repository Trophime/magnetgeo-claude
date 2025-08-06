#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides Screen class for structural components
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


class Screen(StructuralComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Screen structural component
    
    Attributes:
        name: Screen identifier
        r: Radial bounds [r_min, r_max]
        z: Axial bounds [z_min, z_max]
    """

    yaml_tag = "Screen"

    def __init__(self, name: str, r: List[float], z: List[float]):
        """
        Initialize Screen object
        
        Args:
            name: Screen identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
        """
        if BASE_CLASS_AVAILABLE:
            # Use the new base class validation
            super().__init__(name, r, z=z)
        else:
            # Legacy validation
            self.name = name
            self.r = r
            self.z = z

    def get_lc(self) -> float:
        """Get characteristic length"""
        return (self.r[1] - self.r[0]) / 10.0

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
            Empty list (screens don't have channels)
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """
        Get isolants for this component
        
        Args:
            mname: Base name
            debug: Whether to print debug info
            
        Returns:
            Empty list (screens don't have isolants)
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
        solid_names.append(f"{prefix}{self.name}_Screen")
        
        if verbose:
            print(f"Screen/get_names: solid_names {len(solid_names)}")
            
        return solid_names

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, z={self.z!r})"
        )

    def dump(self):
        """Dump object to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to Screen dump")

    def load(self):
        """Load object from YAML file"""
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Screen data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z

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
                "z": self.z
            }
            return json.dumps(data, sort_keys=True, indent=4)

    def write_to_json(self):
        """Write to JSON file"""
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Create Screen from JSON file"""
        try:
            from ...deserialize import unserialize_object
            
            if debug:
                print(f"Screen.from_json: filename={filename}")
                
            with open(filename, "r") as istream:
                return json.loads(
                    istream.read(), object_hook=unserialize_object
                )
        except ImportError:
            # Fallback JSON loading
            if debug:
                print(f"Screen.from_json: filename={filename} (fallback mode)")
                
            with open(filename, "r") as istream:
                data = json.load(istream)
                
            return cls(
                name=data["name"],
                r=data["r"],
                z=data["z"]
            )

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create Screen from dictionary"""
        return cls(
            name=data["name"],
            r=data["r"],
            z=data["z"]
        )

    def validate(self) -> None:
        """Validate screen parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        else:
            # Basic validation for legacy mode
            if not isinstance(self.name, str):
                raise TypeError("Screen name must be a string")
            if not isinstance(self.r, list) or len(self.r) != 2:
                raise ValueError("r must be a list of [r_min, r_max]")
            if not isinstance(self.z, list) or len(self.z) != 2:
                raise ValueError("z must be a list of [z_min, z_max]")


def Screen_constructor(loader, node):
    """YAML constructor for Screen"""
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    
    return Screen(name, r, z)


# Register YAML constructor
yaml.add_constructor("!Screen", Screen_constructor)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides Ring class for structural components
"""

import json
import yaml
from typing import List, Optional

try:
    from ...base.structural_base import StructuralComponentBase
    BASE_CLASS_AVAILABLE = True
except ImportError:
    # Fallback for systems without the new base classes
    StructuralComponentBase = object
    BASE_CLASS_AVAILABLE = False


class Ring(StructuralComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Ring structural component
    
    Attributes:
        name: Ring identifier
        r: Radial bounds [r_min, r_max]
        z: Axial bounds [z_min, z_max]  
        n: Number of rings (optional)
        angle: Angular position (optional)
        BPside: Boolean for BP side (optional)
        fillets: Boolean for fillets (optional)
        cad: CAD identifier (optional)
    """

    yaml_tag = "Ring"

    def __setstate__(self, state):
        """
        This method is called during deserialization (when loading from YAML or pickle)
        We use it to ensure the optional attributes always exist
        """
        self.__dict__.update(state)
        
        # Ensure these attributes always exist
        if not hasattr(self, 'cad'):
            self.cad = ''

    def __init__(
        self,
        name: str,
        r: List[float],
        z: List[float],
        n: int = 0,
        angle: float = 0,
        BPside: bool = True,
        fillets: bool = False,
        cad: Optional[str] = None
    ) -> None:
        """
        Initialize Ring object
        
        Args:
            name: Ring identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
            n: Number of rings
            angle: Angular position
            BPside: Boolean for BP side
            fillets: Boolean for fillets
            cad: CAD identifier
        """
        if BASE_CLASS_AVAILABLE:
            # Use the new base class validation
            super().__init__(name, r, z=z, n=n, angle=angle, BPside=BPside, fillets=fillets, cad=cad)
        else:
            # Legacy validation
            self.name = name
            self.r = r
            self.z = z
            
        self.n = n
        self.angle = angle
        self.BPside = BPside
        self.fillets = fillets
        self.cad = cad if cad is not None else ''

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
            Empty list (rings don't have channels)
        """
        return []

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """
        Get isolants for this component
        
        Args:
            mname: Base name
            debug: Whether to print debug info
            
        Returns:
            Empty list (rings don't have isolants)
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
        solid_names.append(f"{prefix}{self.name}_Ring")
        
        if verbose:
            print(f"Ring/get_names: solid_names {len(solid_names)}")
        
        return solid_names

    def __repr__(self) -> str:
        """String representation"""
        msg = (
            f"{self.__class__.__name__}(name={self.name!r}, r={self.r!r}, "
            f"z={self.z!r}, n={self.n!r}, angle={self.angle!r}, "
            f"BPside={self.BPside!r}, fillets={self.fillets!r}"
        )
        
        if hasattr(self, 'cad'):
            msg += f", cad={self.cad!r}"
        else:
            msg += ", cad=None"
            
        return msg + ")"

    def dump(self):
        """Dump object to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception("Failed to dump Ring data")

    def load(self):
        """Load object from YAML file"""
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Ring data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.angle = data.angle
        self.BPside = data.BPside
        self.fillets = data.fillets
        self.cad = getattr(data, 'cad', '')

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
                "z": self.z,
                "n": self.n,
                "angle": self.angle,
                "BPside": self.BPside,
                "fillets": self.fillets,
                "cad": self.cad
            }
            return json.dumps(data, sort_keys=True, indent=4)

    def write_to_json(self):
        """Write to JSON file"""
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Create Ring from JSON file"""
        try:
            from ...deserialize import unserialize_object
            
            if debug:
                print(f"Ring.from_json: filename={filename}")
                
            with open(filename, "r") as istream:
                return json.loads(
                    istream.read(), object_hook=unserialize_object
                )
        except ImportError:
            # Fallback JSON loading
            if debug:
                print(f"Ring.from_json: filename={filename} (fallback mode)")
                
            with open(filename, "r") as istream:
                data = json.load(istream)
                
            return cls(
                name=data["name"],
                r=data["r"],
                z=data["z"],
                n=data.get("n", 0),
                angle=data.get("angle", 0),
                BPside=data.get("BPside", True),
                fillets=data.get("fillets", False),
                cad=data.get("cad", "")
            )

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create Ring from dictionary"""
        return cls(
            name=data["name"],
            r=data["r"],
            z=data["z"],
            n=data.get("n", 0),
            angle=data.get("angle", 0),
            BPside=data.get("BPside", True),
            fillets=data.get("fillets", False),
            cad=data.get("cad", "")
        )

    def validate(self) -> None:
        """Validate ring parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        else:
            # Basic validation for legacy mode
            if not isinstance(self.name, str):
                raise TypeError("Ring name must be a string")
            if not isinstance(self.r, list) or len(self.r) != 2:
                raise ValueError("r must be a list of [r_min, r_max]")
            if not isinstance(self.z, list) or len(self.z) != 2:
                raise ValueError("z must be a list of [z_min, z_max]")


def Ring_constructor(loader, node):
    """YAML constructor for Ring"""
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values.get("n", 0)
    angle = values.get("angle", 0)
    BPside = values.get("BPside", True)
    fillets = values.get("fillets", False)
    cad = values.get("cad", '')
    
    ring = Ring(name, r, z, n, angle, BPside, fillets, cad)
    if not hasattr(ring, 'cad'):
        ring.cad = ''
    return ring


# Register YAML constructor
yaml.add_constructor("!Ring", Ring_constructor)

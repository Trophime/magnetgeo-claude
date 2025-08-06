#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Supra magnet component - moved to magnetgeo.components.magnet

This is the enhanced Supra class with lazy loading, validation, and
detailed superconducting magnet structure support.
"""

import json
import yaml
from functools import cached_property
from typing import List, Optional, Any

# Import base classes
try:
    from ...base.component_base import MagnetComponentBase

    BASE_CLASS_AVAILABLE = True
except ImportError:
    # Fallback for transition period
    BASE_CLASS_AVAILABLE = False
    MagnetComponentBase = object

# Try to import superconducting structure support
try:
    from ...SupraStructure import HTSinsert

    SUPRA_STRUCTURE_AVAILABLE = True
except ImportError:
    SUPRA_STRUCTURE_AVAILABLE = False
    print("Warning: SupraStructure not available")

# Try to import validation utilities
try:
    from ...utils.validation import validate_dimensions, validate_string_not_empty

    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


class Supra(MagnetComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Superconducting magnet component with enhanced validation and lazy loading

    Supra magnets are superconducting magnets that can operate with detailed
    structural models including double pancakes, pancakes, and individual tapes.

    This version provides comprehensive superconducting structure analysis
    and lazy loading while maintaining backward compatibility.
    """

    yaml_tag = "Supra"

    def __init__(
        self, name: str, r: List[float], z: List[float], n: int = 0, struct: str = ""
    ):
        """
        Initialize superconducting magnet with validation and lazy loading

        Args:
            name: Supra magnet identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
            n: Number of turns (if not using detailed structure)
            struct: Path to detailed structure definition file
        """
        # Validate basic parameters if validation is available
        if VALIDATION_AVAILABLE:
            validate_dimensions(r, z)
            validate_string_not_empty(name, "name")
            if n < 0:
                raise ValueError("Number of turns must be non-negative")

        # Initialize base class if available
        if BASE_CLASS_AVAILABLE:
            super().__init__(name=name, r=r, z=z, odd=False, modelaxi=None)
            self.n = n
            self.struct = struct
        else:
            # Fallback initialization
            self.name = name
            self.r = r.copy()
            self.z = z.copy()
            self.n = n
            self.struct = struct

        # Detail level for geometry representation
        self.detail = "None"  # ['None', 'dblpancake', 'pancake', 'tape']

        # Store structure data for lazy loading
        self._struct_data = struct

        # Clear any cached properties to ensure fresh loading
        self._clear_cached_properties()

    def _clear_cached_properties(self):
        """Clear cached properties to force reload"""
        cached_attrs = ["magnet_struct"]
        for attr in cached_attrs:
            if hasattr(self, f"_{attr}"):
                delattr(self, f"_{attr}")

    @cached_property
    def magnet_struct(self) -> Optional[Any]:
        """Load detailed magnet structure on first access"""
        if not SUPRA_STRUCTURE_AVAILABLE or not self.struct:
            return None

        try:
            return HTSinsert.fromcfg(self.struct)
        except Exception as e:
            print(f"Warning: Could not load structure from '{self.struct}': {e}")
            return None

    def get_magnet_struct(self, directory: Optional[str] = None) -> Optional[Any]:
        """
        Get magnet structure (public interface)

        Args:
            directory: Optional directory path for structure file

        Returns:
            HTSinsert object or None
        """
        if not SUPRA_STRUCTURE_AVAILABLE or not self.struct:
            return None

        try:
            return HTSinsert.fromcfg(self.struct, directory)
        except Exception as e:
            print(f"Warning: Could not load structure: {e}")
            return None

    def check_dimensions(self, magnet: Any = None):
        """
        Check and update dimensions from structure if available

        Args:
            magnet: Optional HTSinsert object (uses cached if not provided)
        """
        if magnet is None:
            magnet = self.magnet_struct

        if not magnet or not self.struct:
            return

        changed = False

        # Update radial bounds
        struct_r0 = magnet.getR0() if hasattr(magnet, "getR0") else None
        struct_r1 = magnet.getR1() if hasattr(magnet, "getR1") else None

        if struct_r0 is not None and self.r[0] != struct_r0:
            changed = True
            self.r[0] = struct_r0

        if struct_r1 is not None and self.r[1] != struct_r1:
            changed = True
            self.r[1] = struct_r1

        # Update axial bounds
        if hasattr(magnet, "getZ0") and hasattr(magnet, "getH"):
            struct_z0 = magnet.getZ0() - magnet.getH() / 2.0
            struct_z1 = magnet.getZ0() + magnet.getH() / 2.0

            if self.z[0] != struct_z0:
                changed = True
                self.z[0] = struct_z0

            if self.z[1] != struct_z1:
                changed = True
                self.z[1] = struct_z1

        # Update turn count
        if hasattr(magnet, "getNtapes"):
            struct_n = sum(magnet.getNtapes())
            if self.n != struct_n:
                changed = True
                self.n = struct_n

        if changed:
            print(
                f"Supra/check_dimensions: Updated dimensions for {self.name} from {self.struct}"
            )
            print(self)

    # Core supra magnet methods
    def get_component_type(self) -> str:
        """Get component type identifier"""
        return "Supra"

    def get_insulator_info(self) -> tuple:
        """
        Get insulator information for this superconducting magnet

        Returns:
            Tuple of (insulator_name, count)
        """
        if self.detail == "None":
            return ("Insulation", 1)

        # For detailed models, insulation is part of the structure
        magnet = self.magnet_struct
        if magnet and hasattr(magnet, "get_names"):
            # Count insulation components from structure
            names = magnet.get_names("", self.detail)
            insulation_count = sum(
                1
                for name in names
                if "insul" in name.lower() or "mandrin" in name.lower()
            )
            return ("StructuralInsulation", max(1, insulation_count))

        return ("Insulation", 1)

    def get_lc(self):
        """Get characteristic length for meshing"""
        if self.detail == "None":
            return (self.r[1] - self.r[0]) / 5.0
        else:
            magnet = self.magnet_struct
            if magnet and hasattr(magnet, "get_lc"):
                return magnet.get_lc()
            return (self.r[1] - self.r[0]) / 10.0

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[str]:
        """Get channel names for analysis (empty for superconducting magnets)"""
        return []

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """Get isolant region names (empty for superconducting magnets)"""
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> List[str]:
        """
        Get names for markers/regions

        Args:
            mname: Base name prefix
            is2D: Whether generating 2D or 3D names
            verbose: Whether to print verbose information

        Returns:
            List of region/marker names
        """
        if self.detail == "None":
            prefix = f"{mname}_" if mname else ""
            return [f"{prefix}{self.name}"]
        else:
            magnet = self.magnet_struct
            if magnet:
                self.check_dimensions(magnet)
                if hasattr(magnet, "get_names"):
                    return magnet.get_names(
                        mname=mname, detail=self.detail, verbose=verbose
                    )

            # Fallback
            prefix = f"{mname}_" if mname else ""
            return [f"{prefix}{self.name}"]

    def get_Nturns(self) -> int:
        """Get total number of turns"""
        if not self.struct:
            return self.n
        else:
            magnet = self.magnet_struct
            if magnet and hasattr(magnet, "getNtapes"):
                return sum(magnet.getNtapes())
            return self.n

    def set_Detail(self, detail: str) -> None:
        """
        Set detail level for geometry representation

        Args:
            detail: Detail level ("None", "dblpancake", "pancake", "tape")
        """
        if VALIDATION_AVAILABLE:
            try:
                from ...utils.enums import DetailLevel

                valid_details = [e.value for e in DetailLevel]
                if detail not in valid_details:
                    raise ValueError(
                        f"detail must be one of {valid_details}, got '{detail}'"
                    )
            except ImportError:
                pass

        valid_details = ["None", "dblpancake", "pancake", "tape"]
        if detail not in valid_details:
            raise ValueError(f"detail must be one of {valid_details}, got '{detail}'")

        self.detail = detail

        # Clear cached properties to force reload with new detail level
        self._clear_cached_properties()

    def boundingBox(self) -> tuple:
        """Return bounding box as (r, z) tuple"""
        return (self.r.copy(), self.z.copy())

    def get_bounds(self) -> tuple:
        """Return geometric bounds (implements GeometryMixin if available)"""
        return self.boundingBox()

    def intersect(self, r: List[float], z: List[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is non-empty

        Args:
            r: Radial bounds [r_min, r_max] of test rectangle
            z: Axial bounds [z_min, z_max] of test rectangle

        Returns:
            True if objects intersect, False otherwise
        """
        # Check if rectangles overlap in both dimensions
        r_overlap = self.r[0] < r[1] and r[0] < self.r[1]
        z_overlap = self.z[0] < z[1] and z[0] < self.z[1]

        return r_overlap and z_overlap

    def get_structure_info(self) -> dict:
        """
        Get comprehensive structure information

        Returns:
            Dictionary with structure properties
        """
        info = {
            "name": self.name,
            "detail_level": self.detail,
            "has_structure": bool(self.struct),
            "basic_turns": self.n,
        }

        magnet = self.magnet_struct
        if magnet:
            try:
                info.update(
                    {
                        "structure_r0": (
                            magnet.getR0() if hasattr(magnet, "getR0") else None
                        ),
                        "structure_r1": (
                            magnet.getR1() if hasattr(magnet, "getR1") else None
                        ),
                        "structure_height": (
                            magnet.getH() if hasattr(magnet, "getH") else None
                        ),
                        "structure_turns": (
                            sum(magnet.getNtapes())
                            if hasattr(magnet, "getNtapes")
                            else None
                        ),
                        "dblpancake_count": (
                            magnet.getN() if hasattr(magnet, "getN") else None
                        ),
                    }
                )
            except Exception as e:
                info["structure_error"] = str(e)

        return info

    # Serialization methods
    def __repr__(self):
        """Enhanced string representation"""
        msg = f"{self.__class__.__name__}(name={self.name}, r={self.r}, z={self.z}, "
        msg += f"n={self.n}, struct={self.struct}, detail={self.detail})"
        return msg

    def dump(self):
        """Dump supra magnet to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to dump Supra data: {e}")

    def load(self):
        """Load supra magnet from YAML file"""
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except Exception:
            raise Exception(f"Failed to load Supra data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.struct = data.struct
        self.detail = getattr(data, "detail", "None")

        # Check dimensions against structure if available
        if self.struct:
            magnet = self.get_magnet_struct()
            if magnet:
                self.check_dimensions(magnet)

    def to_json(self):
        """Convert to JSON string"""
        try:
            from ... import deserialize

            return json.dumps(
                self, default=deserialize.serialize_instance, sort_keys=True, indent=4
            )
        except ImportError:
            # Fallback JSON conversion
            data = {
                "name": self.name,
                "r": self.r,
                "z": self.z,
                "n": self.n,
                "struct": self.struct,
                "detail": self.detail,
            }
            return json.dumps(data, indent=4, sort_keys=True)

    def write_to_json(self):
        """Write supra magnet to JSON file"""
        try:
            with open(f"{self.name}.json", "w") as ostream:
                jsondata = self.to_json()
                ostream.write(jsondata)
        except Exception as e:
            raise Exception(f"Failed to write JSON: {e}")

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Load supra magnet from JSON file"""
        try:
            from ... import deserialize

            if debug:
                print(f"Supra.from_json: filename={filename}")
            with open(filename, "r") as istream:
                return json.loads(
                    istream.read(), object_hook=deserialize.unserialize_object
                )
        except ImportError:
            # Fallback JSON loading
            with open(filename, "r") as f:
                data = json.load(f)
            return cls.from_dict(data, debug=debug)

    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create Supra from dictionary"""
        if debug:
            print(f"Creating Supra from dict: {list(data.keys())}")

        # Extract basic parameters
        name = data["name"]
        r = data["r"]
        z = data["z"]
        n = data.get("n", 0)
        struct = data.get("struct", "")

        supra = cls(name=name, r=r, z=z, n=n, struct=struct)

        # Set detail level if provided
        detail = data.get("detail", "None")
        supra.set_Detail(detail)

        return supra

    def validate(self) -> None:
        """Validate supra magnet parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()

        # Additional supra-specific validation
        if hasattr(self, "n") and self.n < 0:
            raise ValueError("Number of turns must be non-negative")

        if hasattr(self, "detail"):
            valid_details = ["None", "dblpancake", "pancake", "tape"]
            if self.detail not in valid_details:
                raise ValueError(f"detail must be one of {valid_details}")

        # Validate structure file if provided
        if hasattr(self, "struct") and self.struct:
            if not isinstance(self.struct, str):
                raise ValueError("struct must be a string filename")


def Supra_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)

    # Extract required values
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values["n"]
    struct = values["struct"]

    supra = Supra(name, r, z, n, struct)

    # Set detail level if provided
    if "detail" in values:
        supra.set_Detail(values["detail"])

    return supra


# Register YAML constructor
yaml.add_constructor("!Supra", Supra_constructor)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Bitter magnet component - moved to magnetgeo.components.magnet

This is the enhanced Bitter class with lazy loading, validation, and
comprehensive flow/thermal analysis capabilities.
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

# Import from support components location
try:
    from ..support import CoolingSlit, Tierod, ModelAxi
    SUPPORT_IMPORTS_AVAILABLE = True
except ImportError:
    # Fallback to old imports for transition period
    try:
        from ...coolingslit import CoolingSlit
        from ...tierod import Tierod
        from ...ModelAxi import ModelAxi
        SUPPORT_IMPORTS_AVAILABLE = True
    except ImportError:
        SUPPORT_IMPORTS_AVAILABLE = False
        print("Warning: Support components not available")

# Try to import validation utilities
try:
    from ...utils.validation import validate_dimensions, validate_string_not_empty, validate_positive
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


class Bitter(MagnetComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Bitter magnet component with enhanced validation and lazy loading
    
    Bitter magnets are disk-type resistive magnets with radial cooling slits.
    They provide high magnetic fields through water-cooled copper disks
    stacked in series.
    
    This version provides comprehensive flow/thermal analysis capabilities
    and lazy loading of support components while maintaining backward compatibility.
    """
    
    yaml_tag = "Bitter"
    
    def __init__(
        self,
        name: str,
        r: List[float],
        z: List[float],
        odd: bool,
        modelaxi: Any,
        coolingslits: List[Any],
        tierod: Any,
        innerbore: float,
        outerbore: float,
    ):
        """
        Initialize Bitter magnet with enhanced validation and lazy loading
        
        Args:
            name: Bitter magnet identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
            odd: Whether magnet has odd symmetry
            modelaxi: Axisymmetric model data
            coolingslits: List of cooling slit definitions
            tierod: Tie rod definition
            innerbore: Inner bore radius
            outerbore: Outer bore radius
        """
        # Validate basic parameters if validation is available
        if VALIDATION_AVAILABLE:
            validate_dimensions(r, z)
            validate_string_not_empty(name, "name")
            validate_positive(innerbore, "innerbore")
            validate_positive(outerbore, "outerbore")
            if innerbore >= outerbore:
                raise ValueError(f"innerbore ({innerbore}) must be less than outerbore ({outerbore})")
        
        # Initialize base class if available
        if BASE_CLASS_AVAILABLE:
            super().__init__(name=name, r=r, z=z, odd=odd, modelaxi=modelaxi)
            self.innerbore = innerbore
            self.outerbore = outerbore
        else:
            # Fallback initialization
            self.name = name
            self.r = r.copy()
            self.z = z.copy()
            self.odd = odd
            self.innerbore = innerbore
            self.outerbore = outerbore
            self._modelaxi_data = modelaxi
        
        # Store support component data for lazy loading
        if not BASE_CLASS_AVAILABLE:
            self._modelaxi_data = modelaxi
        self._coolingslits_data = coolingslits or []
        self._tierod_data = tierod
        
        # Clear any cached properties to ensure fresh loading
        self._clear_cached_properties()
    
    def _clear_cached_properties(self):
        """Clear cached properties to force reload"""
        cached_attrs = ['modelaxi', 'coolingslits', 'tierod']
        for attr in cached_attrs:
            if hasattr(self, f'_{attr}'):
                delattr(self, f'_{attr}')
    
    @cached_property
    def modelaxi(self) -> Optional[Any]:
        """Load ModelAxi on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._modelaxi_data
        
        return self._load_support_object(self._modelaxi_data, ModelAxi, "ModelAxi")
    
    @cached_property
    def coolingslits(self) -> List[Any]:
        """Load cooling slits on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._coolingslits_data or []
        
        if not self._coolingslits_data:
            return []
        
        loaded_slits = []
        for i, slit_data in enumerate(self._coolingslits_data):
            try:
                slit = self._load_support_object(slit_data, CoolingSlit, f"CoolingSlit[{i}]")
                if slit:
                    loaded_slits.append(slit)
            except Exception as e:
                print(f"Warning: Could not load cooling slit {i}: {e}")
                # Keep original data as fallback
                loaded_slits.append(slit_data)
        
        return loaded_slits
    
    @cached_property
    def tierod(self) -> Optional[Any]:
        """Load tierod on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._tierod_data
        
        return self._load_support_object(self._tierod_data, Tierod, "Tierod")
    
    def _load_support_object(self, data: Any, expected_class: type, context: str) -> Optional[Any]:
        """
        Helper method to load support objects with various data formats
        
        Args:
            data: Data to load (dict, string filename, or object)
            expected_class: Expected class type
            context: Context string for error messages
            
        Returns:
            Loaded object or None
        """
        if data is None:
            return None
        
        # If already an instance of expected class, return as-is
        if isinstance(data, expected_class):
            return data
        
        # If it's a dict, try to convert using from_dict
        if isinstance(data, dict):
            try:
                if hasattr(expected_class, 'from_dict'):
                    return expected_class.from_dict(data)
                else:
                    # Fallback: try to construct directly
                    return expected_class(**data)
            except Exception as e:
                print(f"Warning: Could not load {context} from dict: {e}")
                return data  # Return original data as fallback
        
        # If it's a string, assume it's a filename
        if isinstance(data, str):
            try:
                with open(f"{data}.yaml", "r") as f:
                    yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                    if isinstance(yaml_data, expected_class):
                        return yaml_data
                    elif hasattr(expected_class, 'from_dict') and isinstance(yaml_data, dict):
                        return expected_class.from_dict(yaml_data)
            except Exception as e:
                print(f"Warning: Could not load {context} from file '{data}': {e}")
        
        # Return original data as fallback
        return data
    
    # Core Bitter magnet methods
    def get_component_type(self) -> str:
        """Get component type identifier"""
        return "Bitter"
    
    def get_insulator_info(self) -> tuple:
        """
        Get insulator information for this Bitter magnet
        
        Returns:
            Tuple of (insulator_name, count)
        """
        return ("Kapton", 1)  # Bitter magnets typically use Kapton insulation
    
    def equivalent_eps(self, i: int) -> float:
        """
        Calculate equivalent thickness of annular ring for cooling slit
        
        Args:
            i: Index of cooling slit
            
        Returns:
            Equivalent thickness = n * sh / (2 * pi * r)
        """
        if not self.coolingslits or i >= len(self.coolingslits):
            return 0.0
        
        import math
        slit = self.coolingslits[i]
        
        # Handle both new and old slit formats
        if hasattr(slit, 'r') and hasattr(slit, 'n') and hasattr(slit, 'sh'):
            x = slit.r
            n = slit.n
            sh = slit.sh
        elif isinstance(slit, dict):
            x = slit.get('r', 0)
            n = slit.get('n', 0)
            sh = slit.get('sh', 0)
        else:
            return 0.0
        
        if x == 0:
            return 0.0
        
        return n * sh / (2 * math.pi * x)
    
    def get_channels(self, mname: str, hideIsolant: bool = True, debug: bool = False) -> List[str]:
        """
        Get channel names for CFD analysis
        
        Args:
            mname: Base name for channels
            hideIsolant: Whether to hide isolant channels
            debug: Whether to print debug info
            
        Returns:
            List of channel names
        """
        prefix = f"{mname}_" if mname else ""
        
        n_slits = len(self.coolingslits) if self.coolingslits else 0
        
        # Channel naming: Slit0 (inner bore), Slit1..N (cooling slits), SlitN+1 (outer bore)
        channels = [f"{prefix}Slit{0}"]  # Inner bore channel
        
        if n_slits > 0:
            if debug:
                print(f"Bitter({self.name}): CoolingSlits={n_slits}")
            channels.extend([f"{prefix}Slit{i+1}" for i in range(n_slits)])
        
        channels.append(f"{prefix}Slit{n_slits+1}")  # Outer bore channel
        
        if debug:
            print(f"Bitter({prefix}): {channels}")
        
        return channels
    
    def get_lc(self) -> float:
        """Get characteristic length for meshing"""
        lc = (self.r[1] - self.r[0]) / 10.0
        
        if self.coolingslits:
            # Refine mesh based on cooling slit spacing
            x = self.r[0]
            dr_list = []
            
            for slit in self.coolingslits:
                slit_r = getattr(slit, 'r', slit.get('r', 0) if isinstance(slit, dict) else 0)
                dr_list.append(slit_r - x)
                x = slit_r
            
            dr_list.append(self.r[1] - x)
            lc = min(dr_list) / 5.0
        
        return lc
    
    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """Get isolant region names (empty for Bitter magnets)"""
        return []
    
    def get_names(self, mname: str, is2D: bool = False, verbose: bool = False) -> List[str]:
        """
        Get names for markers/regions
        
        Args:
            mname: Base name prefix
            is2D: Whether generating 2D or 3D names
            verbose: Whether to print verbose information
            
        Returns:
            List of region/marker names
        """
        tol = 1.0e-10
        prefix = f"{mname}_" if mname else ""
        solid_names = []
        
        n_slits = len(self.coolingslits) if self.coolingslits else 0
        
        if is2D:
            # 2D section names based on modelaxi turns
            if self.modelaxi and hasattr(self.modelaxi, 'turns'):
                nsection = len(self.modelaxi.turns)
                
                # Check if geometry extends beyond modelaxi height
                modelaxi_h = getattr(self.modelaxi, 'h', 0)
                if self.z[0] < -modelaxi_h and abs(self.z[0] + modelaxi_h) >= tol:
                    # Bottom extension
                    for i in range(n_slits + 1):
                        solid_names.append(f"{prefix}B0_Slit{i}")
                
                # Main sections
                for j in range(nsection):
                    for i in range(n_slits + 1):
                        solid_names.append(f"{prefix}B{j+1}_Slit{i}")
                
                # Check if geometry extends above modelaxi height
                if self.z[1] > modelaxi_h and abs(self.z[1] - modelaxi_h) >= tol:
                    # Top extension
                    for i in range(n_slits + 1):
                        solid_names.append(f"{prefix}B{nsection+1}_Slit{i}")
            else:
                # Simple case - just use base names
                for i in range(n_slits + 1):
                    solid_names.append(f"{prefix}B_Slit{i}")
        else:
            # 3D names
            solid_names.append(f"{prefix}B")  # Main conductor
            solid_names.append(f"{prefix}Kapton")  # Insulation
        
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        
        return solid_names
    
    def get_Nturns(self) -> float:
        """Get total number of turns from modelaxi"""
        if self.modelaxi and hasattr(self.modelaxi, 'get_total_turns'):
            return self.modelaxi.get_total_turns()
        elif self.modelaxi and hasattr(self.modelaxi, 'get_Nturns'):
            return self.modelaxi.get_Nturns()
        return 0.0
    
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
    
    def get_params(self, workingDir: str = ".") -> tuple:
        """
        Get parameters for thermal/flow analysis
        
        Args:
            workingDir: Working directory for file operations
            
        Returns:
            Tuple of (nslits, Dh, Sh, Zh, filling_factor)
        """
        import math
        
        tol = 1.0e-10
        n_slits = len(self.coolingslits) if self.coolingslits else 0
        
        # Hydraulic diameters and surface areas
        Dh = [2 * (self.r[0] - self.innerbore)]  # Inner bore channel
        Sh = [math.pi * (self.r[0] - self.innerbore) * (self.r[0] + self.innerbore)]
        filling_factor = [1.0]  # Inner bore fully filled with coolant
        
        # Add cooling slits
        if self.coolingslits:
            for slit in self.coolingslits:
                # Handle both new and old slit formats
                if hasattr(slit, 'dh') and hasattr(slit, 'n') and hasattr(slit, 'sh'):
                    Dh.append(slit.dh)
                    Sh.append(slit.n * slit.sh)
                    
                    # Calculate filling factor (wetted perimeter ratio)
                    if hasattr(slit, 'r'):
                        ff = slit.n * ((4 * slit.sh) / slit.dh) / (4 * math.pi * slit.r)
                        filling_factor.append(ff)
                    else:
                        filling_factor.append(1.0)
                elif isinstance(slit, dict):
                    Dh.append(slit.get('dh', 0))
                    Sh.append(slit.get('n', 0) * slit.get('sh', 0))
                    
                    slit_r = slit.get('r', 1)
                    if slit_r > 0:
                        ff = slit.get('n', 0) * ((4 * slit.get('sh', 0)) / max(slit.get('dh', 1), 1e-10)) / (4 * math.pi * slit_r)
                        filling_factor.append(ff)
                    else:
                        filling_factor.append(1.0)
        
        # Outer bore channel
        Dh.append(2 * (self.outerbore - self.r[1]))
        Sh.append(math.pi * (self.outerbore - self.r[1]) * (self.outerbore + self.r[1]))
        filling_factor.append(1.0)
        
        # Axial heights
        Zh = [self.z[0]]
        
        if self.modelaxi and hasattr(self.modelaxi, 'turns') and hasattr(self.modelaxi, 'pitch'):
            modelaxi_h = getattr(self.modelaxi, 'h', 0)
            z = -modelaxi_h
            
            if abs(self.z[0] - z) >= tol:
                Zh.append(z)
            
            # Add heights for each turn section
            for n_turn, pitch in zip(self.modelaxi.turns, self.modelaxi.pitch):
                z += n_turn * pitch
                Zh.append(z)
            
            if abs(self.z[1] - z) >= tol:
                Zh.append(self.z[1])
        else:
            Zh.append(self.z[1])
        
        return (n_slits, Dh, Sh, Zh, filling_factor)
    
    def create_cut(self, format: str):
        """Generate cut files using support utilities"""
        try:
            from ...cut_utils import create_cut
            create_cut(self, format, self.name)
        except ImportError:
            print("Warning: cut_utils not available")
    
    # Serialization methods
    def __repr__(self):
        """Enhanced string representation"""
        return (f"{self.__class__.__name__}(name={self.name}, r={self.r}, z={self.z}, "
                f"odd={self.odd}, modelaxi={type(self.modelaxi).__name__ if self.modelaxi else None}, "
                f"coolingslits={len(self.coolingslits) if self.coolingslits else 0} items, "
                f"tierod={type(self.tierod).__name__ if self.tierod else None}, "
                f"innerbore={self.innerbore}, outerbore={self.outerbore})")
    
    def dump(self):
        """Dump bitter magnet to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to dump Bitter data: {e}")
    
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
                "odd": self.odd,
                "innerbore": self.innerbore,
                "outerbore": self.outerbore,
            }
            
            # Add support component data
            if self._modelaxi_data:
                if hasattr(self._modelaxi_data, 'to_dict'):
                    data["modelaxi"] = self._modelaxi_data.to_dict()
                else:
                    data["modelaxi"] = self._modelaxi_data
            
            if self._coolingslits_data:
                slits_data = []
                for slit in self._coolingslits_data:
                    if hasattr(slit, 'to_dict'):
                        slits_data.append(slit.to_dict())
                    else:
                        slits_data.append(slit)
                data["coolingslits"] = slits_data
            
            if self._tierod_data:
                if hasattr(self._tierod_data, 'to_dict'):
                    data["tierod"] = self._tierod_data.to_dict()
                else:
                    data["tierod"] = self._tierod_data
            
            return json.dumps(data, indent=4, sort_keys=True)
    
    def write_to_json(self):
        """Write bitter magnet to JSON file"""
        try:
            with open(f"{self.name}.json", "w") as ostream:
                jsondata = self.to_json()
                ostream.write(jsondata)
        except Exception as e:
            raise Exception(f"Failed to write JSON: {e}")
    
    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Load bitter magnet from JSON file"""
        try:
            from ... import deserialize
            if debug:
                print(f"Bitter.from_json: filename={filename}")
            with open(filename, "r") as istream:
                return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
        except ImportError:
            # Fallback JSON loading
            with open(filename, "r") as f:
                data = json.load(f)
            return cls.from_dict(data, debug=debug)
    
    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create Bitter from dictionary"""
        if debug:
            print(f"Creating Bitter from dict: {list(data.keys())}")
        
        # Extract basic parameters
        name = data["name"]
        r = data["r"]
        z = data["z"]
        odd = data["odd"]
        innerbore = data.get("innerbore", 0)
        outerbore = data.get("outerbore", 0)
        
        # Extract support component data
        modelaxi = data.get("modelaxi")
        coolingslits = data.get("coolingslits", [])
        tierod = data.get("tierod")
        
        return cls(
            name=name, r=r, z=z, odd=odd, modelaxi=modelaxi,
            coolingslits=coolingslits, tierod=tierod,
            innerbore=innerbore, outerbore=outerbore
        )
    
    def validate(self) -> None:
        """Validate bitter magnet parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        
        # Additional bitter-specific validation
        if hasattr(self, 'innerbore') and hasattr(self, 'outerbore'):
            if self.innerbore >= self.outerbore:
                raise ValueError(f"innerbore ({self.innerbore}) must be less than outerbore ({self.outerbore})")


def Bitter_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    
    # Extract required values
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    modelaxi = values["modelaxi"]
    coolingslits = values["coolingslits"]
    tierod = values["tierod"]
    
    # Optional values with defaults
    innerbore = values.get("innerbore", 0)
    outerbore = values.get("outerbore", 0)
    
    return Bitter(
        name, r, z, odd, modelaxi, coolingslits, tierod, innerbore, outerbore
    )


# Register YAML constructor
yaml.add_constructor("!Bitter", Bitter_constructor)
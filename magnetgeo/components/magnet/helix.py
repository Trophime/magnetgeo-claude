#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Helix magnet component - moved to magnetgeo.components.magnet

This is the enhanced Helix class with lazy loading, validation, and
backward compatibility support.
"""

import math
import json
import yaml
from functools import cached_property
from typing import List, Optional, Any, Union

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
    from ..support import Chamfer, Groove, Shape, ModelAxi, Model3D
    SUPPORT_IMPORTS_AVAILABLE = True
except ImportError:
    # Fallback to old imports for transition period
    try:
        from ...Chamfer import Chamfer
        from ...Groove import Groove  
        from ...Shape import Shape
        from ...ModelAxi import ModelAxi
        from ...Model3D import Model3D
        SUPPORT_IMPORTS_AVAILABLE = True
    except ImportError:
        SUPPORT_IMPORTS_AVAILABLE = False
        print("Warning: Support components not available")

# Try to import validation utilities
try:
    from ...utils.validation import validate_dimensions, validate_string_not_empty
    from ...utils.enums import HelixType, InsulatorType
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False


class Helix(MagnetComponentBase if BASE_CLASS_AVAILABLE else yaml.YAMLObject):
    """
    Helix magnet component with enhanced validation and lazy loading
    
    Helical magnets are coil-type magnets with spiral windings. They can be:
    - HL (Low resistance): Simple double-layer helices
    - HR (High resistance): Helices with cooling channels and shapes
    
    This version uses lazy loading for support components and provides
    comprehensive validation while maintaining backward compatibility.
    """
    
    yaml_tag = "Helix"
    
    def __setstate__(self, state):
        """Handle deserialization with lazy loading setup"""
        self.__dict__.update(state)
        
        # Ensure support component data attributes exist
        if not hasattr(self, '_chamfers_data'):
            self._chamfers_data = getattr(self, 'chamfers', [])
        if not hasattr(self, '_grooves_data'):
            self._grooves_data = getattr(self, 'grooves', None)
        if not hasattr(self, '_shape_data'):
            self._shape_data = getattr(self, 'shape', None)
        if not hasattr(self, '_modelaxi_data'):
            self._modelaxi_data = getattr(self, 'modelaxi', None)
        if not hasattr(self, '_model3d_data'):
            self._model3d_data = getattr(self, 'model3d', None)
    
    def __init__(
        self,
        name: str,
        r: List[float],
        z: List[float],
        cutwidth: float,
        odd: bool,
        dble: bool,
        modelaxi: Any,
        model3d: Any,
        shape: Any,
        chamfers: List = None,
        grooves: Any = None,
    ):
        """
        Initialize helix with enhanced validation and lazy loading
        
        Args:
            name: Helix identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
            cutwidth: Width of helical cut
            odd: Whether helix has odd symmetry
            dble: Whether helix is double layer
            modelaxi: Axisymmetric model data
            model3d: 3D model configuration
            shape: Shape cutting pattern
            chamfers: List of chamfer definitions
            grooves: Groove definition
        """
        # Validate basic parameters if validation is available
        if VALIDATION_AVAILABLE:
            validate_dimensions(r, z)
            validate_string_not_empty(name, "name")
            if cutwidth <= 0:
                raise ValueError("cutwidth must be positive")
        
        # Initialize base class if available
        if BASE_CLASS_AVAILABLE:
            super().__init__(name=name, r=r, z=z, odd=odd, modelaxi=modelaxi)
            self.cutwidth = cutwidth
            self.dble = dble
        else:
            # Fallback initialization
            self.name = name
            self.r = r.copy()
            self.z = z.copy()
            self.odd = odd
            self.cutwidth = cutwidth
            self.dble = dble
            self._modelaxi_data = modelaxi
        
        # Store support component data for lazy loading
        if not BASE_CLASS_AVAILABLE:
            self._modelaxi_data = modelaxi
        self._model3d_data = model3d
        self._shape_data = shape
        self._chamfers_data = chamfers or []
        self._grooves_data = grooves
        
        # Clear any cached properties to ensure fresh loading
        self._clear_cached_properties()
    
    def _clear_cached_properties(self):
        """Clear cached properties to force reload"""
        cached_attrs = ['modelaxi', 'model3d', 'shape', 'chamfers', 'grooves']
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
    def model3d(self) -> Optional[Any]:
        """Load Model3D on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._model3d_data
        
        return self._load_support_object(self._model3d_data, Model3D, "Model3D")
    
    @cached_property
    def shape(self) -> Optional[Any]:
        """Load Shape on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._shape_data
        
        return self._load_support_object(self._shape_data, Shape, "Shape")
    
    @cached_property
    def chamfers(self) -> List[Any]:
        """Load chamfers on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._chamfers_data or []
        
        if not self._chamfers_data:
            return []
        
        loaded_chamfers = []
        for i, chamfer_data in enumerate(self._chamfers_data):
            try:
                chamfer = self._load_support_object(chamfer_data, Chamfer, f"Chamfer[{i}]")
                if chamfer:
                    loaded_chamfers.append(chamfer)
            except Exception as e:
                print(f"Warning: Could not load chamfer {i}: {e}")
                # Keep original data as fallback
                loaded_chamfers.append(chamfer_data)
        
        return loaded_chamfers
    
    @cached_property
    def grooves(self) -> Optional[Any]:
        """Load grooves on first access with lazy loading"""
        if not SUPPORT_IMPORTS_AVAILABLE:
            return self._grooves_data
        
        if self._grooves_data is None:
            # Return empty groove for backward compatibility
            try:
                return Groove()
            except:
                return None
        
        return self._load_support_object(self._grooves_data, Groove, "Groove")
    
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
    
    # Core helix methods with enhanced functionality
    def get_component_type(self) -> str:
        """Get helix component type"""
        return self.get_type()
    
    def get_type(self) -> str:
        """Get helix type based on model3d configuration"""
        if hasattr(self.model3d, 'get_model_type'):
            return self.model3d.get_model_type()
        elif self.model3d and getattr(self.model3d, 'with_shapes', False) and getattr(self.model3d, 'with_channels', False):
            return "HR"
        return "HL"
    
    def get_insulator_info(self) -> tuple:
        """
        Get insulator information for this helix
        
        Returns:
            Tuple of (insulator_name, count)
        """
        return self.insulators()
    
    def get_lc(self) -> float:
        """Get characteristic length for meshing"""
        return (self.r[1] - self.r[0]) / 10.0
    
    def get_Nturns(self) -> float:
        """Get total number of turns from modelaxi"""
        if self.modelaxi and hasattr(self.modelaxi, 'get_total_turns'):
            return self.modelaxi.get_total_turns()
        elif self.modelaxi and hasattr(self.modelaxi, 'get_Nturns'):
            return self.modelaxi.get_Nturns()
        return 0.0
    
    def get_names(self, mname: str, is2D: bool, verbose: bool = False) -> List[str]:
        """
        Get names for markers/regions with enhanced logic
        
        Args:
            mname: Base name prefix
            is2D: Whether generating 2D or 3D names
            verbose: Whether to print verbose information
            
        Returns:
            List of region/marker names
        """
        prefix = f"{mname}_" if mname else ""
        solid_names = []
        
        # Get insulator information
        sInsulator, nInsulators = self.insulators()
        
        if is2D:
            # 2D section names
            if self.modelaxi and hasattr(self.modelaxi, 'turns'):
                nsection = len(self.modelaxi.turns)
                solid_names.append(f"{prefix}Cu{0}")  # HP
                for j in range(nsection):
                    solid_names.append(f"{prefix}Cu{j+1}")
                solid_names.append(f"{prefix}Cu{nsection+1}")  # BP
            else:
                solid_names.append(f"{prefix}Cu")
        else:
            # 3D names
            solid_names.append(f"{prefix}Cu")
            for j in range(nInsulators):
                solid_names.append(f"{prefix}{sInsulator}{j}")
        
        if verbose:
            htype = self.get_type()
            nturns = self.get_Nturns()
            print(f"Helix[{htype}]: solid_names {len(solid_names)}, nturns={nturns}")
        
        return solid_names
    
    def insulators(self) -> tuple:
        """
        Get insulator information based on helix type
        
        Returns:
            Tuple of (insulator_name, count)
        """
        if VALIDATION_AVAILABLE:
            try:
                sInsulator = InsulatorType.GLUE.value
                nInsulators = 1
                htype = self.get_type()
                
                if htype == HelixType.HL.value:
                    nInsulators = 2 if self.dble else 1
                else:  # HR type
                    sInsulator = InsulatorType.KAPTON.value
                    if self.shape and hasattr(self.shape, 'angle'):
                        # Calculate number of shapes
                        angle = getattr(self.shape, 'angle', [360])[0]
                        if angle > 0:
                            nshapes = self.get_Nturns() * (360.0 / angle)
                            nInsulators = int(round(nshapes))
                        else:
                            nInsulators = 1
                    else:
                        nInsulators = 1
                
                return (sInsulator, nInsulators)
            except:
                pass
        
        # Fallback implementation
        sInsulator = "Glue"
        nInsulators = 1
        if self.model3d and getattr(self.model3d, 'with_shapes', False) and getattr(self.model3d, 'with_channels', False):
            sInsulator = "Kapton"
            angle = 360  # Default
            if self.shape and hasattr(self.shape, 'angle'):
                shape_angles = getattr(self.shape, 'angle', [360])
                if shape_angles:
                    angle = shape_angles[0]
            
            if angle > 0:
                nshapes = self.get_Nturns() * (360.0 / angle)
                nInsulators = max(1, int(round(nshapes)))
        else:
            if self.dble:
                nInsulators = 2
        
        return (sInsulator, nInsulators)
    
    def htype(self) -> str:
        """Get helix type (alias for get_type)"""
        return self.get_type()
    
    def boundingBox(self) -> tuple:
        """Return bounding box as (r, z) tuple"""
        return (self.r.copy(), self.z.copy())
    
    def get_bounds(self) -> tuple:
        """Return geometric bounds (implements GeometryMixin if available)"""
        return self.boundingBox()
    
    def generate_cut(self, format: str = "SALOME"):
        """Generate cut files using support utilities"""
        try:
            from ...cut_utils import create_cut
            
            if self.model3d and getattr(self.model3d, 'with_shapes', False):
                create_cut(self, "LNCMI", self.name)
                if self.shape:
                    angles_str = " ".join(f"{t:4.2f}" for t in getattr(self.shape, 'angle', []) if t != 0)
                    length = getattr(self.shape, 'length', [0])[0]
                    shape_name = getattr(self.shape, 'name', '')
                    position = getattr(self.shape, 'position', 'ABOVE')
                    
                    cmd = f'add_shape --angle="{angles_str}" --shape_angular_length={length} --shape={shape_name} --format={format} --position="{position}"'
                    print(f"create_cut: with_shapes not implemented - shall run {cmd}")
                    
                    import subprocess
                    subprocess.run(cmd, shell=True, check=True)
            else:
                create_cut(self, format, self.name)
        except ImportError:
            print("Warning: cut_utils not available")
    
    # Serialization methods
    def __repr__(self):
        """Enhanced string representation"""
        msg = f"{self.__class__.__name__}(name={self.name}, odd={self.odd}, dble={self.dble}, "
        msg += f"r={self.r}, z={self.z}, cutwidth={self.cutwidth}, "
        msg += f"modelaxi={type(self.modelaxi).__name__ if self.modelaxi else None}, "
        msg += f"model3d={type(self.model3d).__name__ if self.model3d else None}, "
        msg += f"shape={type(self.shape).__name__ if self.shape else None}"
        
        if hasattr(self, 'chamfers') and self.chamfers:
            msg += f", chamfers={len(self.chamfers)} items"
        if hasattr(self, 'grooves') and self.grooves:
            msg += f", grooves={type(self.grooves).__name__}"
        
        msg += ")"
        return msg
    
    def dump(self):
        """Dump helix to YAML file"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to dump Helix data: {e}")
    
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
                "cutwidth": self.cutwidth,
                "odd": self.odd,
                "dble": self.dble,
            }
            
            # Add support component data
            if self._modelaxi_data:
                if hasattr(self._modelaxi_data, 'to_dict'):
                    data["modelaxi"] = self._modelaxi_data.to_dict()
                else:
                    data["modelaxi"] = self._modelaxi_data
            
            if self._model3d_data:
                if hasattr(self._model3d_data, 'to_dict'):
                    data["model3d"] = self._model3d_data.to_dict()
                else:
                    data["model3d"] = self._model3d_data
            
            return json.dumps(data, indent=4, sort_keys=True)
    
    def write_to_json(self):
        """Write helix to JSON file"""
        try:
            with open(f"{self.name}.json", "w") as ostream:
                jsondata = self.to_json()
                ostream.write(jsondata)
        except Exception as e:
            raise Exception(f"Failed to write JSON: {e}")
    
    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """Load helix from JSON file"""
        try:
            from ... import deserialize
            if debug:
                print(f"Helix.from_json: filename={filename}")
            with open(filename, "r") as istream:
                return json.loads(istream.read(), object_hook=deserialize.unserialize_object)
        except ImportError:
            # Fallback JSON loading
            with open(filename, "r") as f:
                data = json.load(f)
            return cls.from_dict(data, debug=debug)
    
    @classmethod
    def from_dict(cls, data: dict, debug: bool = False):
        """Create Helix from dictionary"""
        if debug:
            print(f"Creating Helix from dict: {list(data.keys())}")
        
        # Extract basic parameters
        name = data["name"]
        r = data["r"]
        z = data["z"]
        cutwidth = data["cutwidth"]
        odd = data["odd"]
        dble = data["dble"]
        
        # Extract support component data
        modelaxi = data.get("modelaxi")
        model3d = data.get("model3d")
        shape = data.get("shape")
        chamfers = data.get("chamfers", [])
        grooves = data.get("grooves")
        
        return cls(
            name=name, r=r, z=z, cutwidth=cutwidth, odd=odd, dble=dble,
            modelaxi=modelaxi, model3d=model3d, shape=shape,
            chamfers=chamfers, grooves=grooves
        )
    
    def validate(self) -> None:
        """Validate helix parameters"""
        if BASE_CLASS_AVAILABLE:
            super().validate()
        
        # Additional helix-specific validation
        if hasattr(self, 'cutwidth') and self.cutwidth <= 0:
            raise ValueError("cutwidth must be positive")


def Helix_constructor(loader, node):
    """YAML constructor for backward compatibility"""
    values = loader.construct_mapping(node)
    
    # Handle the transition period where some fields might be missing
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    dble = values["dble"]
    cutwidth = values["cutwidth"]
    modelaxi = values["modelaxi"]
    model3d = values["model3d"]
    shape = values["shape"]
    
    # Optional fields with defaults
    chamfers = values.get("chamfers", [])
    grooves = values.get("grooves")
    
    helix = Helix(
        name, r, z, cutwidth, odd, dble, modelaxi, model3d, shape, chamfers, grooves
    )
    
    return helix


# Register YAML constructor
yaml.add_constructor("!Helix", Helix_constructor)
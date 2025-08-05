from functools import cached_property
from typing import Union, Any

class MagnetComponentBase(SerializableBase, GeometryMixin, ABC):
    """
    Base class for individual magnet components
    
    Magnet components are the core magnetic field-generating elements.
    Examples: Helix, Bitter, Supra
    """
    
    def __init__(
        self,
        name: str,
        r: List[float],
        z: List[float], 
        odd: bool = False,
        modelaxi: Any = None,
        **kwargs
    ):
        """
        Initialize magnet component
        
        Args:
            name: Component identifier
            r: Radial bounds [r_min, r_max]
            z: Axial bounds [z_min, z_max]
            odd: Whether component has odd symmetry
            modelaxi: Axisymmetric model data
            **kwargs: Additional component-specific parameters
        """
        # Validate basic geometry
        validate_bounds(r, z)
        validate_string_not_empty(name, "name")
        
        self.name = name
        self.r = r.copy()  # Defensive copy
        self.z = z.copy()  # Defensive copy
        self.odd = bool(odd)
        self._modelaxi_data = modelaxi
        
        # Store component-specific parameters with lazy loading pattern
        for key, value in kwargs.items():
            if self._should_lazy_load(key):
                setattr(self, f"_{key}_data", value)
            else:
                setattr(self, key, value)
        
        # Call validation after initialization
        self.validate()

    def _should_lazy_load(self, key: str) -> bool:
        """
        Determine if a parameter should be lazy-loaded
        
        Args:
            key: Parameter name
            
        Returns:
            True if parameter should be lazy-loaded
        """
        lazy_load_keys = {
            'shape', 'chamfers', 'grooves', 'coolingslits', 
            'tierod', 'model3d', 'struct'
        }
        return key in lazy_load_keys

    @cached_property
    def modelaxi(self) -> Any:
        """
        Load model axi on first access
        
        Returns:
            ModelAxi object or None
        """
        if isinstance(self._modelaxi_data, str):
            # Lazy load from file path
            return self._load_from_file(self._modelaxi_data, 'ModelAxi')
        return self._modelaxi_data

    def _load_from_file(self, filepath: str, expected_type: str) -> Any:
        """
        Helper method for loading objects from files
        
        Args:
            filepath: Path to file
            expected_type: Expected class name
            
        Returns:
            Loaded object
        """
        # This would use the utils.load_file function
        # Implementation depends on your existing file loading system
        try:
            from ..utils.io import load_file
            # Dynamically import expected type
            module_map = {
                'ModelAxi': 'magnetgeo.components.support.modelaxi',
                'Model3D': 'magnetgeo.components.support.model3d',
                'Shape': 'magnetgeo.components.support.shape',
                # Add more as needed
            }
            
            if expected_type in module_map:
                module_path = module_map[expected_type]
                module = __import__(module_path, fromlist=[expected_type])
                expected_class = getattr(module, expected_type)
                return load_file(filepath, expected_class)
            else:
                # Fallback - load without type checking
                return load_file(filepath)
        except ImportError:
            # Fallback if utils not available yet
            import yaml
            with open(filepath, 'r') as f:
                return yaml.load(f, Loader=yaml.SafeLoader)

    # Abstract methods that concrete classes must implement
    @abstractmethod
    def get_component_type(self) -> str:
        """
        Return component type identifier
        
        Returns:
            Component type string ('HL', 'HR', 'Bitter', 'Supra', etc.)
        """
        pass

    @abstractmethod
    def get_insulator_info(self) -> Tuple[str, int]:
        """
        Return insulator information for this component
        
        Returns:
            Tuple of (insulator_name, count)
        """
        pass

    # Common implementations
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Return bounding box as (r, z) tuple
        
        Returns:
            Tuple of (r_bounds, z_bounds)
        """
        return (self.r.copy(), self.z.copy())

    def get_turns(self) -> float:
        """
        Get number of turns from modelaxi
        
        Returns:
            Total number of turns, 0 if no modelaxi
        """
        if self.modelaxi and hasattr(self.modelaxi, 'get_total_turns'):
            return self.modelaxi.get_total_turns()
        return 0.0

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
        prefix = f"{mname}_" if mname else ""
        
        if is2D:
            return self._get_2d_names(prefix, verbose)
        else:
            return self._get_3d_names(prefix, verbose)

    def _get_2d_names(self, prefix: str, verbose: bool = False) -> List[str]:
        """
        Generate 2D section names
        
        Args:
            prefix: Name prefix
            verbose: Whether to print verbose information
            
        Returns:
            List of 2D section names
        """
        # Default implementation - override in subclasses for specific behavior
        base_name = f"{prefix}{self.name}"
        
        if self.modelaxi and hasattr(self.modelaxi, 'turns'):
            # Generate names for each section
            names = []
            for i in range(len(self.modelaxi.turns)):
                names.append(f"{base_name}_section{i}")
            return names
        else:
            return [base_name]

    def _get_3d_names(self, prefix: str, verbose: bool = False) -> List[str]:
        """
        Generate 3D names (conductor + insulators)
        
        Args:
            prefix: Name prefix
            verbose: Whether to print verbose information
            
        Returns:
            List of 3D component names
        """
        names = [f"{prefix}{self.name}"]
        
        # Add insulator names
        insulator_name, count = self.get_insulator_info()
        if insulator_name and count > 0:
            for i in range(count):
                names.append(f"{prefix}{insulator_name}{i}")
        
        return names

    def validate(self) -> None:
        """
        Validate magnet component
        
        Calls parent validation and adds component-specific checks.
        """
        super().validate()
        
        # Additional validation can be added here
        # Subclasses should override and call super().validate()

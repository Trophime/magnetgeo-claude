class StructuralComponentBase(SerializableBase, GeometryMixin):
    """
    Base class for structural components
    
    Structural components provide physical support and connections.
    Examples: Ring, Screen, InnerCurrentLead, OuterCurrentLead
    """
    
    def __init__(self, name: str, r: List[float], **kwargs):
        """
        Initialize structural component
        
        Args:
            name: Component identifier
            r: Radial bounds [r_min, r_max]
            **kwargs: Additional component-specific parameters
        """
        validate_string_not_empty(name, "name")
        
        # Basic validation for radial bounds
        if not isinstance(r, list) or len(r) != 2:
            raise ValueError("r must be a list of [r_min, r_max]")
        
        if r[0] >= r[1]:
            raise ValueError(f"r_min ({r[0]}) must be less than r_max ({r[1]})")
        
        if r[0] < 0:
            raise ValueError("Radial coordinates must be non-negative")
        
        self.name = name
        self.r = r.copy()  # Defensive copy
        
        # Store additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Call validation after initialization
        self.validate()

    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Return bounding box
        
        Default implementation uses r bounds and z from kwargs.
        Override in subclasses for custom geometry.
        
        Returns:
            Tuple of (r_bounds, z_bounds)
        """
        z_bounds = getattr(self, 'z', [0, 0])
        
        # Ensure z_bounds is a valid list
        if not isinstance(z_bounds, list) or len(z_bounds) != 2:
            z_bounds = [0, 0]
        
        return (self.r.copy(), z_bounds)

    def get_structural_type(self) -> str:
        """
        Get structural component type
        
        Returns:
            Component type string
        """
        return self.__class__.__name__

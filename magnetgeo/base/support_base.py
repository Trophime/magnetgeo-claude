class SupportComponentBase(SerializableBase):
    """
    Base class for support components
    
    Support components are auxiliary objects used by main magnet components.
    Examples: Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod, Shape
    """
    
    def __init__(self, name: str = ""):
        """
        Initialize support component
        
        Args:
            name: Component identifier
        """
        self.name = name
        # Call validation after initialization
        self.validate()
    
    def validate(self) -> None:
        """
        Validate support component
        
        Base implementation validates name.
        Override in subclasses for additional validation.
        """
        if hasattr(self, 'name') and not isinstance(self.name, str):
            raise TypeError("Component name must be a string")
    
    def get_component_info(self) -> Dict[str, Any]:
        """
        Get basic component information
        
        Returns:
            Dictionary with component metadata
        """
        return {
            "type": self.__class__.__name__,
            "name": getattr(self, 'name', ''),
            "yaml_tag": getattr(self.__class__, 'yaml_tag', None)
        }
    
    def __repr__(self) -> str:
        """String representation showing component type and name"""
        return f"{self.__class__.__name__}(name='{getattr(self, 'name', '')}')"

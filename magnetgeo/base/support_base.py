import json
import yaml

from .serializable import SerializableBase
from typing import Dict, Any


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

    def get_component_info(self) -> Dict[str, Any]:
        """
        Get basic component information

        Returns:
            Dictionary with component metadata
        """
        return {
            "type": self.__class__.__name__,
            "name": getattr(self, "name", ""),
            "yaml_tag": getattr(self.__class__, "yaml_tag", None),
        }

    def __repr__(self) -> str:
        """String representation showing component type and name"""
        return f"{self.__class__.__name__}(name='{getattr(self, 'name', '')}')"

    # Add missing methods:
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False):
        """
        Create object from dictionary - must be implemented by subclasses

        Args:
            data: Dictionary containing object data
            debug: Whether to print debug information

        Returns:
            Created object instance
        """
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")

    def validate(self) -> None:
        """
        Validate support component

        Base implementation validates name.
        Override in subclasses for additional validation.
        """
        if hasattr(self, "name") and not isinstance(self.name, str):
            raise TypeError("Component name must be a string")

    def dump(self, name: str = None):
        """
        Dump object to YAML file (maintains backward compatibility)

        Args:
            name: Optional filename override
        """
        filename = name or self.name
        try:
            with open(f"{filename}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except Exception:
            raise Exception(f"Failed to dump {self.__class__.__name__} data")

    def to_json(self):
        """
        Convert to JSON string (maintains backward compatibility)

        Returns:
            JSON string representation
        """
        try:
            # Try to use existing deserialize module for compatibility
            from .. import deserialize

            return json.dumps(
                self, default=deserialize.serialize_instance, sort_keys=True, indent=4
            )
        except ImportError:
            # Fallback to standard JSON serialization
            return super().to_json()

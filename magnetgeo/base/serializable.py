import json
import yaml
from abc import ABC
from typing import Dict, Any, Optional, Type

class SerializableBase(ABC):
    """
    Base class providing common serialization functionality
    
    This class provides YAML/JSON serialization capabilities that are
    consistent across all magnetgeo components.
    """
    
    def dump(self, format: str = 'yaml') -> None:
        """
        Dump object to file in specified format
        
        Args:
            format: Output format ('yaml' or 'json')
        """
        filename = f"{self.name}.{format}"
        
        if format == 'yaml':
            with open(filename, "w") as f:
                yaml.dump(self, stream=f, default_flow_style=False)
        elif format == 'json':
            with open(filename, "w") as f:
                json.dump(self.to_dict(), f, indent=4, sort_keys=True)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_json(self) -> str:
        """
        Convert object to JSON string
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert object to dictionary for serialization
        
        Default implementation extracts public attributes.
        Override in subclasses for custom serialization.
        
        Returns:
            Dictionary representation of object
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'SerializableBase':
        """
        Create object from dictionary
        
        Must be implemented by subclasses.
        
        Args:
            data: Dictionary containing object data
            debug: Whether to print debug information
            
        Returns:
            Created object instance
        """
        raise NotImplementedError(f"{cls.__name__} must implement from_dict method")

    @classmethod
    def from_yaml_file(cls, filename: str, debug: bool = False) -> 'SerializableBase':
        """
        Create object from YAML file
        
        Args:
            filename: Path to YAML file
            debug: Whether to print debug information
            
        Returns:
            Created object instance
        """
        with open(filename, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        
        if debug:
            print(f"Loaded YAML data from {filename}: {data}")
        
        return cls.from_dict(data, debug)

    @classmethod
    def from_json_file(cls, filename: str, debug: bool = False) -> 'SerializableBase':
        """
        Create object from JSON file
        
        Args:
            filename: Path to JSON file
            debug: Whether to print debug information
            
        Returns:
            Created object instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if debug:
            print(f"Loaded JSON data from {filename}: {data}")
        
        return cls.from_dict(data, debug)

    def validate(self) -> None:
        """
        Validate object state
        
        Override in subclasses to add validation logic.
        Called automatically after object creation.
        """
        pass

    def __repr__(self) -> str:
        """
        String representation of object
        
        Default implementation shows class name and key attributes.
        Override in subclasses for custom representation.
        """
        class_name = self.__class__.__name__
        if hasattr(self, 'name'):
            return f"{class_name}(name='{self.name}')"
        return f"{class_name}()"

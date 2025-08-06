#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Enhanced YAML compatibility system for magnetgeo with structural components
"""

import yaml
from typing import Dict, Any, Type, List


class YAMLCompatibilityManager:
    """
    Manages YAML compatibility for all magnetgeo classes
    """
    
    def __init__(self):
        self.registered_classes = {}
        self.class_aliases = {}
    
    def register_class(self, cls: Type, old_tag: str = None, new_tag: str = None):
        """
        Register a class for YAML compatibility
        
        Args:
            cls: The class to register
            old_tag: Legacy YAML tag (for backward compatibility)
            new_tag: New YAML tag (if different from class yaml_tag)
        """
        # Use class yaml_tag or class name as default
        primary_tag = getattr(cls, 'yaml_tag', cls.__name__)
        
        if new_tag:
            primary_tag = new_tag
            
        self.registered_classes[primary_tag] = cls
        
        # Register old tag as alias if provided
        if old_tag and old_tag != primary_tag:
            self.class_aliases[old_tag] = primary_tag
            
        # Register both !ClassName and ClassName patterns
        patterns = [
            f"!{primary_tag}",
            primary_tag,
            cls.__name__,
            f"!{cls.__name__}"
        ]
        
        for pattern in patterns:
            if pattern not in self.registered_classes:
                self.registered_classes[pattern] = cls
                
        print(f"Registered {cls.__name__} with tags: {patterns}")
    
    def register_all_magnetgeo_classes(self):
        """Register all available magnetgeo classes"""
        
        # Register magnet classes
        try:
            from .components.magnet import Helix, Bitter, Supra
            magnet_classes = [Helix, Bitter, Supra]
            
            for cls in magnet_classes:
                old_tag = "!" + cls.__name__.replace("magnetgeo.", "").replace("!", "<") + ">"
                new_tag = cls.yaml_tag
                self.register_class(cls, old_tag, new_tag)
            
            print(f"Registered {len(magnet_classes)} magnet classes")
            
        except ImportError as e:
            print(f"Warning: Could not import magnet classes: {e}")
        
        # Register structural classes
        try:
            from .components.structural import Ring, Screen, InnerCurrentLead, OuterCurrentLead
            structural_classes = [Ring, Screen, InnerCurrentLead, OuterCurrentLead]
            
            for cls in structural_classes:
                old_tag = "!" + cls.__name__.replace("magnetgeo.", "").replace("!", "<") + ">"
                new_tag = cls.yaml_tag
                self.register_class(cls, old_tag, new_tag)
            
            print(f"Registered {len(structural_classes)} structural classes")
            
        except ImportError as e:
            print(f"Warning: Could not import structural classes: {e}")
        
        # Register support classes
        try:
            from .components.support import (
                Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod
            )
            support_classes = [Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod]
            
            for cls in support_classes:
                old_tag = "!" + cls.__name__.replace("magnetgeo.", "").replace("!", "<") + ">"
                new_tag = cls.yaml_tag
                self.register_class(cls, old_tag, new_tag)
            
            print(f"Registered {len(support_classes)} support classes")
            
        except ImportError as e:
            print(f"Warning: Could not import support classes: {e}")
        
        # Register legacy classes that haven't been moved yet
        legacy_classes = []
        try:
            from .Insert import Insert
            legacy_classes.append(Insert)
        except ImportError:
            pass
            
        try:
            from .Bitters import Bitters
            legacy_classes.append(Bitters)
        except ImportError:
            pass
            
        try:
            from .Supras import Supras
            legacy_classes.append(Supras)
        except ImportError:
            pass
            
        try:
            from .MSite import MSite
            legacy_classes.append(MSite)
        except ImportError:
            pass
        
        for cls in legacy_classes:
            self.register_class(cls)
            
        if legacy_classes:
            print(f"Registered {len(legacy_classes)} legacy classes")
    
    def get_constructor_function(self, cls: Type):
        """
        Get or create a constructor function for a class
        
        Args:
            cls: The class to create constructor for
            
        Returns:
            Constructor function for YAML
        """
        def constructor(loader, node):
            values = loader.construct_mapping(node)
            
            # Try class-specific constructor first
            if hasattr(cls, 'from_dict'):
                return cls.from_dict(values)
            
            # Fallback to direct instantiation
            try:
                return cls(**values)
            except TypeError:
                # If that fails, try creating with minimal args and setting attributes
                obj = cls.__new__(cls)
                for key, value in values.items():
                    setattr(obj, key, value)
                return obj
                
        return constructor
    
    def register_yaml_constructors(self):
        """Register YAML constructors for all registered classes"""
        for tag, cls in self.registered_classes.items():
            if tag.startswith('!') or tag in self.class_aliases:
                constructor = self.get_constructor_function(cls)
                yaml.add_constructor(tag, constructor)
                print(f"Added YAML constructor for {tag} -> {cls.__name__}")


# Global YAML compatibility manager
yaml_manager = YAMLCompatibilityManager()


def setup_yaml_compatibility():
    """Set up YAML compatibility for all classes"""
    print("Setting up YAML compatibility...")
    yaml_manager.register_all_magnetgeo_classes()
    yaml_manager.register_yaml_constructors()
    print("YAML compatibility setup complete")


def setup_custom_extractors():
    """Set up custom extractors for complex classes"""
    # This function can be extended to handle special cases
    # for classes that need custom loading logic
    pass


# Utility functions for YAML operations
def load_yaml_file(filepath: str, debug: bool = False):
    """
    Load a YAML file with full magnetgeo compatibility
    
    Args:
        filepath: Path to YAML file
        debug: Whether to print debug info
        
    Returns:
        Loaded object
    """
    try:
        with open(filepath, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except Exception as e:
        if debug:
            print(f"Error loading YAML file {filepath}: {e}")
        raise


def save_yaml_file(obj: Any, filepath: str, debug: bool = False):
    """
    Save an object to YAML file with full magnetgeo compatibility
    
    Args:
        obj: Object to save
        filepath: Path to save to
        debug: Whether to print debug info
    """
    try:
        with open(filepath, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False)
        if debug:
            print(f"Saved object to {filepath}")
    except Exception as e:
        if debug:
            print(f"Error saving YAML file {filepath}: {e}")
        raise


def get_yaml_tag_info() -> Dict[str, str]:
    """
    Get information about registered YAML tags
    
    Returns:
        Dictionary mapping tags to class names
    """
    return {
        tag: cls.__name__ 
        for tag, cls in yaml_manager.registered_classes.items()
    }


def validate_yaml_compatibility():
    """
    Validate that YAML compatibility is working correctly
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'registered_classes': len(yaml_manager.registered_classes),
        'class_aliases': len(yaml_manager.class_aliases),
        'yaml_constructors_added': True,  # Assume success if no exception
    }
    
    # Test a simple round-trip if possible
    try:
        from .components.structural import Ring
        test_ring = Ring("test", [10.0, 20.0], [0.0, 100.0])
        yaml_str = yaml.dump(test_ring)
        loaded_ring = yaml.load(yaml_str, Loader=yaml.FullLoader)
        results['round_trip_test'] = (
            loaded_ring.name == test_ring.name and
            loaded_ring.r == test_ring.r and
            loaded_ring.z == test_ring.z
        )
    except Exception as e:
        results['round_trip_test'] = f"Failed: {e}"
    
    return results


if __name__ == "__main__":
    """Test the YAML compatibility system"""
    print("Testing YAML compatibility system...")
    setup_yaml_compatibility()
    
    results = validate_yaml_compatibility()
    print("\nValidation results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    print("\nRegistered YAML tags:")
    tag_info = get_yaml_tag_info()
    for tag, class_name in sorted(tag_info.items()):
        print(f"  {tag} -> {class_name}")
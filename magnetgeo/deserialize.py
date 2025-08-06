#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Enhanced deserialization tools for magnetgeo with structural components
"""

import json
from typing import Dict, Any, Type

# Import classes from new structure
try:
    from .components.magnet import Helix, Bitter, Supra
    MAGNET_CLASSES = [Helix, Bitter, Supra]
except ImportError:
    MAGNET_CLASSES = []

try:
    from .components.structural import Ring, Screen, InnerCurrentLead, OuterCurrentLead
    STRUCTURAL_CLASSES = [Ring, Screen, InnerCurrentLead, OuterCurrentLead]
except ImportError:
    STRUCTURAL_CLASSES = []

try:
    from .components.support import Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod
    SUPPORT_CLASSES = [Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod]
except ImportError:
    SUPPORT_CLASSES = []

# Import legacy classes that haven't been moved yet
LEGACY_CLASSES = []
try:
    from .Insert import Insert
    LEGACY_CLASSES.append(Insert)
except ImportError:
    pass

try:
    from .Bitters import Bitters
    LEGACY_CLASSES.append(Bitters)
except ImportError:
    pass

try:
    from .Supras import Supras
    LEGACY_CLASSES.append(Supras)
except ImportError:
    pass

try:
    from .MSite import MSite
    LEGACY_CLASSES.append(MSite)
except ImportError:
    pass

try:
    from .Shape import Shape
    LEGACY_CLASSES.append(Shape)
except ImportError:
    pass

try:
    from .Shape2D import Shape2D
    LEGACY_CLASSES.append(Shape2D)
except ImportError:
    pass

# Build comprehensive class registry
ALL_CLASSES = MAGNET_CLASSES + STRUCTURAL_CLASSES + SUPPORT_CLASSES + LEGACY_CLASSES

# Create class lookup dictionary
classes = {}
for cls in ALL_CLASSES:
    if cls is not None:
        # Register by class name
        classes[cls.__name__] = cls
        
        # Register by yaml_tag if available
        if hasattr(cls, 'yaml_tag'):
            classes[cls.yaml_tag] = cls

# Print registration status
if __name__ != "__main__":  # Only print when imported, not when run directly
    print(f"Deserialize: Registered {len(classes)} class mappings")
    print(f"  Magnet classes: {len([c for c in MAGNET_CLASSES if c is not None])}")
    print(f"  Structural classes: {len([c for c in STRUCTURAL_CLASSES if c is not None])}")
    print(f"  Support classes: {len([c for c in SUPPORT_CLASSES if c is not None])}")
    print(f"  Legacy classes: {len([c for c in LEGACY_CLASSES if c is not None])}")


def serialize_instance(obj: Any) -> Dict[str, Any]:
    """
    Serialize an object instance to dictionary
    
    Args:
        obj: Object to serialize
        
    Returns:
        Dictionary with class name and object attributes
    """
    d = {"__classname__": type(obj).__name__}
    d.update(vars(obj))
    return d


def unserialize_object(d: Dict[str, Any], debug: bool = False) -> Any:
    """
    Unserialize an object from dictionary
    
    Args:
        d: Dictionary containing object data
        debug: Whether to print debug information
        
    Returns:
        Unserialized object or original dictionary if no class found
    """
    if debug:
        print(f"unserialize_object: d={d}", flush=True)

    # Remove class name from dictionary
    clsname = d.pop("__classname__", None)
    
    if debug:
        print(f"clsname: {clsname}", flush=True)
        
    if clsname:
        cls = classes.get(clsname)
        
        if cls is None:
            if debug:
                print(f"Warning: Unknown class {clsname}, available classes: {list(classes.keys())}")
            # Return the dictionary as-is if class not found
            d["__classname__"] = clsname  # Restore the classname
            return d
        
        try:
            # Try to create object using from_dict method if available
            if hasattr(cls, 'from_dict'):
                if debug:
                    print(f"Using from_dict for {clsname}")
                obj = cls.from_dict(d, debug=debug)
            else:
                # Create instance without calling __init__
                obj = cls.__new__(cls)
                
                # Set attributes, converting keys to lowercase for compatibility
                for key, value in d.items():
                    if debug:
                        print(f"key={key}, value={value} type={type(value)}", flush=True)
                    setattr(obj, key.lower(), value)
                    
        except Exception as e:
            if debug:
                print(f"Error creating {clsname}: {e}")
            # Fallback: return dictionary with classname
            d["__classname__"] = clsname
            return d
            
        if debug:
            print(f"obj={obj}", flush=True)
        return obj
    else:
        if debug:
            print(f"no classname: {d}", flush=True)
        return d


def load_json_file(filename: str, debug: bool = False) -> Any:
    """
    Load an object from JSON file
    
    Args:
        filename: Path to JSON file
        debug: Whether to print debug information
        
    Returns:
        Loaded object
    """
    try:
        with open(filename, "r") as istream:
            return json.loads(
                istream.read(), 
                object_hook=lambda d: unserialize_object(d, debug=debug)
            )
    except Exception as e:
        if debug:
            print(f"Error loading JSON file {filename}: {e}")
        raise


def save_json_file(obj: Any, filename: str, debug: bool = False) -> None:
    """
    Save an object to JSON file
    
    Args:
        obj: Object to save
        filename: Path to save to
        debug: Whether to print debug information
    """
    try:
        with open(filename, "w") as ostream:
            json.dump(
                obj, 
                ostream, 
                default=serialize_instance, 
                sort_keys=True, 
                indent=4
            )
        if debug:
            print(f"Saved object to {filename}")
    except Exception as e:
        if debug:
            print(f"Error saving JSON file {filename}: {e}")
        raise


def get_registered_classes() -> Dict[str, Type]:
    """
    Get dictionary of all registered classes
    
    Returns:
        Dictionary mapping class names to class objects
    """
    return classes.copy()


def register_class(cls: Type, name: str = None) -> None:
    """
    Register a new class for deserialization
    
    Args:
        cls: Class to register
        name: Optional name override (uses cls.__name__ if not provided)
    """
    class_name = name or cls.__name__
    classes[class_name] = cls
    
    # Also register by yaml_tag if available
    if hasattr(cls, 'yaml_tag'):
        classes[cls.yaml_tag] = cls
    
    print(f"Registered class {class_name} -> {cls}")


def unregister_class(name: str) -> bool:
    """
    Unregister a class from deserialization
    
    Args:
        name: Class name to unregister
        
    Returns:
        True if class was found and removed, False otherwise
    """
    if name in classes:
        del classes[name]
        print(f"Unregistered class {name}")
        return True
    return False


def validate_deserialization():
    """
    Validate that deserialization is working correctly
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'registered_classes': len(classes),
        'test_results': {}
    }
    
    # Test each registered class if possible
    for class_name, cls in classes.items():
        if class_name == cls.__name__:  # Only test primary registrations
            try:
                # Create a simple test instance
                if cls.__name__ == 'Ring':
                    test_obj = cls("test_ring", [10.0, 20.0], [0.0, 100.0])
                elif cls.__name__ == 'Screen':
                    test_obj = cls("test_screen", [10.0, 20.0], [0.0, 100.0])
                elif cls.__name__ == 'InnerCurrentLead':
                    test_obj = cls("test_inner", [10.0, 20.0], 100.0)
                elif cls.__name__ == 'OuterCurrentLead':
                    test_obj = cls("test_outer", [10.0, 20.0], 100.0)
                else:
                    # Skip classes that need complex initialization
                    results['test_results'][class_name] = 'skipped'
                    continue
                
                # Test serialization round-trip
                serialized = serialize_instance(test_obj)
                unserialized = unserialize_object(serialized.copy())
                
                # Basic validation
                success = (
                    type(unserialized).__name__ == class_name and
                    hasattr(unserialized, 'name') and
                    unserialized.name == test_obj.name
                )
                
                results['test_results'][class_name] = 'pass' if success else 'fail'
                
            except Exception as e:
                results['test_results'][class_name] = f'error: {e}'
    
    return results


if __name__ == "__main__":
    """Test the deserialization system"""
    print("Testing deserialization system...")
    print(f"Total registered classes: {len(classes)}")
    
    print("\nRegistered classes:")
    for name, cls in sorted(classes.items()):
        print(f"  {name} -> {cls.__name__}")
    
    print("\nRunning validation tests...")
    results = validate_deserialization()
    
    print(f"\nValidation Summary:")
    print(f"  Registered classes: {results['registered_classes']}")
    print(f"  Test results:")
    for class_name, result in results['test_results'].items():
        print(f"    {class_name}: {result}")

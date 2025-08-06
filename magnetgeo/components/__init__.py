#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
MagnetGeo Components Package - Updated Structure

This package contains all magnet component classes organized by type:
- magnet: Main magnetic field-generating components (Helix, Bitter, Supra)
- support: Support/auxiliary components (Chamfer, Groove, ModelAxi, etc.)
- container: Container components (Insert, Bitters, Supras, MSite) [future]
- structural: Structural components (Ring, Screen, CurrentLeads) [future]
"""

# Import main magnet components from new location
try:
    from .magnet import Helix, Bitter, Supra
    MAGNET_COMPONENTS_AVAILABLE = True
except ImportError:
    MAGNET_COMPONENTS_AVAILABLE = False
    Helix = Bitter = Supra = None

# Import support components
try:
    from . import support
    SUPPORT_COMPONENTS_AVAILABLE = True
except ImportError:
    SUPPORT_COMPONENTS_AVAILABLE = False
    support = None

# Future imports (placeholder for upcoming migrations)
# from . import container
# from . import structural

__all__ = []

# Add main magnet components if available
if MAGNET_COMPONENTS_AVAILABLE:
    __all__.extend(['Helix', 'Bitter', 'Supra'])

# Add support module if available
if SUPPORT_COMPONENTS_AVAILABLE:
    __all__.append('support')

# Version info
__version__ = "0.2.0"  # Updated for new structure
__author__ = "MagnetGeo Development Team"

# Component registry for dynamic loading
COMPONENT_REGISTRY = {}

if MAGNET_COMPONENTS_AVAILABLE:
    COMPONENT_REGISTRY.update({
        "Helix": Helix,
        "Bitter": Bitter,
        "Supra": Supra,
    })

# Add support components to registry
if SUPPORT_COMPONENTS_AVAILABLE and hasattr(support, 'SUPPORT_CLASSES'):
    COMPONENT_REGISTRY.update(support.SUPPORT_CLASSES)


def get_component_class(class_name: str):
    """
    Get component class by name
    
    Args:
        class_name: Name of the component class
        
    Returns:
        Component class or None if not found
    """
    return COMPONENT_REGISTRY.get(class_name)


def list_available_components():
    """
    List all available component classes
    
    Returns:
        Dictionary with component categories and their classes
    """
    categories = {}
    
    if MAGNET_COMPONENTS_AVAILABLE:
        categories["magnet"] = ["Helix", "Bitter", "Supra"]
    
    if SUPPORT_COMPONENTS_AVAILABLE and hasattr(support, 'list_support_classes'):
        categories["support"] = support.list_support_classes()
    
    return categories


def create_component(class_name: str, data: dict, debug: bool = False):
    """
    Create component object from class name and data
    
    Args:
        class_name: Name of the component class
        data: Dictionary with component parameters
        debug: Whether to print debug info
        
    Returns:
        Created component object or None if class not found
    """
    cls = get_component_class(class_name)
    if cls and hasattr(cls, 'from_dict'):
        return cls.from_dict(data, debug=debug)
    elif cls:
        try:
            return cls(**data)
        except Exception as e:
            if debug:
                print(f"Failed to create {class_name}: {e}")
            return None
    
    if debug:
        print(f"Class {class_name} not found in registry")
    return None


def get_package_status():
    """
    Get comprehensive package status
    
    Returns:
        Dictionary with package information
    """
    status = {
        "version": __version__,
        "magnet_components": MAGNET_COMPONENTS_AVAILABLE,
        "support_components": SUPPORT_COMPONENTS_AVAILABLE,
        "total_classes": len(COMPONENT_REGISTRY),
        "available_categories": list(list_available_components().keys()),
    }
    
    if MAGNET_COMPONENTS_AVAILABLE:
        status["magnet_classes"] = ["Helix", "Bitter", "Supra"]
    
    if SUPPORT_COMPONENTS_AVAILABLE:
        try:
            status["support_classes"] = support.list_support_classes()
        except:
            status["support_classes"] = []
    
    return status


def print_package_status():
    """Print detailed package status"""
    status = get_package_status()
    
    print(f"MagnetGeo Components v{status['version']}")
    print("=" * 40)
    
    categories = list_available_components()
    
    for category, classes in categories.items():
        print(f"\n{category.title()} Components: {len(classes)} available")
        for cls in classes:
            availability = "✓" if get_component_class(cls) else "✗"
            print(f"  {availability} {cls}")
    
    print(f"\nTotal Classes: {status['total_classes']}")
    print(f"Categories: {', '.join(status['available_categories'])}")
    
    # Migration status
    if MAGNET_COMPONENTS_AVAILABLE and SUPPORT_COMPONENTS_AVAILABLE:
        print("\n✅ All component types available")
    elif MAGNET_COMPONENTS_AVAILABLE:
        print("\n⚠️  Magnet components available, support components missing")
    elif SUPPORT_COMPONENTS_AVAILABLE:
        print("\n⚠️  Support components available, magnet components missing") 
    else:
        print("\n❌ No components available")


def validate_component_structure():
    """
    Validate the component package structure
    
    Returns:
        Tuple of (is_valid, issues_list)
    """
    issues = []
    
    # Check main magnet components
    expected_magnet_classes = ["Helix", "Bitter", "Supra"]
    if MAGNET_COMPONENTS_AVAILABLE:
        for cls_name in expected_magnet_classes:
            cls = get_component_class(cls_name)
            if cls is None:
                issues.append(f"Magnet class {cls_name} not available")
            else:
                # Test basic functionality
                try:
                    if not hasattr(cls, '__init__'):
                        issues.append(f"{cls_name} missing __init__ method")
                    if not hasattr(cls, 'from_dict'):
                        issues.append(f"{cls_name} missing from_dict class method")
                except Exception as e:
                    issues.append(f"{cls_name} validation error: {e}")
    else:
        issues.append("Magnet components package not available")
    
    # Check support components
    if SUPPORT_COMPONENTS_AVAILABLE:
        try:
            expected_support_classes = ["Chamfer", "Groove", "ModelAxi", "Model3D"]
            for cls_name in expected_support_classes:
                if hasattr(support, 'get_support_class'):
                    cls = support.get_support_class(cls_name)
                    if cls is None:
                        issues.append(f"Support class {cls_name} not available")
        except Exception as e:
            issues.append(f"Support components validation error: {e}")
    else:
        issues.append("Support components package not available")
    
    is_valid = len(issues) == 0
    return (is_valid, issues)


def run_component_diagnostics():
    """Run comprehensive component diagnostics"""
    print("Running MagnetGeo Components Diagnostics...")
    print("=" * 50)
    
    # Package status
    print_package_status()
    
    # Structure validation
    print("\nStructure Validation:")
    print("-" * 25)
    is_valid, issues = validate_component_structure()
    
    if is_valid:
        print("✅ Component structure validation passed")
    else:
        print("❌ Component structure validation failed:")
        for issue in issues:
            print(f"  • {issue}")
    
    # Component creation test
    print("\nComponent Creation Test:")
    print("-" * 25)
    
    test_passed = True
    
    if MAGNET_COMPONENTS_AVAILABLE:
        try:
            # Test creating a simple helix
            test_data = {
                "name": "test_helix",
                "r": [10.0, 20.0],
                "z": [-5.0, 5.0],
                "cutwidth": 0.2,
                "odd": True,
                "dble": True,
                "modelaxi": None,
                "model3d": None,
                "shape": None,
            }
            helix = create_component("Helix", test_data, debug=False)
            if helix and helix.name == "test_helix":
                print("✅ Helix creation test passed")
            else:
                print("❌ Helix creation test failed")
                test_passed = False
        except Exception as e:
            print(f"❌ Helix creation test failed: {e}")
            test_passed = False
    
    if SUPPORT_COMPONENTS_AVAILABLE:
        try:
            # Test creating a support component
            if hasattr(support, 'create_support_object'):
                test_data = {"cad": "test", "with_shapes": False, "with_channels": False}
                model3d = support.create_support_object("Model3D", test_data)
                if model3d:
                    print("✅ Support component creation test passed")
                else:
                    print("❌ Support component creation test failed")
                    test_passed = False
        except Exception as e:
            print(f"❌ Support component creation test failed: {e}")
            test_passed = False
    
    overall_status = "HEALTHY" if is_valid and test_passed else "NEEDS ATTENTION"
    print(f"\nOverall Status: {overall_status}")
    
    return is_valid and test_passed


# Convenience functions for backward compatibility
def import_from_old_location(class_name: str):
    """
    Import class from old location with deprecation warning
    
    Args:
        class_name: Name of class to import
        
    Returns:
        Class or None if not found
    """
    import warnings
    
    warnings.warn(
        f"Importing {class_name} from old location is deprecated. "
        f"Use 'from magnetgeo.components.magnet import {class_name}' instead.",
        DeprecationWarning,
        stacklevel=3
    )
    
    return get_component_class(class_name)


if __name__ == "__main__":
    # If run as script, show full diagnostics
    run_component_diagnostics()
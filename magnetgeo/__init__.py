#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Python Magnet Geometry package with new component architecture

This version includes the refactored component structure:
- magnetgeo.components.magnet: Main magnet classes (Helix, Bitter, Supra)
- magnetgeo.components.support: Support components with validation
- Legacy classes still available at root level for backward compatibility
"""

import os
import warnings

# Package metadata
__version__ = "0.5.0"  # Major update for new component structure
__author__ = "Christophe Trophime, Romain Vallet, Jeremie Muzet"
__email__ = "christophe.trophime@lncmi.cnrs.fr"

# Import main magnet classes from new location
try:
    from .components.magnet import Helix, Bitter, Supra
    NEW_MAGNET_STRUCTURE = True
    print("✓ Using new magnet component structure")
except ImportError:
    # Fallback to old imports for transition
    try:
        from .Helix import Helix
        from .Bitter import Bitter
        from .Supra import Supra
        NEW_MAGNET_STRUCTURE = False
        print("⚠ Using legacy magnet classes (consider upgrading)")
    except ImportError:
        Helix = Bitter = Supra = None
        NEW_MAGNET_STRUCTURE = False
        print("✗ Magnet classes not available")

# Import remaining classes (not yet moved)
LEGACY_CLASSES = {}
try:
    from .Insert import Insert
    LEGACY_CLASSES['Insert'] = Insert
except ImportError:
    Insert = None

try:
    from .Bitters import Bitters
    LEGACY_CLASSES['Bitters'] = Bitters
except ImportError:
    Bitters = None

try:
    from .Supras import Supras
    LEGACY_CLASSES['Supras'] = Supras
except ImportError:
    Supras = None

try:
    from .MSite import MSite
    LEGACY_CLASSES['MSite'] = MSite
except ImportError:
    MSite = None

try:
    from .Ring import Ring
    LEGACY_CLASSES['Ring'] = Ring
except ImportError:
    Ring = None

try:
    from .Screen import Screen
    LEGACY_CLASSES['Screen'] = Screen
except ImportError:
    Screen = None

try:
    from .InnerCurrentLead import InnerCurrentLead
    LEGACY_CLASSES['InnerCurrentLead'] = InnerCurrentLead
except ImportError:
    InnerCurrentLead = None

try:
    from .OuterCurrentLead import OuterCurrentLead
    LEGACY_CLASSES['OuterCurrentLead'] = OuterCurrentLead
except ImportError:
    OuterCurrentLead = None

# Import support classes from new location
try:
    from .components import support
    NEW_SUPPORT_STRUCTURE = True
    print("✓ Using new support component structure")
    
    # Make support classes available at root level for convenience
    try:
        from .components.support import (
            Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod, Shape, Shape2D
        )
    except ImportError:
        # Partial support import
        Chamfer = Groove = Model3D = ModelAxi = None
        CoolingSlit = Tierod = Shape = Shape2D = None
        
except ImportError:
    # Fallback to old support imports
    try:
        from .backward_compatibility import (
            Chamfer, Groove, Model3D, ModelAxi, CoolingSlit, Tierod, Shape, Shape2D
        )
        NEW_SUPPORT_STRUCTURE = False
        support = None
        print("⚠ Using backward compatibility support components")
    except ImportError:
        # Final fallback to old individual imports
        support = None
        NEW_SUPPORT_STRUCTURE = False
        try:
            from .Chamfer import Chamfer
            from .Groove import Groove
            from .Model3D import Model3D
            from .ModelAxi import ModelAxi
            from .coolingslit import CoolingSlit
            from .tierod import Tierod
            from .Shape import Shape
            from .Shape2D import Shape2D
            print("⚠ Using legacy support components")
        except ImportError:
            Chamfer = Groove = Model3D = ModelAxi = None
            CoolingSlit = Tierod = Shape = Shape2D = None
            print("✗ Support components not available")

# Import utilities if available
try:
    from .utils import validation, enums
    UTILS_AVAILABLE = True
    print("✓ Validation and type safety utilities available")
except ImportError:
    validation = enums = None
    UTILS_AVAILABLE = False

# Import and setup YAML compatibility system
try:
    from .generic_yaml_compatibility import setup_yaml_compatibility, setup_custom_extractors
    setup_yaml_compatibility()
    setup_custom_extractors()
    print("✓ YAML compatibility system initialized")
except ImportError:
    print("⚠ YAML compatibility system not available")

# Main exports
__all__ = []

# Add main magnet classes
magnet_classes = []
if Helix:
    magnet_classes.append('Helix')
if Bitter:
    magnet_classes.append('Bitter')
if Supra:
    magnet_classes.append('Supra')
__all__.extend(magnet_classes)

# Add legacy classes that are available
legacy_available = [name for name, cls in LEGACY_CLASSES.items() if cls is not None]
__all__.extend(legacy_available)

# Add support classes if available
support_classes = []
if Chamfer:
    support_classes.extend(['Chamfer', 'Groove', 'Model3D', 'ModelAxi'])
if CoolingSlit:
    support_classes.extend(['CoolingSlit', 'Tierod', 'Shape', 'Shape2D'])
__all__.extend(support_classes)

# Add utilities if available
if UTILS_AVAILABLE:
    __all__.extend(['validation', 'enums'])

# Add support module if available
if support:
    __all__.append('support')


def get_package_info():
    """
    Get comprehensive package information
    
    Returns:
        Dictionary with package status and capabilities
    """
    info = {
        "version": __version__,
        "new_magnet_structure": NEW_MAGNET_STRUCTURE,
        "new_support_structure": NEW_SUPPORT_STRUCTURE,
        "validation_utils": UTILS_AVAILABLE,
        "total_classes": len(__all__),
    }
    
    if magnet_classes:
        info["magnet_classes"] = magnet_classes
    
    if legacy_available:
        info["legacy_classes"] = legacy_available
    
    if support_classes:
        info["support_classes"] = support_classes
    
    if UTILS_AVAILABLE:
        info["utilities"] = ['validation', 'enums']
    
    return info


def print_package_status():
    """Print current package status and migration progress"""
    print(f"Python MagnetGeo v{__version__}")
    print("=" * 50)
    
    info = get_package_info()
    
    # Magnet components status
    if info.get('magnet_classes'):
        structure_type = "New Structure" if NEW_MAGNET_STRUCTURE else "Legacy"
        print(f"Magnet Classes ({structure_type}): {len(info['magnet_classes'])} available")
        for cls in info['magnet_classes']:
            print(f"  ✓ {cls}")
    else:
        print("Magnet Classes: Not available")
    
    # Legacy classes status  
    if info.get('legacy_classes'):
        print(f"\nLegacy Classes: {len(info['legacy_classes'])} available")
        for cls in info['legacy_classes']:
            print(f"  ✓ {cls}")
    
    # Support components status
    if info.get('support_classes'):
        structure_type = "New Structure" if NEW_SUPPORT_STRUCTURE else "Legacy"
        print(f"\nSupport Components ({structure_type}): {len(info['support_classes'])} available")
        for cls in info['support_classes']:
            print(f"  ✓ {cls}")
    else:
        print("\nSupport Components: Not available")
    
    # Utilities status
    if info.get('utilities'):
        print(f"\nUtilities: {len(info['utilities'])} available")
        for util in info['utilities']:
            print(f"  ✓ {util}")
    else:
        print("\nUtilities: Not available")
    
    # Architecture status
    print(f"\nArchitecture Status:")
    print(f"  {'✓' if NEW_MAGNET_STRUCTURE else '⚠'} New magnet component structure")
    print(f"  {'✓' if NEW_SUPPORT_STRUCTURE else '⚠'} New support component structure")
    print(f"  {'✓' if UTILS_AVAILABLE else '⚠'} Enhanced validation utilities")
    
    # Overall status
    if NEW_MAGNET_STRUCTURE and NEW_SUPPORT_STRUCTURE and UTILS_AVAILABLE:
        print(f"\n🎉 All new architecture features available!")
    elif NEW_MAGNET_STRUCTURE or NEW_SUPPORT_STRUCTURE or UTILS_AVAILABLE:
        print(f"\n📈 Migration in progress...")
    else:
        print(f"\n📋 Using legacy architecture")


def validate_installation():
    """
    Validate that the package is properly installed and configured
    
    Returns:
        Tuple of (is_valid, issues_list)
    """
    issues = []
    
    # Check main magnet classes
    required_magnet_classes = ['Helix', 'Bitter', 'Supra']
    for cls_name in required_magnet_classes:
        cls = globals().get(cls_name)
        if cls is None:
            issues.append(f"Main magnet class {cls_name} not available")
    
    # Check YAML loading
    try:
        import yaml
        test_data = {"name": "test", "r": [1, 2], "z": [0, 1]}
        yaml_str = yaml.dump(test_data)
        loaded = yaml.load(yaml_str, Loader=yaml.SafeLoader)
        if loaded != test_data:
            issues.append("YAML serialization not working correctly")
    except Exception as e:
        issues.append(f"YAML support issue: {e}")
    
    # Check new component structure if available
    if NEW_MAGNET_STRUCTURE:
        try:
            from .components.magnet import get_magnet_class
            if get_magnet_class("Helix") is None:
                issues.append("New magnet structure not working correctly")
        except Exception as e:
            issues.append(f"New magnet structure issue: {e}")
    
    if NEW_SUPPORT_STRUCTURE:
        try:
            from .components.support import get_support_class
            if get_support_class("Model3D") is None:
                issues.append("New support structure not working correctly")
        except Exception as e:
            issues.append(f"New support structure issue: {e}")
    
    # Check validation utilities if available
    if UTILS_AVAILABLE:
        try:
            from .utils.validation import validate_positive
            validate_positive(1.0, "test")  # Should not raise
        except Exception as e:
            issues.append(f"Validation utilities issue: {e}")
    
    is_valid = len(issues) == 0
    return (is_valid, issues)


def run_diagnostics():
    """Run comprehensive package diagnostics"""
    print("Running MagnetGeo Package Diagnostics...")
    print("=" * 60)
    
    # Package status  
    print_package_status()
    
    # Component diagnostics if available
    if NEW_MAGNET_STRUCTURE or NEW_SUPPORT_STRUCTURE:
        print("\nComponent Structure Diagnostics:")
        print("-" * 35)
        try:
            from .components import run_component_diagnostics
            run_component_diagnostics()
        except ImportError:
            print("Component diagnostics not available")
    
    # Installation validation
    print("\nInstallation Validation:")
    print("-" * 25)
    is_valid, issues = validate_installation()
    
    if is_valid:
        print("✅ Package validation passed - all systems operational")
    else:
        print("❌ Package validation failed with issues:")
        for issue in issues:
            print(f"  • {issue}")
    
    # Migration recommendations
    print("\nMigration Recommendations:")
    print("-" * 30)
    
    if not NEW_MAGNET_STRUCTURE:
        print("📈 Consider migrating to new magnet component structure:")
        print("   from magnetgeo.components.magnet import Helix, Bitter, Supra")
    
    if not NEW_SUPPORT_STRUCTURE:
        print("📈 Consider migrating to new support component structure:")
        print("   from magnetgeo.components.support import Chamfer, Groove, ...")
    
    if not UTILS_AVAILABLE:
        print("📈 Consider adding validation utilities for enhanced error checking")
    
    if NEW_MAGNET_STRUCTURE and NEW_SUPPORT_STRUCTURE and UTILS_AVAILABLE:
        print("🎉 No migration needed - using latest architecture!")
    
    status = "HEALTHY" if is_valid else "NEEDS ATTENTION"
    print(f"\nOverall Package Status: {status}")
    return is_valid


# Convenience functions for users
def create_helix(name, r, z, **kwargs):
    """
    Convenience function to create a Helix with validation
    
    Args:
        name: Helix name
        r: Radial bounds [r_min, r_max]
        z: Axial bounds [z_min, z_max]
        **kwargs: Additional helix parameters
        
    Returns:
        Helix instance
    """
    if not Helix:
        raise ImportError("Helix class not available")
    
    # Set defaults for required parameters
    defaults = {
        'cutwidth': 0.2,
        'odd': True,
        'dble': True,
        'modelaxi': ModelAxi() if ModelAxi else None,
        'model3d': Model3D(cad="default") if Model3D else None,
        'shape': Shape("", "") if Shape else None,
    }
    
    # Merge with user-provided parameters
    for key, default_value in defaults.items():
        if key not in kwargs:
            kwargs[key] = default_value
    
    return Helix(name, r, z, **kwargs)


def create_bitter(name, r, z, **kwargs):
    """
    Convenience function to create a Bitter magnet with validation
    
    Args:
        name: Bitter magnet name
        r: Radial bounds [r_min, r_max]  
        z: Axial bounds [z_min, z_max]
        **kwargs: Additional bitter parameters
        
    Returns:
        Bitter instance
    """
    if not Bitter:
        raise ImportError("Bitter class not available")
    
    # Set defaults for required parameters
    defaults = {
        'odd': True,
        'modelaxi': ModelAxi() if ModelAxi else None,
        'coolingslits': [],
        'tierod': None,
        'innerbore': r[0] * 0.8 if r else 0,
        'outerbore': r[1] * 1.2 if r else 0,
    }
    
    # Merge with user-provided parameters
    for key, default_value in defaults.items():
        if key not in kwargs:
            kwargs[key] = default_value
    
    return Bitter(name, r, z, **kwargs)


def create_supra(name, r, z, **kwargs):
    """
    Convenience function to create a Supra magnet with validation
    
    Args:
        name: Supra magnet name
        r: Radial bounds [r_min, r_max]
        z: Axial bounds [z_min, z_max]
        **kwargs: Additional supra parameters
        
    Returns:
        Supra instance
    """
    if not Supra:
        raise ImportError("Supra class not available")
    
    # Set defaults for required parameters
    defaults = {
        'n': 0,
        'struct': "",
    }
    
    # Merge with user-provided parameters
    for key, default_value in defaults.items():
        if key not in kwargs:
            kwargs[key] = default_value
    
    return Supra(name, r, z, **kwargs)


# Backward compatibility helpers
def get_class_by_name(class_name: str):
    """
    Get class by name with deprecation warning for old usage patterns
    
    Args:
        class_name: Name of class to retrieve
        
    Returns:
        Class object or None if not found
    """
    # Check if it's available in globals
    cls = globals().get(class_name)
    if cls:
        return cls
    
    # Try new component structure
    if NEW_MAGNET_STRUCTURE:
        try:
            from .components.magnet import get_magnet_class
            cls = get_magnet_class(class_name)
            if cls:
                return cls
        except ImportError:
            pass
    
    if NEW_SUPPORT_STRUCTURE:
        try:
            from .components.support import get_support_class  
            cls = get_support_class(class_name)
            if cls:
                return cls
        except ImportError:
            pass
    
    return None


def check_compatibility():
    """Check if package is compatible with older magnetgeo code"""
    required_classes = ['Helix', 'Bitter', 'Supra', 'Insert', 'Ring']
    missing = []
    
    for cls_name in required_classes:
        if cls_name not in globals() or globals()[cls_name] is None:
            missing.append(cls_name)
    
    if missing:
        print(f"⚠ Compatibility issue: Missing classes {missing}")
        return False
    
    print("✅ Backward compatibility confirmed")
    return True


# Show status on import (can be disabled by setting environment variable)
if os.environ.get('MAGNETGEO_SHOW_STATUS', '1') == '1':
    print(f"Python MagnetGeo v{__version__} loaded")
    
    if NEW_MAGNET_STRUCTURE and NEW_SUPPORT_STRUCTURE and UTILS_AVAILABLE:
        print("🎉 All new architecture features available")
    elif NEW_MAGNET_STRUCTURE and NEW_SUPPORT_STRUCTURE:
        print("✅ New component architecture available")
    elif NEW_MAGNET_STRUCTURE or NEW_SUPPORT_STRUCTURE:
        print("📈 Partial migration to new architecture")
    else:
        print("📋 Using legacy architecture")


# Deprecation warnings for old import patterns
def _warn_old_import(old_path: str, new_path: str):
    """Issue deprecation warning for old import patterns"""
    warnings.warn(
        f"Importing from '{old_path}' is deprecated. Use '{new_path}' instead.",
        DeprecationWarning,
        stacklevel=3
    )


# Override __getattr__ to provide deprecation warnings for direct imports
def __getattr__(name: str):
    """Handle attribute access with deprecation warnings"""
    
    # Check if it's a magnet class that should use new import
    if name in ['Helix', 'Bitter', 'Supra'] and NEW_MAGNET_STRUCTURE:
        _warn_old_import(
            f"magnetgeo.{name}", 
            f"magnetgeo.components.magnet.{name}"
        )
        return globals().get(name)
    
    # Check if it's a support class that should use new import
    support_classes = ['Chamfer', 'Groove', 'Model3D', 'ModelAxi', 'CoolingSlit', 'Tierod', 'Shape', 'Shape2D']
    if name in support_classes and NEW_SUPPORT_STRUCTURE:
        _warn_old_import(
            f"magnetgeo.{name}",
            f"magnetgeo.components.support.{name}"
        )
        return globals().get(name)
    
    # Default behavior
    try:
        return globals()[name]
    except KeyError:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


if __name__ == "__main__":
    # If run as script, show full diagnostics
    run_diagnostics()

#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Python Magnet Geometry package with new component architecture

This version includes the refactored component structure:
- magnetgeo.components.magnet: Main magnet classes (Helix, Bitter, Supra)
- magnetgeo.components.support: Support components with validation
- magnetgeo.components.structural: Structural components (Ring, Screen, CurrentLeads)
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

# Import structural classes from new location
try:
    from .components.structural import Ring, Screen, InnerCurrentLead, OuterCurrentLead
    NEW_STRUCTURAL_STRUCTURE = True
    print("✓ Using new structural component structure")
except ImportError:
    # Fallback to old imports for transition
    try:
        from .Ring import Ring
        from .Screen import Screen
        from .InnerCurrentLead import InnerCurrentLead
        from .OuterCurrentLead import OuterCurrentLead
        NEW_STRUCTURAL_STRUCTURE = False
        print("⚠ Using legacy structural classes (consider upgrading)")
    except ImportError:
        Ring = Screen = InnerCurrentLead = OuterCurrentLead = None
        NEW_STRUCTURAL_STRUCTURE = False
        print("✗ Structural classes not available")

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
    from .utils import validation, enum_types
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    validation = enum_types = None

# Import YAML compatibility system if available
try:
    from .yaml_compatibility import setup_yaml_compatibility
    YAML_COMPATIBILITY_AVAILABLE = True
    
    # Automatically set up YAML compatibility
    setup_yaml_compatibility()
    print("✓ YAML compatibility system initialized")
    
except ImportError:
    YAML_COMPATIBILITY_AVAILABLE = False
    print("⚠ YAML compatibility system not available")

# Define what's available for import
__all__ = []

# Add available classes to __all__
if Helix is not None:
    __all__.append('Helix')
if Bitter is not None:
    __all__.append('Bitter')
if Supra is not None:
    __all__.append('Supra')
if Ring is not None:
    __all__.append('Ring')
if Screen is not None:
    __all__.append('Screen')
if InnerCurrentLead is not None:
    __all__.append('InnerCurrentLead')
if OuterCurrentLead is not None:
    __all__.append('OuterCurrentLead')
if Insert is not None:
    __all__.append('Insert')
if Bitters is not None:
    __all__.append('Bitters')
if Supras is not None:
    __all__.append('Supras')
if MSite is not None:
    __all__.append('MSite')

# Add support classes if available
support_classes = ['Chamfer', 'Groove', 'Model3D', 'ModelAxi', 'CoolingSlit', 'Tierod', 'Shape', 'Shape2D']
for cls_name in support_classes:
    if globals().get(cls_name) is not None:
        __all__.append(cls_name)

# Add support module if available
if support is not None:
    __all__.append('support')

# Utility functions
def get_available_classes():
    """Get list of available classes"""
    available = {}
    
    # Check magnet classes
    magnet_classes = {'Helix': Helix, 'Bitter': Bitter, 'Supra': Supra}
    available['magnet'] = {k: v is not None for k, v in magnet_classes.items()}
    
    # Check structural classes  
    structural_classes = {
        'Ring': Ring, 'Screen': Screen, 
        'InnerCurrentLead': InnerCurrentLead, 'OuterCurrentLead': OuterCurrentLead
    }
    available['structural'] = {k: v is not None for k, v in structural_classes.items()}
    
    # Check legacy classes
    available['legacy'] = {k: v is not None for k, v in LEGACY_CLASSES.items()}
    
    # Check support classes
    support_classes_dict = {
        'Chamfer': Chamfer, 'Groove': Groove, 'Model3D': Model3D, 'ModelAxi': ModelAxi,
        'CoolingSlit': CoolingSlit, 'Tierod': Tierod, 'Shape': Shape, 'Shape2D': Shape2D
    }
    available['support'] = {k: v is not None for k, v in support_classes_dict.items()}
    
    return available

def print_status():
    """Print current package status"""
    print("\nMagnetGeo Package Status:")
    print(f"  Version: {__version__}")
    print(f"  New magnet structure: {NEW_MAGNET_STRUCTURE}")
    print(f"  New structural structure: {NEW_STRUCTURAL_STRUCTURE}")
    print(f"  New support structure: {NEW_SUPPORT_STRUCTURE}")
    print(f"  YAML compatibility: {YAML_COMPATIBILITY_AVAILABLE}")
    print(f"  Utils available: {UTILS_AVAILABLE}")
    
    available = get_available_classes()
    for category, classes in available.items():
        available_count = sum(classes.values())
        total_count = len(classes)
        print(f"  {category.title()} classes: {available_count}/{total_count} available")

# Optional: Print status when imported (can be disabled with environment variable)
if os.environ.get('MAGNETGEO_QUIET') != '1':
    print(f"MagnetGeo v{__version__} loaded")
    
# Optional: Show warnings for missing components
if os.environ.get('MAGNETGEO_SHOW_WARNINGS') == '1':
    missing_components = []
    if not NEW_MAGNET_STRUCTURE:
        missing_components.append("magnet components")
    if not NEW_STRUCTURAL_STRUCTURE:
        missing_components.append("structural components")
    if not NEW_SUPPORT_STRUCTURE:
        missing_components.append("support components")
    if not YAML_COMPATIBILITY_AVAILABLE:
        missing_components.append("YAML compatibility")
        
    if missing_components:
        warnings.warn(
            f"Some magnetgeo components are using legacy implementations: {', '.join(missing_components)}. "
            "Consider upgrading to the new component structure.",
            UserWarning
        )

# Backward compatibility notice
def _show_migration_notice():
    """Show migration notice for users of old import structure"""
    notice = """
    NOTE: MagnetGeo has been restructured with a new component architecture.
    
    New import structure:
    - from magnetgeo.components.magnet import Helix, Bitter, Supra
    - from magnetgeo.components.structural import Ring, Screen, InnerCurrentLead, OuterCurrentLead
    - from magnetgeo.components.support import Chamfer, Groove, ModelAxi, etc.
    
    Legacy imports still work but consider updating for better performance and features.
    """
    return notice

# Make the migration notice available but don't print it automatically
__migration_notice__ = _show_migration_notice

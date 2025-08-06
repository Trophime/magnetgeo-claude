#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
MagnetGeo Components Package - Updated Structure

This package contains all magnet component classes organized by type:
- magnet: Main magnetic field-generating components (Helix, Bitter, Supra)
- support: Support/auxiliary components (Chamfer, Groove, ModelAxi, etc.)
- structural: Structural components (Ring, Screen, CurrentLeads)
- container: Container components (Insert, Bitters, Supras, MSite) [future]
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

# Import structural components
try:
    from .structural import Ring, Screen, InnerCurrentLead, OuterCurrentLead
    STRUCTURAL_COMPONENTS_AVAILABLE = True
    
    # Make structural components available at package level
    __all__ = ['Ring', 'Screen', 'InnerCurrentLead', 'OuterCurrentLead']
    
    if MAGNET_COMPONENTS_AVAILABLE:
        __all__.extend(['Helix', 'Bitter', 'Supra'])
    
    if SUPPORT_COMPONENTS_AVAILABLE:
        __all__.append('support')
        
except ImportError:
    STRUCTURAL_COMPONENTS_AVAILABLE = False
    Ring = Screen = InnerCurrentLead = OuterCurrentLead = None

# Future imports (placeholder for upcoming migrations)
# from . import container

# Status reporting
def get_component_status():
    """Get status of component imports"""
    return {
        'magnet_components': MAGNET_COMPONENTS_AVAILABLE,
        'support_components': SUPPORT_COMPONENTS_AVAILABLE,
        'structural_components': STRUCTURAL_COMPONENTS_AVAILABLE
    }

# Convenience function to check if all components are available
def all_components_available():
    """Check if all component types are available"""
    status = get_component_status()
    return all(status.values())

if __name__ == "__main__":
    print("MagnetGeo Components Status:")
    status = get_component_status()
    for component_type, available in status.items():
        symbol = "✓" if available else "✗"
        print(f"  {symbol} {component_type}: {available}")

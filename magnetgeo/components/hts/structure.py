#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
HTS Insert geometric structure definition

Defines complete HTS insert geometric structures as assemblies of
double pancakes with isolation between them. Provides support for
the Supra magnet component.
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple
from .tape import Tape
from .pancake import Pancake
from .isolation import Isolation
from .dblpancake import DblPancake

try:
    from ...base.support_base import SupportComponentBase
    from ...utils.validation import validate_positive, validate_non_negative, validate_string_not_empty
    BASE_AVAILABLE = True
except ImportError:
    BASE_AVAILABLE = False
    SupportComponentBase = object
    def validate_positive(val, name): pass
    def validate_non_negative(val, name): pass
    def validate_string_not_empty(val, name): pass


def flatten(nested_list: List) -> List:
    """Flatten nested list structure"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


class HTSinsert(SupportComponentBase if BASE_AVAILABLE else object):
    """
    HTS insert geometric structure definition
    
    Represents complete HTS insert geometry as an assembly of double pancakes
    with isolation layers between them. Serves as geometric support structure
    for the Supra magnet component.
    
    Attributes:
        name: Insert identifier
        z0: Center position of insert assembly
        h: Total height of insert
        r0: Inner radius of insert
        r1: Outer radius of insert
        z1: Bottom position of insert
        n: Number of double pancakes
        dblpancakes: List of double pancake geometries
        isolations: List of isolation geometries between double pancakes
    """
    
    yaml_tag = "!HTSinsert"
    
    def __init__(
        self,
        name: str = "",
        z0: float = 0,
        h: float = 0,
        r0: float = 0,
        r1: float = 0,
        z1: float = 0,
        n: int = 0,
        dblpancakes: List[DblPancake] = None,
        isolations: List[Isolation] = None,
    ):
        """
        Initialize HTS insert geometry
        
        Args:
            name: Insert identifier
            z0: Center position of insert assembly
            h: Total height of insert
            r0: Inner radius of insert
            r1: Outer radius of insert
            z1: Bottom position of insert
            n: Number of double pancakes
            dblpancakes: List of double pancake geometries
            isolations: List of isolation geometries between double pancakes
        """
        if BASE_AVAILABLE:
            super().__init__(name)
        else:
            self.name = str(name)
        
        self.z0 = float(z0)
        self.h = float(h)
        self.r0 = float(r0)
        self.r1 = float(r1)
        self.z1 = float(z1)
        self.n = int(n)
        self.dblpancakes = dblpancakes if dblpancakes is not None else []
        self.isolations = isolations if isolations is not None else []
        
        self.validate()
    
    def validate(self) -> None:
        """Validate HTS insert geometric parameters"""
        if BASE_AVAILABLE:
            super().validate()
        
        validate_string_not_empty(self.name, "name")
        validate_non_negative(self.h, "h (height)")
        validate_non_negative(self.r0, "r0 (inner radius)")
        validate_non_negative(self.r1, "r1 (outer radius)")
        
        if self.r0 >= self.r1:
            raise ValueError(f"Inner radius ({self.r0}) must be less than outer radius ({self.r1})")
        
        if self.n < 0:
            raise ValueError("Number of double pancakes must be non-negative")
        
        # Validate components
        for i, dp in enumerate(self.dblpancakes):
            if dp:
                try:
                    dp.validate()
                except Exception as e:
                    raise ValueError(f"Double pancake {i} validation failed: {e}")
        
        for i, iso in enumerate(self.isolations):
            if iso:
                try:
                    iso.validate()
                except Exception as e:
                    raise ValueError(f"Isolation {i} validation failed: {e}")
    
    # Geometric property methods
    def getZ0(self) -> float:
        """Get center position of insert"""
        return self.z0
    
    def getZ1(self) -> float:
        """Get bottom position of insert"""
        return self.z1
    
    def getZ2(self) -> float:
        """Get top position of insert"""
        return self.z1 + self.h
    
    def getH(self) -> float:
        """Get total height of insert"""
        return self.h
    
    def getR0(self) -> float:
        """Get inner radius of insert"""
        return self.r0
    
    def getR1(self) -> float:
        """Get outer radius of insert"""
        return self.r1
    
    def getW(self) -> float:
        """Get radial width of insert"""
        return self.r1 - self.r0
    
    def getN(self) -> int:
        """Get number of double pancakes"""
        return len(self.dblpancakes)
    
    def getArea(self) -> float:
        """Get insert cross-sectional area in r-z plane"""
        return self.getW() * self.getH()
    
    def get_bounds(self) -> Tuple[List[float], List[float]]:
        """
        Get geometric bounds
        
        Returns:
            Tuple of ([r_min, r_max], [z_min, z_max])
        """
        return ([self.r0, self.r1], [self.z1, self.z1 + self.h])
    
    # Component access methods
    def getNtapes(self) -> List[int]:
        """Get number of tapes for each double pancake"""
        n_tapes = []
        for dp in self.dblpancakes:
            if dp and dp.pancake:
                # Each double pancake has 2 pancakes
                n_tapes.append(2 * dp.pancake.getN())
            else:
                n_tapes.append(0)
        return n_tapes
    
    def getHtapes(self) -> List[float]:
        """Get tape heights for each double pancake"""
        h_tapes = []
        for dp in self.dblpancakes:
            if dp and dp.pancake and dp.pancake.tape:
                h_tapes.append(dp.pancake.tape.getH())
            else:
                h_tapes.append(0.0)
        return h_tapes
    
    def getWtapes_SC(self) -> List[float]:
        """Get superconductor tape widths for each double pancake"""
        w_tapes = []
        for dp in self.dblpancakes:
            if dp and dp.pancake and dp.pancake.tape:
                w_tapes.append(dp.pancake.tape.getW_Sc())
            else:
                w_tapes.append(0.0)
        return w_tapes
    
    def getWtapes_Isolation(self) -> List[float]:
        """Get tape isolation widths for each double pancake"""
        w_iso = []
        for dp in self.dblpancakes:
            if dp and dp.pancake and dp.pancake.tape:
                w_iso.append(dp.pancake.tape.getW_Isolation())
            else:
                w_iso.append(0.0)
        return w_iso
    
    def get_dblpancake_positions(self) -> List[float]:
        """Get z-positions of double pancake centers"""
        return [dp.getZ0() for dp in self.dblpancakes if dp]
    
    def get_dblpancake_bounds(self) -> List[Tuple[float, float]]:
        """Get z-bounds for each double pancake"""
        bounds = []
        for dp in self.dblpancakes:
            if dp:
                bounds.append((dp.getZ1(), dp.getZ2()))
            else:
                bounds.append((0.0, 0.0))
        return bounds
    
    # Naming methods for meshing/CAD
    def get_names(self, mname: str, detail: str, verbose: bool = False) -> List[str]:
        """
        Get component names for meshing/CAD
        
        Args:
            mname: Base name for components
            detail: Detail level ("dblpancake", "pancake", "turn", or "tape")
            verbose: Whether to print verbose info
            
        Returns:
            List of component names
        """
        names = []
        prefix = f"{mname}_" if mname else ""
        
        n_dp = len(self.dblpancakes)
        
        # Double pancake components
        for i, dp in enumerate(self.dblpancakes):
            if dp:
                if verbose:
                    print(f"HTSinsert.get_names: dblpancake[{i}]")
                
                dp_name = f"{prefix}dp{i}"
                dp_names = dp.get_names(dp_name, detail, verbose)
                
                if isinstance(dp_names, str):
                    names.append(dp_names)
                else:
                    names.extend(dp_names)
            
            # Isolation between double pancakes (not after last one)
            if i < n_dp - 1 and i < len(self.isolations):
                iso = self.isolations[i]
                if iso and not iso.is_empty():
                    iso_name = f"{prefix}iso{i}"
                    iso_names = iso.get_names(iso_name, detail, verbose)
                    names.extend(iso_names)
        
        if verbose:
            print(f"HTSinsert '{mname}' total components ({detail}): {len(names)}")
        
        return names
    
    def get_lc(self) -> Tuple[float, ...]:
        """
        Get characteristic lengths for meshing
        
        Returns:
            Tuple of characteristic lengths for different components
        """
        if not self.isolations or not self.dblpancakes:
            return (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        
        # Use first available components for characteristic sizing
        dp = self.dblpancakes[0] if self.dblpancakes else None
        iso = self.isolations[0] if self.isolations else None
        
        if not dp or not dp.pancake or not dp.pancake.tape:
            return (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        
        # Isolation between double pancakes
        lc_iso = iso.getH() / 3.0 if iso else 1.0
        
        # Double pancake
        lc_dp = dp.getH() / 10.0
        
        # Single pancake
        lc_pancake = dp.pancake.getH() / 10.0
        
        # Isolation within double pancake
        lc_dp_iso = dp.isolation.getH() / 3.0 if dp.isolation else 0.3
        
        # Mandrel region
        mandrel_gap = abs(dp.pancake.getMandrin() - dp.pancake.getR0())
        lc_mandrel = mandrel_gap / 3.0 if mandrel_gap > 0 else 0.5
        
        # Superconductor tape
        lc_sc = dp.pancake.tape.getW_Sc() / 5.0
        
        # Tape insulation
        lc_tape_iso = max(dp.pancake.tape.getW_Isolation() / 3.0, 0.1)
        
        return (lc_iso, lc_dp, lc_pancake, lc_dp_iso, lc_mandrel, lc_sc, lc_tape_iso)
    
    # Configuration loading
    @classmethod
    def fromcfg(
        cls,
        inputcfg: str,
        directory: Optional[str] = None,
        debug: Optional[bool] = False,
    ) -> 'HTSinsert':
        """
        Create HTS insert from configuration file
        
        Args:
            inputcfg: Configuration file path
            directory: Optional directory path
            debug: Whether to print debug info
            
        Returns:
            HTSinsert instance
        """
        filename = inputcfg
        if directory is not None:
            filename = os.path.join(directory, filename)
        
        if debug:
            print(f"HTSinsert.fromcfg({filename})")
        
        with open(filename) as f:
            data = json.load(f)
            
            if debug:
                print("HTSinsert configuration data:", list(data.keys()))
        
        # Load base definitions
        base_tape = Tape()
        if "tape" in data:
            base_tape = Tape.from_dict(data["tape"], debug=debug)
        
        base_pancake = Pancake()
        if "pancake" in data:
            base_pancake = Pancake.from_dict(data["pancake"], debug=debug)
            if debug:
                print(f"Base pancake: {base_pancake}")
        
        base_isolation = Isolation()
        if "isolation" in data:
            base_isolation = Isolation.from_dict(data["isolation"], debug=debug)
        
        # Initialize geometry parameters
        z = 0.0
        r0 = r1 = z0 = z1 = h = 0.0
        n = 0
        dblpancakes = []
        isolations = []
        
        if "dblpancakes" in data:
            dp_config = data["dblpancakes"]
            
            if "n" in dp_config:
                # Uniform double pancakes
                n = dp_config["n"]
                if debug:
                    print(f"Creating {n} uniform double pancakes")
                
                # Isolation between double pancakes
                dp_isolation = base_isolation
                if "isolation" in dp_config:
                    dp_isolation = Isolation.from_dict(dp_config["isolation"], debug=debug)
                
                # Create uniform double pancakes
                for i in range(n):
                    dp = DblPancake(z, base_pancake, base_isolation)
                    dblpancakes.append(dp)
                    
                    if i < n - 1:  # Not the last one
                        isolations.append(dp_isolation)
                    
                    z += dp.getH()
                    if i < n - 1:
                        z += dp_isolation.getH()
                
                h = z
                r0 = dblpancakes[0].getR0() if dblpancakes else 0.0
                r1 = dblpancakes[0].getR1() if dblpancakes else 0.0
                
            else:
                # Variable double pancakes
                if debug:
                    print("Creating variable double pancakes")
                
                dp_names = [key for key in dp_config.keys() if key != "isolation"]
                n = len(dp_names)
                
                for i, dp_name in enumerate(dp_names):
                    dp_data = dp_config[dp_name]
                    
                    # Load pancake for this DP
                    if "pancake" in dp_data:
                        pancake = Pancake.from_dict(dp_data["pancake"], debug=debug)
                    else:
                        pancake = base_pancake
                    
                    # Load isolation for this DP
                    if "isolation" in dp_data:
                        isolation = Isolation.from_dict(dp_data["isolation"], debug=debug)
                    else:
                        isolation = base_isolation
                    
                    dp = DblPancake(z, pancake, isolation)
                    dblpancakes.append(dp)
                    
                    # Update geometry bounds
                    if i == 0:
                        r0 = dp.getR0()
                        r1 = dp.getR1()
                    else:
                        r0 = min(r0, dp.getR0())
                        r1 = max(r1, dp.getR1())
                    
                    z += dp.getH()
                    
                    # Add isolation between DPs
                    if i < n - 1:
                        isolations.append(base_isolation)
                        z += base_isolation.getH()
                
                h = z
        
        # Calculate final positions
        z1 = z0 - h / 2.0
        z_current = z1
        
        # Update double pancake positions
        for i, dp in enumerate(dblpancakes):
            dp_height = dp.getH()
            dp.setZ0(z_current + dp_height / 2.0)
            z_current += dp_height
            
            if i < len(isolations):
                z_current += isolations[i].getH()
        
        if debug:
            print("=== HTSinsert geometry loaded ===")
            print(f"Name: {os.path.splitext(os.path.basename(inputcfg))[0]}")
            print(f"Inner radius: {r0:.3f} mm")
            print(f"Outer radius: {r1:.3f} mm")
            print(f"Total height: {h:.3f} mm")
            print(f"Center position: {z0:.3f} mm")
            print(f"Double pancakes: {len(dblpancakes)}")
            for i, dp in enumerate(dblpancakes):
                print(f"  DP[{i}]: z={dp.getZ0():.3f}, h={dp.getH():.3f}")
            print("================================")
        
        name = os.path.splitext(os.path.basename(inputcfg))[0]
        return cls(name, z0, h, r0, r1, z1, n, dblpancakes, isolations)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], debug: bool = False) -> 'HTSinsert':
        """
        Create HTSinsert from dictionary
        
        Args:
            data: Dictionary with insert parameters
            debug: Whether to print debug info
            
        Returns:
            HTSinsert instance
        """
        if debug:
            print(f"Creating HTSinsert from dict: {list(data.keys())}")
        
        # Basic parameters
        name = data.get("name", "")
        z0 = data.get("z0", 0)
        h = data.get("h", 0)
        r0 = data.get("r0", 0)
        r1 = data.get("r1", 0)
        z1 = data.get("z1", 0)
        n = data.get("n", 0)
        
        # Load double pancakes
        dblpancakes = []
        if "dblpancakes" in data:
            for dp_data in data["dblpancakes"]:
                dp = DblPancake.from_dict(dp_data, debug=debug)
                dblpancakes.append(dp)
        
        # Load isolations
        isolations = []
        if "isolations" in data:
            for iso_data in data["isolations"]:
                isolation = Isolation.from_dict(iso_data, debug=debug)
                isolations.append(isolation)
        
        return cls(name, z0, h, r0, r1, z1, n, dblpancakes, isolations)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "z0": self.z0,
            "h": self.h,
            "r0": self.r0,
            "r1": self.r1,
            "z1": self.z1,
            "n": self.n,
            "dblpancakes": [dp.to_dict() for dp in self.dblpancakes],
            "isolations": [iso.to_dict() for iso in self.isolations]
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"HTSinsert(name={self.name}, r0={self.r0:.1f}, r1={self.r1:.1f}, "
                f"h={self.h:.1f}, n_dp={len(self.dblpancakes)})")
    
    def __str__(self) -> str:
        """Detailed string representation"""
        msg = f"HTS Insert Geometry: {self.name}\n"
        msg += f"  Radial extent: {self.r0:.1f} - {self.r1:.1f} mm (width: {self.getW():.1f} mm)\n"
        msg += f"  Axial extent: {self.z1:.1f} - {self.z1 + self.h:.1f} mm (height: {self.h:.1f} mm)\n"
        msg += f"  Center position: z = {self.z0:.1f} mm\n"
        msg += f"  Double pancakes: {len(self.dblpancakes)}\n"
        
        total_tapes = sum(self.getNtapes())
        if total_tapes > 0:
            msg += f"  Total tape turns: {total_tapes}\n"
        
        if self.dblpancakes:
            msg += "  Double pancake positions:\n"
            for i, dp in enumerate(self.dblpancakes):
                msg += f"    DP[{i}]: z={dp.getZ0():.1f} mm, h={dp.getH():.1f} mm\n"
        
        return msg